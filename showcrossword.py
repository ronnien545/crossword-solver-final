import tkinter as tk
from tkinter import Frame
from tkinter import messagebox
import crosswordclues
import constraintsolver

finalized = False
n = 0
som = []
lstofpossible = []

def loaddataset():
   labelload = tk.Label(root,bg="#f7e4d2", text="Loading dataset...", font=('Helvetica', 15))
   labelload.pack(anchor=tk.CENTER)
   root.update()
   constraintsolver.finishload()
   labelload.destroy()

def creategrid(r,c):
    global frame_id
    global canvas

    for i in range(r):
        for j in range(c):
            var = tk.BooleanVar()
            lbl = tk.Label(framebot, bg='white', width=4, height=2, relief='solid', borderwidth=1)
            lbl.bind('<Button-1>', lambda e, v=var, l=lbl: togglesq(v, l))
            lbl.var = var
            lbl.grid(row=i, column=j, sticky="nsew")

    canvas_width = canvas.winfo_reqwidth()
    canvas_height = canvas.winfo_reqheight()

    x_coord= (canvas_width - c) // 2
    y_coord = (canvas_height - r) // 2

    frame_id = canvas.create_window(x_coord+210,y_coord, window=framebot)

    canvas.bind('<Configure>', on_configure)

def togglesq(var, label):
  #only toggle square if crossword not finalized
  if finalized == False:
    var.set(not var.get())
    label.config(bg='black' if var.get() else 'white')


def create_arr(r,c):
   arr = []
   row = []
   for i in range(r):
      row = []
      for j in range(c):
         row.append(-1)
      arr.append(row)
   return arr

def click_btn():
    global r
    global c
    global next_button
    rstscreen()

    try:
      r = int(entryrows.get())
      c = int(entrycols.get())
    except ValueError as e:
       messagebox.showerror("Error", "Enter a valid number")
       return None
    
    for widget in root.winfo_children():
      if widget==next_button:
        widget.destroy()
      
    next_button = tk.Button(framemid, text="Next", command=gotonext, bg='orange',fg='white', relief='flat', font=('Helvetica', 10))

    next_button.pack(side = "left", padx=4,pady=4)

    creategrid(r,c)

    root.update_idletasks()
    canvas.yview_moveto(0.0)

    

def showans(nsom,anslst):
   global root
   count = 0
   n = len(nsom[0])

   mlist = []
   for i in range(r):
     inner_list = []
     for j in range(c):
        inner_list.append("")
     mlist.append(inner_list)
   
   #define anslst based on created crossword
   for i in range(r):
     for j in range(c):
        if nsom[i][j] != 0 and nsom[i][j] != -1:
           if anslst[count][0] != None and  anslst[count][0] != 0:
              a = 0
              for b in anslst[count][0][0]:
                 mlist[i][j+a]= b
                 a+=1
           if anslst[count][1] != None and  anslst[count][1] != 0:
              a = 0
              print(anslst[count][1])
              for b in anslst[count][1][0]:
                 mlist[i+a][j]=b
                 a+=1
           count+=1
   
   for widget in canvas.winfo_children():
    if isinstance(widget, Frame) and widget== framebot:
       print("isinstance widget frame")
       for lbl in widget.winfo_children():
          coords = lbl.grid_info()
          print(coords)
          if mlist[coords['row']][coords['column']] != "":
             lbl.config(text=mlist[coords['row']][coords['column']])




def submit_action():
   click_btn()

def findentries(som):
   r = len(som)
   c = len(som[0])
   count= 0
   global lstofpossible
   #define all possible down and right clues for crossword
   for i in range(r):
     for j in range(c):
       if (i == 0  or som[i-1][j]==0) and (i!=r-1) and som[i+1][j]!=0 and som[i][j] !=0:
          count+=1
          som[i][j] = count
          possible = []
          if((j==0 or som[i][j-1]==0) and (j!=c-1) and som[i][j+1]!=0 and som[i][j] !=0):
             possible = ["down","right"]
          else:
             possible = ["down"]
          lstofpossible.append(possible)
       elif(j==0 or som[i][j-1]==0) and (j!=c-1) and som[i][j+1]!=0 and som[i][j] !=0:
          count+=1
          som[i][j] = count
          if((i == 0  or som[i-1][j]==0) and (i!=r-1) and som[i+1][j]!=0 and som[i][j] !=0):
             possible = ["down","right"]
          else:
             possible = ["right"]
          lstofpossible.append(possible)
   return som

def lenofentries(nsom):
   r = len(nsom)
   c = len(nsom[0])
   lstoflens = []
   for i in range(r):
     for j in range(c):
        if nsom[i][j] != 0 and nsom[i][j] != -1:
           cool = []
           if "right" in  lstofpossible[nsom[i][j]-1]:
              count = 0
              while (j+count)<c and  nsom[i][j+count]!=0:
                 count+=1
              cool.append(count)
              print(j+count)
           if "down" in  lstofpossible[nsom[i][j]-1]:
              count = 0
              while (i+count)<r and nsom[i+count][j]!=0:
                 count+=1
              cool.append(count)
           lstoflens.append(cool)
   return lstoflens


def gotonext():
   global finalized
   finalized = True
   global som
   som = create_arr(r,c)
   global root 

   next_button.destroy()

   #go through each label and if its black then put a corresponding 0 in matrix
   for widget in canvas.winfo_children():
     if isinstance(widget, Frame):
       for lbl in widget.winfo_children():
          coords = lbl.grid_info()
          if lbl.cget("bg") == "black":
             som[coords['row']][coords['column']] = 0
   nsom = findentries(som)
   for widget in canvas.winfo_children():
     if isinstance(widget, Frame) and widget == framebot:
       for lbl in widget.winfo_children():
          coords = lbl.grid_info()
          if som[coords['row']][coords['column']] != 0 and som[coords['row']][coords['column']] != -1:
             lbl.config(text=som[coords['row']][coords['column']])

   abslst = []
   abslst = crosswordclues.inputclues(root,lstofpossible)

   if abslst == []:
      return None

   anslst = constraintsolver.solve(nsom, abslst)
   showans(nsom,anslst)

def rstscreen():
  global finalized
  global som
  global r
  global c
  global canvas
  global lstofpossible
  global framebot
  global frame_id
  global scrollbar

  canvas.destroy()
  next_button.destroy()
  scrollbar.destroy()
  
  scrollbar = tk.Scrollbar(root)
  scrollbar.pack(side="right", fill="y")

  canvas = tk.Canvas(root, yscrollcommand=scrollbar.set, bg="#f7e4d2", borderwidth=0, highlightthickness=0)

  canvas.pack(side="left", fill="both", expand=True)

  canvas.update()

  scrollbar.config(command=canvas.yview)

  finalized = False
  som = []
  lstofpossible = []
  r = 0
  c = 0
  
  framebot = tk.Frame(canvas)


def on_configure(event):
  canvas.configure(scrollregion=canvas.bbox('all'))


root = tk.Tk()
root.geometry("800x500")
root.configure(bg="#f7e4d2")
root.title("Crossword solver")

loaddataset()

framehelp = tk.Frame(root, bg="#f7e4d2", highlightthickness=0)
framehelp.pack()
frametop = tk.Frame(root, bg="#f7e4d2", highlightthickness=0)
frametop.pack()

helplabel = tk.Label(framehelp,bg="#f7e4d2", text="Enter the dimensions then click to set the black squares for the crossword")
helplabel.pack( padx=6, pady= 2)
labelrows = tk.Label(frametop,bg="#f7e4d2", text="Num of rows:")
labelrows.pack(side = tk.LEFT, padx=6, pady= 2)
entryrows = tk.Entry(frametop, font=('Helvetica', 14), width=5,borderwidth=0, highlightthickness=0)
entryrows.pack(side=tk.LEFT, padx=6, pady=2)

labelcols = tk.Label(frametop, bg="#f7e4d2",text="Num of cols:")
labelcols.pack(side = tk.LEFT, padx=6, pady= 2)
entrycols = tk.Entry(frametop, font=('Helvetica', 14), width=5, borderwidth=0, highlightthickness=0)
entrycols.pack(side = tk.RIGHT, padx=6, pady= 2)

framemid = tk.Frame(root, bg="#f7e4d2", highlightthickness=0)
framemid.pack()

submit_button = tk.Button(framemid, text="Create", command=click_btn, bg='orange',fg='white', relief='flat', font=('Helvetica', 10))
submit_button.pack(side="left", padx=4,pady=4)

reset_button = tk.Button(framemid,text = "Reset",command=rstscreen, bg='orange',fg='white', relief='flat', font=('Helvetica', 10))
reset_button.pack(pady=4)

scrollbar = tk.Scrollbar(root)
scrollbar.pack(side="right", fill="y")

canvas = tk.Canvas(root, yscrollcommand=scrollbar.set, bg="#f7e4d2", borderwidth=0, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

framebot = tk.Frame(canvas)

next_button = tk.Button(root, text="Next", command=gotonext)


root.mainloop()


