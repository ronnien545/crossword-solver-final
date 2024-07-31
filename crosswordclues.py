import tkinter as tk
from tkinter import Scrollbar
from tkinter import ttk

#lstofstuff = []

def inputclues(root,nlst):
    global lstofstuff
    sroot= tk.Toplevel(root)
    sroot.title("Crossword solver")

    indexes_of_left= [i for i, value in enumerate(nlst) if value == ["right"] or value == ["down","right"]]
    indexes_of_right = [i for i, value in enumerate(nlst) if value == ["down"] or value == ["down","right"]]

    canvas = tk.Canvas(sroot, width=800,bg="#f7e4d2", height=500)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(sroot, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    frame = tk.Frame(canvas,bg="#f7e4d2")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    
    framehelp = tk.Frame(frame,bg="#f7e4d2")
    framehelp.pack()

    framemid = tk.Frame(frame,bg="#f7e4d2")
    framemid.pack()
  
    helplabel = tk.Label(framehelp,bg="#f7e4d2", text="Enter the clues then click on the finish button (Solving may take up to 1 minute)")
    helplabel.pack( padx=6, pady= 2)

    title_a = tk.Label(framemid, text="Across",bg="#f7e4d2", font=("Helvetica", 16, "bold"))
    title_a.grid(row=0, column=0,columnspan=2, padx=10, pady=5, sticky="n")

    title_b = tk.Label(framemid, text="Down",bg="#f7e4d2", font=("Helvetica", 16, "bold"))
    title_b.grid(row=0, column=2,columnspan=2, padx=10, pady=5, sticky="n")


    i=0

    #create labels for first column
    for i in range(len(indexes_of_left)):
        label_a = tk.Label(framemid, font=('Helvetica', 11), bg="#f7e4d2", text=str(indexes_of_left[i]+1))
        label_a.grid(row=i+1, column=0, padx=10, pady=5, sticky="w")

        entry_a = tk.Entry(framemid,font=('Helvetica', 11), width=40, name=str(indexes_of_left[i]+1) + "right")
        entry_a.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")

    button = tk.Button(framemid, text="Finish", bg='orange',fg='white', relief='flat', font=('Helvetica', 10), command=lambda: go_back(framemid,sroot))
    button.grid(row=i+2, column=1, padx=10, pady=5, sticky="w")

    #create labels for second column
    for i in range(len(indexes_of_right)):
        label_b = tk.Label(framemid,font=('Helvetica', 11),bg="#f7e4d2", text=str(indexes_of_right[i]+1))
        label_b.grid(row=i+1, column=2, padx=10, pady=5, sticky="w")

        entry_b = tk.Entry(framemid, font=('Helvetica', 11), width=40, name=str(indexes_of_right[i]+1) + "down")
        entry_b.grid(row=i+1, column=3, padx=10, pady=5, sticky="w")

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    lstofstuff = []

    sroot.wait_window()

    return lstofstuff


def go_back(frame,sroot):
   
    global lstofstuff
    lsta= {}
    lstb= {}
    count = 0
    a = False
    maxcount =0
    for widget in frame.winfo_children():
      if(widget.winfo_name().endswith("right")):
         count+=1
         if widget.get():
           lsta[widget.winfo_name()[:-5]] = widget.get()
         else:
           lsta[widget.winfo_name()[:-5]] = ""
         a=True
         if(int(widget.winfo_name()[:-5])>maxcount):
            maxcount=int(widget.winfo_name()[:-5])
      if(widget.winfo_name().endswith("down")):
         #if the right field was not counted as a row count the left field
         if(a==False):
           count+=1
         if widget.get():
           lstb[widget.winfo_name()[:-4]] = widget.get()
         else:
           lstb[widget.winfo_name()[:-4]] = ""
         if(int(widget.winfo_name()[:-4])>maxcount):
            maxcount=int(widget.winfo_name()[:-4])

    count = 1
    slst = []
    while(count != maxcount+1):
      slst.append(lsta.get(str(count)))
      slst.append(lstb.get(str(count)))
      lstofstuff.append(slst)
      slst = []
      count+=1
    
    print(lstofstuff)
    sroot.destroy()
