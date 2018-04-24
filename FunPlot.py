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

author Derick Falk
"""
try:
	DEFAULT_HEIGHT = 500
	DEFAULT_WIDTH = 500
	

		# The graph frame
	class graph(tk.Tk):

		def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
			
			tk.Tk.__init__(self)
			self.width = width
			self.height = height
			

			self.can = Canvas(self, width = width, height = height, bg = 'white')
			self.can.pack()
		
		# Method to draw the marks for the interval
		def drawmarks(self, interval):

			s = interval[1] - interval[0]
			mark = self.width//s
			for i in range(0, self.width, mark):
				self.can.create_line(i, self.height/2+10, i, self.height/2-10)

			for i in range(0,self.height, mark):
				self.can.create_line(self.width/2+10, i, self.width/2-10, i)

		# Method to draw the graph implement an arg parser at a later time *work
		def drawgraph(self, expression=1, interval=(-10,10)):
			self.can.delete('all')
			self.can.create_line(0, self.height/2, self.width, self.height/2)
			self.can.create_line(self.width/2, 0, self.width/2, self.height)
			s = interval[1] - interval[0]
			mark = self.width//s
			y = 0
			self.drawmarks(interval)
			ypoints = self.argparse(expression, interval)
			
			for x in np.arange(interval[0], interval[1], 0.001):
				self.can.create_oval((self.width/2)+x*mark-1, (self.height/2)+-ypoints[y]*mark-1, (self.width/2)+x*mark+1, (self.height/2)+-ypoints[y]*mark+1 )
				y += 1

		# The arg parser for the string expression *work
		def argparse(self, expression, interval):
			ypts = [] 
			try:
				for x in np.arange(interval[0], interval[1], 0.001):
					ypts.append(eval(expression))
				return ypts 
			except:
				pass # Put some error code in here incase of bad expression that python does not understand
	
		



	# Root window for graphing program
	app = graph()
	app.title("Fun Plot")

	# Input window for expression

	input_expression = Toplevel(bg = 'white', width = DEFAULT_WIDTH, height = DEFAULT_HEIGHT/2)
	input_expression.wm_title('f(x)')
	expression = StringVar()
	

	w = Label(input_expression, text="f(x) =" ,bg='white')
	w.pack(side=LEFT)
	
	e = Entry(input_expression, textvariable=expression)
	e.pack(side=LEFT)
	
	
	b = Button(input_expression, text="Plot", command = lambda: app.drawgraph(expression=e.get()))
	b.pack(side = RIGHT)
		



	app.mainloop()
except Exception as e:
	traceback.print_exc(e)

