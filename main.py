import pygame,random
import sys,time


#Define pygame.Colors constant
RED=pygame.Color(255,0,0)
GREEN=pygame.Color(0,255,0)
BLUE=pygame.Color(0,0,255)
BLACK=pygame.Color(0,0,0)
GRAY=pygame.Color(128,128,128)
WHITE=pygame.Color(255,255,255)

#Define constants
SHAPE=(((0,1,1),(1,1,0)),((1,1),(1,1)),((1,1,1,1),),((0,1,0),(1,1,1)))
SHAPE=(((0,1,0),(1,1,1)),)


#Define global settings
SIZE=(600,600)
FPS=60
BLOCK_SIZE=36
SPD=3
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
            self.__pos=pos
            self.rect.move_ip([pos[k]-self.__pos[k] for k in range(2)])
        elif spd:
            assert type(spd) is list or type(spd) is tuple, f'type error: type of spd {type(spd)}'
            assert len(spd)==2, f'length of spd:{len(spd)}!=2:length of pos'
            for k in range(2):
                self.__pos[k]+=spd[k]
            '''
            self.__pos[0]+=spd[0]
            self.__pos[1]+=spd[1]
            '''
            self.rect.move_ip(*spd)
        if size:
            assert type(size) is list or type(size) is tuple, f'type error: type of size {type(size)}'
            assert len(pos)==2, 'length error'
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
        self.__pause=False
        
        self.__x_spd=0
        self.__y_multi=1
        self.__block_g=[]
        self.__fixed_g=[]
        self.__frame_count=0
        
        self.__run()
    
    def __run(self):
        self.__next_block()
        while self.__running:
            while self.__pause:
                self.__event_handler_paused()
                clocker.tick(FPS)
            direction=self.__get_direction()
            self.__event_handler(direction)
            self.__display_handler()
            pygame.display.flip()
            self.__get_crash(direction)
            self.__del_line()
            clocker.tick(FPS)
        self.__quit()
    
    def __next_block(self):
        block=SHAPE[random.randint(0,len(SHAPE)-1)]
        color=random.choice((RED,GREEN,BLUE,GRAY))
        for k in range(len(block)):
            for j in range(len(block[0])):
                if block[k][j]:
                    self.__block_g.append(Block([(j+(9-len(block[0]))//2)*BLOCK_SIZE+30,k*BLOCK_SIZE+30],color))
    
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
                    self.__next_block()
                    return
            if pos_b[1]>=534:
                reached=True
        if reached:
            self.__fixed_g+=self.__block_g
            self.__block_g=[]
            self.__next_block()
    
    def __del_line(self):
        rows=[0]*15
        k=0
        for block in self.__fixed_g:
            pos=block.get_pos()
            row=int((pos[1]-30)/BLOCK_SIZE)
            column=int((pos[0]-30)/BLOCK_SIZE)
            try:
                rows[row]|=2**column
            except IndexError as e:
                print(row,'/',rows,'\n',e)
            k+=1
        k=0
        for row in rows:
            if row==511:
                for j in range(len(self.__fixed_g)-1,-1,-1):
                    if (self.__fixed_g[j].get_pos()[1]-30)/BLOCK_SIZE==k:
                        del(self.__fixed_g[j])
                for block in self.__fixed_g:
                    if (block.get_pos()[1]-30)/BLOCK_SIZE<k:
                        block.update(spd=[0,BLOCK_SIZE])
            k+=1
        print(rows)
    
    def __get_direction(self):
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
                    if diff_y<0:
                        flag|=S
                    '''
                    else:
                        flag|=N
                    '''
                elif not diff_y:
                    if diff_x>0:
                        flag|=W
                    else:
                        flag|=E
                elif diff_x==diff_y==BLOCK_SIZE:
                    if diff_y<0:
                        if diff_x>0:
                            flag|=SW
                        else:
                            flag|=SE
                    '''
                    else:
                        if diff_x>0:
                            flag|=NW
                        else:
                            flag|=NE
                    '''
        return flag
    
    def __get_blocks_ddown(self):
        flag=0
        for block in self.__block_g:
            pos_b=block.get_pos()
            if pos_b[1]>=13*BLOCK_SIZE+30:
                flag|=S
            for f_block in self.__fixed_g:
                pos_f=f_block.get_pos()
                diff_x=pos_b[0]-pos_f[0]
                diff_y=pos_b[1]-pos_f[1]
                if not diff_x:
                    if diff_y<0:
                        flag|=S
                elif diff_x==BLOCK_SIZE and diff_y==BLOCK_SIZE*2:
                    if diff_y<0:
                        if diff_x>0:
                            flag|=SW
                        else:
                            flag|=SE
        return flag
    
    def __event_handler(self,direction):
        key_unprocessed=True
        for event in pygame.event.get():
            event_type=event.type
            if event_type==pygame.QUIT:
                self.__running=False
            elif event_type==pygame.KEYDOWN and key_unprocessed:
                key_unprocessed=False
                if event.key==274: #down
                    if not self.__get_blocks_ddown()&S:
                        self.__y_multi=2
                else:
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
                            self.__pause=True
        if key_unprocessed:
            self.__x_spd=0
            if self.__frame_count==0:
                self.__y_multi=1
    
    def __event_handler_paused(self):
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN and event.key==32: #space
                self.__pause=False
    
    def __display_handler(self):
        display.fill(WHITE)
        pygame.draw.rect(display,BLACK,pygame.Rect(30,30,BLOCK_SIZE*9,BLOCK_SIZE*15))
        if self.__frame_count==DOWNSPD:
            self.__frame_count=-1
            for block in self.__block_g:
                block.update(spd=[self.__x_spd,BLOCK_SIZE*self.__y_multi])
        else:
            for block in self.__block_g:
                block.update(spd=[self.__x_spd,0])
        self.__frame_count+=1
        for block in self.__fixed_g:
            block.update()
    
    def __quit(self):
        pygame.display.quit()
        pygame.quit()


#Launch
if __name__=='__main__':
    Main()