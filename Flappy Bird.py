
import  pygame
import neat
import os
import random
import time
pygame.font.init()

WIN_WID = 500
WIN_HEIGHT = 700


Bird_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("bird.png")))
Pipe_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("pipe.png")))
Base_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("Base.png")))
BG_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("BG.png")))

bird_img_scaled = pygame.transform.scale(Bird_Img, (Bird_Img.get_width() * 0.75, Bird_Img.get_height() * 0.75))
bird_Img = bird_img_scaled

Sat_Font = pygame.font.SysFont("timesnewroman",45)


class Bird:
    Img = Bird_Img
    Max_Rotation = 25
    Rot_Vel = 20
    Ani_time = 5

    def __init__(self,x,y): #Constructor to initialize the objects
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height =  self.y
        self.img_count = 0
        self.img = self.Img

    def jump(self):
        self.vel = -10.5 #To make the bird move up
        self.tick_count = 0 #A counter to know when the last jump was made. It is similar to the time required while jumping
        self.height = self.y   

    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count + 1.5*self.tick_count**2 #No.of pixels we are moving upwards

        if(d >= 16): #Terminal Ve
            d = 16
        if(d<0):
            d -= 2
        
        self.y = self.y + d
        if d < 0 or self.y < self.height + 50: #Tilt up
            if(self.tilt < self.Max_Rotation):
                self.tilt = self.Max_Rotation
            
        if(self.tilt > -90): #Tilt down
            self.tilt -= self.Rot_Vel

    def draw(self,win):
        self.img_count += 1
        if(self.img_count < self.Ani_time):
            self.img = self.Img
        elif(self.img_count == self.Ani_time*4 + 1):
            self.img = self.Img
            self.img_count = 0
        
        if(self.tilt <= -80):
            self.img = self.Img
            self.img_count = self.Ani_time*2
        
        rotated_image  = pygame.transform.rotate(self.img,self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    Gap = 400
    Velocity = 5

    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap = 160

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(Pipe_Img, False, True) # Pipe that is flipped
        self.PIPE_Bottom = Pipe_Img

        self.passed = False # If the bird has already passed the pipe
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height() 
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.Velocity#To move the pipe in each frame

    def draw(self,win):
        win.blit(self.PIPE_TOP, (self.x,self.top))
        win.blit(self.PIPE_Bottom, (self.x,self.bottom))

    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_Bottom)
        
        top_offset = (self.x - bird.x , self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask,bottom_offset)#Tells us how far the bird is from the Pipe
        t_point = bird_mask.overlap(top_mask,top_offset)#Both of these return None if they are not colliding

        if b_point or t_point:
            return True
        return False

class Base:
    Velo = 5
    Width = Base_Img.get_width()
    Img = Base_Img

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.Width
    
    def move(self):
        self.x1 -= self.Velo
        self.x2 -= self.Velo

        #We are trying to create a circular pattern of 2 imgs of the baseto make us feel that teh base is moving.
        if self.x1 + self.Width < 0: #If the 1st image os of the screen
            self.x1 = self.x2+self.Width
        
        if self.x2 + self.Width < 0:
            self.x2 = self.x1+self.Width
            
    def draw(self,win):
        win.blit(self.Img,(self.x1,self.y))
        win.blit(self.Img,(self.x2,self.y))

    
def draw_window(win,birds,pipes,base,score):
    win.blit(BG_Img,(0,0))
    for p in pipes:
        p.draw(win)

    text = Sat_Font.render("Score: "+str(score),1,(0,255,255))
    win.blit(text, (WIN_WID  - 330 - text.get_width() , 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


def main(genomes,config): #Fitness Function. Evaluates all birds
    pygame.init()
    score = 0
    birds = []
    nets = []
    gen = []
    #The indexes of all the 3 lists will point to the same bird
    for _,g in genomes:#We are traversing a tuple here
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        gen.append(g) #Append the genome into our list
    base = Base(630)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WID, WIN_HEIGHT))
    pygame.display.set_caption('Hopping Bird')
    clock = pygame.time.Clock()
    run = True
    add_pipe = False #If this doesn't work then we will want to put this inside the loop
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        pipe_index = 0
        if(len(birds) > 0):#If the bird passes the pipe we want to increase the pipe index   
            if(len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width()):
                pipe_index = 1
        
        else:
            run = False
            break
        
        for x,bird in enumerate(birds):
            bird.move() #Encouraging the bird to continue the game
            gen[x].fitness += 0.1 #It increases at a fast rate, so we set the increment low
            #Passing the bird position, top and bottom pillar position
            output = nets[x].activate((bird.y ,abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5: #Here we have only 1 output neuron i.e either to jump or not
                bird.jump()

            
        rem = []        
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird):#We remove the bird which is not eligible from the network
                   gen[x].fitness -= 1
                   birds.pop(x)
                   nets.pop(x)
                   gen.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)            

            if add_pipe:
                score += 1
                for g in gen:
                    g.fitness += 5 #We motivate the bird to fly into the Hole
                pipes.append(Pipe(700))
                add_pipe = False
            
            for r in rem:
                pipes.remove(r)
            
            for x,bird in enumerate(birds):#Elimination of unworthy birds
                if bird.y + bird.img.get_height() >= 630 or bird.y < 0:
                    birds.pop(x)
                    nets.pop(x)
                    gen.pop(x)

            pipe.move()
        base.move()
        draw_window(win, birds,pipes,base,score)
    

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    popu = neat.Population(config) #The population

    popu.add_reporter(neat.StdOutReporter(True)) #Just some statistical data
    stats = neat.StatisticsReporter()
    popu.add_reporter(stats)

    winner = popu.run(main,200) #We could store this data into a pickle file so that we can use this parent in the forhtcoming processes

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config.txt")
    run(config_path)
