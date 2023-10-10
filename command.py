import pygame
from pygame import Vector2

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_state import GameState
    from unit import Unit, GameItem

from unit import Bullet



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
        
