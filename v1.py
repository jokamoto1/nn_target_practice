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


target_x = WEIDTH/2-40
target_y = HEIGHT/10
target_x_direction = 'left'
target_surf = pygame.image.load('images/target.png').convert_alpha()
target_rect = target_surf.get_rect(center =(target_x,target_y) )

arrow_surf =  pygame.image.load('images/arrow2.jpg').convert_alpha()
arrow_surf1 =  pygame.image.load('images/arrow2.jpg').convert_alpha()
arrow_rect = arrow_surf.get_rect(center =(target_x,target_y+300) )
arrow_shoot = False
arrow_direction = 0

grass_surf = pygame.image.load('images/grass.jpeg').convert_alpha()



hits = 0
misses = 0
arrows_launched = 0


def rot_center(image, rect, angle):
        """rotate an image while keeping its center"""
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image,rot_rect
def vector_length(x, y):
    return math.sqrt(x*x + y*y)

def normalize_vector(x, y):
    norm = vector_length(x, y)
    return x/norm, y/norm




while True:

    hits_surf = font.render(f"Hits: {hits}/{hits+misses}", False, 'Black')
    hits_rect = hits_surf.get_rect(bottomleft = (0,400))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
       
        if event.type ==  pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not arrow_shoot:

                    correction_angle = 90  
                    mx, my = pygame.mouse.get_pos()
                    dx, dy = mx -  360, my - 340
                    angle = math.degrees(math.atan2(-dy, dx)) - correction_angle
                    if not angle < -90: 
                        arrow_shoot = True
                        arrows_launched += 1
                        arrow_surf, arrow_rect = rot_center(arrow_surf1, arrow_rect, angle)



    if target_rect.left <= 0:
        target_x_direction = 'right'
    elif target_rect.right >= 800:
        target_x_direction = 'left'

    if target_x_direction =='left':
        target_rect.left-=2
    else:
        target_rect.right +=2

       
        
    if arrow_shoot:


        target = normalize_vector(dy, dx)
        arrow_rect.x += target[1] * 7
        arrow_rect.y += target[0] * 7
        # slope = dy/dx

        # max_num = max(abs(dy),abs(dx))
        # min_num = min(abs(dy),abs(dx))

        # ratio = min_num/max_num

        # if dy > dx:
        #     if angle < 0:
        #         arrow_rect.centery += ((dx/dy))*-2
        #         arrow_rect.centerx += (1-(dx/dy))*-2
        #     else:
        #         arrow_rect.centery += ((dx/dy))*2
        #         arrow_rect.centerx += (1-(dx/dy))*2
        # else:
        #     if angle < 0:
        #         arrow_rect.centery += (1-(dy/dx)) *-2
        #         arrow_rect.centerx += ((dy/dx)) *-2
        #     else:
        #         arrow_rect.centery += (1-(dy/dx)) *-2
        #         arrow_rect.centerx += ((dy/dx)) *-2



    # print(arrow_rect.center)
    if arrow_rect.centerx <= 0 or arrow_rect.centerx >=800 or arrow_rect.centery <=0 or arrow_rect.centery >= 400 or arrow_rect.colliderect(target_rect):
        # arrow_rect = arrow_surf.get_rect(center =(360,340))
        # arrow_surf, arrow_rect = rot_center(arrow_surf, arrow_rect, - angle)

        if arrow_rect.colliderect(target_rect):
            hits += 1
        else:
            misses += 1
        arrow_surf = arrow_surf1
        arrow_rect.center = (360,340)
        arrow_shoot = False

    # arrow_rect.center
    # 360,340
    # arrow_shoot = False

    screen.blit(grass_surf,(0,0))
    screen.blit(hits_surf,hits_rect)
    screen.blit(target_surf,target_rect)
    screen.blit(arrow_surf,arrow_rect)

    pygame.display.update()
    clock.tick(60)


