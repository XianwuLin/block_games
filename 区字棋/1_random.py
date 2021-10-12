#!/bin/python3
import tkinter as tk
import time
import random
class Point():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())


Chess = {
    "A": Point(0, 0),
    "B": Point(0, 2),
    "C": Point(2, 0),
    "D": Point(2, 2),
}

NextStep = {
    Point(0, 0): [Point(2, 0), Point(0, 2), Point(1, 1)],
    Point(0, 2): [Point(0, 0), Point(1, 1)],
    Point(2, 0): [Point(0, 0), Point(1, 1), Point(2, 2)],
    Point(2, 2): [Point(2, 0), Point(1, 1)],
    Point(1, 1): [Point(0, 0), Point(0, 2), Point(2, 0), Point(2, 2)]
}

StepNow = "AB"
StepNext = "CD"
Steps = 0

def draw():
    global canvas
    global Chess
    canvas.create_rectangle(0, 0, 500, 500, fill="white") 
    canvas.create_line(40, 40, 440, 40, width=2)
    canvas.create_line(40, 40, 40, 440, width=2)
    canvas.create_line(40, 40, 440, 440, width=2)
    canvas.create_line(40, 440, 440, 440, width=2)
    canvas.create_line(40, 440, 440, 40, width=2)
    for i in Chess:
        item = Chess[i]
        if i in ("A", "B"):
            canvas.create_oval(item.y * 200+20, item.x * 200+20,
                               item.y * 200+60, item.x * 200 + 60, fill='SlateGray', width=2)
        else:
            canvas.create_oval(item.y * 200+20, item.x * 200+20,
                               item.y * 200+60, item.x * 200 + 60, fill='DarkBlue', width=2)
        canvas.create_text(item.y * 200 + 40, item.x * 200 + 40, text=i, fill="white", font=('Helvetica','24','bold'))
    canvas.pack()
    canvas.update()

def chess_can_move(c):
    global Chess
    can_go = NextStep[c].copy()
    for item in Chess.values():
        if item in can_go:
            can_go.remove(item)
    return can_go


def can_move_chess(sn):
    global Chess
    steps = []
    for i in sn:
        can_move = chess_can_move(Chess[i])
        if can_move:
            steps.append(i)
    return steps

def game(event):

    global Chess
    global StepNow
    global StepNext
    global Steps
    while True:
        Steps += 1
        cmc = can_move_chess(StepNow)
        if len(cmc) == 0:
            canvas.create_text(250, 100, text="%s 输了" % StepNow, fill="red", font=('Helvetica','48','bold'))
            print("执手(%s), 无路可走！" % StepNow)
            break
        elif len(cmc) == 1:
            # 自动移动
            c = cmc[0]
            print("执手(%s), 自动选择：%s" % (StepNow, c))
            can_move = chess_can_move(Chess[c])
        else :
            # c = input("执手(%s), 请选择移动棋子:" % StepNow).upper()
            print("执手(%s), 请选择移动棋子:" % StepNow, end='')
            if Steps == 1:
                c = "A"
                print("选择棋子： %s" % c)
            else:
                c = random.choice(StepNow)
                print("随机选择棋子： %s" % c)
            if c not in StepNow:
                print("输入错误，请重新输入。")
                continue
            can_move = chess_can_move(Chess[c])
        time.sleep(0.3)
        go = can_move[0]
        Chess[c] = go
        StepNow, StepNext = StepNext, StepNow
        draw()
    print("总步数：", Steps-1)

def main():
    global canvas
    window = tk.Tk()
    window.title('区字棋')
    print("!!! 点击窗口后，在终端操作。")
    window.geometry('500x500')
    canvas = tk.Canvas(window, bg='white', height=500, width=500)
    canvas.bind(sequence="<Button-1>", func=game)
    canvas.pack()
    draw()
    window.mainloop()

main()
