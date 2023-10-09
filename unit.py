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
    def __init__(self, state: "GameState", position: Vector2, tile: Vector2):
        super().__init__(state, position, tile)

        self.startPosition = Vector2(0, 0)
        self.endPosition = Vector2(0, 0)


class Tank(Unit):
    pass


class Tower(Unit):
    pass