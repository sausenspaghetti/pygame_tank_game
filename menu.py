import pygame
from os.path import join


class Menu:

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((16 * 64, 10 * 64))
        pygame.display.set_caption('Python pattern\'s')
        pygame.display.set_icon(pygame.image.load(join('images', 'icon2.png')))

        self.titleFont = pygame.font.Font(join('fonts', 'big-shot.ttf'), 42)
        self.itemFont = pygame.font.Font(join('fonts', 'big-shot.ttf'), 30)
        self.menuItem = [
            {
                'action': lambda: self.load_level(join('maps', 'level1.tmx')),
                'title': 'Level 1' 
            },
            
            {
                'action': lambda: self.load_level(join('maps', 'level2.tmx')),
                'title': 'Level 2' 
            },
            {
                'action': lambda: self.exit_menu(),
                'title': 'Quit' 
            }
        ]
        
        self.currentMenuItem = 0
        self.menuCursor = pygame.image.load(join('images','cursor.png'))

        _, itemHeight = self.itemFont.size(self.menuItem[0]['title'])
        self.menuCursor = pygame.transform.scale(self.menuCursor, (itemHeight, itemHeight))
        print(itemHeight)

        self.running = True
        self.clock = pygame.time.Clock()

    def load_level(self, fileName):
        print('{} is loading...'.format(fileName))
        

    def exit_menu(self):
        print('Window is closing...')

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.exit_menu()
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.currentMenuItem = max(0, self.currentMenuItem - 1)
                elif event.key == pygame.K_DOWN:
                    self.currentMenuItem = min(len(self.menuItem) - 1, self.currentMenuItem + 1)
                elif event.key == pygame.K_RETURN:
                    menuItem = self.menuItem[self.currentMenuItem]
                    try:
                        menuItem['action']()
                    except Exception as ex:
                        print(ex)
                


                

    def update(self):
        pass

    def render(self):
        self.window.fill('black')
        y = 50

        # Title
        surface = self.titleFont.render('TANK BATTLEGROUND!!!', True, (200, 0, 0))
        x = (self.window.get_width() - surface.get_width()) // 2
        self.window.blit(surface, (x, y))

        y += (surface.get_height() * 200)  // 100

        # calculate width of items
        widthItem = 0
        for item in self.menuItem:
            surface = self.itemFont.render(item['title'], True, (200, 0, 0))
            widthItem = max(widthItem, surface.get_width())
            item['surface'] = surface
        
        x = (self.window.get_width() - widthItem) // 2
        for index, item in enumerate(self.menuItem):
            self.window.blit(item['surface'], (x, y))

            if index == self.currentMenuItem:
                cursorX = x - self.menuCursor.get_width() - 10
                cursorY = y
                self.window.blit(self.menuCursor, (cursorX, cursorY))

            y += (item['surface'].get_height() * 120) // 100



        pygame.display.update()


    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(30)
        # pygame.quit()

    

if __name__ == '__main__':
    menu = Menu()
    menu.run()