import pygame,random,json
pygame.font.init()

#load config
with open('config.conf','r') as file:
    config=json.load(file)
COLOR      = config['color']
SHAPE      = config['shape']
TXTFONT    = pygame.font.SysFont(config['font'],50)
SIZE       = config['size']
FPS        = config['fps']
BLOCK_SIZE = config['blocksize']
TABLE_SIZE = config['tablesize']
DOWNSPD    = 60/config['spdfersec']
SPDBOOST   = config['spdboost']
PADDING    = config['padding']

#direction flags
#   2^:876543210
N  = 0b000000001
NE = 0b000000010
E  = 0b000000100
SE = 0b000001000
S  = 0b000010000
SW = 0b000100000
W  = 0b001000000
NW = 0b010000000
C  = 0b100000000


#Define global variables
clocker=pygame.time.Clock()
display=pygame.display.set_mode(SIZE)
pygame.display.set_caption('Tetris')


#Block class
class Block:
    def __init__(self,pos,color,size=None):
        super().__init__()
        self.__pos=pos
        self.__color=color
        if size:
            self.__size=size
        else:
            self.__size=(BLOCK_SIZE,BLOCK_SIZE)
    
    def update(self,*,pos=None,spd=None,size=None,color=None):
        #get position & update position
        if pos:
            self.__pos[0]=pos[0]
            self.__pos[1]=pos[1]
        elif spd:
            self.__pos[0]+=spd[0]
            self.__pos[1]+=spd[1]
        if size:
            self.__size=size

        #draw block
        if not color:
            color=self.__color
        if self.__pos[1]>=0:
            pygame.draw.rect(display,color,pygame.Rect((self.__pos[0]*BLOCK_SIZE+PADDING,self.__pos[1]*BLOCK_SIZE+PADDING),self.__size))
    
    def move(self,pos):
        assert len(pos)==2
        self.__pos=pos
    
    def pos(self):
        return self.__pos


#Main Run class
class Main:
    def __init__(self):
        self.__running=True
        self.__paused=False
        self.__overed=False
        
        tmp=SHAPE[random.randint(0,len(SHAPE)-1)]
        self.__next_block=(tmp[:-1],tmp[-1])
        
        self.__reset()
        self.__run()
    
    def __reset(self):
        self.__x_spd=0
        self.__block_g=[]
        self.__fixed_g=[]
        self.__next_g=[]
        self.__point=0
        self.__frame_count=0
        self.__spd_multi=1
        self.__delay=0
        self.__add_block()
    
    def __run(self):
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
                self.__reset()
            direction=self.__get_touched()
            if not direction&S:
                self.__delay=0
            self.__event_handler(direction)
            self.__get_crash(direction)
            self.__draw()
            pygame.display.flip()
            self.__get_crash(direction)
            self.__del_line()
            clocker.tick(FPS)
        self.__quit()
    
    def __add_block(self):
        self.__frame_count=0
        block,color=self.__next_block
        for k in range(len(block)):
            for j in range(len(block[0])):
                if block[k][j]:
                    self.__block_g.append(Block([(j+(9-len(block[0]))//2),k],color))
        self.__next_g.clear()
        tmp=SHAPE[random.randint(0,len(SHAPE)-1)]
        self.__next_block=block,color=(tmp[:-1],tmp[-1])
        for k in range(len(block)):
            for j in range(len(block[0])):
                if block[k][j]:
                    self.__next_g.append((j*BLOCK_SIZE+410,k*BLOCK_SIZE+200))
        self.__next_g.append(color)
    
    def __get_crash(self,direction):
        if direction&S:
            if self.__delay>=DOWNSPD:
                self.__delay=0
                self.__fixed_g+=self.__block_g
                self.__block_g=[]
                self.__add_block()
            else:
                self.__delay+=1
    
    def __get_touched(self,pos=None):
        flag=0
        pos_fs=tuple(f_block.pos() for f_block in self.__fixed_g)
        for block in (pos if pos else self.__block_g):
            if pos:
                pos_b=block
            else:
                pos_b=block.pos()
            #get x border touch
            if pos_b[1]>=TABLE_SIZE[1]-1:
                flag|=S
            elif pos_b[1]<=0:
                flag|=N
            #get y border touch
            if pos_b[0]>=TABLE_SIZE[0]-1:
                flag|=E
            elif pos_b[0]<=0:
                flag|=W
            #get block touch
            for pos_f in pos_fs:
                diff_x=pos_b[0]-pos_f[0]
                diff_y=pos_b[1]-pos_f[1]
                if not diff_x:
                    if diff_y==-1:
                        flag|=S
                    elif diff_y==1:
                        flag|=N
                elif not diff_y:
                    if diff_x==-1:
                        flag|=E
                    elif diff_x==1:
                        flag|=W
                elif diff_x==diff_y==1:
                    if diff_y<0:
                        if diff_x>0:
                            flag|=SW
                        else:
                            flag|=SE
                    else:
                        if diff_x>0:
                            flag|=NW
                        else:
                            flag|=NE
        return flag
    
    def __get_covered(self,pos_fs,pos=None):
        flag=0
        for block in (pos if pos else self.__block_g):
            if pos:
                pos_b=block
            else:
                pos_b=block.pos()
            #get x border touch
            if pos_b[1]>TABLE_SIZE[1]-1:
                flag|=S
            elif pos_b[1]<0:
                flag|=N
            #get y border touch
            if pos_b[0]>TABLE_SIZE[0]-1:
                flag|=E
            elif pos_b[0]<0:
                flag|=W
            #get block touch
            for pos_f in pos_fs:
                if pos_b==pos_f:
                    flag|=C
        return flag
    
    def __rotate(self):
        #get size
        min_x=14
        min_y=14
        max_x=0
        max_y=0
        #get size
        for block in self.__block_g:
            pos=block.pos()
            if pos[0]<min_x:
                min_x=pos[0]
            if pos[1]<min_y:
                min_y=pos[1]
            if pos[0]>max_x:
                max_x=pos[0]
            if pos[1]>max_y:
                max_y=pos[1]
        size=(max_x-min_x,max_y-min_y)
        #calculate position
        pos_x=[]
        pos_y=[]
        can_move=True
        pos_fs=tuple(f_block.pos() for f_block in self.__fixed_g)
        for block in self.__block_g:
            pos=block.pos()
            x=min_x-min_y+pos[1]           #=(pos[1]-min_y-size[1]-1)+(size[1]+1+min_x)
            y=min_x+min_y-pos[0]+size[0]   #=(min_x-pos[0]-1)        +(size[0]+1+min_y)
            if self.__get_covered(pos_fs,([x,y],)):
                can_move=False
                return
            else:
                pos_x.append(x)
                pos_y.append(y)
        if can_move:
            #move
            for block,x,y in zip(self.__block_g,pos_x,pos_y):
                #block.move([x+x_plus,y])
                block.move([x,y])
        
    def __del_line(self):
        rows=[0]*TABLE_SIZE[1]
        #check end&get row count
        for block in self.__fixed_g:
            pos=block.pos()
            if pos[1]<=0:
                self.__overed=True
                return
            rows[pos[1]]|=2**pos[0]
        #delete line if line is fill
        for k,row in enumerate(rows):
            if row==511:
                for j in range(len(self.__fixed_g)-1,-1,-1):
                    if self.__fixed_g[j].pos()[1]==k:
                        del(self.__fixed_g[j])
                for block in self.__fixed_g:
                    if block.pos()[1]<k:
                        block.update(spd=[0,1])
                self.__point+=10
    
    def __event_handler(self,direction):
        key_unprocessed=True
        for event in pygame.event.get():
            event_type=event.type
            if event_type==pygame.QUIT:
                self.__running=False
            elif event_type==pygame.KEYDOWN:
                if key_unprocessed:
                    key_unprocessed=False
                    if event.key==pygame.K_RIGHT:
                        self.__x_spd=1
                        for block in self.__block_g:
                            if direction&E:
                                self.__x_spd=0
                            elif self.__frame_count==DOWNSPD//self.__spd_multi and direction&SE:
                                self.__x_spd=0
                    elif event.key==pygame.K_LEFT:
                        self.__x_spd=-1
                        for block in self.__block_g:
                            if direction&W:
                                self.__x_spd=0
                            elif self.__frame_count==DOWNSPD//self.__spd_multi and direction&SW:
                                self.__x_spd=0
                    else:
                        self.__x_spd=0
                        if event.key==pygame.K_UP and not self.__delay:
                            self.__rotate()
                        elif event.key==pygame.K_SPACE:
                            self.__paused=True
                        elif event.key==pygame.K_r:
                            self.__reset()
        pressed=pygame.key.get_pressed()
        if pressed[pygame.K_DOWN]:
            self.__spd_multi=SPDBOOST
            if self.__frame_count==DOWNSPD//self.__spd_multi:
                self.__point+=.25
        elif pressed[pygame.K_b]:
            self.__spd_multi=SPDBOOST*2
            if self.__frame_count==DOWNSPD//self.__spd_multi:
                self.__point+=.5
        elif pressed[pygame.K_o]:
            self.__overed=True
        elif self.__frame_count==0:
            self.__spd_multi=1
        if key_unprocessed:
            self.__x_spd=0
    
    def __event_handler_paused(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.__running=False
                self.__paused=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE: #space
                    self.__paused=False
                elif event.key==pygame.K_r:
                    self.__paused=False
                    self.__reset()
    
    def __event_handler_overed(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.__running=False
                self.__overed=False
            elif event.type==pygame.KEYDOWN and 273>event.key<276:
                self.__overed=False
    
    def __draw(self):
        display.fill(COLOR['white'])
        pygame.draw.rect(display,COLOR['black'],pygame.Rect(PADDING,PADDING,TABLE_SIZE[0]*BLOCK_SIZE,TABLE_SIZE[1]*BLOCK_SIZE))
        pygame.draw.rect(display,COLOR['black'],pygame.Rect(410,200,4*BLOCK_SIZE,3*BLOCK_SIZE))
        display.blit(TXTFONT.render(f'{int(self.__point):03d}',True,COLOR['black']),(450,100))
        if self.__frame_count>=DOWNSPD//self.__spd_multi and not self.__delay:
            for block in self.__block_g:
                block.update(spd=[self.__x_spd,1])
            self.__frame_count=0
        else:
            for block in self.__block_g:
                block.update(spd=[self.__x_spd,0])
            self.__frame_count+=1
        for block in self.__fixed_g:
            block.update()
        for pos in self.__next_g[:-1]:
            pygame.draw.rect(display,self.__next_g[-1],pygame.Rect(pos,(BLOCK_SIZE,BLOCK_SIZE)))
    
    def __draw_over(self):
        display.fill(COLOR['white'])
        texts=((f'Score: {int(self.__point):03d}',190,-175),('Game Over',200,-50),('Press A key to Restart',365,75))
        for text,width,y_plus in texts:
            text_render=TXTFONT.render(text,True,COLOR['black'])
            display.blit(text_render,((SIZE[0]-width)//2,(SIZE[1]+y_plus)//2-text_render.get_height()//4))
    
    def __quit(self):
        pygame.display.quit()
        pygame.quit()


#Launch
if __name__=='__main__':
    Main()