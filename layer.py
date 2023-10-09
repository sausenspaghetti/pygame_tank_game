import math

import pygame
from pygame import Vector2

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user_interface import UserInterface
    from unit import Unit
    from game_state import GameState


class Layer:
    def __init__(self, ui: "UserInterface", imageFile: str):
        self.ui = ui
        self.texture = pygame.image.load(imageFile)

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
        

    def render(self):
        NotImplemented


class ArrayLayer(Layer):
    def __init__(self, ui: "UserInterface", imageFile: str, gameState: "GameState", array: list[list[Vector2]]):
        super().__init__(ui, imageFile)
        self.array = array
        self.gameState = gameState

    def render(self):
        for y in range(self.gameState.worldHeight):
            for x in range(self.gameState.worldWidth):
                tile = self.array[y][x]
                if tile is not None:
                    self.renderTile(self.ui.window, Vector2(x, y), tile)



class UnitsLayer(Layer):
    def __init__(self, ui: "UserInterface", imageFile: str, gameState: "GameState", units: list["Unit"]):
        super().__init__(ui, imageFile)
        self.units = units
        self.gameState = gameState


    def render(self):
        for unit in self.units:
            self.renderTile(self.ui.window, unit.position, unit.tile, unit.orientation)
            target = unit.weaponTarget - unit.position
            angle = math.atan2(-target.x, -target.y) * 180 / math.pi

            self.renderTile(self.ui.window, unit.position, Vector2(0, 6), angle)
