import tkinter as tk
from tkinter import ttk

text = "The Label widget doesn't line-wrap. The Message widget will line-wrap text, but forces it to be roughly square. Here's an example."

form = tk.Tk()
form.title='asfd'

window = tk.Frame(form)
window.grid(row=0, column=0)

label = tk.Label(window,text=text)
label.grid(row=0,column=0)

form.mainloop()