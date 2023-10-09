import pygame
from pygame import Vector2

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_state import GameState
    from unit import Unit


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


