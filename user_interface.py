import os
from os.path import join

import pygame
from pygame import Vector2

from game_state import GameState
from layer import ArrayLayer, UnitsLayer, Layer
from unit import Unit
from command import MoveCommand, TargetCommand, Command


os.environ['SDL_VIDEO_CENTERED'] = '1'
FPS = 30


class UserInterface:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Python test game')
        pygame.display.set_icon(pygame.image.load(join('images', 'icon2.png')))

        self.gameState = GameState()
        self.cellSize = Vector2(64, 64)

        # (x1, y1) * (x2, y2) --> (x1*x2, y1*y2)
        worldSize = self.gameState.worldSize.elementwise() * self.cellSize
        self.window = pygame.display.set_mode((int(worldSize.x), int(worldSize.y)))

        self.layers: list[Layer] = [
            ArrayLayer(self, join('images', 'background', 'ground.png'), self.gameState, self.gameState.ground),
            ArrayLayer(self, join('images', 'background', 'walls.png'), self.gameState, self.gameState.walls),
            UnitsLayer(self, join('images', 'units','units.png'), self.gameState, self.gameState.units)
        ]

        self.commands: list[Command] = []

        # other staffs
        self.running = True
        self.clock = pygame.time.Clock()
        self.playerUnit = self.gameState.units[0]   # hack


    @property
    def cellWidth(self):
        return int(self.cellSize.x)
    
    
    @property
    def cellHeight(self):
        return int(self.cellSize.y)


    def processInput(self):
        moveVector = Vector2(0, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    moveVector = Vector2(1, 0)
                elif event.key == pygame.K_LEFT:
                    moveVector = Vector2(-1, 0)
                elif event.key == pygame.K_UP:
                    moveVector = Vector2(0, -1)
                elif event.key == pygame.K_DOWN:
                    moveVector = Vector2(0, 1)
        
        if not self.running:
            return
        
        # add TargetCommand for main unit
        mousePos = Vector2(pygame.mouse.get_pos())
        targetVector = Vector2(mousePos.x / self.cellWidth, mousePos.y / self.cellHeight) - Vector2(0.5, 0.5)      
        cmd = TargetCommand(self.gameState, self.playerUnit, targetVector)
        self.commands.append(cmd)

        # if tank is moving then add MoveCommand
        if moveVector.x != 0 or moveVector.y != 0:
            cmd = MoveCommand(self.gameState, self.playerUnit, moveVector)
            self.commands.append(cmd)

        # for all unit except playerUnit add TargetCommand (direction is player)
        for unit in self.gameState.units:
            if unit != self.playerUnit:
                cmd = TargetCommand(self.gameState, unit, self.playerUnit.position)
                self.commands.append(cmd)
        
        

    def update(self):
        for cmd in self.commands:
            cmd.run()
        self.commands.clear()


    def render(self):
        for layer in self.layers:
            layer.render()
        pygame.display.update()


    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()



