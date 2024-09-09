import pygame
import random
import math
import os
from os import listdir
from os.path import isfile, join
pygame.init()

FPS = 60
PLAYER_VEL = 5

# flipping our character image 
def flip (sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites] 

def load_sprite_sheets (dir1, dir2, width, height, direction = False):
    