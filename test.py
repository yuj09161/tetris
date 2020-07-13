import pygame,sys


#Define pygame.Colors
RED=pygame.Color(255,0,0)
GREEN=pygame.Color(0,255,0)
BLUE=pygame.Color(0,0,255)
BLACK=pygame.Color(0,0,0)
GRAY=pygame.Color(128,128,128)
WHITE=pygame.Color(255,255,255)


#Define global settings
SIZE=(800,600)
FPS=60


#Define global variables
clocker=pygame.time.Clock()
display=pygame.display.set_mode(SIZE)


#Block class
class Block(pygame.sprite.Sprite):
    def __init__(self,size):
        assert type(size) is tuple
        super().__init__()
        


#Main Run class
class Main:
    def __init__(self):
        self.__running=True
        
        self.__run()
    
    def __run(self):
        while self.__running:
            self.__event_handler()
            #self.__graphic_handler()
            display.fill(WHITE)
            pygame.display.flip()
            clocker.tick(FPS)
        self.__quit()
    
    def __event_handler(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.__running=False
    
    def __display_handler(self):
        pass
    
    def __quit(self):
        pygame.display.quit()
        pygame.quit()


#Launcher
if __name__=='__main__':
    Main()
    sys.exit()