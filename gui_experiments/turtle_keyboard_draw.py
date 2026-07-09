import turtle as tur
import random
t=tur.Turtle(shape="classic",visible=True)
win=tur.Screen()
win.setup(width=1000,height=500)
win.bgcolor('black')
win.bgpic()
t.hideturtle()
t.color('white')
t.width(1)
running = False
def goup():
 y=t.ycor()
 y=y+10
 t.sety(y)
def godown():
 y=t.ycor()
 y=y-10
 t.sety(y)
def left():
 x=t.xcor()
 x=x-10
 t.setx(x)
def right():
 x=t.xcor()
 x=x+10
 t.setx(x) 
def clear():
 t.clear() 
 t.penup()
 t.goto(0,0)
 t.pendown()
def rand():
 global running
 if running:
   t.speed(100)
   t.goto(random.randint(-700,700), random.randint(-400, 400))
   win.ontimer(rand,10)
def rand_start():
    global running
    if not running:
        running= True
        rand()
     
def rand_stop():
    global running
    running=False 

win.listen()

win.onkeypress(goup,'Up')
win.onkeypress(godown,'Down')
win.onkeypress(left,'Left')
win.onkeypress(right,'Right')
win.onkeypress(clear,'x')
win.onkeypress(rand_start,'r')
win.onkeypress(rand_stop,'s')
tur.done()
