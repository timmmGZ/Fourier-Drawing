import tkinter as tk
from pylab import *


def paint(e):
    canv.create_oval(e.x, e.y, e.x + 1, e.y + 1, fill="black")
    p.append([e.x, e.y])


p, lastP = [], []
root = tk.Tk()
root.geometry('+' + str(root.winfo_screenwidth() // 2 - 100) + '+' + str(root.winfo_screenheight() // 2 - 100))
canv = tk.Canvas(root, height=200, width=200)
canv.pack()
canv.bind("<B1-Motion>", paint)
canv.bind("<Button-1>", lambda x: exec("lastP=copy(p).tolist()", globals()))


def back(event):
    global p
    p = lastP
    canv.delete("all")
    for x, y in p:
        canv.create_oval(x, y, x + 1, y + 1, fill="black")


button = tk.Button(root, text='back only once')
button.pack(side=tk.BOTTOM)
button.bind('<Button-1>', back)

tk.mainloop()
p = array(p)
p -= p.min()
p[:, 0] -= (max(p[:, 0]) // 2)
p[:, 1] -= (max(p[:, 1]) // 2)
p[:, 1] = -p[:, 1]
a_file = open("drawing.txt", "w")
for row in p:
    savetxt(a_file, row)
a_file.close()
