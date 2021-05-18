from tkinter import *
from turtle import RawTurtle,TurtleScreen
from random import randint,choice
from time import time;T = time()

#window
root = Tk();root.title("Elev8");root.geometry("608x405")
menu = Menu(root);root.config(menu=menu)
firstFloorEntry = Entry(root);firstFloorEntry.grid(row=1,sticky="w")
#menu
mono = True
def hueFlip():
    global mono
    if (not mono) or floors <= 7:
        mono = not mono
        menu.entryconfig(1,label="Colours: "+["Rainbow","Mono"][int(mono)])
framePeriod = 17
def fpsFlip():
    global framePeriod
    framePeriod = 17 - framePeriod
    menu.entryconfig(2,label="Speed: "+["Max","Throttled"][int(framePeriod == 17)])
menu.add_command(label="Colours: Mono",command=hueFlip)
menu.add_command(label="Speed: Throttled",command=fpsFlip)


#parameters
floors = 7
FIRST_FLOOR_WEIGHT = 0 #UNUSED AS OF YET

#graphics
def floorHeight(floor):
    return int(floor*(405/floors)) - 199

#simulation
def between(a,b,c):return b <= a <= c or c <= a <= b
class Passenger:
    def __init__(self,from_,to,random=False):
        self.from_ = from_
        self.to = to
        self.frames = 0
        if random:
            self.from_ = randint(0,floors-1)
            self.to = choice([z for z in range(floors) if z != self.from_])
    def tick(self):self.frames += 1
class ElevatorSim:
    def __init__(self,col,docking):
        self.docking = docking
        self.waitTimes = []
        self.col = col
        self.contents = []
        self.pos = floorHeight(0)
        self.canvases = [Canvas(root,width=300,height=400) for z in range(2)]
        self.screens = [TurtleScreen(self.canvases[0]),
                        TurtleScreen(self.canvases[1])]
        self.t = [RawTurtle(self.screens[0]),
                  RawTurtle(self.screens[1])]
        for z in range(2):
            self.t[z].speed(0)
            self.t[z].ht()
            self.t[z].pu()
            self.screens[z].tracer(0)
        self.speed = 0
        self.frame = 1
        self.canvases[0].grid(row=0,column=col)
        self.destination = 0
        self.delivered = 0
        self.waiting = 1
        self.waitingPassengers = []
    def renderFrame(self):
        frame = self.frame
        
        self.canvases[1 - frame].grid_forget()
        self.canvases[frame].grid(row=0,column=self.col)
        self.screens[frame].update()
        
        self.t[1 - frame].reset()
        self.t[1 - frame].ht()
        self.t[1 - frame].pu()
        self.t[1 - frame].speed(0)
        
        self.frame = 1 - self.frame
    def draw(self):
        frame = self.frame

        #rectangle
        self.t[frame].color("#000000")
        self.t[frame].seth(90)
        self.t[frame].pd()
        for z in range(4):
            self.t[frame].fd(30 - 10*(z%2))
            self.t[frame].rt(90)
        self.t[frame].pu()

        #arrow
        if self.contents:
            if self.pos < floorHeight(self.contents[0].to):#going up!
                self.t[frame].goto(10,self.pos + 5)
                self.t[frame].seth(90)
            if self.pos > floorHeight(self.contents[0].to):#going down!
                self.t[frame].goto(10,self.pos + 25)
                self.t[frame].seth(270)
            if self.pos != floorHeight(self.contents[0].to):
                self.t[frame].color("#AAAAAA")
                self.t[frame].pd()
                self.t[frame].fd(20)
            
                self.t[frame].rt(30)
                self.t[frame].bk(10);self.t[frame].fd(10)
                self.t[frame].lt(60)
                self.t[frame].bk(10);self.t[frame].fd(10)
                self.t[frame].rt(30)

                self.t[frame].pu()
                self.t[frame].color("#000000")
            
        #contents
        for z in range(len(self.contents)):
            if not mono:
                self.t[frame].color(["red","orange","yellow","green","blue","purple","violet"][self.contents[z].to])
            self.t[frame].goto(6 + 8*(z%2),5 + self.pos + 7*(z//2))
            self.t[frame].dot(6)
    def drawShaft(self):
        frame = self.frame
        self.t[frame].seth(0)
        for floor in range(floors):
            self.t[frame].color("#AAAAAA")
            self.t[frame].goto(30,floorHeight(floor))
            self.t[frame].pd()

            length = 70
            for z in [q for q in self.waitingPassengers
                      if q.from_ == floor]:
                if not mono:
                    self.t[frame].color(["red","orange","yellow","green","blue","purple","violet"][z.to])
                if z.to == 0:self.t[frame].write("G",align="CENTER",font=("Arial",15))
                else:self.t[frame].write(z.to,align="CENTER",font=("Arial",15))

                if not mono:
                    self.t[frame].color(["red","orange","yellow","green","blue","purple","violet"][floor])
                self.t[frame].fd(14)
                length -= 14
            if not mono:
                self.t[frame].color(["red","orange","yellow","green","blue","purple","violet"][floor])
            self.t[frame].fd(length)
            self.t[frame].bk(100)
            self.t[frame].pu()

        #Stats
        self.t[frame].color("#000000")
        self.t[frame].goto(-145,170)
        string = "Delivered: "+str(self.delivered)+"\nAverage time: "
        if self.delivered:
            a = sum(self.waitTimes)/self.delivered
            a *= 17/1000
            a = round(a,ndigits=2)
            string += str(a)+"s"
        self.t[frame].write(string,align="LEFT")
    def tick(self):
        for z in range(len(self.contents)):
            self.contents[z].tick()
        frame = self.frame
        #adjusting speed
        if abs(self.pos - floorHeight(self.destination)) < self.speed*(self.speed+1)/2:
            self.speed -= 1
        elif self.speed < 5:
            if abs(self.pos - floorHeight(self.destination)) >= (self.speed+1)*(self.speed+2)/2:
                self.speed += 1
        #moving
        if self.pos < floorHeight(self.destination):
            self.pos += self.speed
        else:
            self.pos -= self.speed
        #reacting to arriving at destination
        if self.pos == floorHeight(self.destination):
            self.speed = 0
            #waiting (simulating people getting off)
            if self.waiting == 0:
                #Letting passengers off
                self.delivered += len([z for z in self.contents if z.to == self.destination])
                self.waitTimes += [z.frames for z in self.contents if z.to == self.destination]
                self.contents = [z for z in self.contents if z.to != self.destination]
                
                self.waiting = 60
            elif self.waiting > 1:
                self.waiting -= 1
                if self.waiting == 30:
                    #Loading passengers on
                    for z in range(len(self.waitingPassengers)):
                        if self.waitingPassengers[z].from_ == self.destination:
                            self.contents.append(self.waitingPassengers[z])
                    self.waitingPassengers = [z for z in self.waitingPassengers
                                              if z.from_ != self.destination]
            else:
                self.waiting = 0
                
                if self.waitingPassengers == [] and self.contents == []:
                    if self.docking:self.destination = 0
                    else:self.waiting == 1
                else:
                    if self.contents != []:destination = self.contents[0].to
                    else:destination = self.waitingPassengers[0].from_

                    for z in range(destination,self.destination,1-2*int(self.destination < destination)):
                        if len([q for q in self.waitingPassengers
                                if q.from_ == z and between(q.to,z,destination)]) > 0:
                            destination = z
                        if len([q for q in self.contents if q.to == z]) > 0:destination = z
                    self.destination = destination
            
        self.drawShaft()
        self.t[frame].goto(0,self.pos)
        self.draw()
        self.renderFrame()

        if randint(0,200) == 0:
            self.waitingPassengers.append(Passenger(0,0,random=True))
        
elevators = [ElevatorSim(z,z==1) for z in range(2)]
elevators[0].drawShaft()
elevators[0].renderFrame()


def frameTick():
    global T
    elevators[0].tick()
    elevators[1].tick()

    while time() - T < framePeriod*0.001:root.update()
    T = time()
    root.after(0,frameTick)

root.after(0,frameTick)
root.mainloop()
