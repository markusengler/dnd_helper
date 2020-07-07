import tkinter as tk
from random import random
from math import ceil, floor

def roll_initiative(dex_mod):
    return roll(1, 20, dex_mod)


def get_modifier(ability_score):
    return floor(int(ability_score) / 2 - 5)


def roll(number_of_dice, die_type, modifier):
    result = 0
    for i in range(number_of_dice):
        result += ceil(random() * die_type)
    result += modifier
    return result



monsters = {'Kobold': {
    'Name': 'Kobold',
    'HP': 5,
    'AC': 11,
    'Stats': {
        'Str': 11,
        'Dex': 13,
        'Con': 10,
        'Int': 5,
        'Wis': 4,
        'Cha': 1
    },
    'actions': {
        '1': {
            'name': 'Dagger',
            'hit': 4,
            'dmg': 4,
            'dmg roll': {
                'number of dice': 1,
                'die type': 4,
                'modifier': 1
            }
        }
    }
}}


titles = ("Name", "Initiative", "HP", "AC")
enemies = ['Kobold'] * 12


def get_value(title, enemy):
    if title == "Initiative":
        return roll_initiative(get_modifier(monsters[enemy]['Stats']['Dex']))
    else:
        return monsters[enemy][title]


root = tk.Tk()
root.grid_rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

window = tk.Frame(root, bg="red")
window.grid(sticky='news')

frame_main = tk.Frame(window, bg="gray")
frame_main.grid(sticky='news')

label1 = tk.Label(frame_main, text="Label 1", fg="green")
label1.grid(row=0, column=0, pady=(5, 0), sticky='nw')

label2 = tk.Label(frame_main, text="Label 2", fg="blue")
label2.grid(row=1, column=0, pady=(5, 0), sticky='nw')

label3 = tk.Label(frame_main, text="Label 3", fg="red")
label3.grid(row=3, column=0, pady=5, sticky='nw')

# Create a frame for the canvas with non-zero row&column weights
frame_canvas = tk.Frame(frame_main)
frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky='nw')
frame_canvas.grid_rowconfigure(0, weight=1)
frame_canvas.grid_columnconfigure(0, weight=1)
# Set grid_propagate to False to allow 5-by-5 buttons resizing later
frame_canvas.grid_propagate(False)

# Add a canvas in that frame
canvas = tk.Canvas(frame_canvas, bg="grey")
canvas.grid(row=0, column=0, sticky="news")

# Link a scrollbar to the canvas
vsb = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
vsb.grid(row=0, column=1, sticky='ns')
canvas.configure(yscrollcommand=vsb.set)

# Create a frame to contain the text
frame_actors = tk.Frame(canvas, bg="blue")
canvas.create_window((0, 0), window=frame_actors, anchor='nw')

# Add 9-by-5 buttons to the frame

content = [[get_value(title, enemy) for title in titles] for enemy in enemies]

for title in titles:
    title_labels = [tk.Label() for j in range(len(titles))]
    j = titles.index(title)
    title_labels[j] = tk.Label(frame_actors, text=title, font=("Arial Bold", 12))
    title_labels[j].grid(row=0, column=j, sticky="e")

buttons = [[tk.Label() for j in range(len(titles))] for i in range(len(enemies))]
for i in range(0, len(enemies)):
    for j in range(0, len(titles)):
        buttons[i][j] = tk.Label(frame_actors, text=content[i][j])
        buttons[i][j].grid(row=i+1, column=j, sticky='news')

# Update buttons frames idle tasks to let tkinter calculate buttons sizes
frame_actors.update_idletasks()

# Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
first5columns_width = sum([buttons[0][j].winfo_width() for j in range(0, 4)])
first5rows_height = buttons[1][0].winfo_height() * 25
frame_canvas.config(width=first5columns_width + vsb.winfo_width(),
                    height=first5rows_height)

# Set the canvas scrolling region
canvas.config(scrollregion=canvas.bbox("all"))

# Launch the GUI
root.mainloop()