# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import PhotoImage
from calculator import pet_calculate, formatted_distribution

# Function for calculations (example: sum of values from textboxes)
def calculate():
    try:
        distribution = pet_calculate(
            int(entries[0].get()),
            int(entries[1].get()),
            int(entries[2].get()),
            int(entries[3].get()),
            int(entries[4].get())
        )
        result_box.config(state=tk.NORMAL)
        result_box.delete("1.0", tk.END)
        result_box.insert("1.0", formatted_distribution(distribution))
        result_box.config(state=tk.DISABLED)
    except ValueError:
        result_box.delete("1.0", tk.DISABLED)
        result_box.insert("1.0", "잘못된 입력")

# Create the main window
root = tk.Tk()

root.title("StoneAge Classic - Level 1 Pet Base Distribution")

# Create labels for text entry fields
labels = ['초기계수', '체', '공', '방', '순']  # You can change the labels here
entries = []  # List to store entry widgets

# Create entry fields and labels on the left side
for i in range(5):
    # Label
    label = tk.Label(root, text=labels[i])
    label.grid(row=i+1, column=0, padx=10, pady=10, sticky="e")  # Align labels to the right
    
    # Entry field
    entry = tk.Entry(root)
    entry.grid(row=i+1, column=1, padx=10, pady=10)
    entries.append(entry)


# Create a label for the calculation result on the right side, above the result textbox
result_label = tk.Label(root, text="레벨1 페트 스탯이 베이스맥스(+2, +2, +2, +2)일 확률:")
result_label.grid(row=0, column=3, padx=0, pady=0)

# Result box (uneditable and spans the height of the window)
result_box = tk.Text(root, state=tk.DISABLED)
result_box.grid(row=1, column=3, rowspan=5, padx=1, pady=1, sticky="nsew")

# Calculate button (centered below the input and result textboxes)
calculate_button = tk.Button(root, text="계산", command=calculate)
calculate_button.grid(row=6, column=0, columnspan=5, pady=20)

# Configure the grid to make the result box and button flexible
root.grid_rowconfigure(1, weight=0)  # Make the result box span all the way down
root.grid_columnconfigure(3, weight=1)  # Make the result box span the entire width

# Run the main event loop
root.mainloop()
