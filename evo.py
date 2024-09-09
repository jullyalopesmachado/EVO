import pygame
import random
import math
import os 
from os import listdir
from os.path import isfile, join 
pygame.init()

pygame.display.set_caption("EVO")

# # BG_COLOR = (255,255,255) # Code for white rgb (color input type)
WIDTH, HEIGHT = 1000, 800 # Size of the screen
FPS = 60 # Frames per second
PLAYER_VEL = 5 # Speed my player moves around    

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip (sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites] # flipping our character image to face left when needed. (sprites, True, False) == (Sprites, x direction, y direction)

def load_sprite_sheets(dir1, dir2, width, height, direction = False): # Loads all the imgs (spite sheets) for the actions (such as jumping)
# Dir1 and Dir2 so we can load other images that arent just the charascters. Width and heigt of the image. And the direction = falso is so that we only load the left and the right side image (flip them) if we pass the direction equal to true.  
    path = join ("assets", dir1, dir2) # determining the path to the images to be loaded. 
    images = [f for f in listdir (path) if isfile (join(path, f))] # lisiting all that is in path directory 
    #four loop in list: loads all files that are inside that directory.
    
    all_sprites = {} #dictionary will have key value pares. Key is animation style and val is all the images in animation.
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()  #individual sprite sheet to be loaded = pygame.image
        
        sprites = [] # list
        # load all diff files == sprite sheets: done above
        # Now you need to get the individual pics 
        for i in range(sprite_sheet.get_width() // width): # width here being of the image we are loading (width of the individual image inside animation (sprite sheet)). Ex: for a 32 pixel image, you pass 32, and it will give you an image that is 32 pixels wide.
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) # .SRCALPHA allows transparent background (same as convert_alpha). 32 is the depth. 
            # rectangle to say where in this image (the sprite sheet we are taking an individual img from)  and blit it onto the surface. We are creating a surface that is the size of our desired individual animation frame, then grab animation frmae from main image, draw it onto surface, then export surface.          
            rect = pygame.Rect(i * width, 0, width, height) #rect(i*width) is the location in our acatual image where we want to grab the frame from. Then 0, then width and height of my image. 
            surface.blit(sprite_sheet, (0,0), rect) # draw my sprite_sheet at (0,0) and only draw the portion that is my rectangle. So bli:(source, destination, area of my sourse that i am drawing.)
            # so in position 0,0 (top left hand corner), of my new surface i am drawing my sprite sheet, but only the frame from my sprite sheet that I want. 
            # blit means draw
            sprites.append(pygame.transform.scale2x(surface)) # append surface two times larger (to be bigger than default)
            # so they were 32x32 now they are 64x64
            
            # handle directions now
            # if you want a multidirectional animation we need to add two keys to the all_sprites = {} dictionary for every single one of our animations. 
            # so for fall, hit, etc we need a left and right side. 
            # the right side we already have (image is positioned to the right already)
            # so we need to say all sprites at (we need to get rid of .png from images which will give us run, jump, hit (instead of hit.png))
            # then instead of having run.png we will have hit_right. For the left the only extra step is to flip (with the function done previously) to the left side first. 
        if direction: 
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites [image.replace(".png", "") + "_left"] = flip(sprites) # flip function written before
        else:
            all_sprites[image.replace(".png", "")] = sprites # this just removes .png
            
    return all_sprites   # sprite sheets are now loaded! 
    
def get_block(size): # size passes what size we want the block
    # find block that i want 
    path = join("assets", "Terrain", "Terrain.png") # passing locatiom
    image = pygame.image.load(path).convert_alpha() # 
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32) # create image of that size. Size will be passed later but it will probably be 64 pixels (doubled).
    rect = pygame.Rect (96, 64, size, size) # 96 is the math with the pixels to see where the block is located. So 96 is the position within the picture you are getting. 0 too. Size size is the size of the pic. 
    surface.blit(image, (0,0), rect) # blit image onto surface (which will be the image we will return)
    return pygame.transform.scale2x(surface) # scale doubles the image's size. 
                
# Movement for the player
# Look more into SPRITE! 
class Player (pygame.sprite.Sprite): #sprite objs allow knowing if sprites are colliding with eachother. 
    
    COLOR = (255, 0,0) # color for player
    GRAVITY = 2
    ANIMATION_DELAY = 3 # this is to change/animate the character moving, changing positions. 
    # grab images
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True) # using the load_sprite_sheets function created above to be passing (from inside of assets) the directory for MainCharacters. Then pass the second directory which is the name of the character. (You'll pick from available characters, the file names inside the MainCharacters.) Then you insert width and height. This is 32 for both. And true because we want a multidirectional sprite (left and right.)
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)  # rather than representing all these valus individually, we just put them into the rectangle so its easier to move the player arounf and do collision.
        # a rect is a tuple storing for the individual values. 
        self.x_vel = 0 # x&y velocity will denote how fast we move our player every single frame in both directions.
        self.y_vel = 0 # so to move our player we just apply a velocity in whatever direction.
        self.mask = None
        self.direction = "left" # need to keep track of direction player is facing. 
        self.animation_count = 0 # this resets the count we are using to change the animation frames and this helps it does look all "wonky."
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False # for taking hits
        self.hit_count = 0
        
    def jump(self):
        # jumping is taking y velocity, equal to the negative gravity multiplied by whatever factor you want (will define speen of jump)
        # what brings you down is the fact that you have gravity inside of the loop function.
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1: 
            self.fall_count = 0  # we want to remove gravity to jump easily and then apply gravity after jump
            # so as soon as I jump, I'm resetting the fall count to be equal to zero, so that any gravity I have accumulated is removed.
            # But we are only doing this if this is first jump I am making (jump_count == 1) cause for the second jump we have to time it based on when we are jumping.
    
    def move (self, dx, dy): # move takes a "displpacement in x direction and similarly in the y direction"
        self.rect.x += dx # To move up down or left or right these will be changed
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        
        
    def move_left(self, vel):
        self.x_vel = -vel # Moving left will require that you do -vel.
        # You must subtract from the x position. In pygame, coordinate 00 is the top left hand corner of screen so to move down, you add to Y coordinate, to move to the right you add to the X coordinate.
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
            
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
            
    def loop(self, fps): # this will be called once every frame (in the while loop) and it will move the character in the correct direction and update the animation. 
        self.y_vel += min(1, (self.fall_count/fps) * self.GRAVITY) # if fps 60, as soon as self.fall_count is 60, then you been falling for 1 second. Take that time, multiply by gravity and that will tell you what my y velocity will be increased by. We add a minimum of 1 so every frame there is some gravity. 
        self.move(self.x_vel, self.y_vel) # all frames in loop we increase y velocity by gravity. How much to increse vel by? it will vary by how long we have been falling for which must be tracked in order to make this work. 
        # so vertical velocity is set by gravity and function move is applied to allow player to move in set velocity. 
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2: # fps * 2 is 2 seconds # Defining how long you touch fire in order to get hit.
            self.hit = False
            self.hit_count = 0 # make sure you're not always looking hit. 
        
        self.fall_count += 1
        self.update_sprite() # updates sprite every single frame and draws it on the screen.
    
    def landed(self):
        # reset gravity or fall counter when just landed so we stop adding gravity.
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        
    def hit_head (self):
        self.count = 0
        self.y_vel *= -1 # you want to make you velocity negative so when you hit your head you bounce off the block and go downswards. 
    
    
    def update_sprite(self): # this makes sure he is always moving and not just standing there. Looks like he is breathing, really. 
        sprite_sheet = "idle" # default position (if not running/jumping/etc)
        
        if self.hit:
            sprite_sheet = "hit" # updating sprite sheet to show the hit animation
        elif self.y_vel < 0: # velocity less than zero == moving up
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2: # so falling # avoiding glitches by comparing to gravity.
            sprite_sheet = "fall"
                
        elif self.x_vel != 0:
            sprite_sheet = "run" # if velocity, change to run
            
        # so now change the main sprite sheet name, add the direction to it, and this tells us what sprite sheet we want.
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name] # changing it to whatever sprite name it is.
        sprite_index = (self.animation_count // self.ANIMATION_DELAY)  % len (sprites) # we have an animation delay that is every 5 frames (as written above). So every 5 frames, we want to show a different sprite, regardless of what the character is doing.
        # we take the animation count, divide it by 5 (delay) and then mod the whatever the line of our sprite is.
        # so for example: if we have 5 sprites and are on animation count 10, then we are showing the second sprite.
        # this will work for any single sprite. We are trying to get a new index at every anumation frame from the srpite.
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self): # update the rectangle that bounds the character
        #depending what sprite image we have (size wise) we will adjust the width and height of it but we will use the same width and height. 
        # the rectangle used to bound our sprites is constantly changing based on the sprites being used. 
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y)) 
        # mask is a mapping of all of the pixels that exist in the sprite.  
        self.mask = pygame.mask.from_surface(self.sprite) # the mask allows us to perform pixel perfect collision because we can overlap it with another mask and make sure that we only say two objs collide if the PIXELS collide, not the rectangule collide. This is a feature of sprite.
           
   # offset_x is for scrolling background.        
    def draw(self, win, offset_x): # win = window
            # pygame.draw.rect(win, self.COLOR, self.rect) 
            # draw the sprite
            ## self.sprite = self.SPRITES["idle_" + self.direction][0] # idle is the name of one of the animations available in NinjaFrog FILE. So with this we are accessing key from dictionary.
            # then we access the first frame (as shown above) of that key which is ZERO. [0]
            # position on the screen.
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
     
class Object (pygame.sprite.Sprite):
        # base class defines all properties we need for a valid sprite. 
        def __init__(self,x,y,width, height, name=None):
            super().__init__()
            self.rect = pygame.Rect(x,y,width,height) # defining a rectangle
            self.image = pygame.Surface((width, height), pygame.SRCALPHA) # when we change the image, the draw function will draw it for us automatically. 
            self.width = width 
            self.height = height 
            self.name = name
            
        def draw (self, win, offset_x):
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
    
class Block(Object): # inherits from class object above us. Block is a square only needs one dimension.      
        # 
        def __init__(self, x, y, size):
            super().__init__(x, y, size, size) # duplicate size cause its the same for width and height ( square ).
            block = get_block(size)
            self.image.blit(block, (0,0)) # blit imge to out surface
            self.mask = pygame.mask.from_surface(self.image)
            
class Enemy(Object): # Creating an enemy 
    #enemy_walk_right = [pygame.image.load('R1E.png'), pygame.image.load('R2E.png'), pygame.image.load('R3E.png'), pygame.image.load('R4E.png')]
    #enemy_walk_left = [pygame.image.load('L1E.png'),pygame.image.load('L2E.png'), pygame.image.load('L3E.png'), pygame.image.load('L4E.png')]
    
    ANIMATION_DELAY = 3
    def __init__ (self, x, y, width, height):
        super().__init__(x, y, width, height, "enemy") # add a name to the obj so we can determine what happens when ewe collide with it. 
        self.enemy = load_sprite_sheets("Traps" , "Fire", width, height)
        self.image = self.enemy["L1"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "L1"
        
    # Movement direction: -1 means left, 1 means right
        self.direction = -1 
        # Speed at which the enemy moves
        self.speed = 2
        # Total horizontal movement range (in pixels) from the initial position
        self.movement_range = 200
        # Initial x position to calculate movement range
        self.initial_x = x
    def move_enemy(self):
        # Check if the enemy has reached the left or right boundary of its movement range
        if self.rect.left <= self.initial_x - self.movement_range or self.rect.right >= self.initial_x + self.movement_range:
            # Reverse direction if boundary is reached
            self.direction *= -1 
        
        # Update the enemy's position based on the direction and speed
        self.rect.x += self.direction * self.speed
        # Call the loop method to handle animation updates
        self.loop()
        
    def loop (self):
        # Getting the apple animations.
        sprites = self.enemy[self.animation_name] # fire represents all fire images.
        sprite_index = (self.animation_count // self.ANIMATION_DELAY)  % len (sprites) # we have an animation delay that is every 5 frames (as written above). So every 5 frames, we want to show a different sprite, regardless of what the character is doing.
        # we take the animation count, divide it by 5 (delay) and then mod the whatever the line of our sprite is.
        # so for example: if we have 5 sprites and are on animation count 10, then we are showing the second sprite.
        # this will work for any single sprite. We are trying to get a new index at every anumation frame from the srpite.
        self.image = sprites[sprite_index]
        self.animation_count += 1
        
        # Instead of calling update function we just copy it into here. 
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) 
        # mask is a mapping of all of the pixels that exist in the sprite.  
        self.mask = pygame.mask.from_surface(self.image) # the mask allows us to perform pixel perfect collision because we can overlap it with another mask and make sure that we only say two objs collide if the PIXELS collide, not the rectangule collide. This is a feature of sprite.
            
        if self.animation_count // self.ANIMATION_DELAY > len(sprites): # so my animation count won't get too large because its static, so it wont reset and get to big and lag the program. 
            self.animation_count = 0
            


'''self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.end = end
        self.path = [self.x, self.end]
        self.walkCount = 0
        self.vel = 3
        
    def draw (self, win): # every time we draw, we move first.
        self.move()
        self.walkCount = 33
        if self.walkCount + 1 >= 33:
            self.walkCount = 0
        if self.vel > 0:
            win.blit(self.enemy_walk_right[self.walkCount//3], (self.x, self.y))
            self.walkCount += 1
        else:
            win.blit(self.enemy_walk_left[self.walkCount//3], (self.x, self.y))
            self.walkCount += 1
            
    def move (self):
        
        if self.vel > 0:
            if self.x + self.vel < self.path[1] : # only allows character to move in case the x coordinate is less than the self.path.
                self.x += self.vel
            else:
                self.vel = self.vel * -1 # swicthing sides
                self.walkCount = 0
        else: 
            if self.x - self.vel > self.path[0]:
                self.x += self.vel
            else:      
                self.vel = self.vel * -1 # swicthing sides
                self.walkCount = 0'''


class Fire (Object):
    ANIMATION_DELAY = 3   
    def __init__ (self, x, y, width, height):
        super().__init__(x, y, width, height, "fire") # add a name to the obj so we can determine what happens when ewe collide with it. 
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
        self.x_vel = 2 # Initial horizontal velocity
        self.y_vel = 0  # Initial vertical velocity
    
    # on and off are names of files in fire. 
    def on (self):
        self.animation_name = "on"
        
    def off (self):
        self.animation_name = "off"
     
 
    def loop (self):
            # Getting the fire animations.
            sprites = self.fire[self.animation_name] # fire represents all fire images.
            sprite_index = (self.animation_count // self.ANIMATION_DELAY)  % len (sprites) # we have an animation delay that is every 5 frames (as written above). So every 5 frames, we want to show a different sprite, regardless of what the character is doing.
            # we take the animation count, divide it by 5 (delay) and then mod the whatever the line of our sprite is.
            # so for example: if we have 5 sprites and are on animation count 10, then we are showing the second sprite.
            # this will work for any single sprite. We are trying to get a new index at every anumation frame from the srpite.
            self.image = sprites[sprite_index]
            self.animation_count += 1
                
            # Instead of calling update function we just copy it into here. 
            self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) 
            # mask is a mapping of all of the pixels that exist in the sprite.  
            self.mask = pygame.mask.from_surface(self.image) # the mask allows us to perform pixel perfect collision because we can overlap it with another mask and make sure that we only say two objs collide if the PIXELS collide, not the rectangule collide. This is a feature of sprite.
            
            if self.animation_count // self.ANIMATION_DELAY > len(sprites): # so my animation count won't get too large because its static, so it wont reset and get to big and lag the program. 
                self.animation_count = 0
            

class Spikes (Object): # Adding spikes 
    ANIMATION_DELAY = 3
    def __init__ (self, x, y, width, height):
        super().__init__(x, y, width, height, "spikes") # add a name to the obj so we can determine what happens when ewe collide with it. 
        self.spikes = load_sprite_sheets("Traps", "Spikes", width, height)
        self.image = self.spikes["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle" 
        
    def loop (self):
        # Getting the fire animations.
        sprites = self.spikes[self.animation_name] # fire represents all fire images.
        sprite_index = (self.animation_count // self.ANIMATION_DELAY)  % len (sprites) # we have an animation delay that is every 5 frames (as written above). So every 5 frames, we want to show a different sprite, regardless of what the character is doing.
        # we take the animation count, divide it by 5 (delay) and then mod the whatever the line of our sprite is.
        # so for example: if we have 5 sprites and are on animation count 10, then we are showing the second sprite.
        # this will work for any single sprite. We are trying to get a new index at every anumation frame from the srpite.
        self.image = sprites[sprite_index]
        self.animation_count += 1
        
        # Instead of calling update function we just copy it into here. 
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) 
        # mask is a mapping of all of the pixels that exist in the sprite.  
        self.mask = pygame.mask.from_surface(self.image) # the mask allows us to perform pixel perfect collision because we can overlap it with another mask and make sure that we only say two objs collide if the PIXELS collide, not the rectangule collide. This is a feature of sprite.
            
        if self.animation_count // self.ANIMATION_DELAY > len(sprites): # so my animation count won't get too large because its static, so it wont reset and get to big and lag the program. 
            self.animation_count = 0
                
class Apple (Object):
    ANIMATION_DELAY = 3
    def __init__ (self, x, y, width, height):
        super().__init__(x, y, width, height, "apple") # add a name to the obj so we can determine what happens when ewe collide with it. 
        self.apple = load_sprite_sheets("Items" , "Fruits", width, height)
        self.image = self.apple["Apple"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Apple" 
        
    def loop (self):
        # Getting the apple animations.
        sprites = self.apple[self.animation_name] # fire represents all fire images.
        sprite_index = (self.animation_count // self.ANIMATION_DELAY)  % len (sprites) # we have an animation delay that is every 5 frames (as written above). So every 5 frames, we want to show a different sprite, regardless of what the character is doing.
        # we take the animation count, divide it by 5 (delay) and then mod the whatever the line of our sprite is.
        # so for example: if we have 5 sprites and are on animation count 10, then we are showing the second sprite.
        # this will work for any single sprite. We are trying to get a new index at every anumation frame from the srpite.
        self.image = sprites[sprite_index]
        self.animation_count += 1
        
        # Instead of calling update function we just copy it into here. 
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) 
        # mask is a mapping of all of the pixels that exist in the sprite.  
        self.mask = pygame.mask.from_surface(self.image) # the mask allows us to perform pixel perfect collision because we can overlap it with another mask and make sure that we only say two objs collide if the PIXELS collide, not the rectangule collide. This is a feature of sprite.
            
        if self.animation_count // self.ANIMATION_DELAY > len(sprites): # so my animation count won't get too large because its static, so it wont reset and get to big and lag the program. 
            self.animation_count = 0

def get_background(name): # function will return a list of all background tiles that we will need to draw.
    # Load background image
    image = pygame.image.load(join("assets", "background", name)) # this loads from background file in assets, and searches for a specific file name.
    _, _, width, height = image.get_rect() # this will give you the x, y (dont care so _, _,) width, height but needed the last two. We are grabbing width and heigth.
    tiles = [] # empty list
    
    # loop through how many tiles you need to create in x and y direction
    for i in range (WIDTH // width + 1): # size of screen divided by size of image (tile) being added.
        for j in range (HEIGHT // height + 1): # This will tell you how many tiles you'll need for the whole screen.
            pos = (i * width, j * height) # **** This denotes the position of top left-hand corner of the current tile being added to the tiles list. In pygame to draw something you draw it from the left-hand corner. **** 
            tiles.append(pos)
            
    return tiles, image 
    
def draw(window, background, bg_image, player, objects, offset_x):
    # Loop through each tile position in the background list.
    # The background list contains positions where each background image tile should be drawn.
    for tile in background: 
        # Draw the background image (bg_image) onto the game window (window) at the position specified by 'tile'.
        # 'tile' is a tuple containing the (x, y) coordinates where the top-left corner of the background image will be placed.
        # The 'blit' function stands for "Block Transfer," and it effectively copies the bg_image to the window at the given position.
        window.blit(bg_image, tile)
        
    for obj in objects:
        obj.draw(window, offset_x)
        
    # After the background is fully drawn, we proceed to draw the player character.
    # The player object has its own 'draw' method which handles rendering the player sprite onto the window.
    # By calling player.draw(window), the player is drawn on top of the background, ensuring it appears in the correct layer order.
    player.draw(window, offset_x)
    # Finally, after all the drawing operations (background and player) have been executed,
    # we need to update the display to reflect these changes on the screen.
    # pygame.display.update() will refresh the entire screen, making sure the newly drawn elements are visible to the player.
    # Without this update, the drawings would not be shown, and the screen would appear static.
    pygame.display.update()
  
# How These Functions Work Together:
# get_background(name): This function prepares the background by determining where each tile of the background image should be placed. It does not draw anything on the screen directly. Instead, it returns a list of positions (tiles) and the background image (image) to be used later.
# Player.draw(self, win): This method is part of the Player class. It specifically handles drawing the player onto the screen. It uses pygame.draw.rect() to draw the player as a rectangle (or sprite) at the player's current position (self.rect) with the specified color (self.COLOR).
# draw(window, background, bg_image, player):This function combines everything and performs the actual rendering onto the screen during each game loop iteration.
# It uses the list of tile positions (background) and the background image (bg_image) provided by get_background(name) to draw the entire background onto the window.
# After the background is drawn, it then calls player.draw(window) to draw the player on top of the background.
# Finally, pygame.display.update() is called to ensure all the drawing operations are shown on the screen.

def handle_vertical_collision(player, objects, dy):
    collided_objects = [] # list
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0: # moving down == colliding with the top of the obj. if so, you take the bottom of player rectangle (feet) and make it equal to the top of the obj youre colliding with.  
                player.rect.bottom = obj.rect.top 
                player.landed() # method to handle what happens when land or hit
            elif dy < 0:
                player.rect.top = obj.rect.bottom # Likewise, if youre moving up, your velocity is negative, and you are hitting the bottom of an object with your top (head). So now my top will be equal to the bottom of that object I am colliding with. 
                player.hit_head()
            
            collided_objects.append(obj) # obj from above
    return collided_objects

def collide (player, objects, dx):
    # moving player to where they would be moving if theyre going left or right, then updating mask and rectangle.
    player.move(dx, 0) # This is to check if the player were to move to the right or left will they hit a block on not. 
    player.update() # need to update the rectangle and the mask before checking for collision.
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj): # using the updated mask I check: would I be colliding with an object
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update() # Overall: I am updating the mask, checking if they would collide with something, then if they did then ok, they collided with objects
    # But after checking this collision I have to move them back to where they originally where (reverse movement -dx, 0) and update mask again.
    return collided_object


def handle_move(player, objects): # check the keys being pressed on keyboard. L or R.
    keys = pygame.key.get_pressed() # tells what keys are being pressed
    player.x_vel = 0 # if not, as soon as you move left it will set the x velocity and then youll continue moving in that direction unilt it gets set back to zero. WE ONLY WANT TO MOVE WHILE HOLDING DOWN THE KEY! SO ZERO HERE!
    collide_left = collide(player, objects, -PLAYER_VEL * 2 )
    collide_right = collide(player, objects, PLAYER_VEL * 2) # * 2 to add between character and block to avoid collision glitch.
    
    if keys[pygame.K_LEFT] and not collide_left: # another option would be pygame.K_a for key a.
        player.move_left(PLAYER_VEL) # this function makes use of move_left and move_right functions to set a keyboard key to each action.
    if keys[pygame.K_RIGHT] and not collide_right: # checking if we should be able to move left or right based on where I am (and not collide_right)
        player.move_right(PLAYER_VEL)
        
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    # we will loop through all these objects and see if we hit fire (check what objs are returned if fire or not by looking at their names)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire": # you need obj first to see right or left, then obj.name to see what it is.
            player.make_hit()
        if obj and obj.name == "spikes": # you need obj first to see right or left, then obj.name to see what it is.
            player.make_hit()
    
def main(window): # The main function of the game. It sets up the background and player, then enters a loop where it updates the game state, handles events, and redraws the screen.

    clock = pygame.time.Clock() # Importing clock func
    background, bg_image = get_background("savana.png") # now pick a color from images in background. 
    
    block_size = 96 # Not 64 as we thought 
    
    player = Player(100, 100, 50, 50)
    enemy = Enemy(500, HEIGHT - block_size - 120, 64, 64)
    fire = Fire (200, HEIGHT - block_size - 64, 16 , 32) # we need x, y, width and heigth for fire. The fire file size is 16x32. This part: (HEIGHT - block_size - 64) will put it on top of a block. Then 32 width, 64 height. 
    fire.on() # or off
    spikes = Spikes (610, (HEIGHT - block_size * 2.65) - 64, 16 , 32)
    apple = Apple (690, (HEIGHT - block_size * 6.90) - 64, 32 , 32)
    # Make the floor
    # This loop says I want blocks that go left and right of the screen. Not just the current scree, but even at a scrolling background.
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range (-WIDTH // block_size, WIDTH * 2 // block_size)]
    # Fire is added here to objects:
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(block_size * 3, HEIGHT - block_size * 4, block_size), Block(block_size*4, HEIGHT - block_size * 6, block_size),
               Block(block_size * 6, HEIGHT - block_size * 3, block_size) , Block(block_size * 7, HEIGHT - block_size * 7, block_size) , fire, spikes, apple, enemy] # * breaks the floor and passes it to the list as individual elements. 
    # the line above: collision with blocks on the horizontal. We are passing another block placed at zero (x) and y will be heigth of the screen multiplied by 2 so we can run into it and then we pass the block size.
    # the second Block (Block(0, HEIGHT - block_size * 2, block_size)) adds another block. 
    # blocks = [Block(0, HEIGHT - block_size, block_size)] # positioned at 0  HEIGHT - block_size will put it in the bottom. This dislays one terrain square. 
       

    # Scrolling background:
    offset_x = 0 
    scroll_area_width = 200 # when I get to 200 pixels on the left or right of scree we start scrolling. 
    run = True 
    while run: # Necessary to regulate the frame 
        clock.tick(FPS) # Makes sure while loop runs at 60 FPS
    
        for event in pygame.event.get(): # check for events such as exit 
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN: # for double jumping
                if event.key == pygame.K_SPACE and player.jump_count < 2: #   
                    player.jump()
                
        # player.loop(FPS), handle_move(player), draw(...): These are called in the loop to update the player's state, handle movement, and render the game.
        player.loop(FPS) # loop is what actually moves the player.
        fire.loop()
        spikes.loop() 
        enemy.loop()
        enemy.move_enemy()
        apple.loop()
        fire.update()
  
        handle_move(player, objects)
        
        draw(window, background, bg_image, player, objects, offset_x)    
       # Scrolling background
       # when I get to 200 pixels on the left or right of scree we start scrolling. 
        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0): # (player.x_vel > 0) checks if we are scrolling/moving to the right. (player.rect.right) == right position of my player. (offset_x) offset we already have.
            # Checking for left and right
           offset_x += player.x_vel # checks if character is right on the screen/like if its crosses a specific boundary.
    pygame.quit()
    quit()     

if __name__ == "__main__": # We only run main function if window is called. Otherwise game code won't run.
    main(window)

