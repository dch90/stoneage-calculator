# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from calculator import pet_calculate, formatted_distribution

# Load presets from file
preset_data = {}
with open("data.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 6:
            key = parts[0]
            values = list(map(int, parts[1:]))
            preset_data[key] = values

all_labels = list(preset_data.keys())

# GUI Setup
root = tk.Tk()
root.title("StoneAge Classic - Level 1 Pet Base Distribution")

# Dropdown logic
preset_var = tk.StringVar()
preset_dropdown = ttk.Combobox(root, textvariable=preset_var)
preset_dropdown['values'] = all_labels
preset_dropdown.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

# Input labels and fields
labels = ['초기계수', '체', '공', '방', '순']
entries = []
for i in range(5):
    tk.Label(root, text=labels[i]).grid(row=i + 1, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(root)
    entry.grid(row=i + 1, column=1, padx=10, pady=5)
    entries.append(entry)

# Result display
tk.Label(root, text="레벨1 페트 스탯이 베이스맥스(+2, +2, +2, +2)일 확률:").grid(row=0, column=3, padx=10, pady=10)
result_box = tk.Text(root, height=10, width=40, state=tk.DISABLED)
result_box.grid(row=1, column=3, rowspan=5, padx=10, pady=10, sticky="nsew")

# Populate input boxes
def populate_entries(values):
    for i in range(5):
        entries[i].delete(0, tk.END)
        entries[i].insert(0, str(values[i]))

# Button: Calculate
def calculate():
    try:
        values = [int(e.get()) for e in entries]
        dist = pet_calculate(*values)
        result_box.config(state=tk.NORMAL)
        result_box.delete("1.0", tk.END)
        result_box.insert("1.0", formatted_distribution(dist))
        result_box.config(state=tk.DISABLED)
    except ValueError:
        result_box.config(state=tk.NORMAL)
        result_box.delete("1.0", tk.END)
        result_box.insert("1.0", "잘못된 입력")
        result_box.config(state=tk.DISABLED)

tk.Button(root, text="계산", command=calculate).grid(row=6, column=0, columnspan=5, pady=20)

# Update dropdown suggestions and optionally populate
def on_dropdown_change(event=None):
    typed = preset_var.get()

    # If exact match, populate
    if typed in preset_data:
        populate_entries(preset_data[typed])
        return

    # Filter matches (case-sensitive startswith)
    matches = [label for label in all_labels if label.startswith(typed)]
    
    # Only update values, not the input field
    preset_dropdown['values'] = matches if matches else all_labels

    # Open the dropdown when there's text input
    if typed:
        preset_dropdown.event_generate('<Down>')  # Simulate the dropdown open event

update_timer = None

def on_user_type(*args):
    global update_timer
    if update_timer:
        root.after_cancel(update_timer)

    def delayed():
        on_dropdown_change()
    
    update_timer = root.after(200, delayed)

preset_var.trace_add("write", on_user_type)

# Let user type freely without auto-overwriting input
def on_key_press(event):
    if event.keysym in ("BackSpace", "Delete"):
        preset_dropdown['values'] = all_labels  # Reset dropdown if clearing
    return

preset_dropdown.bind("<Key>", on_key_press)

# Layout stretch
root.grid_columnconfigure(3, weight=1)
root.grid_rowconfigure(1, weight=1)

root.mainloop()
