import tkinter as tk
from tkinter import simpledialog
from random import random
from math import ceil, floor
import pandas as pd
import re
from PIL import Image, ImageTk
from tkinter import ttk

def get_monster_dict():
    monsters_raw = pd.read_csv('../../Dropbox/games/dnd/monsters.csv', encoding='unicode_escape')
    actions_raw = pd.read_csv('../../Dropbox/games/dnd/actions.csv', encoding='unicode_escape')
    monsters = {}
    stats_names = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
    current_stats = {}
    action_cols = actions_raw.columns[1:]

    actions_raw.rename(columns={'monster': 'name'}, inplace=True)

    full_data = monsters_raw.merge(actions_raw, on='name')

    columns = full_data.columns

    for monster in full_data['name'].unique():

        monster_table = full_data.loc[full_data['name'] == monster]

        for stat_name in stats_names:
            current_stats[stat_name] = monster_table[stat_name.upper()].iloc[0]

        actions = {}
        multiattack, multiattacks, multiattack_info = False, 1, ''
        for i in range(len(monster_table.index)):
            action = {}
            if monster_table['category'].iloc[i] == 'Multiattack':
                multiattack = True
                multiattacks = monster_table['action name'].iloc[i]
                multiattack_info = monster_table['full detail'].iloc[i]
                continue
            for col in action_cols:
                roll = {}
                if col[-4:] == 'roll':
                    if str(monster_table[col].iloc[i]) == 'nan': continue
                    res = re.findall("^(\\d*)(d(\\d*)[^\\d]*(\\d*))?$", str(monster_table[col].iloc[i]))
                    roll['number'] = res[0][0]
                    roll['type'] = res[0][2]
                    roll['mod'] = res[0][3]
                    action[col] = roll
                    continue
                action[col] = monster_table[col].iloc[i]
            actions[i] = action

        monsters[monster] = {
            'Name': monster,
            'Stats': current_stats,
            'HP': monster_table['HP'].iloc[0],
            'Multiattack': multiattack,
            'Multiattacks': multiattacks,
            'multiattack_info': multiattack_info,
            'AC': monster_table['AC'].iloc[0],
            'CR': monster_table['CR'].iloc[0],
            'XP': monster_table['XP'].iloc[0],
            'Immunity': monster_table['Immunity'].iloc[0],
            'Resistance': monster_table['Resistance'].iloc[0],
            'Actions': actions
        }

    return monsters



class ScrollTable():
    def __init__(self, root_tk):
        # self.root.grid_rowconfigure(0, weight=1)
        # self.root.columnconfigure(0, weight=1)

        self.root = root_tk


        # Create a frame for the canvas with non-zero row&column weights
        self.frame_canvas = tk.Frame(self.root)
        self.frame_canvas.grid(row=0, column=0, pady=(5, 0), sticky='nw')
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        self.frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        self.canvas = tk.Canvas(self.frame_canvas)
        self.canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        self.vsb = tk.Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Create a frame to contain the text
        self.frame_list = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_list, anchor='nw')

    def fill(self, table_content = None):
        if table_content is None:
            table_content = self.monster_table_content
        else:
            self.monster_table_content = table_content
        self.input_label = None
        self.input_label = [[tk.Label() for c in range(len(table_content[0]))] for r in range(len(table_content))]
        for r in range(len(table_content)):
            for c in range(len(table_content[0])):
                if c != 0: # first column (name) should align left, the rest middle
                    sticky_str = 'we'
                else:
                    sticky_str = 'w'

                self.input_label[r][c] = tk.Label(self.frame_list, text=table_content[r][c], relief=tk.FLAT)
                self.input_label[r][c].grid(row=r, column=c, sticky=sticky_str)

        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.frame_list.update_idletasks()

    def resize(self, width=None, height=None):
        self.frame_list.update_idletasks()
        if width is None:
            # width = sum([self.input_label[0][c].winfo_width() for c in range(len(self.input_label[0]))])
            # width += self.vsb.winfo_width()
            width = self.frame_list.winfo_width() + self.vsb.winfo_width()
        if height is None:
            monsters_len = len(self.input_label)
            cap = 20
            if monsters_len < cap:
                height = sum([self.input_label[r][0].winfo_height() for r in range(monsters_len)])
            else:
                height = sum([self.input_label[r][0].winfo_height() for r in range(cap)])
        self.frame_canvas.config(height=height, width=width)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # self.root.mainloop()

class MonsterTable(ScrollTable):
    def inflict_damage_to_current_enemy(self):
        monster = self.monster_table_content[self.current_enemy]
        temp_hp = monster[self.monster_table_content[0].index('HP')]
        name = monster[self.monster_table_content[0].index('Name')]
        damage = simpledialog.askinteger("Damage", "How much damage is this poor %s going to take?" % name)
        if damage is None: damage = 0
        self.monster_table_content[self.current_enemy][self.monster_table_content[0].index('HP')] = int(temp_hp) - damage
        self.fill()


    def choose_this_enemy(self, r):
        self.current_enemy = r
        self.inflict_damage_to_current_enemy()
        self.resize()



    def fill(self, table_content=None, monster_display_function=None):
        image = Image.open("sword.png")
        self.sword_logo = ImageTk.PhotoImage(image)
        image = Image.open("inspect.png")
        self.logo_inspect = ImageTk.PhotoImage(image)

        if monster_display_function is not None:
            self.monster_display_function = monster_display_function


        if table_content is None:
            table_content = self.monster_table_content
        else:
            self.monster_table_content = table_content
        self.input_label = None
        self.input_label = [[tk.Frame() for c in range(len(table_content[0]))] for r in range(len(table_content))]
        for r in range(len(table_content)):
            for c in range(len(table_content[0])):
                if c != 0: # first column (name) has also an attack button, the rest middle
                    self.input_label[r][c] = tk.Label(self.frame_list, text=table_content[r][c])
                    self.input_label[r][c].grid(row=r, column=c, sticky='we')
                else:
                    if r == 0:
                        self.input_label[r][c] = tk.Label(self.frame_list, text=table_content[r][c])
                        self.input_label[r][c].grid(row=r, column=c, sticky='w')
                    else:
                        self.input_label[r][c] = tk.Frame(self.frame_list)
                        self.input_label[r][c].grid(row=r, column=c, sticky='w')

                        attack_button = tk.Button(self.input_label[r][c], image=self.sword_logo)
                        attack_button.image = self.sword_logo
                        attack_button.configure(command=lambda row=r: self.choose_this_enemy(row))
                        attack_button.pack(side='right')

                        inspect_button = tk.Button(self.input_label[r][c], image=self.logo_inspect)
                        inspect_button.image = self.logo_inspect
                        inspect_button.configure(command=lambda enemy=table_content[r][c]: self.monster_display_function(monster=enemy))
                        inspect_button.pack(side='right')

                        name = tk.Label(self.input_label[r][c], text=table_content[r][c])
                        name.pack(side='left')

        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.frame_list.update_idletasks()


class MonsterList(ScrollTable):

    def fill(self, table_content=None, monster_display_function=None, monster_add_function=None):
        image = Image.open("add.png")
        self.logo_add = ImageTk.PhotoImage(image)
        image = Image.open("inspect.png")
        self.logo_inspect = ImageTk.PhotoImage(image)

        if monster_display_function is not None:
            self.monster_display_function = monster_display_function

        if table_content is None:
            table_content = self.monster_table_content
        else:
            self.monster_table_content = table_content
        self.input_label = None
        self.input_label = [[tk.Frame() for c in range(len(table_content[0]))] for r in range(len(table_content))]
        for r in range(len(table_content)):
            for c in range(len(table_content[0])):
                if c != 0:  # first column (name) has also an attack button, the rest middle
                    self.input_label[r][c] = tk.Label(self.frame_list, text=table_content[r][c])
                    self.input_label[r][c].grid(row=r, column=c, sticky='we')
                else:
                    if r == 0:
                        self.input_label[r][c] = tk.Label(self.frame_list, text=table_content[r][c])
                        self.input_label[r][c].grid(row=r, column=c, sticky='w')
                    else:
                        self.input_label[r][c] = tk.Frame(self.frame_list)
                        self.input_label[r][c].grid(row=r, column=c, sticky='w')

                        add_button = tk.Button(self.input_label[r][c], image=self.logo_add)
                        add_button.image = self.logo_add
                        add_button.configure(command=lambda enemy=table_content[r][c]: monster_add_function(monsters=enemy))
                        add_button.pack(side='right')

                        inspect_button = tk.Button(self.input_label[r][c], image=self.logo_inspect)
                        inspect_button.image = self.logo_inspect
                        inspect_button.configure(
                            command=lambda enemy=table_content[r][c]: self.monster_display_function(monster=enemy))
                        inspect_button.pack(side='right')

                        name = tk.Label(self.input_label[r][c], text=table_content[r][c])
                        name.pack(side='left')

        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.frame_list.update_idletasks()


class CombatTab():

    def __init__(self):
        self.monsters = get_monster_dict()

        self.enemies = ['Kobold', 'Kobold', 'Kobold Sergeant', 'Kobold Warrior', 'Kobold']

        self.titles = ("Name", "Initiative", "HP", "AC")

        self.stat_list = ("Str", "Dex", "Con", "Int", "Wis", "Cha")

        self.current_actor = 0

        self.MonsterTable = None

    def set_enemies(self, enemies):
        self.enemies = enemies

    def set_root_tk(self, root_tk):
        self.root = root_tk

    def set_top_window_tk(self, top_window_tk):
        self.top_window_tk = top_window_tk

    def roll(self, number_of_dice, die_type, modifier):
        result = 0
        for i in range(number_of_dice):
            result += ceil(random() * die_type)
        result += modifier
        return result

    def roll_initiative(self, dex_mod):
        return self.roll(1, 20, dex_mod)

    def get_modifier(self, ability_score):
        return floor(int(ability_score) / 2 - 5)

    def get_value_for_table(self, title, enemy):
        if title == "Initiative":
            return self.roll_initiative(self.get_modifier(self.monsters[enemy]['Stats']['Dex']))
        else:
            return self.monsters[enemy][title]

    def fill_monster_table(self, tk_root_container):
        self.monster_table_content = [self.titles]
        self.monster_table_content += \
            [[self.get_value_for_table(title, enemy) for title in self.titles] for enemy in self.enemies]
        if self.MonsterTable is None:
            self.MonsterTable = MonsterTable(tk_root_container)
        self.MonsterTable.fill(table_content=self.monster_table_content, monster_display_function=self.fill_monster_display)
        self.MonsterTable.resize()

    def reload(self):
        self.top_window_tk.mainloop()

    def add_monster_content(self, monsters = None):
        if monsters is not None:
            enemies = monsters.split(",")
            self.monster_table_content += \
                [[self.get_value_for_table(title, enemy) for title in self.titles] for enemy in enemies]
            self.MonsterTable.fill(table_content=self.monster_table_content)
            self.reload()


    def fill_monster_display(self, tk_root_container = None, monster=None):
        if monster is None:
            monster = 'Kobold'

        monster_info = self.monsters[monster]

        if tk_root_container is None:
            tk_root_container = self.monster_display

        self.monster_container = tk.Frame(tk_root_container)
        self.monster_container.grid(row=0, column=0, sticky='nw')

        # self.monster_container.grid_propagate(False)

        current_row = 0
        # name
        self.monster_container_name = tk.Label(self.monster_container, text=monster_info['Name'])
        self.monster_container_name.grid(row=current_row, column=0)
        current_row += 1

        # stat grid
        self.monster_container_stats = tk.Frame(self.monster_container)
        self.monster_container_stats.grid(row=current_row, column=0)
        current_row += 1

        self.stats = monster_info['Stats']
        self.stat_labels = [[tk.Label() for c in range(len(self.stats))] for r in range(2)]
        for c in range(len(self.stats)):
            self.stat_labels[0][c] = tk.Label(self.monster_container_stats, text=self.stat_list[c])
            self.stat_labels[0][c].grid(row=0, column=c)
            self.stat_labels[1][c] = tk.Label(self.monster_container_stats, text=self.stats[self.stat_list[c]])
            self.stat_labels[1][c].grid(row=1, column=c)

        self.monster_container_stats.update_idletasks()

        # actions
        if monster_info['Multiattack'] == True:
            self.multiattack_label = tk.Label(self.monster_container, text='Multiattack: %s attacks' % monster_info['Multiattacks'])
            self.multiattack_label.grid(row=current_row, column=0, sticky='w')
            current_row += 1

            wraplength = self.monster_container_stats.winfo_width()
            text = monster_info['multiattack_info']
            self.multiattack_text = tk.Label(self.monster_container, wraplength=wraplength, text=text, justify='left')
            self.multiattack_text.grid(row=current_row, column=0)
            current_row += 1

        self.monster_container_action_title = tk.Label(self.monster_container, text='Actions')
        self.monster_container_action_title.grid(row=current_row, column=0, sticky='w')
        current_row += 1

        self.monster_container_actions = tk.Frame(self.monster_container)
        self.monster_container_actions.grid(row=current_row, column=0)
        current_row += 1
        actions = monster_info['Actions']
        # for action in actions:

    def inspect_enemy(self, enemy):
        self.fill_monster_display(monster=enemy)

    def change_monster_table_row_color(self, row):
        for c in range(len(self.titles)):
            self.MonsterTable.input_label[row][c].configure(bg='red')


    def reselect_current_enemy(self):
        self.change_monster_table_row_color(self.current_actor)
        self.root.mainloop()


    def change_selected_enemy(self):

        changed = False
        i = self.current_actor
        while not changed:
            if self.current_actor == 0:
                self.current_actor = 1
            j = (i + 1) % len(self.monster_table_content)
            if j == 0:
                j = 1
            if self.monster_table_content[j][self.titles.index('HP')] > 0:
                self.current_actor = j
                break
            i += 1

        self.MonsterTable.fill(self.monster_table_content)
        self.change_monster_table_row_color(self.current_actor)

        self.root.mainloop()

    def attack_enemy(self):
        self.MonsterTable.select_enemy_to_attack()

    def add_enemy(self):
        self.add_monster_content(simpledialog.askstring("Add monsters", "What monsters do you want to add?"))

    def close_window(self):
        self.top_window_tk.destroy()

    def add_main_frames(self):
        self.monster_table = tk.Frame(self.root)
        self.monster_table.grid(row=1, column=0)
        self.fill_monster_table(self.monster_table)

        self.title_frame = tk.Frame(self.root)
        self.title_frame.grid(row=0, column=0)

        self.monster_display = tk.Frame(self.root)
        self.monster_display.grid(row=0, column=1, rowspan=2, sticky='n')
        self.fill_monster_display(self.monster_display)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=2, column=0, columnspan=2)
        self.btn_next_actor = tk.Button(self.button_frame, text="next actor", command=self.change_selected_enemy)
        self.btn_next_actor.grid(row=0, column=0)
        self.btn_close = tk.Button(self.button_frame, text="close", command=self.close_window)
        self.btn_close.grid(row=0, column=1)
        self.add_monster = tk.Button(self.button_frame, text="add enemy", command=self.add_enemy)
        self.add_monster.grid(row=0, column=2)

        # self.root.mainloop()

class MonsterListTab(CombatTab):

    def set_titles_and_monsters(self):
        self.enemies = list(self.monsters.keys())
        self.titles = ("Name", "Initiative", "HP", "AC", "CR", "XP")
        self.MonsterTable = None

    def add_main_frames(self):
        self.monster_table = tk.Frame(self.root)
        self.monster_table.grid(row=1, column=0)
        self.set_titles_and_monsters()
        self.fill_monster_table(self.monster_table)

        self.title_frame = tk.Frame(self.root)
        self.title_frame.grid(row=0, column=0)

        self.monster_display = tk.Frame(self.root)
        self.monster_display.grid(row=0, column=1, rowspan=2, sticky='n')
        self.fill_monster_display(self.monster_display)

    def fill_monster_table(self, tk_root_container):
        self.monster_table_content = [self.titles]
        self.monster_table_content += \
            [[self.get_value_for_table(title, enemy) for title in self.titles] for enemy in self.enemies]
        if self.MonsterTable is None:
            self.MonsterTable = MonsterList(tk_root_container)
        self.MonsterTable.fill(table_content=self.monster_table_content, monster_display_function=self.fill_monster_display, monster_add_function=self.add_monster_content)
        self.MonsterTable.resize()

class MainWindow:
    def __init__(self):
        self.root_tk = tk.Tk()
        self.window = ttk.Notebook(self.root_tk)

        self.fight_tab_frame = ttk.Frame(self.window)
        self.window.add(self.fight_tab_frame, text="Fight")
        self.fight_tab = CombatTab()
        self.fight_tab.set_root_tk(self.fight_tab_frame)
        self.fight_tab.set_top_window_tk(self.root_tk)
        self.fight_tab.add_main_frames()

        self.monster_list_frame = ttk.Frame(self.window)
        self.window.add(self.monster_list_frame, text="Monsters")
        self.monster_list_tab = MonsterListTab()
        self.monster_list_tab.set_root_tk(self.monster_list_frame)
        self.monster_list_tab.set_top_window_tk(self.root_tk)
        self.monster_list_tab.add_main_frames()

        # self.all


        self.window.pack(expand=1, fill='both')
        self.root_tk.mainloop()




tw = MainWindow()
