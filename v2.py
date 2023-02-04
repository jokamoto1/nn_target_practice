import pygame
import math
from sys import exit

pygame.init()


HEIGHT = 400
WEIDTH = 800
screen  = pygame.display.set_mode((WEIDTH,HEIGHT))
pygame.display.set_caption('Target Practice')
clock = pygame.time.Clock()
font = pygame.font.Font(None,50)

grass_surf = pygame.image.load('images/grass.jpeg').convert_alpha()
arrows_launched = 0


def rot_center(image, rect, angle):
        """rotate an image while keeping its center"""
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image, rot_rect

def vector_length(x, y):
    return math.sqrt(x*x + y*y)

def normalize_vector(x, y):
    norm = vector_length(x, y)
    return x/norm, y/norm

def collision(target,arrow_group):

    if pygame.sprite.spritecollide(target.sprite,arrow_group,True):
        target.sprite.hits += 1

def display_hits(target):
    hits = target.sprite.hits
    arrows_launched = target.sprite.arrows_launched
    font = pygame.font.Font(None,50)
    hits_surf = font.render(f"Hits: {hits}/{arrows_launched}", False, 'Black')
    hits_rect = hits_surf.get_rect(bottomleft = (0,400))
    screen.blit(hits_surf,hits_rect)
class Target(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/target.png').convert_alpha()
        self.rect = self.image.get_rect(center=(400, 40))
        self.x_direction = 'left'
        self.hits = 0
        self.arrows_launched = 0

    def move(self):
        if self.rect.left <= 0:
            self.x_direction = 'right'
        elif self.rect.right >= 800:
            self.x_direction = 'left'
        if self.x_direction == 'left':
            self.rect.centerx -= 2
        else:
            self.rect.centerx += 2

    def update(self):
        self.move()

class Arrow(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/arrow2.jpg').convert_alpha()
        self.image2 = pygame.image.load('images/arrow2.jpg').convert_alpha()
        self.rect = self.image.get_rect(center=(400, 350))
        self.x_velo = 0
        self.y_velo = 0

    def shoot(self,target):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.x_velo == 0:
            correction_angle = 90
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx -  360, my - 340
            angle = math.degrees(math.atan2(-dy, dx)) - correction_angle
            if not angle < -90:
                self.y_velo, self.x_velo = normalize_vector(dy, dx)
                target.sprite.arrows_launched +=1
                self.image, self.rect = rot_center(self.image2, self.rect, angle)     

    def move(self):
        self.rect.x += self.x_velo * 7
        self.rect.y += self.y_velo * 7
    def in_bounds(self):
        if self.rect.centerx <= 0 or self.rect.centerx >=800 or self.rect.centery <=0 or self.rect.centery >= 400:
            self.kill()
    def update(self,target):
        self.in_bounds()
        self.shoot(target)
        self.move()
        

target = pygame.sprite.GroupSingle()
target.add(Target())

arrow_group = pygame.sprite.Group()
arrow_group.add(Arrow())


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    screen.blit(grass_surf,(0,0))



    collision(target,arrow_group)

    if not arrow_group:
        arrow_group.add(Arrow())

    arrow_group.draw(screen)
    arrow_group.update(target)

    target.draw(screen)
    target.update()

    display_hits(target)
    
    pygame.display.update()
    clock.tick(60)
