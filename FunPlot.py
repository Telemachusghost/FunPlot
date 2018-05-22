import sys
import tkinter as tk
from tkinter import *
import numpy as np
from math import *
import re
from MySQLdb import *
import socket


"""

A simple plotting program that parses expressions
and plots them using tkinter. Can understand standard python expressions.

author Derick Falk, Daniel Denniston, Thomas Bowers
"""

# Some important variables
DEFAULT_HEIGHT = 500
DEFAULT_WIDTH = 500

# Protects from eval being used incorrectly
#make a list of safe functions
safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'de\
grees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 
'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh', 'max']
#use the list to filter the local namespace
safe_dict = dict([ (k, globals().get(k, None)) for k in safe_list ])
#add any needed builtins back in.
safe_dict['abs'] = abs
safe_dict['max'] = max
safe_dict['min'] = min


# Connect to database

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

		# Bindings for the canvas
		self.can.bind("<MouseWheel>",self.zoomer)
		self.can.bind("<ButtonPress-1>", self.move_start)
		self.can.bind("<B1-Motion>", self.move_move)
		
		self.can.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set, scrollregion=(0,0,5000,5000))
		self.can.pack(side=LEFT,expand=True,fill=BOTH)
		
	# Method to draw the marks for the interval
	def drawmarks(self, interval):
		sign = lambda x: (1,-1)[ x < 0]
		r = interval[0]
		s = interval[1] - interval[0]
		mark = self.width/s
		
		# The app just supports equal intervals
		if sign(r) == sign(s) and abs(r) != abs(s) : return False
		
		
		for i in np.arange(0, self.width, mark):
			self.can.create_line(i, self.height//2+10, i, self.height//2-10)
			if r != interval[0]:
				self.can.create_text(i+5,self.height//2+15,fill="darkblue",font="Times 8 italic bold",text=r, width=0)
			r += 1
		
		r = interval[0]
		
		for i in np.arange(0, self.height, mark):
			self.can.create_line(self.width//2+10, i, self.width//2-10, i)
			if r != interval[0] and r != 0:
				self.can.create_text(self.width//2+15,i+5,fill="darkblue",font="Times 8 italic bold",text=-r, width=0)
			r += 1
		return True
	# Method to draw the graph implement an arg parser at a later time *work
	def drawgraph(self, expression, interval):
		freq = 0.01
		s = interval[1] - interval[0]
		if s <= 10: freq = 0.0001
		if s <= 2: freq = 0.00001
		mark = self.width//s
		if mark < 15:
			self.adjustcanvas(s)

		mark = self.width/s
		self.can.delete('all')
		self.can.create_line(0, self.height/2, self.width, self.height/2)
		self.can.create_line(self.width/2, 0, self.width/2, self.height)
		
		y = 0
		if self.drawmarks(interval):
			ypoints = self.argparse(expression, interval, freq)
			
			for x in np.arange(interval[0], interval[1], freq):
				"""
				if  (self.height/2)+-ypoints[y]*mark-2 > self.height: 
					y += 1
					continue
				"""
				self.can.create_oval((self.width/2)+x*mark-2, (self.height/2)+-ypoints[y]*mark-2, (self.width/2)+x*mark+2, (self.height/2)+-ypoints[y]*mark+2, fill='black')
				y += 1

	# Adjusts canvas size
	def adjustcanvas(self,interval):

		self.width *= 1.5
		self.height *= 1.5
		self.config(width=self.width,height=self.height)
		s = self.width//interval
		if s < 15:
			self.adjustcanvas(s)

	# The arg parser for the string expression
	def argparse(self, expression, interval, freq):
		ypts = [] 
		if re.search(r'\bx\*\*[a-z]*[\d\(\)\+\-\*\/\.]*[0-9]*x[\d\(\)\+\-\*\/\.]*[0-9]*',expression) or re.search(r'\(*x[\*\-\+0-9]*\)*\*\*[0-9]+.5',expression):
			if interval[0]<0:
				interval[0]=0
		try:
			for x in np.arange(interval[0], interval[1], freq):
				try:
					safe_dict['x'] = x
					
					y = eval(expression,{"__builtins__":None},safe_dict)
					ypts.append(y)
				except TypeError:
					continue
				except ValueError:
					interval[0] = 0
					interval[1] = 1
			return ypts 
		except:
			pass # Put some error code in here incase of bad expression that python does not understand

	# Zooming function	
	def zoomer(self,event):
		if (event.delta > 0):
			self.can.scale("all", event.x, event.y, 1.01,1.01)
		elif (event.delta < 0):
			self.can.scale("all", event.x, event.y, 0.95, 0.95)
		self.can.configure(scrollregion = self.can.bbox("all"))
	
	# Functions for moving canvas around with mouse
	def move_start(self, event):
		self.can.scan_mark(event.x, event.y)
	def move_move(self, event):
		self.can.scan_dragto(event.x, event.y, gain=1)
	
	# Allows user to upload an ORGINAL plot to the database
	def upload(self, expression):
		cnx = connect(user='testprojects', password='Testing123!',host='den1.mysql4.gear.host',database='testprojects')
		cursor = cnx.cursor()

		hostname = str(socket.gethostname())
		try:
			add_plot = f'INSERT INTO users_plots (hostname, plot) VALUES ("{hostname}", "{expression}");'
			cursor.execute(add_plot)
			cnx.commit()
		except:
			pass

	# Allows user to see plots other users have thought up
	def download(self, cursor):
		cnx = connect(user='testprojects', password='Testing123!',host='den1.mysql4.gear.host',database='testprojects')
		cursor = cnx.cursor()

		hosts = []
		plots = []
		
		get_users = 'SELECT hostname FROM users_plots'
		cursor.execute(get_users)
		for i in cursor:
			hosts.append(str(i)[2:-3])

		get_plots = 'SELECT plot FROM users_plots'
		cursor.execute(get_plots)
		for i in cursor:
			plots.append(str(i)[2:-3])

		plotwindow = tk.Tk()
		plotwindow.maxsize(width=400,height=250)
		plotwindow.wm_title('Users Plots')
		scrolld = Scrollbar(plotwindow)
		scrolld.pack(side=RIGHT,fill=Y)

		t = Text(plotwindow, height=20, width=50)
		t.pack()
		scrolld.config(command=t.yview)
		t.insert(END,'<Hostname>: <plot>\n')
		
		for i in range(len(hosts)):
			t.insert(END, f"{hosts[i]}: ")
			t.insert(END, f"{plots[i]}\n")
		t.config(state=DISABLED)
		plotwindow.mainloop()
	

# Gets interval from interval
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



# The expressions widgets, includes an upload to database button
w = Label(expressionin, text="f(x) =" ,bg='white')
w.pack(side=LEFT)
	
e = Entry(expressionin, textvariable=expression)
e.pack(side=LEFT)

db = Button(expressionin, text='Download', command= lambda: app.download(cursor))
db.pack(side = RIGHT)
	
pb = Button(expressionin, text='Upload', command= lambda: app.upload(e.get()))
pb.pack(side = RIGHT)
	
b = Button(expressionin, text="Plot", command = lambda: app.drawgraph(expression=e.get(), interval=intervalget()))
b.pack(side = RIGHT)


# Interval widgets
intervalleft = Entry(intervalin, textvariable = intervalexpleft, width=25)
intervalleft.pack(side=LEFT)

intervalright = Entry(intervalin, textvariable = intervalexpright, width=25)
intervalright.pack(side = RIGHT)


# key bindings	
app.bind('<Return>',lambda event: app.drawgraph(expression=e.get()))

input_expression.bind('<Return>',lambda event: app.drawgraph(expression=e.get(), interval = intervalget()))

# Main loop of program
app.mainloop()
