import pygame
import pygame.display
import random
import pygame.draw
import pygame_menu


from pygame.locals import(
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
pygame.init()
#constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
PLAYER_SIZE = (25,25)
#our clock to control frame rate
clock = pygame.time.Clock()
#screen draw
screen = pygame.display.set_mode([SCREEN_WIDTH,SCREEN_HEIGHT])
#arrow key list
ARROW_KEYS = [K_DOWN,K_UP,K_LEFT,K_RIGHT]
#Starting location is drawn from the top down. So starting Y is the top most conveyor
#This centers the game on the screen
#position of first conveyor belt
#position is set for the center of the screen and subtracts half the size of 7 conveyor belts
#The math here ensures that the position is a multiple of 25 so that our block movement is correct
#Note: This could be logically wrong and this is a quick fix. If there are issues with positioning of blocks
#later look at this
#TODO: Pass in NUM_CONV constant when it gets changed to global
FIRST_CONVEYOR_LINE = (0,round(int((SCREEN_HEIGHT/2)-((25*7)/2))/25)*25)
CONVEYOR_STARTING_Y = round(int((SCREEN_HEIGHT/2)-((25*7)/2))/25)*25
CONVEYOR_STARTING_X = 0

#This should be the only location that our player can move
#TODO:Need to figure out a way to make safe space included. Or just
#make starting positions a single spot
MOVEABLE_AREA_RECT_POS = (FIRST_CONVEYOR_LINE,(SCREEN_WIDTH,25*7))
MOVEABLE_AREA_RECT = pygame.Rect(MOVEABLE_AREA_RECT_POS)
print(str(MOVEABLE_AREA_RECT))


#our player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player,self).__init__()
        self.surf = pygame.Surface(PLAYER_SIZE)
        self.surf.fill((255,255,0))
        self.rect = self.surf.get_rect(
                left = FIRST_CONVEYOR_LINE[0],
                top = FIRST_CONVEYOR_LINE[1]-25
            )
    
    def update(self,key_event):
        self.prev_location = self.rect.copy()
        if key_event == K_UP:
            self.rect.move_ip(0,-25)
        elif key_event == K_DOWN:
            self.rect.move_ip(0,25)
        elif key_event == K_RIGHT:
            self.rect.move_ip(25,0)
        elif key_event == K_LEFT:
            self.rect.move_ip(-25,0)
            
        #bounds checking
        print(str(not(MOVEABLE_AREA_RECT.contains(self.rect))))
        if not(MOVEABLE_AREA_RECT.contains(self.rect)):
            self.rect = self.prev_location
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT  
        if self.rect.top <= 0:
            self.rect.top = 0
        
        

class EnemyBlock(pygame.sprite.Sprite):
    #This is our enemy block class
    #The only values it holds is the size and speed at which it moves
    #Currently the size is fixed at 25 units high and the width is passed in
    #Width is stored individually for each conveyor belt in the conveyor belt class
    
    
    def __init__(self,conveyor_stats):
        super(EnemyBlock,self).__init__()
        self.surf = pygame.Surface((conveyor_stats.block_width,25))
        #make it red
        self.surf.fill((255,0,0))
        #Puts our rectangle starting location based on the direction it is supposed to be moving
        if conveyor_stats.direction == 1:
            #speed 
            self.speed = conveyor_stats.block_speed   
            self.rect = self.surf.get_rect(
                left = conveyor_stats.location[0]-conveyor_stats.block_width,
                top =conveyor_stats.location[1]
            )
        elif conveyor_stats.direction == -1:
            #negates block speed to move right to left
            self.speed = conveyor_stats.block_speed*-1
            self.rect = self.surf.get_rect(
                left = (conveyor_stats.location[0]+1000)+conveyor_stats.block_width,
                top = conveyor_stats.location[1]
            )
        

    def update(self):
        #we will just be moving to the right
        self.rect.move_ip(self.speed,0)
        #bounds checking
        #Uses the speed as a reference. If moving right to left speed will always be negative
        if self.speed > 0:
            if self.rect.left >= SCREEN_WIDTH:
                self.kill()
        else:
            if self.rect.right < 0:
                self.kill()


class ConveyorBelt():
    #TODO Get rid of setters if they are not doing any type of input validation. This is more pythonic
    def __init__(self):
        #default values
        self.block_speed=1
        #1 is right -1 is left
        self.direction = 1
        #block size?
        #may not be needed here
        block_width = 25
        #how often blocks are made on belt
        self.timing = 3000

        #location of the loop
        self.location = (0,0)

    def setBlockSpeed(self,bs):
        self.block_speed = bs
    
    def setDirection(self,direct):
        #if blocks move left to right value is 1
        #if blocks move right to left value is -1
        if direct == 1 or direct == -1:
            self.direction = direct
    
    def setTiming(self,timing):
        #how often blocks will be created on the line. 
        #default value is 3000ms
        self.timing = timing
    def setLocation(self,x,y):
        self.location = (x,y)
    
    def setBlockWidth(self,w):
        self.block_width = w


def create_conv_list(num,cl):
    for i in range(num):
        cl.append(ConveyorBelt())

def initConveyors(conveyor_list):
    #this funciton populates our conveyor object attributes
    direction = 1
    x = CONVEYOR_STARTING_X
    y = CONVEYOR_STARTING_Y
    for c in conveyor_list:
        #set location and increment y value
        c.setLocation(x,y)
        y += 25
        #set direction and flip
        c.setDirection(direction)
        direction *= -1
        #set block speed
        rand_speed = random.randint(5,20)
        c.setBlockSpeed(rand_speed)
        #set timing
       
        c.setTiming(random.randint(1000,6000))
        #set block width
        w = random.randint(25,150)
        c.setBlockWidth(w)

def createCustomEvents(e_list,num):
    #create custom events for our conveyor lines
    #our e_list[0] will refer to first conveyor line
    #e_list[1] will refer to second conveyor line
    #FIXME Custom user events can only go from 25-32 because anything more will cause timing issues.
    #TODO Maybe need to re-evaluate how custom events are handled 
    for i in range(num):
        e_list.append(pygame.USEREVENT + (i+1))

def main_menu():
    menu = pygame_menu.Menu(SCREEN_HEIGHT,SCREEN_WIDTH, 'Chicken Crossing',theme=pygame_menu.themes.THEME_BLUE)
    menu.add_button("Play",main)
    menu.add_button("Quit",pygame_menu.events.EXIT)
    menu.mainloop(screen)
    

def main():

    #determine how many lines
    #TODO: Make this a global constant since it will be fixed. Will need to subsequently 
    #change all future function calls because this can be accessed globally
    num_conv = 7
    #conv_list object contains all of our conveyor line objects
    #conv_list[0] will be the top most line
    #conv_list[1] will be the one directly below that
    conv_list = []
    #see createcustom event method for doc
    event_list = [] 
    create_conv_list(num_conv,conv_list)
    initConveyors(conv_list)
    createCustomEvents(event_list,num_conv)


    #This loop will create our custom timers for each row
    for i in range(num_conv):
        pygame.time.set_timer(event_list[i],conv_list[i].timing)

    #create our player
    player = Player()

    #sprite groups
    all_sprites = pygame.sprite.Group()
    conveyor_blocks = pygame.sprite.Group()
    all_sprites.add(player)

    running = True

    #conveyor belt background
  
    
    while running:
        #background color
        screen.fill((255,255,255))
        #draw safe space
        #TODO: Consolidate into function
        #Safe space is drawn on center of screen
        first_conv_rect = (FIRST_CONVEYOR_LINE,(SCREEN_WIDTH,25*num_conv))
        screen.fill((95,141,188),first_conv_rect)   
        #draw starting and finishing area
        starting_zone_rect = ((FIRST_CONVEYOR_LINE[0],FIRST_CONVEYOR_LINE[1]-25),(50,25))
        finishing_zone_rect = ((SCREEN_WIDTH-50,FIRST_CONVEYOR_LINE[1]+(25*7)),(50,25))
        screen.fill((0,0,0),finishing_zone_rect)
        screen.fill((0,0,0),starting_zone_rect)
        #event loop
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                #check if it was an arrow key. these are the only ones we want to pass to our player
                if event.key in ARROW_KEYS:
                    player.update(event.key)
            #Checks if the event is a custom event
            elif event.type in event_list:
                #creates an index to use when referencing our conveyor object list
                list_index = event_list.index(event.type)  
                #create new stuff
                new_enemy_block = EnemyBlock(conv_list[list_index])
                conveyor_blocks.add(new_enemy_block)
                all_sprites.add(new_enemy_block)

        #update all of our auto update
        conveyor_blocks.update()

        #draw sprites
        for entity in all_sprites:
            screen.blit(entity.surf,entity.rect)

        #collision check
        if pygame.sprite.spritecollideany(player, conveyor_blocks):
            # If so, then remove the player and stop the loop
                player.kill()
                running = False

        pygame.display.flip()
        
        clock.tick(30)

    pygame.quit()



#main_menu()
main()