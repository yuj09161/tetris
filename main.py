import pygame,random,sys


#Define pygame.Colors constant
RED=pygame.Color(255,0,0)
GREEN=pygame.Color(0,255,0)
BLUE=pygame.Color(0,0,255)
BLACK=pygame.Color(0,0,0)
GRAY=pygame.Color(128,128,128)
WHITE=pygame.Color(255,255,255)

#Define constants
SHAPE=(((0,1,1),(1,1,0)),((1,1),(1,1)),((1,1,1,1),),((0,1,0),(1,1,1)))


#Define global settings
SIZE=(600,600)
FPS=5
BLOCK_SIZE=36


#Define global variables
clocker=pygame.time.Clock()
display=pygame.display.set_mode(SIZE)


#Block class
class Block(pygame.sprite.Sprite):
    def __init__(self,pos,color,size=None):
        assert type(pos) is list, f'type error: type of pos {type(pos)}'
        assert len(pos)==2, f'length error: length of pos {len(pos)}'
        assert type(size) is list or type(size) is tuple or type(size)==type(None), f'type error: type of size {type(size)}'
        assert len(pos)==2, 'length error'
        super().__init__()
        self.__pos=pos
        self.__color=color
        if size:
            self.__size=size
        else:
            self.__size=(BLOCK_SIZE,BLOCK_SIZE)
        self.rect=pygame.Rect(self.__pos,self.__size)
    
    def update(self,*,pos=None,spd=None,size=None,color=None):
        #get position & update position
        if pos:
            assert type(pos) is list and len(pos)==2, 'length error'
            self.rect.move_ip([pos[k]-self.__pos[k] for k in range(2)])
            self.__pos=pos
        elif spd:
            assert type(spd) is list or type(spd) is tuple, f'type error: type of spd {type(spd)}'
            assert len(spd)==2, f'length of spd:{len(spd)}!=2:length of pos'
            if 30<=self.__pos[0]<=354:
                self.__pos[0]+=spd[0]
            else:
                spd[0]=0
            self.__pos[1]+=spd[1]
            self.rect.move_ip(*spd)
            print(self.__pos,spd,self.rect)
        if size:
            assert type(size) is list or type(size) is tuple, f'type error: type of size {type(size)}'
            assert len(pos)==2, 'length error'
            size=self.__size
            self.rect.w=size[0]
            self.rect.h=size[1]
        
        #draw block
        if not color:
            color=self.__color
        pygame.draw.rect(display,color,self.rect)
    
    def get_pos(self):
        return (self.rect.x,self.rect.y)
    
    def get_y(self):
        return self.rect.y


#Main Run class
class Main:
    def __init__(self):
        self.__running=True
        
        self.__x_spd=0
        self.__y_multi=1
        self.__block_g=[]
        self.__fixed_g=[]
        
        self.__run()
    
    def __run(self):
        self.__next_block()
        while self.__running:
            self.__event_handler()
            self.__display_handler()
            self.__get_colision()
            pygame.display.flip()
            clocker.tick(FPS)
        self.__quit()
    
    def __next_block(self):
        print('next')
        block=SHAPE[random.randint(0,len(SHAPE)-1)]
        color=random.choice((RED,GREEN,BLUE,GRAY))
        for k in range(len(block)):
            for j in range(len(block[0])):
                if block[k][j]:
                    self.__block_g.append(Block([(j+(9-len(block[0]))//2)*BLOCK_SIZE+30,k*BLOCK_SIZE+30],color))
    
    def __get_colision(self):
        y=[]
        for block in self.__block_g:
            pos_b=block.get_pos()
            for f_block in self.__fixed_g:
                pos_f=f_block.get_pos()
                if (pos_b[0]==pos_f[0] and -BLOCK_SIZE<=pos_b[1]-pos_f[1]<=BLOCK_SIZE or
                    pos_b[1]==pos_f[1] and -BLOCK_SIZE<=pos_b[0]-pos_f[0]<=BLOCK_SIZE):
                    self.__fixed_g+=self.__block_g
                    self.__block_g=[]
                    self.__next_block()
                    return
            y.append(pos_b[1])
        if max(y)>=534:
            self.__fixed_g+=self.__block_g
            self.__block_g=[]
            self.__next_block()
    
    def __event_handler(self):
        RESET_XSPEED=True
        for event in pygame.event.get():
            event_type=event.type
            if event_type==pygame.QUIT:
                self.__running=False
            elif event_type==pygame.KEYDOWN:
                RESET_XSPEED=False
                print(event.key)
                if event.key==274: #down
                    print('down')
                    self.__y_multi=2
                else:
                    self.__y_multi=1
                if event.key==275: #right
                    print('right')
                    self.__x_spd=BLOCK_SIZE
                    for block in self.__block_g:
                        x,y=block.get_pos()
                        if x>=318 or :
                            self.__x_spd=0
                elif event.key==276: #left
                    print('left')
                    self.__x_spd=-BLOCK_SIZE
                    for block in self.__block_g:
                        x,y=block.get_pos()
                        if x<=30:
                            self.__x_spd=0
                else:
                    self.__x_spd=0
        if RESET_XSPEED:
            self.__x_spd=0
    
    def __display_handler(self):
        display.fill(WHITE)
        pygame.draw.rect(display,BLACK,pygame.Rect(30,30,BLOCK_SIZE*9,BLOCK_SIZE*15))
        for block in self.__block_g:
            block.update(spd=[self.__x_spd,BLOCK_SIZE*self.__y_multi])
        print('#####')
        for block in self.__fixed_g:
            blocimport pygame,random,sys


#Define pygame.Colors constant
RED=pygame.Color(255,0,0)
GREEN=pygame.Color(0,255,0)
BLUE=pygame.Color(0,0,255)
BLACK=pygame.Color(0,0,0)
GRAY=pygame.Color(128,128,128)
WHITE=pygame.Color(255,255,255)

#Define constants
SHAPE=(((0,1,1),(1,1,0)),((1,1),(1,1)),((1,1,1,1),),((0,1,0),(1,1,1)))


#Define global settings
SIZE=(600,600)
FPS=5
BLOCK_SIZE=36


#Define global variables
clocker=pygame.time.Clock()
display=pygame.display.set_mode(SIZE)


#Block class
class Block(pygame.sprite.Sprite):
    def __init__(self,pos,color,size=None):
        assert type(pos) is list, f'type error: type of pos {type(pos)}'
        assert len(pos)==2, f'length error: length of pos {len(pos)}'
        assert type(size) is list or type(size) is tuple or type(size)==type(None), f'type error: type of size {type(size)}'
        assert len(pos)==2, 'length error'
        super().__init__()
        self.__pos=pos
        self.__color=color
        if size:
            self.__size=size
        else:
            self.__size=(BLOCK_SIZE,BLOCK_SIZE)
        self.rect=pygame.Rect(self.__pos,self.__size)
    
    def update(self,*,pos=None,spd=None,size=None,color=None):
        #get position & update position
        if pos:
            assert type(pos) is list and len(pos)==2, 'length error'
            self.rect.move_ip([pos[k]-self.__pos[k] for k in range(2)])
            self.__pos=pos
        elif spd:
            assert type(spd) is list or type(spd) is tuple, f'type error: type of spd {type(spd)}'
            assert len(spd)==2, f'length of spd:{len(spd)}!=2:length of pos'
            if 30<=self.__pos[0]<=354:
                self.__pos[0]+=spd[0]
            else:
                spd[0]=0
            self.__pos[1]+=spd[1]
            self.rect.move_ip(*spd)
            print(self.__pos,spd,self.rect)
        if size:
            assert type(size) is list or type(size) is tuple, f'type error: type of size {type(size)}'
            assert len(pos)==2, 'length error'
            size=self.__size
            self.rect.w=size[0]
            self.rect.h=size[1]
        
        #draw block
        if not color:
            color=self.__color
        pygame.draw.rect(display,color,self.rect)
    
    def get_pos(self):
        return (self.rect.x,self.rect.y)
    
    def get_y(self):
        return self.rect.y


#Main Run class
#class Main:
class Main(pygame.Surface):
    def __init__(self):
        self.__running=True
        
        self.__x_spd=0
        self.__y_multi=1
        self.__block_g=[]
        self.__fixed_g=[]
        
        self.__run()
    
    def __run(self):
        self.__next_block()
        while self.__running:
            self.__event_handler()
            self.__display_handler()
            self.__get_colision()
            pygame.display.flip()
            clocker.tick(FPS)
        self.__quit()
    
    def __next_block(self):
        print('next')
        block=SHAPE[random.randint(0,len(SHAPE)-1)]
        color=random.choice((RED,GREEN,BLUE,GRAY))
        for k in range(len(block)):
            for j in range(len(block[0])):
                if block[k][j]:
                    self.__block_g.append(Block([(j+(9-len(block[0]))//2)*BLOCK_SIZE+30,k*BLOCK_SIZE+30],color))
    
    def __get_colision(self):
        y=[]
        for block in self.__block_g:
            pos_b=block.get_pos()
            for f_block in self.__fixed_g:
                pos_f=f_block.get_pos()
                if pos_b[0]==pos_f[0] and pos_b[1]==pos_f[1]-BLOCK_SIZE:
                    self.__fixed_g+=self.__block_g
                    self.__block_g=[]
                    self.__next_block()
                    return
            y.append(pos_b[1])
        if max(y)>=534:
            self.__fixed_g+=self.__block_g
            self.__block_g=[]
            self.__next_block()
    
    def __event_handler(self):
        RESET_XSPEED=True
        for event in pygame.event.get():
            event_type=event.type
            if event_type==pygame.QUIT:
                self.__running=False
            elif event_type==pygame.KEYDOWN:
                RESET_XSPEED=False
                print(event.key)
                if event.key==274: #down
                    print('down')
                    self.__y_multi=2
                else:
                    self.__y_multi=1
                if event.key==275: #right
                    print('right')
                    if max(block.get_pos()[0] for block in self.__block_g)<318:
                        self.__x_spd=BLOCK_SIZE
                    else:
                        self.__x_spd=0
                elif event.key==276: #left
                    print('left')
                    if min(block.get_pos()[0] for block in self.__block_g)>30:
                        self.__x_spd=-BLOCK_SIZE
                    else:
                        self.__x_spd=0
                else:
                    self.__x_spd=0
        if RESET_XSPEED:
            self.__x_spd=0
    
    def __display_handler(self):
        display.fill(WHITE)
        pygame.draw.rect(display,BLACK,pygame.Rect(30,30,BLOCK_SIZE*9,BLOCK_SIZE*15))
        for block in self.__block_g:
            block.update(spd=[self.__x_spd,BLOCK_SIZE*self.__y_multi])
        print('#####')
        for block in self.__fixed_g:
            block.update()
    
    def __quit(self):
        pygame.display.quit()
        pygame.quit()


#Launcher
if __name__=='__main__':
    Main()k.update()
    
    def __quit(self):
        pygame.display.quit()
        pygame.quit()


#Launch
if __name__=='__main__':
    Main()