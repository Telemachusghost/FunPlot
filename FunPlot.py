import sys
import tkinter as tk
from tkinter import *
import numpy as np
from math import *


"""

A simple plotting program that parses expressions
and plots them using tkinter. Can understand standard python expressions.

***Possible additions***

1. Some more error code in order to handle expressions python does not understand
2. Some general clean up
3. Have the canvas be cleaned when every new graph is drawn *Done*
4. Better drawing representation *Possibly done I made it draw more dots to get a better plot of the function which impacted performance*
5. Ability to change interval and screen size possibly through command line arguments
6. Be able to use it through the command line
7. x**x seems off and may be an issue with how I i transform the equation to be drawn to screen

************************

author Derick Falk, Daniel Denniston, Thomas Bowers
"""

# Some important variables
DEFAULT_HEIGHT = 500
DEFAULT_WIDTH = 500


	

# The root plotting window
class graph(tk.Tk):

	def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
		
		tk.Tk.__init__(self)
		self.width = width
		self.height = height

		self.can = Canvas(self, width = width , height = height, bg = 'white')
		
		hbar=Scrollbar(self,orient=HORIZONTAL)
		hbar.pack(side=BOTTOM,fill=X)
		hbar.config(command=self.can.xview)
		
		vbar=Scrollbar(self,orient=VERTICAL)
		vbar.pack(side=RIGHT,fill=Y)
		vbar.config(command=self.can.yview)

		
		self.can.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set, scrollregion=(0,0,2000,2000))
		self.can.pack(side=LEFT,expand=True,fill=BOTH)
		
	# Method to draw the marks for the interval
	def drawmarks(self, interval):

		s = interval[1] - interval[0]
		mark = self.width/s
		for i in np.arange(0, self.width, mark):
			self.can.create_line(i, self.height//2+10, i, self.height//2-10)
		

		for i in np.arange(0, self.height, mark):
			self.can.create_line(self.width//2+10, i, self.width//2-10, i)


	# Method to draw the graph implement an arg parser at a later time *work
	def drawgraph(self, expression=1, interval=[-10,10]):
		
		s = interval[1] - interval[0]
		mark = self.width//s
		if mark < 10:
			self.adjustcanvas(s)

		mark = self.width/s
		self.can.delete('all')
		self.can.create_line(0, self.height/2, self.width, self.height/2)
		self.can.create_line(self.width/2, 0, self.width/2, self.height)
		
		y = 0
		self.drawmarks(interval)
		ypoints = self.argparse(expression, interval)
			
		for x in np.arange(interval[0], interval[1], 0.01):
			self.can.create_oval((self.width/2)+x*mark-2, (self.height/2)+-ypoints[y]*mark-2, (self.width/2)+x*mark+2, (self.height/2)+-ypoints[y]*mark+2 )
			y += 1

	# Adjusts canvas size
	def adjustcanvas(self,interval):
		self.width *= 1.5
		self.height *= 1.5
		self.can.config(scrollregion=self.can.bbox('all'))
		s = self.width//interval
		if s < 10:
			self.adjustcanvas(s)

	# The arg parser for the string expression *work
	def argparse(self, expression, interval):
		ypts = [] 
		if 'x**x' or 'x**0.5' in expression:
			interval[0]=0
		try:
			for x in np.arange(interval[0], interval[1], 0.01):
				ypts.append(eval(expression))
			return ypts 
		except:
			pass # Put some error code in here incase of bad expression that python does not understand
	
		

def intervalget():
	interval = []
	interval.append(int(intervalleft.get()))
	interval.append(int(intervalright.get()))
	return interval

# Root window for graphing program
app = graph()
app.title("Fun Plot")

# Input window for expression

input_expression = Toplevel(bg = 'white', width = DEFAULT_WIDTH, height = DEFAULT_HEIGHT/2)
input_expression.wm_title('f(x)')
expression = StringVar()

intervalexpleft = StringVar()
intervalexpright = StringVar()

intervalexpleft.set('-10')
intervalexpright.set('10')

# Sub frames for input_expression
expressionin = Frame(master=input_expression, bg = 'white')
expressionin.pack()
intervalin = Frame(master=input_expression, bg='white', width=25)
intervalin.pack()


# The expressions widgets
w = Label(expressionin, text="f(x) =" ,bg='white')
w.pack(side=LEFT)
	
e = Entry(expressionin, textvariable=expression)
e.pack(side=LEFT)
	
	
b = Button(expressionin, text="Plot", command = lambda: app.drawgraph(expression=e.get(), interval=intervalget()))
b.pack(side = RIGHT)


intervalleft = Entry(intervalin, textvariable = intervalexpleft, width=25)
intervalleft.pack(side=LEFT)

intervalright = Entry(intervalin, textvariable = intervalexpright, width=25)
intervalright.pack(side = RIGHT)

# key bindings	
app.bind('<Return>',lambda event: app.drawgraph(expression=e.get()))
input_expression.bind('<Return>',lambda event: app.drawgraph(expression=e.get(), interval = intervalget()))

# Main loop of program
app.mainloop()


