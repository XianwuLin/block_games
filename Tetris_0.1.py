#!/usr/bin/env python
# -*- coding:utf-8 -*   -
#
# Author  :   Victor Lin
#   E-mail  :   linxianwusx@gmail.com
#   Date    :   2015/1/10

import random
from copy import deepcopy
import numpy as np
import pygame,sys
from pygame.locals import *
import time
import easygui

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

class Block(object):
    shapeCounts = 0
    shapeList = []
    def __init__(self, shapeCounts = 1):
        self.shapeCounts = shapeCounts

@singleton
class ActivityBlock(Block):
    currentBlock = Block
    currentBlockRotate = 0
    positionX, positionY = 4, 0
    nextBlock = Block
    nextBlockRotate = 0

    def __init__(self):
        self.currentBlock = Block3
        self.currentBlockRotate = 1
        self.nextBlock = Block6
        self.nextBlockRotate = 3

    def rotate(self):
        #旋转
        game = Game()
        if self.currentBlock.shapeCounts == 1:
            pass
        elif self.currentBlock.shapeCounts == 2:
            if self.currentBlockRotate == 1:
                flag = game.collisionDetect([self.positionX, self.positionY], self.currentBlock.shapeList[0])
                if flag:
                    self.currentBlockRotate = 0
            else:
                flag = game.collisionDetect([self.positionX, self.positionY], self.currentBlock.shapeList[self.currentBlockRotate + 1])
                if flag:
                    self.currentBlockRotate += 1
        else:
            if self.currentBlockRotate == 3:
                flag = game.collisionDetect([self.positionX, self.positionY], self.currentBlock.shapeList[0])
                if flag:
                    self.currentBlockRotate = 0
            else:
                flag = game.collisionDetect([self.positionX, self.positionY], self.currentBlock.shapeList[self.currentBlockRotate + 1])
                if flag:
                    self.currentBlockRotate += 1

    def autoDown(self):
        #自动下降

        game = Game()
        flag = game.collisionDetect([self.positionX, self.positionY+1], self.currentBlock.shapeList[self.currentBlockRotate])
        if flag:
            self.positionY += 1
            canvas = Canvas()
            canvas.reDraw(self.currentBlock.shapeList[self.currentBlockRotate],[self.positionX,self.positionY])
        else:
            game = Game()
            game.next()
        return flag

    def down(self):
        #按下键的动作
        flag = self.autoDown()
        while flag:
            flag = self.autoDown()
        return

    def up(self):
        self.rotate()
        canvas = Canvas()
        canvas.reDraw(self.currentBlock.shapeList[self.currentBlockRotate],[self.positionX,self.positionY])
        return

    def left(self):
        #按下左键的动作
        game = Game()
        flag = game.collisionDetect([self.positionX-1, self.positionY], self.currentBlock.shapeList[self.currentBlockRotate])
        if flag:
            self.positionX -= 1
            canvas = Canvas()
            canvas.reDraw(self.currentBlock.shapeList[self.currentBlockRotate],[self.positionX,self.positionY])
        return

    def right(self):
        #按下右键的动作
        game = Game()
        flag = game.collisionDetect([self.positionX+1, self.positionY], self.currentBlock.shapeList[self.currentBlockRotate])
        if flag:
            self.positionX += 1
            canvas = Canvas()
            canvas.reDraw(self.currentBlock.shapeList[self.currentBlockRotate],[self.positionX,self.positionY])
        return

    def getNext(self):
        #获取下一个图形
        id1 = random.randint(1,7)
        if id1 == 1:
            return [Block1,0]
        elif id1 <= 4:
            id2 = random.randint(0,1)
            return [globals()["Block"+str(id1)], id2]
        elif id1 <=7:
            id2 = random.randint(1,3)
            return [globals()["Block"+str(id1)], id2]

@singleton
class Canvas(object):

    def __init__(self):
        self.backCanvasList = np.array([[0]*12]*22)
        self.foreCanvasList= []
        self.foreCanvasList = None
        for i in self.backCanvasList:
            i[0],i[-1] = 1,1
        self.backCanvasList[-1] = 1
        self.foreCanvasList = self.backCanvasList.copy()

    def removeBlock(self):
        import time
        reverseBlock = self.backCanvasList[::-1]
        for i in xrange(20):
            line = 0
            for j in reverseBlock[1:]:
                line += 1
                if not any(j-[1,1,1,1,1,1,1,1,1,1,1,1]): #消行
                    for i in xrange(line,20):
                        reverseBlock[i] = reverseBlock[i+1]
                    reverseBlock[-1] = [1,0,0,0,0,0,0,0,0,0,0,1]
                    self.backCanvasList = deepcopy(reverseBlock[::-1])
                    game = Game()
                    game.score += 100
        return True

    def reDraw(self, blockList, position):
        newBlock = np.array([[0]*12]*22)
        x, y = position
        for i in range(len(blockList)):
            for j in range(len(blockList[0])):
                newBlock[y+i][x+j] = blockList[i][j]
        newCanvastList = self.backCanvasList + newBlock
        if 2 in newCanvastList:
            game = Game()
            game.endGame()
            return
        self.foreCanvasList = newCanvastList

    def show(self):
        canvas = np.array([[0]*10]*20)
        canvas = self.foreCanvasList[2:-1,1:-1]
        return canvas

@singleton
class Game(object):

    def __init__(self):
        self.score = 0
        self.status = 1

    def run(self, level=0.5):
        while self.status:
            activityBlock = ActivityBlock()
            if self.breakstatus == 0:
                activityBlock.autoDown()
            time.sleep(level)

    def startGame(self,level=0.5):
        import thread
        self.status = 1
        self.breakstatus = 0
        activityBlock = ActivityBlock()
        canvas = Canvas()

        pygame.init()
        screencaption=pygame.display.set_caption("Block")
        screen = pygame.display.set_mode([300,380])
        screen.fill([255,255,255])
        my_font = pygame.font.SysFont("arial", 16)
        clock = pygame.time.Clock()
        thread.start_new_thread(self.run,(level,))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        activityBlock.left()
                    elif event.key == K_RIGHT:
                        activityBlock.right()
                    elif event.key == K_UP:
                        activityBlock.up()
                    elif event.key == K_DOWN:
                        activityBlock.down()
            if self.status:
                screen.fill([255,255,255])
                list = canvas.show()
                x,y = 0,0
                for i in list:
                    y += 1
                    x = 0
                    for j in i:
                        x += 1
                        if j == 1:
                            newRect = ((x-1)*20,(y-1)*20,20,20)
                            pygame.draw.rect(screen,[0,200,100],newRect,0)
                            pygame.draw.rect(screen,[0,0,0],newRect,1)
                pygame.draw.rect(screen,[0,0,0],[0,0,200,380],3)
                text_surface = my_font.render(str(self.score), True, (0,0,0), (255, 255, 255)) # 绘制分数
                screen.blit(text_surface,[220,50])
                nextList = activityBlock.nextBlock.shapeList[activityBlock.nextBlockRotate]
                t = 0
                for i in nextList:
                    t += 1
                    x = 0
                    for j in i:
                        x += 1
                        if j == 1:
                            newRect = ((x-1)*20+220,(t-1)*20+100,20,20)
                            pygame.draw.rect(screen,[0,200,100],newRect,0)
                            pygame.draw.rect(screen,[0,0,0],newRect,1)
                pygame.display.flip()
                pygame.time.delay(30)

    def endGame(self):
        #停止游戏
        self.status = 0
        easygui.msgbox(str(self.score), u"得分")


    def next(self):
        import time
        #消行
        canvas = Canvas()
        #前景与背景的转换
        canvas.backCanvasList = canvas.foreCanvasList
        self.breakstatus = 1
        time.sleep(0.15)
        self.breakstatus = 0
        canvas.removeBlock()
        #得到下一个方块，转换当前方块
        activityBlock = ActivityBlock()
        nextBlock = activityBlock.getNext()
        activityBlock.currentBlock = activityBlock.nextBlock #第二个方块传到第一个方块
        activityBlock.currentBlockRotate = activityBlock.nextBlockRotate

        activityBlock.nextBlock,activityBlock.nextBlockRotate = nextBlock
        activityBlock.positionX = 4
        activityBlock.positionY = 0
        canvas.reDraw(activityBlock.currentBlock.shapeList[activityBlock.currentBlockRotate],[activityBlock.positionX,activityBlock.positionY])
        return

    def collisionDetect(self, position, blockList):
        canvas = Canvas()
        #检测block是否可以移动到position处，如果检测到一个块内画布和块重叠，则说明会有碰撞。不可移动，返回为False，否则为True。
        newBlock = np.array([[0]*12]*22)
        x, y = position
        for i in range(len(blockList)):
            for j in range(len(blockList[0])):
                try:
                    newBlock[y+i][x+j] = blockList[i][j]
                except:
                    return False
        newBlock = canvas.backCanvasList + newBlock
        return True if 2 not in newBlock else False

Block1 = Block(1)
Block1.shapeList = [[[1,1],[1,1]]]

Block2 = Block(2)
Block2.shapeList = [[[1,1,1,1]],
                  [[1],[1],[1],[1]]]

Block3 = Block(2)
Block3.shapeList = [[[1,1,0],[0,1,1]],
                     [[0,1],[1,1],[1,0]]]

Block4 = Block(2)
Block4.shapeList = [[[0,1,1],[1,1,0]],
                     [[1,0,0],[1,1,0],[0,1,0]]]

Block5 = Block(4)
Block5.shapeList = [[[0,1,0],[1,1,1]],
                  [[1,0],[1,1],[1,0]],
                  [[1,1,1],[0,1,0]],
                  [[0,1],[1,1],[0,1]]]

Block6 = Block(4)
Block6.shapeList = [[[1,1,1],[0,0,1]],
                     [[0,1],[0,1],[1,1]],
                     [[1,0,0],[1,1,1],[0,0,0]],
                     [[1,1],[1,0],[1,0]]]

Block7 = Block(4)
Block7.shapeList= [[[0,0,1],[1,1,1]],
                     [[1,0],[1,0],[1,1]],
                     [[1,1,1],[1,0,0]],
                     [[1,1],[0,1],[0,1]]]


if __name__ == "__main__":
    Game().startGame(0.4)
