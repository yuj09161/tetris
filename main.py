import pygame,random
import sys,time
pygame.font.init()


#Define pygame.Colors constant
RED     = pygame.Color(255,0,0)
GREEN   = pygame.Color(0,255,0)
BLUE    = pygame.Color(0,0,255)
YELLOW  = pygame.Color(255,255,0)
CYAN    = pygame.Color(0,255,255)
MAGENTA = pygame.Color(255,0,255)
BLACK   = pygame.Color(0,0,0)
GRAY    = pygame.Color(128,128,128)
WHITE   = pygame.Color(255,255,255)

#Define constants
SHAPE=(((0,1,1),(1,1,0),RED),((1,1),(1,1),GREEN),((1,1,1,1),BLUE),((1,1,1,1),(0,0,0,1),YELLOW),((0,1,0),(1,1,1),CYAN))
#SHAPE=(((0,1,0),(1,1,1)),)
TXTFONT=pygame.font.SysFont('NanumBarunGothic',50)


#Define global settings
SIZE=(600,600)
FPS=60
BLOCK_SIZE=36
SPD=5
DOWNSPD=60/SPD

#direction flags
N  = 0b00000001
NE = 0b00000010
E  = 0b00000100
SE = 0b00001000
S  = 0b00010000
SW = 0b00100000
W  = 0b01000000
NW = 0b10000000


#Define global variables
clocker=pygame.time.Clock()
display=pygame.display.set_mode(SIZE)


#Block class
class Block(pygame.sprite.Sprite):
    def __init__(self,pos,color,size=None):
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
            self.__pos=pos
            self.rect.move_ip([pos[k]-self.__pos[k] for k in range(2)])
        elif spd:
            for k in range(2):
                self.__pos[k]+=spd[k]
            self.rect.move_ip(*spd)
        if size:
            self.__size=size
            self.rect.w=size[0]
            self.rect.h=size[1]
        
        #draw block
        if not color:
            color=self.__color
        pygame.draw.rect(display,color,self.rect)
    
    def get_pos(self):
        return self.__pos
    
    def get_y(self):
        return self.rect.y


#Main Run class
class Main:
    def __init__(self):
        self.__running=True
        self.__paused=False
        self.__overed=False
        
        self.__x_spd=0
        self.__y_multi=1
        self.__block_g=[]
        self.__fixed_g=[]
        self.__next_g=[]
        self.__point=0
        self.__frame_count=0
        
        self.__run()
    
    def __run(self):
        tmp=SHAPE[random.randint(0,len(SHAPE)-1)]
        self.__next_block=(tmp[:-1],tmp[-1])
        self.__add_block()
        while self.__running:
            while self.__paused:
                self.__event_handler_paused()
                clocker.tick(FPS)
            if not self.__running:
                self.__quit()
                return
            if self.__overed:
                self.__draw_over()
                pygame.display.flip()
                while self.__overed:
                    self.__event_handler_overed()
                    clocker.tick(FPS)
                if not self.__running:
                    self.__quit()
                    return
                #reset
                self.__x_spd=0
                self.__y_multi=1
                self.__block_g=[]
                self.__fixed_g=[]
                self.__next_g=[]
                self.__frame_count=0
                self.__add_block()
            direction=self.__get_touched()
            self.__event_handler(direction)
            self.__draw()
            pygame.display.flip()
            self.__get_crash(direction)
            self.__del_line()
            clocker.tick(FPS)
        self.__quit()
    
    def __add_block(self):
        block,color=self.__next_block
        for k in range(len(block)):
            for j in range(len(block[0])):
                if block[k][j]:
                    self.__block_g.append(Block([(j+(9-len(block[0]))//2)*BLOCK_SIZE+30,k*BLOCK_SIZE+30],color))
        self.__next_g.clear()
        tmp=SHAPE[random.randint(0,len(SHAPE)-1)]
        self.__next_block=(tmp[:-1],tmp[-1])
        #print(self.__next_block)
        block,color=self.__next_block
        for k in range(len(block)):
            for j in range(len(block[0])):
                if block[k][j]:
                    self.__next_g.append(Block([j*BLOCK_SIZE+410,k*BLOCK_SIZE+200],color))
    
    def __get_crash(self,direction):
        #get collision
        reached=False
        for block in self.__block_g:
            pos_b=block.get_pos()
            for f_block in self.__fixed_g:
                pos_f=f_block.get_pos()
                if pos_b[0]==pos_f[0] and pos_f[1]-pos_b[1]==BLOCK_SIZE:
                    self.__fixed_g+=self.__block_g
                    self.__block_g=[]
                    self.__add_block()
                    return
            if pos_b[1]>=14*BLOCK_SIZE+30:
                reached=True
        if reached:
            self.__fixed_g+=self.__block_g
            self.__block_g=[]
            self.__add_block()
    
    def __del_line(self):
        rows=[0]*15
        k=0
        for block in self.__fixed_g:
            pos=block.get_pos()
            if pos[1]<=BLOCK_SIZE+30:
                self.__overed=True
                return
            #         row                              column
            rows[int((pos[1]-30)/BLOCK_SIZE)]|=2**int((pos[0]-30)/BLOCK_SIZE)
            k+=1
        k=0
        for row in rows:
            if row==511:
                print(k)
                for j in range(len(self.__fixed_g)-1,-1,-1):
                    if (self.__fixed_g[j].get_pos()[1]-30)/BLOCK_SIZE==k:
                        del(self.__fixed_g[j])
                for block in self.__fixed_g:
                    if (block.get_pos()[1]-30)/BLOCK_SIZE<k:
                        block.update(spd=[0,BLOCK_SIZE])
                self.__point+=10
            k+=1
    
    def __get_touched(self):
        flag=0
        for block in self.__block_g:
            pos_b=block.get_pos()
            if pos_b[1]>=14*BLOCK_SIZE+30:
                flag|=S
            if pos_b[0]>=8*BLOCK_SIZE+30:
                flag|=E
            elif pos_b[0]<=30: #+0*BLOCK_SIZE
                flag|=W
            for f_block in self.__fixed_g:
                pos_f=f_block.get_pos()
                diff_x=pos_b[0]-pos_f[0]
                diff_y=pos_b[1]-pos_f[1]
                if not diff_x:
                    if diff_y==-BLOCK_SIZE:
                        flag|=S
                elif not diff_y:
                    if diff_x==BLOCK_SIZE:
                        flag|=W
                    elif diff_x==-BLOCK_SIZE:
                        flag|=E
                elif diff_x==diff_y==BLOCK_SIZE:
                    if diff_y<0:
                        if diff_x>0:
                            flag|=SW
                        else:
                            flag|=SE
        return flag
    '''
    def __get_double_down(self):
        flag=0
        for block in self.__block_g:
            pos_b=block.get_pos()
            if pos_b[1]>=12*BLOCK_SIZE+30:
                flag|=S
            for f_block in self.__fixed_g:
                pos_f=f_block.get_pos()
                diff_x=pos_b[0]-pos_f[0]
                diff_y=pos_b[1]-pos_f[1]
                if not diff_x:
                    if diff_y==BLOCK_SIZE*2:
                        flag|=S
                elif diff_y==BLOCK_SIZE*2:
                    if diff_x==BLOCK_SIZE:
                        flag|=SW
                    elif diff_x==-BLOCK_SIZE:
                        flag|=SE
        return flag
    '''
    def __event_handler(self,direction):
        key_unprocessed=True
        for event in pygame.event.get():
            event_type=event.type
            if event_type==pygame.QUIT:
                self.__running=False
            elif event_type==pygame.KEYDOWN and key_unprocessed:
                key_unprocessed=False
                '''
                if event.key==274: #down
                    if not self.__get_double_down()&S:
                        self.__y_multi=2
                else:
                '''
                self.__y_multi=1
                if event.key==275: #right
                    self.__x_spd=BLOCK_SIZE
                    for block in self.__block_g:
                        x,_=block.get_pos()
                        if direction&E or (self.__frame_count==DOWNSPD and direction&SE):
                            self.__x_spd=0
                elif event.key==276: #left
                    self.__x_spd=-BLOCK_SIZE
                    for block in self.__block_g:
                        x,_=block.get_pos()
                        if direction&W or (self.__frame_count==DOWNSPD and direction&SW):
                            self.__x_spd=0
                else:
                    self.__x_spd=0
                    if event.key==32: #space
                        self.__paused=True
        if key_unprocessed:
            self.__x_spd=0
            if self.__frame_count==0:
                self.__y_multi=1
    
    def __event_handler_paused(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.__running=False
                self.__paused=False
            elif event.type==pygame.KEYDOWN and event.key==32: #space
                self.__paused=False
    
    def __event_handler_overed(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.__running=False
                self.__overed=False
            elif event.type==pygame.KEYDOWN and 273>event.key<276:
                self.__overed=False
    
    def __draw(self):
        display.fill(WHITE)
        pygame.draw.rect(display,BLACK,pygame.Rect(30,30,BLOCK_SIZE*9,BLOCK_SIZE*15))
        pygame.draw.rect(display,BLACK,pygame.Rect(410,200,BLOCK_SIZE*4,BLOCK_SIZE*3))
        display.blit(TXTFONT.render(f'{self.__point:03d}',True,BLACK),(450,100))
        if self.__frame_count==DOWNSPD:
            for block in self.__block_g:
                block.update(spd=[self.__x_spd,BLOCK_SIZE*self.__y_multi])
            self.__frame_count=0
        else:
            for block in self.__block_g:
                block.update(spd=[self.__x_spd,0])
            self.__frame_count+=1
        for block in self.__fixed_g:
            block.update()
        for block in self.__next_g:
            block.update()
    
    def __draw_over(self):
        display.fill(WHITE)
        display.blit(TXTFONT.render('Game Over',True,BLACK),((SIZE[0]-200)//2,(SIZE[1]-100)//2))
        display.blit(TXTFONT.render('Press A Key to Restart',True,BLACK),((SIZE[0]-400)//2,(SIZE[1]+50)//2))
    
    def __quit(self):
        pygame.display.quit()
        pygame.quit()


#Launch
if __name__=='__main__':
    Main()