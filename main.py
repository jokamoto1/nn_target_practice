import pygame
import math
import os
import neat
import pickle
import random
import numpy as np
from sklearn.preprocessing import StandardScaler
from sys import exit

pygame.init()


HEIGHT = 400
WEIDTH = 800

ARROW_CENTER_Y = 350
screen = pygame.display.set_mode((WEIDTH, HEIGHT))
pygame.display.set_caption('Target Practice')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)

grass_surf = pygame.image.load('images/grass.jpeg').convert_alpha()


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


def collision(target, arrow_group):

    if pygame.sprite.spritecollide(target.sprite, arrow_group, True):
        target.sprite.hits += 1
        return True


def display_hits(target):
    hits = target.sprite.hits
    misses = target.sprite.misses
    font = pygame.font.Font(None, 50)
    hits_surf = font.render(f"Hits: {hits}/{hits+misses}", False, 'Black')
    hits_rect = hits_surf.get_rect(bottomleft=(0, HEIGHT))
    screen.blit(hits_surf, hits_rect)


class Target(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/target.png').convert_alpha()
        self.rect = self.image.get_rect(center=(HEIGHT, 40))
        self.hits = 0
        self.misses = 0
        self.directionx = random.choice([-1, 1])
        self.directiony = random.choice([-1, 1])
        self.directionx = 1
        self.directiony = 1
        self.rect.centerx = (random.randint(200, 600))
        self.rect.centery = (random.randint(40, 100))


    def move(self):
      
        if self.rect.left <= 0 or self.rect.right >= 800:
            self.directionx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= 150:
            self.directiony *= -1
     
        self.rect.centerx += 1* self.directionx
        self.rect.centery += 1 * self.directiony

        if random.randint(1, 50) == 50:
            self.directionx *= -1
        if random.randint(1, 50) == 50:
            self.directiony *= -1

    def update(self):
        self.move()
        


class Arrow(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/arrow2.jpg').convert_alpha()
        self.image2 = pygame.image.load('images/arrow2.jpg').convert_alpha()
        self.rect = self.image.get_rect(center=(HEIGHT, ARROW_CENTER_Y))
        self.x_velo = 0
        self.y_velo = 0

    def shoot(self, target):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.x_velo == 0:
            correction_angle = 90
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - HEIGHT, my - ARROW_CENTER_Y
            angle = math.degrees(math.atan2(-dy, dx)) - correction_angle
            if not angle < -90:
                self.y_velo, self.x_velo = normalize_vector(dy, dx)
                self.image, self.rect = rot_center(
                    self.image2, self.rect, angle)

    def shoot(self, target, mx, my, choose_to_shoot):

        if choose_to_shoot  and self.x_velo == 0:
            correction_angle = 90
            dx, dy = mx - HEIGHT, my - ARROW_CENTER_Y
            angle = math.degrees(math.atan2(-dy, dx)) - correction_angle
            if not angle < -90:
                self.y_velo, self.x_velo = normalize_vector(dy, dx)
                self.image, self.rect = rot_center(
                    self.image2, self.rect, angle)

    def move(self):
        self.rect.x += self.x_velo * 30
        self.rect.y += self.y_velo * 30

    def in_bounds(self, target):
        if self.rect.centerx <= 0 or self.rect.centerx >= 800 or self.rect.centery <= 0 or self.rect.centery >= HEIGHT:
            target.sprite.misses += 1
            self.kill()

    def update(self, target, mx, my, choose_to_shoot):
        self.in_bounds(target)
        self.shoot(target, mx, my, choose_to_shoot)
        self.move()


class Game():
    def __init__(self):
        self.num_of_arrows_left = 100
        self.score = 0

    def test_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        target = pygame.sprite.GroupSingle()
        target.add(Target())

        arrow_group = pygame.sprite.Group()
        arrow_group.add(Arrow())

        ticks = 1200
        arrow = 1

        # run = True

        while self.num_of_arrows_left > 0 and ticks > 0:
            ticks = 1
            # reload -=1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            mx, my = net.activate(
                (target.sprite.rect.centerx,  target.sprite.rect.centery,target.sprite.directionx,target.sprite.directiony )
                )

            collision(target, arrow_group)

            self.score = target.sprite.hits/(20)
            
            screen.blit(grass_surf,(0,0))

            if not arrow_group:

                arrow_group.add(Arrow())
                self.num_of_arrows_left -= 1
                # reload = 50
            arrow_group.draw(screen)
            arrow_group.update(target, mx, my, True)
# 
            target.draw(screen)
            target.update()

            display_hits(target)
            
            pygame.display.update()
            clock.tick(30)
        return target.sprite.hits,  target.sprite.misses
        # print(self.score)

def eval_genomes(genomes, config_file):
    max_fitness = 0
    for i, (genome_id, genome) in enumerate(genomes):
        if genome.fitness==None:
            genome.fitness=0
        game = Game()
        hits,misses =game.test_ai(genome, config_file)
        if max_fitness < genome.fitness:
            max_fitness =  genome.fitness
        if max_fitness > genome.fitness:
            genome.fitness += hits*2
            genome.fitness -= misses 
        else:
            genome.fitness += hits
            genome.fitness -= misses 
        
  


def run(config_file):
    """
    :param config_file: location of config file
    :return: None
    # """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(500))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 30)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


def test_best_network(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    with open("best97%.pickle", "rb") as f:
        winner = pickle.load(f)
    # winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    game = Game()
    game.test_ai(winner, config)


if __name__ == "main":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
# run("config-feedforward.txt")
test_best_network("config-feedforward.txt")
# 