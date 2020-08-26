import pygame,random,json
pygame.font.init()

#load config
with open('config.conf','r') as file:
    config=json.load(file)
COLOR=config['color']
SHAPE=config['shape']
TXTFONT=pygame.font.SysFont(config['font'],50)
SIZE=config['size']
FPS=config['fps']
BLOCK_SIZE=config['blocksize']
DOWNSPD=60/config['spdfersec']
SPDMULTI=config['spdmulti']
PADDING=config['padding']

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
        #get collision
        reached=False
        for block in self.__block_g:
            pos_b=block.pos()
            for f_block in self.__fixed_g:
                pos_f=f_block.pos()
                if pos_b[0]==pos_f[0] and pos_f[1]-pos_b[1]==1:
                    self.__fixed_g+=self.__block_g
                    self.__block_g=[]
                    self.__add_block()
                    return
            if pos_b[1]>=14:
                reached=True
        if reached:
            self.__fixed_g+=self.__block_g
            self.__block_g=[]
            self.__add_block()
    
    def __get_touched(self):
        flag=0
        for block in self.__block_g:
            pos_b=block.pos()
            if pos_b[1]>=14:
                flag|=S
            if pos_b[0]==8:
                flag|=E
            elif pos_b[0]==0:
                flag|=W
            for f_block in self.__fixed_g:
                pos_f=f_block.pos()
                diff_x=pos_b[0]-pos_f[0]
                diff_y=pos_b[1]-pos_f[1]
                if not diff_x:
                    if diff_y==-1:
                        flag|=S
                elif not diff_y:
                    if diff_x==1:
                        flag|=W
                    elif diff_x==-1:
                        flag|=E
                elif diff_x==diff_y==1:
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
            pos_b=block.pos()
            if pos_b[1]>=12:
                flag|=S
            for f_block in self.__fixed_g:
                pos_f=f_block.pos()
                diff_x=pos_b[0]-pos_f[0]
                diff_y=pos_b[1]-pos_f[1]
                if not diff_x:
                    if diff_y==2:
                        flag|=S
                elif diff_y==2:
                    if diff_x==1:
                        flag|=SW
                    elif diff_x==-1:
                        flag|=SE
        return flag
    '''
    def __rotate(self):
        #get size
        min_x=14
        min_y=14
        max_x=0
        max_y=0
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
        #calculate position, get min x
        min_x2=14
        min_y2=14
        position=[]
        for block in self.__block_g:
            pos=block.pos()
            x=pos[1]-min_y-size[1]+min_x
            y=min_x-pos[0]-1
            position.append((x,y))
            if x<min_x2:
                min_x2=x
            if y<min_y2:
                min_y2=y
        #set x extra
        if min_x2<0:
            x_extra=-min_x2
        else:
            x_extra=0
        y_extra=-min_y2
        #move
        for block,pos in zip(self.__block_g,position):
            block.move([pos[0]+x_extra,pos[1]+y_extra+min_y])
        
    def __del_line(self):
        rows=[0]*15
        k=0
        for block in self.__fixed_g:
            pos=block.pos()
            if pos[1]<=1:
                self.__overed=True
                return
            rows[pos[1]]|=2**pos[0]
            k+=1
        k=0
        for row in rows:
            if row==511:
                for j in range(len(self.__fixed_g)-1,-1,-1):
                    if self.__fixed_g[j].pos()[1]==k:
                        del(self.__fixed_g[j])
                for block in self.__fixed_g:
                    if block.pos()[1]<k:
                        block.update(spd=[0,1])
                self.__point+=10
            k+=1
    
    def __event_handler(self,direction):
        key_unprocessed=True
        for event in pygame.event.get():
            event_type=event.type
            if event_type==pygame.QUIT:
                self.__running=False
            elif event_type==pygame.KEYDOWN:
                #print(event.key)
                if key_unprocessed:
                    key_unprocessed=False
                    if event.key==pygame.K_RIGHT: #right
                        self.__x_spd=1
                        for block in self.__block_g:
                            if direction&E:
                                self.__x_spd=0
                            elif self.__frame_count==DOWNSPD//self.__spd_multi and direction&SE:
                                self.__x_spd=0
                    elif event.key==pygame.K_LEFT: #left
                        self.__x_spd=-1
                        for block in self.__block_g:
                            if direction&W:
                                self.__x_spd=0
                            elif self.__frame_count==DOWNSPD//self.__spd_multi and direction&SW:
                                self.__x_spd=0
                    else:
                        self.__x_spd=0
                        if event.key==pygame.K_SPACE: #space
                            self.__paused=True
                        elif event.key==pygame.K_r:
                            self.__rotate()
                        elif event.key==pygame.K_q:
                            self.__reset()
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.__spd_multi=SPDMULTI
        elif pygame.key.get_pressed()[pygame.K_b]:
            self.__spd_multi=SPDMULTI*2
        else:
            self.__spd_multi=1
        if key_unprocessed:
            self.__x_spd=0
    
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
        display.fill(COLOR['white'])
        pygame.draw.rect(display,COLOR['black'],pygame.Rect(PADDING,PADDING,9*BLOCK_SIZE,15*BLOCK_SIZE))
        pygame.draw.rect(display,COLOR['black'],pygame.Rect(410,200,4*BLOCK_SIZE,3*BLOCK_SIZE))
        display.blit(TXTFONT.render(f'{self.__point:03d}',True,COLOR['black']),(450,100))
        if self.__frame_count>=DOWNSPD//self.__spd_multi:
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
        display.blit(TXTFONT.render('Game Over',True,COLOR['black']),((SIZE[0]-200)//2,(SIZE[1]-100)//2))
        display.blit(TXTFONT.render('Press A Key to Restart',True,COLOR['black']),((SIZE[0]-375)//2,(SIZE[1]+50)//2))
    
    def __quit(self):
        pygame.display.quit()
        pygame.quit()


#Launch
if __name__=='__main__':
    Main()