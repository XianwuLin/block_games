#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import sys
import operator
import pygame
from pygame import image
from pygame.color import THECOLORS
import time
import threading
import numpy as np

def weighted_choice(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i
grass_rate = float(10) / float(100) 
X, Y = 20, 20
rabbit_list = []
death_rabbit_list = []
world_map = [weighted_choice([int(1/ grass_rate),1]) for i in xrange(X * Y)]
life_time = []
game_status = ["",""]
game_main = None
pygame.init()
screencaption=pygame.display.set_caption('grass-rabbit')
screen=pygame.display.set_mode([900,900])
block_length = 40
y_bias = 80
x_bias = 80

def get_grass_position_list():
    global world_map
    global X, Y
    grass_position_list = list()
    map_t = np.array(world_map).reshape([X,Y])
    for x in xrange(X):
        for y in xrange(Y):
            if map_t[x,y]:
                grass_position_list.append(Point(x,y))
    return grass_position_list

def get_rabbit_position_list():
    global rabbit_list
    rabbit_position_list = [rabbit.position for rabbit in rabbit_list]
    return rabbit_position_list 

def get_rabbit_home_list():
    global rabbit_list
    rabbit_home_list = [rabbit.home for rabbit in rabbit_list]
    return rabbit_home_list 

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __eq__(self, obj):
        assert isinstance(obj, Point)
        return self.x == obj.x and self.y == obj.y
    
    def __ge__(self, obj):
        assert isinstance(obj, Point)
        return self.x >= obj.x and self.y >= obj.y
        
    def __lt__(self, obj):
        assert isinstance(obj, Point)
        return self.x < obj.x and self.y < obj.y
        
    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)
        
    def __add__(self, obj):
        assert isinstance(obj, Point)
        return Point(self.x + obj.x, self.y + obj.y)
        
    def distance(self,obj):
        assert isinstance(obj, Point)
        return max(abs(self.x - obj.x), abs(self.y - obj.y))
    
    def xy(self):
        return self.x, self.y
        
        
class Bio(object):
    def __init__(self, value = 1, max_value = 10, *args):
        super(Bio, self).__init__(*args)
        self.value = value
        self.max_value = max_value
        self.name = "Bio"
        
    def is_alive(self):
        return bool(self.value)
        
    def __str__(self):
        return self.name + " value:" + str(self.value)
        
    def growth(self, value = 1):
        if self.value:
            if self.value < self.max_value:
                self.value += value
            else:
                self.death()
                
    def kill(self):
        if self.is_alive():
            self.death()
        
    def death(self, value = 0):
        self.value = value
        
    def distance(self, point):
        return self.position.distance(point)
    
    def tick(self):
        pass

		
class Grass(Bio):
    def __init__(self ,*args, **kwargs):
        super(Grass, self).__init__(*args, **kwargs)
        self.name = "Grass"
        self.nur = 2
                
    def tick(self):
        self.growth(value = 1)
        

class Rabbit(Bio):
    def __init__(self, full = 25, position = Point(), *args, **kwargs):
        global X,Y
        super(Rabbit, self).__init__(*args, **kwargs)
        self.full = full
        self.name = "Rabbit"
        self.position = position
        self.home = self.get_home_position()
        self.last_status = ""
        self.most_home_vision = 3
        self.vision = 3
        self.home_vision = 2
        self.tick_cost = 3
        self.last_eat = []
        
    def eat(self,food):
        self.full += food.nur
        if self.home_vision >= self.most_home_vision:
            self.home_vision -= 1
        food.death()
        return food.nur, self.full
        
    def get_home_position(self):
        x,y = self.position.x, self.position.y
        
        if x % 10 == 0 and x != 0:
            hx = x / 10 * 10 - 3
        elif x % 10 <= 5:
            hx = x / 10 * 10 + 2
        else:
            hx = x / 10 * 10 + 7
        
        if y % 10 == 0 and y != 0:
            hy = y / 10 * 10 - 3
        elif y % 10 <= 5:
            hy = y / 10 * 10 + 2
        else:
            hy = y / 10 * 10 + 7
        
        return Point(hx, hy)
        
        
    def goto(self, point):
        if self.position == point:
            return self.position
        else:
            if (self.position.x != point.x):
                self.position += Point((point.x - self.position.x)/abs(self.position.x - point.x),0)
            if (self.position.y != point.y):
                self.position += Point(0,(point.y - self.position.y)/abs(self.position.y - point.y))
            return self.position
            
    def walk(self, stag = 1):
        global X, Y
        global world_map
        map_l = np.array(world_map).reshape([X,Y])
        can_eat_grass = []
        can_see_range_x0 = max(self.position.x - self.vision, self.home.x - self.home_vision)
        can_see_range_x1 = min(self.position.x + self.vision + 1, self.home.x + self.home_vision + 1)
        can_see_range_y0 = max(self.position.y - self.vision, self.home.y - self.home_vision)
        can_see_range_y1 = min(self.position.y + self.vision + 1, self.home.y + self.home_vision + 1)
        if can_see_range_x0 <= can_see_range_x1:
            can_see_range_x = [can_see_range_x0, can_see_range_x1]
        else:
            can_see_range_x = []
        
        if can_see_range_y0 <= can_see_range_y1:
            can_see_range_y = [can_see_range_y0, can_see_range_y1]
        else:
            can_see_range_y = []
        
        if can_see_range_x and can_see_range_y:
            for x in range(can_see_range_x0, can_see_range_x1):
                for y in range(can_see_range_y0, can_see_range_y1):
                    if x >= 0 and x < X and y >= 0 and y <Y and map_l[x, y]:
                        point_t = Point(x,y)
                        can_eat_grass.append([point_t, self.distance(point_t)])
        
        if can_eat_grass:
            can_eat_grass.sort(key=operator.itemgetter(1),reverse=False)
            best_grass_list = []
            best_score = can_eat_grass[0][1]
            for k,v in can_eat_grass:
                if best_score == v:
                    best_grass_list.append(k)
            self.goto(random.choice(best_grass_list))
            return self.position
        else:      
            if stag > self.most_home_vision:
                self.goto(self.home)
                return self.position
            else:
                if map_l[self.home.x - self.home_vision:self.home.x + self.home_vision + 1, self.home.y - self.home_vision:self.home.y + self.home_vision + 1].any():
                    self.goto(self.home)
                    return self.position
                else:
                    self.home_vision += 1
                    stag += 1
                    return self.walk(stag)
        
    def walk1(self):
        weight = [2,-4,-1] # 食物、其他竞争者、距离的权重
        global X, Y
        global world_map
        map_l = np.array(world_map).reshape([X,Y])
        grass_set = set(get_grass_position_list())
        hunter_set = get_rabbit_position_list()
        hunter_set.remove(self.position)
        hunter_set = set(hunter_set)
        hunter_set = hunter_set if hunter_set else set()
        can_eat_grass = list()

        for grass_position in grass_set:
            distance = self.distance(grass_position)
            #食物在脚下
            if distance == 0:
                return self.position
            grass = Grass()
            grass.position = grass_position
            if grass.max_value - grass.value > distance and self.full > distance and self.max_value - self.value > distance:
                food_score  = 0.0
                hunter_score = 0.0
                for x in xrange(-self.vision,self.vision + 1):
                    for y in xrange(-self.vision, self.vision + 1):
                        point_t = Point(x,y) + self.position
                        if self.position != point_t:
							if point_t in grass_set:
								food_score += weight[0] * float(grass.nur/grass.distance(point_t)) #周围食物评分
							if point_t in hunter_set:
								hunter_score += weight[1] * float(grass.nur/grass.distance(point_t)) #周围其他捕猎者评分
                score = food_score + hunter_score + distance * weight[2]
                can_eat_grass.append([grass.position, score])
        if can_eat_grass:
            can_eat_grass.sort(key=operator.itemgetter(1),reverse=True)
            best_grass_list = []
            best_score = can_eat_grass[0][1]
            for k,v in can_eat_grass:
                if best_score == v:
                    best_grass_list.append(k)
            self.goto(random.choice(best_grass_list))
            return self.position
        else:                
            while True:
                x = random.randint(-1,1)
                y = random.randint(-1,1)
                if self.position + Point(x, y) >= Point(0,0) and self.position + Point(x, y) < Point(X,Y):
                    self.position += Point(x, y)
                    return self.position

    def death(self):
        life_time.append(self.value)
        # print "A rabbit death, age:", self.value
        super(Rabbit, self).death()
        
    def tick(self):
        self.growth(value = 1)
        self.full -= self.tick_cost
        if self.full <= 0:
            self.death()
            
        elif self.full > 50:
            self.full = 50
			

def redraw(X, Y):
    for x in xrange(X):
        for y in xrange(Y):
            block = [x * block_length + x_bias, y * block_length + y_bias, block_length, block_length]
            pygame.draw.rect(screen,THECOLORS["slateblue1"],block,1)
    
    for x in xrange(X):
        for y in xrange(Y):
            block = [x * block_length + x_bias, y * block_length + y_bias, block_length, block_length]        
            if (x % 10 == 2 or x % 10 == 7) and (y % 10 == 2 or y % 10 == 7): 
                pygame.draw.rect(screen,THECOLORS["red"],block,2)
    
    for x in xrange(X / 5):
        for y in xrange(Y / 5):
            block = [x * 5 * block_length + x_bias, y * 5 * block_length + y_bias, block_length * 5, block_length * 5]        
            pygame.draw.rect(screen,THECOLORS["black"],block,2)
    
def draw_grass(positions):
    grass_image = pygame.image.load('grass.jpg')
    grass_image = pygame.transform.scale(grass_image, (block_length - 2, block_length - 2))
    for pos in positions:
        x,y = pos.x, pos.y
        top = x * block_length + 1 + x_bias
        left = y * block_length + 1 + y_bias
        screen.blit(grass_image,[top, left])
        
        
def draw_rabbit(positions):
    
    grass_image = pygame.image.load('rabbit.png').convert_alpha()
    grass_image = pygame.transform.scale(grass_image, (block_length - 4, block_length - 4))
    for pos in positions:
        x,y = pos.x, pos.y
        top = x * block_length + 2 + x_bias
        left = y * block_length + 2 + y_bias
        screen.blit(grass_image,[top, left])
        
def draw_points(positions, color, random_use = True):
    for pos in positions:
        x,y = pos.x, pos.y
        if random_use:
            top = random.randint(x * 20 + 2 + x_bias, x * 20 + 18 + x_bias)
            left = random.randint(y * 20 + 2 + y_bias, y * 20 + 18 + y_bias)
        else:
            top = x * 20 + 10 + x_bias
            left = y * 20 + 10 + y_bias
        pygame.draw.circle(screen,THECOLORS[color],[top,left],3,0)
        
def draw_word():
    global game_status
    my_font = pygame.font.SysFont("arial", 18)
    text_surface = my_font.render(str(game_status[0]), False, THECOLORS["black"], (230, 230, 230))
    text_surface1 = my_font.render(str(game_status[1]), False, THECOLORS["black"], (230, 230, 230))
    screen.blit(text_surface,[130, int(y_bias / 2)])
    screen.blit(text_surface1,[130 + 130, int(y_bias / 2)])

def draw():
    while True:
        screen.fill([230,230,230])
        draw_word()
        draw_grass(get_grass_position_list())
        draw_rabbit(get_rabbit_position_list())
        redraw(X, Y)
        pygame.display.update()
        time.sleep(0.1)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit(0)
                
def get_total_home_list():
    global X, Y
    total_home_list = list()
    for x in xrange(X / 5):
        for y in xrange(Y / 5):
            total_home_list.append(Point(x * 5 + 2, y * 5 + 2))
    return total_home_list
    
def get_remain_home_list():
    rabbit_home_list = get_rabbit_home_list()
    total_home_list = get_total_home_list()
    remain_home_list = []
    for i in total_home_list:
        if i not in rabbit_home_list:
            remain_home_list.append(i)
    return remain_home_list
    
def main():
    global world_map
    global X
    global Y
    global rabbit_list
    global death_rabbit_list
    global game_status
        
    for i in xrange(200):
        death_rabbit_list = []
        game_status[0] = "Day {0}".format(i+1)
        world_map = map(tick, world_map)
        tmp = np.array(world_map).reshape([X,Y])

        if len(rabbit_list) < len(get_total_home_list()):
            rabbit = Rabbit(position = random.choice(get_remain_home_list()),max_value=50)
            rabbit_list.append(rabbit)

        for k in xrange(5):
            game_status[1] = "Loop {0}".format(k+1)
            rabbit_list_t = range(len(rabbit_list))

            random.shuffle(rabbit_list_t)
            for j in rabbit_list_t:
                rabbit = rabbit_list[j]
                if tmp[rabbit.position.x, rabbit.position.y]:
                    grass = Grass(tmp[rabbit.position.x, rabbit.position.y])
                    value,_ = rabbit.eat(grass)
                    rabbit.last_status += "({0}) eat {1}; ".format(rabbit.position, value)
                    rabbit.last_eat.append(value)
                    tmp[rabbit.position.x, rabbit.position.y] = 0
                else:
                    rabbit.walk()
                    rabbit.last_eat.append(0)
                    rabbit.last_status += "({0}) walk; ".format(str(rabbit.position))
                world_map = list(tmp.reshape([1,X*Y])[0])
                time.sleep(0.1)
        for j in xrange(len(rabbit_list)):
            rabbit = rabbit_list[j]
            rabbit.tick()
            if not rabbit.is_alive():
                death_rabbit_list.append(rabbit)

        for death_rabbit in death_rabbit_list:
            rabbit_list.remove(death_rabbit)
        
        world_map = list(tmp.reshape([1,X*Y])[0])
        
        if len(rabbit_list) == 0:
            break

        time.sleep(0.2)
        
    if life_time:
        print  "average life time:", sum(life_time) / float(len(life_time))

def tick(value):
    global grass_rate
    if value == 0:
        choice = weighted_choice([int(1/ grass_rate),1])
        if choice:
            return int(Grass().value)
        else:
            return 0
    else:
        grass = Grass(value)
        grass.tick()
        if not grass.is_alive():
            return 0
        else:
            return int(grass.value)
            
            
if __name__ == '__main__':
    game_main = threading.Thread(target=main)
    game_main.setDaemon(True)
    game_main.start()
    draw()
