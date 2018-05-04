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

# Protects from eval being used incorrectly
#make a list of safe functions
safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'de\
grees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 
'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
#use the list to filter the local namespace
safe_dict = dict([ (k, globals().get(k, None)) for k in safe_list ])
#add any needed builtins back in.
safe_dict['abs'] = abs

# Connect to database
cnx = connect(user='testprojects', password='Testing123!',host='den1.mysql4.gear.host',database='testprojects')
cursor = cnx.cursor()

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

		
		self.can.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set, scrollregion=(0,0,5000,5000))
		self.can.pack(side=LEFT,expand=True,fill=BOTH)
		
	# Method to draw the marks for the interval
	def drawmarks(self, interval):
		r = interval[0]
		s = interval[1] - interval[0]
		mark = self.width/s
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

	# Method to draw the graph implement an arg parser at a later time *work
	def drawgraph(self, expression, interval):
		freq = 0.01
		s = interval[1] - interval[0]
		if s <= 20: freq = 0.0001
		if s <= 2: freq = 0.00001
		mark = self.width//s
		if mark < 15:
			self.adjustcanvas(s)

		mark = self.width/s
		self.can.delete('all')
		self.can.create_line(0, self.height/2, self.width, self.height/2)
		self.can.create_line(self.width/2, 0, self.width/2, self.height)
		
		y = 0
		self.drawmarks(interval)
		ypoints = self.argparse(expression, interval, freq)
			
		for x in np.arange(interval[0], interval[1], freq):
			if self.width < (self.height/2)+-ypoints[y]*mark-2 > self.height: 
				y += 1
				continue
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
	# Need to work on it so that x**(linexp) works
	# Modify regex
	#
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
	
	# Allows user to upload an ORGINAL plot to the database
	def upload(self, expression):
		hostname = str(socket.gethostname())
		try:
			add_plot = f'INSERT INTO users_plots (hostname, plot) VALUES ("{hostname}", "{expression}");'
			cursor.execute(add_plot)
			cnx.commit()
		except:
			pass

	# Allows user to see plots other users have thought up
	def download(self, cursor):
		
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

# Mouse click event
xPos = 0
yPos = 0
def showPosEvent(event):
    xPos = event.x / 25
    if xPos < 10:
                xPos = xPos - 10
    elif xPos > 10:
            xPos = xPos - 10
    elif xPos == 10:
            xPos = 0
    yPos = event.y / 25
    if yPos < 10:
            yPos = 10 - yPos
    elif yPos > 10:
            yPos = 10 - yPos
    elif yPos == 10:
            yPos = 0
    xPos = '%.2f'%(xPos)
    yPos = '%.2f'%(yPos)
    print('X=%s Y=%s' % (xPos, yPos))
    app.can.create_text(event.x, event.y - 10, fill='black', font='Times', text=f'({xPos}, {yPos})')

def onLeftClick(event):
    print(showPosEvent(event))

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
app.bind('<Button-1>', onLeftClick)
input_expression.bind('<Return>',lambda event: app.drawgraph(expression=e.get(), interval = intervalget()))

# Main loop of program
app.mainloop()


