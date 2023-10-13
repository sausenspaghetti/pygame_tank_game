import os
import tmx

import pygame
from pygame import Vector2

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from game_state import GameState
    from unit import Unit, GameItem
    from user_interface import UserInterface

from unit import Bullet, Tank, Tower, Unit



class OrientationError(Exception):
    pass


class Command:
    def run(self):
        raise NotImplementedError()
    

class MoveCommand(Command):

    def __init__(self, state: "GameState", unit: "Unit", moveVector: Vector2):
        self.state = state
        self.unit = unit
        self.moveVector = moveVector
    
    def run(self):
        newPos = self.unit.position + self.moveVector
        if not self.state.inside_world(newPos):
            return
    

        # Collisions with walls aren't allowed
        if not self.state.walls[int(newPos.y)][int(newPos.x)] is None:
            return
        
        
        # Collisions with other unit aren't allowed
        for unit in self.state.units:
            if unit != self.unit:
                if unit.position == newPos:
                    return
        
        self.unit.position = newPos  

        # choose orientation  
        if self.moveVector.x < 0: 
            self.unit.orientation = 90
        elif self.moveVector.x > 0: 
            self.unit.orientation = -90
        if self.moveVector.y < 0: 
            self.unit.orientation = 0
        elif self.moveVector.y > 0: 
            self.unit.orientation = 180
        

class TargetCommand(Command):
    
    def __init__(self, state: "GameState", unit: "Unit", targetVector: Vector2):
        self.state = state
        self.unit = unit
        self.targetVector = targetVector

    def run(self):
        self.unit.weaponTarget = self.targetVector


class ShootCommand(Command):
    def __init__(self, state: "GameState", unit: "Unit"):
        self.state = state
        self.unit = unit

    def run(self):
        if self.unit.status != 'alive':
            return
        if self.state.epoch - self.unit.lastBulletEpoch < self.state.bulletDelay:
            return
        self.unit.lastBulletEpoch = self.state.epoch
        self.state.bullets.append(Bullet(self.state, self.unit))


class MoveBulletCommand(Command):
    def __init__(self, state: "GameState", bullet: "Bullet"):
        self.state = state
        self.bullet = bullet
    
    def run(self):
        newPos = self.bullet.position + self.bullet.direction * self.state.bulletSpeed * 0.1
        newCenterPos = newPos + Vector2(0.5, 0.5)

        # outside the screen
        if not self.state.inside_world(newPos):
            self.bullet.status = 'destroyed'
            return

        # outside the range
        if newPos.distance_to(self.bullet.startPosition) >= self.state.bulletRange:
            self.bullet.status = 'destroyed'
            return
        
        # 
        unit = self.state.findLiveUnit(newCenterPos)
        if not unit is None and self.bullet.unit != unit:
            unit.status = 'destroyed'
            self.bullet.status = 'destroyed'
            self.state.notifyDestroyed(unit)
            return
        
        self.bullet.position = newPos


class DeleteDestroyedCommand(Command):
    def __init__(self, itemList: list["GameItem"]):
        self.itemList = itemList
    
    def run(self):
        self.itemList[:] = [item for item in self.itemList if item.status == 'alive']
        

class LoadLevelCommand(Command):
    def __init__(self, ui: "UserInterface", fileName: str):
        self.ui = ui
        self.fileName = fileName

    def run(self):
        if not os.path.exists(self.fileName):
            raise RuntimeError('No such file {}'.format(self.fileName))
        tileMap: tmx.TileMap = tmx.TileMap.load(self.fileName)

        if tileMap.orientation != 'orthogonal':
            raise RuntimeError("Error in {}: invalid orientation".format(self.fileName))
        
        if len(tileMap.layers) != 5:
            raise RuntimeError("Error in {}: 5 layers are expected".format(self.fileName))
        

        state = self.ui.gameState
        state.worldSize = Vector2(tileMap.width,tileMap.height) 

        # load Ground tileset
        tileset, array = self.decodeArrayLayer(tileMap,tileMap.layers[0])
        cellSize = Vector2(tileset.tilewidth,tileset.tileheight)
        state.ground[:] = array
        imageFile = tileset.image.source
        self.ui.layers[0].setTileset(cellSize, imageFile)

        # load walls tilesets
        tileset, array = self.decodeArrayLayer(tileMap,tileMap.layers[1])
        if tileset.tilewidth != cellSize.x or tileset.tileheight != cellSize.y:
            raise RuntimeError("Error in {}: tile sizes must be the same in all layers".format(self.fileName))
        state.walls[:] = array
        imageFile = tileset.image.source
        self.ui.layers[1].setTileset(cellSize,imageFile)

        # load tank and towers 
        tanksTileset, tanks = self.decodeUnitsLayer(state,tileMap,tileMap.layers[3], Tank)
        towersTileset, towers = self.decodeUnitsLayer(state,tileMap,tileMap.layers[2], Tower)
        if tanksTileset != towersTileset:
            raise RuntimeError("Error in {}: tanks and towers tilesets must be the same".format(self.fileName))
        if tanksTileset.tilewidth != cellSize.x or tanksTileset.tileheight != cellSize.y:
            raise RuntimeError("Error in {}: tile sizes must be the same in all layers".format(self.fileName))
        state.units[:] = tanks + towers
        cellSize = Vector2(tanksTileset.tilewidth,tanksTileset.tileheight)
        imageFile = tanksTileset.image.source
        self.ui.layers[2].setTileset(cellSize,imageFile)

        # set player Unit
        self.ui.playerUnit = tanks[0]


        # load bullets
        tileset, array = self.decodeArrayLayer(tileMap,tileMap.layers[4])
        if tileset.tilewidth != cellSize.x or tileset.tileheight != cellSize.y:
            raise RuntimeError("Error in {}: tile sizes must be the same in all layers".format(self.fileName))
        state.bullets.clear()
        imageFile = tileset.image.source
        self.ui.layers[3].setTileset(cellSize,imageFile)

        windowSize = state.worldSize.elementwise() * cellSize
        self.ui.window = pygame.display.set_mode((int(windowSize.x),int(windowSize.y))) 

        
    
    def decodeArrayLayer(self, tileMap: tmx.TileMap, layer: tmx.Layer) -> Tuple[tmx.Tileset, list[list[Vector2]]]:
        tileset = self.decodeLayer(tileMap, layer)

        array: list[list[Vector2]] = [None] * tileMap.height
        for y in range(tileMap.height):
            array[y] = [None] * tileMap.width
            for x in range(tileMap.width):
                tile = layer.tiles[x + y * tileMap.width]
                if tile.gid == 0:
                    continue # 274 = 531 - 257
                lid = tile.gid - tileset.firstgid
                if lid < 0 or lid >= tileset.tilecount:
                    raise RuntimeError("Error in {}: invalid tile id".format(self.fileName))
                
                tileX = lid % tileset.columns
                tileY = lid // tileset.columns
                array[y][x] = Vector2(tileX, tileY)


        return tileset, array


    def decodeUnitsLayer(self, state, tileMap, layer, clsUnit=Unit):
        tileset = self.decodeLayer(tileMap, layer)

        array = []
        for y in range(tileMap.height):
            for x in range(tileMap.width):
                tile = layer.tiles[x + y * tileMap.width]
                if tile.gid == 0:
                    continue
                lid = tile.gid - tileset.firstgid
                
                if lid < 0 or lid >= tileset.tilecount:
                    raise RuntimeError("Error in {}: invalid tile id".format(self.fileName))

                tileX = lid % tileMap.width
                tileY = lid // tileMap.width
                array.append(clsUnit(state=state, position=Vector2(x, y), tile=Vector2(tileX, tileY)))

        return tileset, array
        


    def decodeLayer(self, tileMap: tmx.TileMap, layer: tmx.Layer) -> tmx.Tileset:
        if not isinstance(layer, tmx.Layer):
            raise RuntimeError("Error in {}: invalid layer type".format(self.fileName))
        if len(layer.tiles) != tileMap.width * tileMap.height:
            raise RuntimeError("Error in {}: invalid layer size".format(self.fileName))

        gid = None
        for tile in layer.tiles:
            if tile.gid != 0:
                gid = tile.gid
                break
        if gid is None:
            if len(tileMap.tilesets) == 0:
                raise RuntimeError("Error in {}: no tilesets".format(self.fileName))
            tileset = tileMap.tilesets[-1]  
        else:
            tileset = None
            for tset in tileMap.tilesets:
                if tset.firstgid <= gid and gid < tset.firstgid + tset.tilecount:
                    tileset = tset
                    break
        
            if tileset is None:
                raise RuntimeError("Error in {}: no corresponding tileset for gid {}".format(self.fileName, gid))

        if tileset.columns <= 0:
            raise RuntimeError("Error in {}: invalid columns count".format(self.fileName))
        if tileset.image.data is not None:
            raise RuntimeError("Error in {}: embedded tileset image is not supported".format(self.fileName))
        
        return tileset



    




