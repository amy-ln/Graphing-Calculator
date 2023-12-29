import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
import random
import sympy as sp
from os.path import exists
import time 

lines=[] #array to hold all lines
xpoints = [-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10]
colors = ["red","orangered","orange","yellow","lawngreen","forestgreen","darkgreen","turquoise","teal","dodgerblue","royalblue","navy","blueviolet",
          "indigo","purple","magenta","white"] #15 standard colour options
styles = ["solid","dashed","dotted","dashdot"] #4 line style options 


class LineBasics:
    def __init__(self,postorder,inorder,linetype):
        self.linetype = linetype
        self.inorder_exp = inorder 
        self.equation = Expression(postorder) #create an expression tree for the new object
        self.color = self.initColor() #default settings for the style of each line when it is created 
        self.weight = 10
        self.style = "solid"
        self.xpoints = xpoints
        self.displayedPoints = [] #used in plot function to show chosen points
    def initColor(self):
        index = random.randint(0,15)
        return(colors[index])

class Line(LineBasics): #use this line for straight lines, quadratics etc (anything polynomial)
    def __init__(self,postorder,inorder,linetype):
        super().__init__(postorder,inorder,linetype)
        self.ypoints = self.findYpoints() #has an array of y points
        self.xpoints = self.getXpoints() #has an array of x points 
    def getXpoints(self):
        return(xpoints) #return the global variable xpoints 
    def findYpoints(self):
        newYpoints = []
        for x in self.xpoints:#evluate expression tree for each value of x 
            str_x = str(x)
            y = self.equation.evaluateExpression(str_x) # find value of y for given x coordinate
            newYpoints.append(y)
        return(newYpoints)

class Log(LineBasics):
    def __init__(self,postorder,inorder,linetype):
        super().__init__(postorder,inorder,linetype)
        self.ypoints = xpoints #logarithmic is inverse of exponential so the ypoints become the xpoints
        self.xpoints = self.getXpoints() 
    def getXpoints(self):
        newXpoints = []
        for y in self.ypoints: #for each y point
            x = self.equation.evaluateExpression(y) #find the value of x 
            newXpoints.append(x) #and append to the list 
        return(newXpoints)
        
    
class Reciprocal(LineBasics): #use for reciprocal graphs to avoid errors when dividing by 0
    def __init__(self,postorder,inorder,linetype):
        super().__init__(postorder,inorder,linetype) #inherit from line basics class
        self.xpoints = self.getXpoints() #create xpoints which don't contain
        self.index = len(self.xpoints) //2 
        self.ypoints = self.findYpoints()
    def getXpoints(self):
        original = xpoints
        AVOID = 0 #constant represents what value the asymptote is at 
        if AVOID in original:
            index = original.index(0) #get index of where the value to remove is located
            original.remove(0) #remove the value which would produce an error
            firsthalf = original[:index]
            secondhalf = original[index:]
            i = firsthalf[-1] + 0.1
            while i < AVOID: #create a gradient of points going towards the asymptote so graph doesn't look cut off
                firsthalf.append(i)
                i = round(i+0.1,1)
            i = secondhalf[0] - 0.1
            while i > AVOID:
                secondhalf.insert(0,i)
                i = round(i-0.1,1)
            self.index = len(firsthalf)
            final = firsthalf + secondhalf
            return(final)
        else:
            return(original)
    def findYpoints(self):
        newYpoints = []
        for x in self.xpoints:
            str_x = str(x)
            y = self.equation.evaluateExpression(str_x) # find value of y for given x coordinate
            newYpoints.append(y)
        return(newYpoints)


class stack: #used in the expression tree
    def __init__(self):
        self.array=[]
    def push(self,data): #add to the top of the stack
        self.array.append(data)
    def pop(self): #remove and return item from top of stack
        if len(self.array)>0:
            return (self.array.pop(-1))
        else:
            pass
    def top(self): #return item from top of stack
        if len(self.array)>0:
            return (self.array[-1])
        else:
            pass
    def size(self): #return size of the stack
        return(len(self.array))
    
class node:
    def __init__(self,data): #node class which is used to build expression tree 
        self.data = data
        self.right = None
        self.left = None

def ISnumeric(string): #checks if a string is numeric (will output true if any character in the string is a number)
    output = False
    if type(string) == str:
        for i in string:
            if i.isnumeric():
                output = True
    return(output)

def evaluate(root,x):
    if root.data == "x":  
        #root.data = x
        if ISnumeric(x) == True:
            return float(x) #if node is x return the entered value of x 
        else:
            return(x)
    elif root.data == "-x":
        if ISnumeric(x) == True:
            return (-1*float(x))
        else:
            return(-1*x)
    if (ISnumeric(root.data) == True):
        return float(root.data) #if node is a number return that number 
    else:
        left_val = evaluate(root.left,x) #evaluate left of the root 
        right_val = evaluate(root.right,x) #evaluate right of the root 
        if root.data == "+":  
            return(left_val + right_val)
        elif root.data == "S":
            return(left_val - right_val)
        elif root.data == "*":
            return(left_val * right_val)
        elif root.data == "/":
            return(left_val / right_val)
        elif root.data == "^":
            return(left_val ** right_val)
        else:
            return("Error")
        
class Expression:
    def __init__(self,postorder):
        self.postfix = postorder #post order traversal of the expression tree
        self.root = None
        self.buildTree(postorder) # create the tree
    def isOperator(self,char): # returns whether the character is an operator
        operators = [" ", "S", "*", "/","^","+"] #list of operators 
        if char in operators:
            return(True)
        else:
            return(False)
    def buildTree(self, p):
        post = p
        s = stack() #initialise stack used to store operators in the tree
        self.root = node(post[-1]) #last character in a post order expression is always an operator so start tree with that node
        s.push(self.root) #push this node to the top of the stack because it is an operator
        post.pop(-1) #remove the operator in the node from the postorder expression so it is not added twice
        post.reverse() #reverse the expression and work backwards
        for i in post:
            current_node = s.top() #take from the top of the stack(without removing)
            if current_node.right== None:
                temp=node(i) #create new node with next data in postorder expression
                current_node.right=temp #add the new node to the tree
                if self.isOperator(i):
                    s.push(temp) #if this node is an operator, push to the stack so that more nodes are added to it
            elif current_node.left == None:
                temp=node(i) #if right of the node is already taken, do same for the left
                current_node.left=temp
                s.pop() #left and right of current node now full so pop current node from stack 
                if self.isOperator(i):
                    s.push(temp)
    def inorder(self,root): #used to test tree has been constructed correctly
        exp = []
        if root: # is not null
            exp = self.inorder(root.left)
            exp.append(root.data)
            exp = exp + self.inorder(root.right)
        return exp
    def postorder(self,root):
        exp = []
        if root:
            exp = self.postorder(root.left)
            exp = exp + self.postorder(root.right)
            exp.append(root.data)
        return exp
    def postfixExp(self):
        return(self.postorder(self.root))
    def infixExp(self):
        return(self.inorder(self.root))
    def evaluateExpression(self,x):
        root = self.root
        return(evaluate(root,x))

def changeStominus(str_exp):
    exp = [char for char in str_exp] #make into array
    for index in range(1,len(exp)-1): #iterate through array starting with second item
        if exp[index] == "-" and (exp[index-1].isnumeric() or exp[index-1] == "x"): #if the item is -, decide whether it is an operator or signifys a negative value
            exp[index] = "S" #if it is an operator, change to an S
    exp = "".join(exp) #convert back to a string
    return(exp) #return the expression


def convertToRPN(infix):
    if " " in infix:
        infix = infix.replace(" ","") #remove whitespace
    operators = ["+","S","/","*","^"] # use S for subtract to differentiate from a negative value
    brackets = ["(",")"]
    infix_altered = changeStominus(infix) #change S to - if necessary to distinguish between operators and negative values
    print(infix_altered)
    arr = splitIntoArr(infix_altered) #split the infix expression into an array where each item is a value or operator
    print(arr)
    arr = multiplySigns(arr)
    print(arr)
    exp_split = addBrackets(arr) #add brackets to the expression abiding to the rules of BIDMAS, returns a string
    print(exp_split)
    exp_split = splitIntoArr(exp_split) #split string back up into an array
    for i in range(0,len(exp_split)):
        if exp_split[i] in brackets:
            pass
        elif exp_split[i] in operators:
            while exp_split[i+1] != ")": #shift all operators to the end of their bracket 
                temp = exp_split[i+1]
                exp_split[i+1] = exp_split[i]
                exp_split[i] = temp
                i = i +1
        else:
            pass

    while "(" in exp_split:
        exp_split.remove("(") #remove any brackets remaining in the expression 
        exp_split.remove(")")
    return(exp_split) #return expression as an array

def multiplySigns(arr):
    index = 0 #initialise count variable
    while index < (len(arr)-1): #iterate until the second to last item
        if ISnumeric(arr[index]) == True and arr[index + 1] == "x": #check if a multiply sign is needed
            arr.insert(index+1, "*") #insert a multiply sign at the correct location
            index += 2 #list has increased in size so increment index by 2
        elif arr[index] == "-" and arr[index + 1] == "x": 
            arr[index] = "-1" #if it is -x should be changed to -1*x
        else:
            index += 1 #list has not increased in size so only increment index 
    return(arr)

def addBrackets(arr):
    #use bidmas to add brackets then use original function
    #BRACKETS #INDICES #DIVIDE #MULTIPLY #ADD #SUBTRACT
    operators = ["^","/","*","+","S"]
    for op in operators: #iterate through operators in order of BIDMAS
        openBracketCount = 0
        index = 0
        while index < len(arr): #iterate through array
            if arr[index] == op:
                arr[index-1] = "(" + arr[index-1]+arr[index]+arr[index+1] + ")" #combine operators with their operands
                arr.pop(index+1)
                arr.pop(index)
            else:
                index = index + 1
    string = "".join(arr) #change array back into a string
    return(string)

def splitIntoArr(user_exp):
    exp_split = [char for char in user_exp]
    newArr = [""]
    brackets = ["(",")"]
    for i in range (0,len(exp_split)):
        if (exp_split[i].isnumeric() or exp_split[i] == "-" or exp_split[i] == "."):
            newArr[-1] = newArr[-1] + exp_split[i]
        else:
            if newArr[-1] == "":
                newArr[-1] = exp_split[i]
                newArr.append("")
            else:
                newArr.append(exp_split[i])
                newArr.append("")
    if newArr[-1] == "":
        newArr.pop(-1)
    return(newArr)

canvasWidget = 0

def plot():
    global canvasWidget
    if plt.fignum_exists(1): #checks if a graph has already been plotted
        plt.clf() #if it has then it clears the graph and deletes that widget
        canvasWidget.destroy()
    fig = Figure( #create new figure to hold the graph 
        figsize = (5,5),
        dpi = 100)
    plot1=fig.add_subplot(111)
    plt.gcf().number
    plot1.grid(True, which = "both") #draw a grid
    plot1.axhline(y=0, color = "k") #draw x axis
    plot1.axvline(x=0, color = "k") #draw y axis 
    for i in lines: #iterates through all lines and plots them
        if i.linetype == "reciprocal":
            plot1.plot(i.xpoints[:i.index],i.ypoints[:i.index],color = i.color, linestyle = i.style) #plot reciprocal lines in two goes 
            plot1.plot(i.xpoints[i.index:],i.ypoints[i.index:],color = i.color, linestyle = i.style)
        else:
            plot1.plot(i.xpoints,i.ypoints, color = i.color, linestyle = i.style)
        if len(i.displayedPoints) > 0:
            for j in i.displayedPoints: 
                print(i.displayedPoints)
                
                string = "".join(str(j)) #create string of the coordinates of the point 
                plot1.plot(j[0],j[1],marker = "o",label = string) #create the label to display the point 
                plot1.text(j[0],j[1],string) #add text to the point to show coordinates
    canvas = FigureCanvasTkAgg(fig,master = frm_graph) #assigns the graph to the correct frame
    canvas.draw() #draws the plot
    canvasWidget = canvas.get_tk_widget() #assigns the plot to a widget
    canvasWidget.pack() #packs the graph onto the frame

def createNewFunction(inorder_exp):
    if "log" in inorder_exp: #is a logarithmic graph
        #need to find the logbase
        startindex = 3 #first index after "log"
        endindex = inorder_exp.index("(")
        logbase = inorder_exp[startindex:endindex] #finds the logbase (the number in between the log and the (x))
        postorder_exp = [logbase,"x","^"] #create a postorder expression with the logbase of an exponential
        i = Log(postorder_exp, inorder_exp,"logarithmic") #the log class swaps the xpoints and ypoints to create a log graph using an exponential expression
        lines.append(i) # add to the array 
        updateLineDisplay()
    else:
        postorder_exp = convertToRPN(inorder_exp)
        if "/" in postorder_exp: #check if it is a reciprocal
            i = Reciprocal(postorder_exp,inorder_exp,"reciprocal") #create a specifically reciprocal line to avoid errors
            lines.append(i) #add line to the global array
            updateLineDisplay()
        else:
            i = Line(postorder_exp,inorder_exp,"normal") #create new object
            lines.append(i) # add the new line to the array
            updateLineDisplay()
    plot()

def updateLineDisplay():
    FOREGROUNDCOLOUR = "white" #initialise variable 
    global frm_currentLines #get the global widget
    for widgets in frm_currentLines.winfo_children(): #remove all labels currently in the frame
        widgets.destroy()
    for i in lines:
        lbl_exp = tk.Label( #for each line create a new label 
            master = frm_currentLines, 
            width = 30,
            height = 1,
            text = "y=" + i.inorder_exp, #the text should be the inorder expression of the line
            bg = FOREGROUNDCOLOUR,
            fg = i.color #the color should be same color as on the graph to help user see which expression
        )                #corresponds to which line 
        lbl_exp.pack() 

def displayErrorMessage(message):
    global frm_currentLines #get the global widget for the frame
    for widgets in frm_currentLines.winfo_children(): #remove all labels currently in the frame
        widgets.destroy() #delete all current widgets in the frame
    if len(message) > 30:
        #look for " " which is nearest to 25th index 
        indexCheck = 30
        while message[indexCheck] != " " and indexCheck > 1:
            indexCheck -= 1 #check every index from 30 down to 1
        if message[indexCheck] == " ": #if a space is found then use this to split the message by line
            message = message[:indexCheck] + "\n" + message[indexCheck:]
    lbl_error = tk.Label( #create the label which will display the error message
        master = frm_currentLines,
        width = 30, #set height and width
        height = 2,
        bg = FOREGROUNDCOLOUR, #set background to white
        fg = "red", # text colour is red because it is an error 
        text = message #the appropriate error message is the text
    )
    lbl_error.pack()

def enterFunction(): #this it the function called when user clicks enter function button 
    exp = ent.get() #get the input from the textbox
    if validateFunction(exp) == True:
        createNewFunction(exp) #pass to other subroutine
    ent.delete(0,"end") #delete input from the textbox

def validateFunction(exp):
    #make sure exp only contains valid characters
    validChars = ["x","+","-","*","(",")","^"," ","/","."]
    valid = True
    if len(exp) == 0:
        valid = False
    for char in exp:
        if not((char.isnumeric()) or (char in validChars)):
            valid = False 
    if valid == False:
        displayErrorMessage("Error: Not a valid input please enter another equation")
    return(valid)

def createMenu(options):
    #subroutine to create a drop down menu and return the user input
    firstoption = tk.StringVar() #the variable which holds the first option to be displayed
    firstoption.set(options[0]) 
    menu = tk.OptionMenu( #create tk object menu
        frm_display, #attach to the top left frame
        firstoption, #the first option which will be displayed
        *options) #the other options (array)
    menu.pack(fill = tk.X) #display the menu using pack
    waitVar = tk.IntVar() #create variable to detect when the ok button is clicked
    entryButton = tk.Button( #create an entry button
        master = frm_display,
        text = "Enter",
        command = lambda: waitVar.set(1)) #command so that program can move on when button clicked
    entryButton.pack()
    entryButton.wait_variable(waitVar) #wait for the button to be pressed
    userChoice = firstoption.get() #get the user input 
    menu.destroy() #delete widgets 
    entryButton.destroy()
    return(userChoice) #return the users option
    
def chooseLine():
    lbl = tk.Label(
        master = frm_display,
        text = "                 Select a Line:                 ",
        bg = "#282929",
        fg = "white")
    #remove the unecessary widgets to make space for the drop down menu
    global lbl_entry,lbl_entry2,ent
    lbl_entry.pack_forget()
    lbl_entry2.pack_forget()
    ent.pack_forget()
    lbl.pack(fill = tk.X)
    options = [] #create an array with the inorder exp of each line
    for i in lines:
        inorder = i.inorder_exp #get the inorder expression of the line 
        options.append(inorder) #add to the options list
    inorder = createMenu(options)
    lineIndex = options.index(inorder) #finds the index (which is the same index as the line object in the lines array)
    lbl.destroy()
    lbl_entry.pack()
    lbl_entry2.pack(side = tk.LEFT)
    ent.pack(side = tk.LEFT)
    return(lineIndex) #return line index to show which line has been selected 
    
def findTurningPoints():
    if check1Line() == True:
        lineIndex = chooseLine() #get input from the user
        exp = lines[lineIndex].equation.infixExp() #find inorder exp of line chosen
        while "S" in exp: #change S back to - for sympy 
            i = exp.index("S")
            exp[i] = "-"
        exp = "".join(exp) #make a string for differentiation
        x = sp.Symbol("x")
        print("Inorder before differentiating:",exp)
        derivative = sp.diff(exp) #use sympy to differentiate the expression
        print("The derivative is:", derivative)
        X = sp.solveset(derivative,x,domain=sp.S.Reals) #solve equation to find x when derivative = 0 only for real values
        xpoints = [] #create two arrays to hold the turning points
        ypoints = []
        for xval in X:
            xval = float(xval)
            yval = lines[lineIndex].equation.evaluateExpression(xval) #find value of y using equation.evaluate(x)
            xpoints.append(xval)
            ypoints.append(yval)
            print(xpoints)
            print(ypoints)
        displayPoints(xpoints,ypoints,lineIndex) #pass the turning points and the line to the display points subroutine 
        if len(xpoints) == 0: #checks for case when there are no turning points
            displayErrorMessage("Error: Line has no turning points")
    else:
        displayErrorMessage("Error: No line has been entered")
        
def displayPoints(x,y,lineIndex): #where x and y are lists
    if len(x) == 1: #if we only want to append one point do it this way
        xpoint = round(x[0],3) #round numbers so they display nicely
        ypoint = round(y[0],3)
        point = (xpoint,ypoint)
        lines[lineIndex].displayedPoints.append(point) #adds the point to the list in line object
    else:
        for i in range(len(x)): #if there are several points to add we need to create a loop
            xpoint = round(x[i],3) #round numbers so they display nicely
            ypoint = round(y[i],3)
            point = [xpoint,ypoint]
            lines[lineIndex].displayedPoints.append(point) #adds the points to the list in line object
    plot()
    lines[lineIndex].displayedPoints = [] #don't want to display some points again as makes graph messy

def findAxisIntercepts():
    if check1Line() == True:
        lineIndex = chooseLine() #select line to find intercept of 
        #for y intercepts set x = 0
        yintercept = lines[lineIndex].equation.evaluateExpression(0)
        #for x intercept solve for y = 0
        exp = lines[lineIndex].equation.infixExp() #get the expression for the line in infix form
        while "S" in exp: #change S back to - for sympy 
            i = exp.index("S")
            exp[i] = "-"
        x = sp.Symbol("x")
        exp_str = "".join(exp) #make exp into string to be solved
        xintercepts_set = sp.solveset(exp_str,x,domain=sp.S.Reals) #solve for exp = 0
        if len(xintercepts_set) == 0:
            displayErrorMessage("There is no x intercept")
        xpoints = [] #create arrays of all xpoints to be displayed
        for point in xintercepts_set:
            xpoints.append(float(point))
        if 0 in xpoints:
            xpoints.remove(0) #avoid displaying same point twice
        xpoints.insert(0,0) #insert 0 for the y intercept
        ypoints = [yintercept] #create array of all y points to be displayed
        for n in range(0,len(xpoints)-1):
            ypoints.append(0)
        displayPoints(xpoints,ypoints,lineIndex) #display all the axis intercepts on the graph
    else:
        displayErrorMessage("Error: No line has been entered")
    

def adjustScale():
    #get user to enter max and min value of x using sliders
    frm_sliders = tk.Frame(
        master = frm_display,
        width = 200,
        height = 50,
        bg = BACKGROUNDCOLOUR)
    global lbl_entry
    global lbl_entry2
    global ent
    lbl_entry.pack_forget()
    lbl_entry2.pack_forget()
    ent.pack_forget()
    frm_sliders.pack()
    top_lbl = tk.Label( #create labels to tell the user how to use the sliders
        master = frm_sliders,
        text = "Slide to maximum value of x",
        bg = "#282929",
        fg = "white")
    bottom_lbl = tk.Label(
        master = frm_sliders,
        text = "Slide to minimum value of x",
        bg = "#282929",
        fg = "white")
    top_slider = tk.Scale( #create the sliders
        master = frm_sliders,
        from_=-50,
        to = 50,
        orient = tk.HORIZONTAL)
    bottom_slider = tk.Scale(
        master = frm_sliders,
        from_=-50,
        to = 50,
        orient = tk.HORIZONTAL)
    var = tk.IntVar() 
    entry_btn = tk.Button( #create a button to collect input 
        master = frm_sliders,
        text = "Enter",
        command = lambda: var.set(1))
    top_lbl.pack() #pack all widgets in correct order
    top_slider.pack(fill = tk.X)
    bottom_lbl.pack()
    bottom_slider.pack(fill = tk.X)
    entry_btn.pack()
    
    entry_btn.wait_variable(var) #wait for user to click enter
    maxX = top_slider.get() #get the maximum value of X from the slider
    minX = bottom_slider.get() #get the minimum value of X from the slider
    #check that valid inputs have been given
    if maxX == minX:
        displayErrorMessage("Error: Maximum and minimum x are the same value")
    elif maxX < minX:
        displayErrorMessage("Error: Minimum value bigger than maximum value")
    else:
        newXpoints = [] #create array of the new xpoints
        temp = minX
        if maxX-minX < 10:
            interval = 0.2
        elif maxX - minX > 50:
            interval = 5
        else:
            interval = 1
        while temp <= maxX: #create new xpoints at predetermined intervals that go between min and max X values
            newXpoints.append(temp)
            temp = round(temp + interval,1) #increase by interval
        global xpoints
        xpoints = newXpoints #change value of global variable so that new lines have correct scale
        for i in lines:
            if i.linetype == "logarithmic":
                i.ypoints = newXpoints
                i.xpoints = i.getXpoints()
            else:
                i.xpoints = i.getXpoints() #set each line's x points to the new xpoints
                i.ypoints = i.findYpoints() #must change y points of each line to match new xpoints
        plot() #plot graph again now scale has been adjusted
    top_lbl.destroy()
    bottom_lbl.destroy()
    top_slider.destroy()
    bottom_slider.destroy()
    entry_btn.destroy()
    frm_sliders.destroy()
    lbl_entry.pack()
    lbl_entry2.pack(side=tk.LEFT)
    ent.pack(side=tk.LEFT)

def check1Line():
    if len(lines) >= 1:
        return(True)
    else:
        return(False)
def check2Lines():
    if len(lines) >= 2:
        return(True)
    else:
        return(False)

def arrToString(arr):
    string = ""
    for n in arr:
        string = string + n
    return(string)

def removeS(arr):
    for n in range (0,len(arr)-1):
        if arr[n] == "S":
            arr[n] = "-"
    return(arr)


def findLineIntersects():
    if check2Lines() == True: #check that at least two lines exist
        Index1 = chooseLine() #select first line
        Index2 = chooseLine() #select second line 
        if Index1 != Index2: #checks that user has not selected same line twice
            line1_exp = lines[Index1].equation.infixExp() #get equation of first line
            line2_exp = lines[Index2].equation.infixExp() #get equation of second line
            line1_exp = removeS(line1_exp)
            line2_exp = removeS(line2_exp)
            exp = "("+arrToString(line1_exp)+")-("+arrToString(line2_exp)+")" #subtract one equation from the other to have the final equation = 0
            x = sp.Symbol("x")
            interceptsX = sp.solveset(exp,x,domain=sp.S.Reals) #solve equation to find x coordinates of the intersects
            print(interceptsX)
            if len(interceptsX) == 0: #then there is no line intersects
                print("These lines do not intersect")
            else:
                xpoints = []
                ypoints = []
                for xval in interceptsX:
                    xval = float(xval)
                    xpoints.append(xval) #add x coordinate to array
                    yval = lines[Index1].equation.evaluateExpression(xval) #find corresponding y coordinate
                    ypoints.append(yval) #add y coordinate to array
                displayPoints(xpoints,ypoints,Index1) #display coordinates - can use either line index
        else:
            displayErrorMessage("Error: Must select two different lines")
    else:
        displayErrorMessage("Error: At least two lines must be entered")

def changeStyle():
    if check1Line() == True:
        index = chooseLine() #select line to change style of 
        global lbl_entry, lbl_entry2, ent #get global widgets so they can be temporairly removed
        lbl_entry.pack_forget() #hide the widgets to make space for the options menu
        lbl_entry2.pack_forget()
        ent.pack_forget()
        colorOptions = colors #use global colors array
        lbl = tk.Label( #create label to instruct user 
            master = frm_display,
            text = "Select a Color:",
            bg = "#282929",
            fg = "white")
        lbl.pack()
        colorChoice = createMenu(colorOptions) #create drop down menu for user to select color
        lines[index].color = colorChoice #change value of the attribute to the chosen color
        lbl.destroy() #destroy label
        styleOptions = styles #use global array of styles
        lbl2 = tk.Label( #create new label to instruct user
            master = frm_display,
            text = "Select a Style:",
            bg = "#282929",
            fg = "white")
        lbl2.pack()
        styleChoice = createMenu(styleOptions) #create menu with the linestyle options
        lines[index].style = styleChoice #change value of attribute to the chosen style
        lbl2.destroy() #destroy label
        lbl_entry.pack()
        lbl_entry2.pack(side = tk.LEFT)
        ent.pack(side = tk.LEFT)
        updateLineDisplay()
        plot() #plot lines again to finalise changes
    else:
        displayErrorMessage("Error: No line has been entered")

def deleteLine():
    if check1Line() == True:
        index = chooseLine()
        global lines
        lines.pop(index)
        updateLineDisplay()
        plot()
    else:
        displayErrorMessage("Error: At least one line must be entered")

def sketchGradientFunction():
    if check1Line() == True: #gradient function can only be done if a line exists
        index = chooseLine() #select line to be differentiated 
        exp = lines[index].equation.infixExp() #get the expression for the line
        exp = "".join(exp) #make into a string 
        exp = exp.replace("S","-") #change S to - for sympy
        derivative = str(sp.diff(exp)) #differtiate and make into another string
        derivative = derivative.replace("**","^") #sympy replaces ^ with ** so change this back
        createNewFunction(derivative) #create a new line with the equation for the derivative 
    else:
        displayErrorMessage("Error: At least one line must be entered")

def loadGraph():
    global lines
    lines = [] #remove all current lines 
    if exists("graphsaves.txt"):
        file = open("graphsaves.txt","r") #open the file 
        filedata = file.read() #read the file
        exps = filedata.splitlines() #create array of expressions from each line of the file
        for inorder_exp in exps:
            createNewFunction(inorder_exp)  #for each expression in the array create a new function
    else:
        displayErrorMessage("Error: There are no lines saved")

    
def saveGraph():
    if check1Line() == True: #at least one line must be entered to save graph
        global lines 
        file = open("graphsaves.txt","w") #open or create a text file to save the graphs
        stringToWrite = "" #initialise string
        for i in lines:
            inorder = i.inorder_exp #get the inorder expression for the line
            stringToWrite = stringToWrite+inorder+"\n" #write the inorder exps of each line to file so they can be recreated
        file.write(stringToWrite) #write to file 
        file.close() #close file
        lines = [] #set lines to empty array
        plot() #plot so that graph looks empty
    else:
        displayErrorMessage("Error: At least one line must be entered")

def enterLogFunction():
    global lbl_entry, lbl_entry2, ent #get widgets to be hidden
    lbl_entry.pack_forget() #hide the widgets to make space for the log ones 
    lbl_entry2.pack_forget()
    ent.pack_forget()
    #make them enter base so do y = logbase x therefore x = base^y
    entrybox = tk.Entry( #create textbox to get their entry
        master = frm_display,
        width = 10)
    label = tk.Label( #instruct user to what they need to enter
        master = frm_display,
        text = "Enter the base of the log:",
        bg = "#282929",
        fg = "white") 
    waitVar = tk.IntVar()
    entryButton = tk.Button( #button to get the user input 
        master = frm_display,
        text = "Enter",
        command = lambda: waitVar.set(1),
        bg = "#282929",
        fg = "white")
    label.pack() #pack all widgets inside frm_display
    entrybox.pack()
    entryButton.pack()
    entryButton.wait_variable(waitVar) #once the user has clicked enter continue
    logbase = entrybox.get() #get the base of the log from the entry box
    label.destroy() #destroy the widgets as they are no longer needed 
    entrybox.destroy()
    entryButton.destroy()
    lbl_entry.pack()
    lbl_entry2.pack(side = tk.LEFT)
    ent.pack(side = tk.LEFT)
    inorder_exp = "log"+logbase+"(x)" #create an inorder expression for display purposes
    createNewFunction(inorder_exp) #pass the inorder expression to createNewFunction

def exitCommand():
    quit()

BACKGROUNDCOLOUR = "#282929"
FOREGROUNDCOLOUR = "white"
window = tk.Tk() #create a tk window
frm_graph = tk.Frame( #create frame to display the graph
    master=window,
    width = 500,
    height = 500,
    bg = BACKGROUNDCOLOUR)
frm_graph.pack(side = tk.RIGHT)

frm_display = tk.Frame( #create frame to hold the equations of lines
    master=window,
    width = 30,
    height = 150,
    bg = BACKGROUNDCOLOUR)
frm_display.pack(side = tk.TOP)

frm_buttons = tk.Frame( #create frame to hold the buttons
    master=window,
    width = 30,
    height = 400,
    bg = BACKGROUNDCOLOUR)


frm_currentLines = tk.Frame( #create a frame to display the equations of lines currently on the graph
    master = window,
    width = 30,
    height = 6,
    bg = FOREGROUNDCOLOUR)
frm_currentLines.pack()
frm_buttons.pack(fill = tk.X,side = tk.BOTTOM)

#create input box
lbl_entry = tk.Label( #add label to instruct user
    master = frm_display,
    text = "Enter equation of your line \nand select from options below:",
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width = 30)
lbl_entry.pack()
lbl_entry2 = tk.Label(
    master = frm_display,
    text = "y=",
    bg= BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=5)
lbl_entry2.pack(side = tk.LEFT)
ent = tk.Entry( #create the box and put this in the correct frame
    master = frm_display,
    width = 25)
ent.pack(side = tk.LEFT)

#create buttons

btn_enterNewFunction = tk.Button(
    master = frm_buttons,
    text = "Enter New Function",
    command = enterFunction,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_enterNewFunction.pack()

btn_enterLogFunction = tk.Button(
    master = frm_buttons,
    text = "Enter Log Function",
    command = enterLogFunction,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_enterLogFunction.pack()

btn_findTurningPoints = tk.Button(
    master = frm_buttons,
    text = "Find Turning Points",
    command = findTurningPoints,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_findTurningPoints.pack()

btn_findAxisIntercepts = tk.Button(
    master = frm_buttons,
    text = "Find Axis Intercepts",
    command = findAxisIntercepts,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_findAxisIntercepts.pack()

btn_findLineIntersects = tk.Button(
    master = frm_buttons,
    text = "Find Line Intersects",
    command = findLineIntersects,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_findLineIntersects.pack()

btn_sketchGradientFunction = tk.Button(
    master = frm_buttons,
    text = "Sketch Gradient Function",
    command = sketchGradientFunction,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_sketchGradientFunction.pack()

btn_adjustScale = tk.Button(
    master = frm_buttons,
    text = "Adjust Scale",
    command = adjustScale,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_adjustScale.pack()

btn_changeStyle = tk.Button(
    master = frm_buttons,
    text = "Change Style of Line",
    command = changeStyle,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_changeStyle.pack()

btn_saveGraph = tk.Button(
    master = frm_buttons,
    text = "Save Current Graph",
    command = saveGraph,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_saveGraph.pack()

btn_loadGraph = tk.Button(
    master = frm_buttons,
    text = "Load Previous Graph",
    command = loadGraph,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_loadGraph.pack()

btn_deleteLine = tk.Button(
    master = frm_buttons,
    text = "Delete Line",
    command = deleteLine,
    bg = BACKGROUNDCOLOUR,
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_deleteLine.pack()

btn_exit = tk.Button(
    master = frm_buttons,
    text = "Exit Program",
    command = exitCommand,
    bg = "red",
    fg = FOREGROUNDCOLOUR,
    width=30)
btn_exit.pack()

window.mainloop()