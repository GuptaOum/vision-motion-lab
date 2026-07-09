import tkinter as tk
import tkinter as tkk #widgets
import ttkbootstrap as ttk
import customtkinter as ctk
from PIL import Image , ImageTk
window=ttk.Window(themename='darkly')
window.geometry('600x400')
window.title('ohm')
text=tk.Text(master=window)
text.pack() 
window.mainloop()