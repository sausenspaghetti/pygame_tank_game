from pygame import Vector2

from typing import TYPE_CHECKING

# hack
if TYPE_CHECKING:
    from game_state import GameState


class GameItem:
    def __init__(self, state: "GameState", position: Vector2, tile: Vector2):
        self.state = state
        self.position = position
        self.tile = tile
        self.orientation = 0                # angle
        self.status = 'alive'  

        self.weaponTarget = Vector2(0, 1)   # default


class Unit(GameItem):
    def __init__(self, state: "GameState", position: Vector2, tile: Vector2):
        super().__init__(state, position, tile)
        
        self.weaponTarget = Vector2(0, 1)   
        self.lastBulletEpoch = -100


class Bullet(GameItem):
    def __init__(self, state: "GameState", unit: "Unit"):
        super().__init__(state, unit.position, Vector2(6, 1))

        self.unit = unit
        self.startPosition = unit.position
        self.endPosition = unit.weaponTarget
        self.direction = (self.endPosition - self.startPosition).normalize()


class Tank(Unit):
    pass


class Tower(Unit):
    pass