import math

import pygame
from pygame import Vector2

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user_interface import UserInterface
    from unit import Unit, Bullet
    from game_state import GameState


class GameStateObserver:
    def unitDestroyed(self, unit):
        pass



class Layer(GameStateObserver):
    def __init__(self, ui: "UserInterface", imageFile: str):
        super().__init__()
        self.ui = ui
        self.texture = pygame.image.load(imageFile)
        self.imageFile = imageFile

    def renderTile(self, surface: pygame.Surface, position: Vector2, tile: Vector2, angle=None):
        spritePos = position.elementwise() * self.ui.cellSize
        texturePos = tile.elementwise() * self.ui.cellSize
        textureRect = pygame.Rect(
            int(texturePos.x),
            int(texturePos.y),
            int(self.ui.cellSize.x),
            int(self.ui.cellSize.y)
        )
        if angle is None:
            surface.blit(self.texture, spritePos, textureRect)
        else:
            # extract image on isolate Surface
            textureTile = pygame.Surface((self.ui.cellWidth, self.ui.cellHeight), pygame.SRCALPHA)
            textureTile.blit(self.texture, (0, 0), textureRect)

            # rotate image
            rotatedTile = pygame.transform.rotate(textureTile, angle)

            # calculate position
            dx = (rotatedTile.get_width() - textureTile.get_width()) // 2
            dy = (rotatedTile.get_height() - textureTile.get_height()) // 2
            spritePos = spritePos - Vector2(dx, dy)

            surface.blit(rotatedTile, spritePos)
        

    def render(self, surface: pygame.Surface):
        NotImplemented

    
    def setTileset(self, cellSize, imageFile):
        self.texture = pygame.image.load(imageFile)
        self.imageFile = imageFile




class ArrayLayer(Layer):
    def __init__(self, ui: "UserInterface", imageFile: str, gameState: "GameState", array: list[list[Vector2]]):
        super().__init__(ui, imageFile)
        self.array = array
        self.gameState = gameState

    def render(self,surface: pygame.Surface):
        for y in range(self.gameState.worldHeight):
            for x in range(self.gameState.worldWidth):
                tile = self.array[y][x]
                if tile is not None:
                    # self.renderTile(self.ui.window, Vector2(x, y), tile)
                    self.renderTile(surface, Vector2(x, y), tile)

    



class UnitsLayer(Layer):
    def __init__(self, ui: "UserInterface", imageFile: str, gameState: "GameState", units: list["Unit"]):
        super().__init__(ui, imageFile)
        self.units = units
        self.gameState = gameState


    def render(self, surface: pygame.Surface):
        for unit in self.units:
            # self.renderTile(self.ui.window, unit.position, unit.tile, unit.orientation)
            self.renderTile(surface, unit.position, unit.tile, unit.orientation)
            target = unit.weaponTarget - unit.position
            angle = math.atan2(-target.x, -target.y) * 180 / math.pi

            # self.renderTile(self.ui.window, unit.position, Vector2(0, 6), angle)
            self.renderTile(surface, unit.position, Vector2(0, 6), angle)


class BulletLayer(Layer):
    def __init__(self, ui: "UserInterface", imageFile: str, gameState: "GameState", bullets: list["Bullet"]):
        super().__init__(ui, imageFile)
        self.bullets = bullets
        self.gameState = gameState

    def render(self, surface: pygame.Surface):
        for bullet in self.bullets:
            # self.renderTile(self.ui.window, bullet.position, bullet.tile)
            self.renderTile(surface, bullet.position, bullet.tile)


class ExplosionsLayer(Layer):
    def __init__(self, ui: "UserInterface", imageFile: str):
        super().__init__(ui, imageFile)
        self.explosions = []
        self.maxFrameIndex = 27

    def add(self, position: Vector2):
        self.explosions.append({
            'position': position,
            'frameIndex': 0
        })

    def render(self, surface: pygame.Surface):
        for explosion in self.explosions:
            frameIndex = int(explosion['frameIndex'])
            self.renderTile(surface, explosion['position'], Vector2(frameIndex, 4))
            explosion['frameIndex'] += 0.5

        self.explosions = [ex for ex in self.explosions if ex['frameIndex'] <= self.maxFrameIndex]
    
    def unitDestroyed(self, unit: "Unit"):
        self.add(unit.position)



    
    
