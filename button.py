from tkinter import *

window = Tk()

window.title("Welcome to LikeGeeks app")

window.geometry('350x200')
sword_logo = PhotoImage('/sword sybol.png')

lbl = Label(window, image=sword_logo)

lbl.grid(column=0, row=0)

def clicked():
    print(Button.cget('text'))
    lbl.configure(text=lbl.cget('text'))

btn = Button(window, text="Click Me", command=clicked)

btn.grid(column=1, row=0)

window.mainloop()
