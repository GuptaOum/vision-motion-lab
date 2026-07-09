import os
import tkinter as tk
from PIL import Image, ImageTk

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

root = tk.Tk()

# Create a label widget
image_tk = Image.open(os.path.join(ASSETS_DIR, 'goku.png'))
image_tk=image_tk.resize((500,500))
image_tk=image_tk.rotate(50)
image_tk = ImageTk.PhotoImage(image_tk)

labely = tk.Label(master=root, image=image_tk )
#labely.grid(column=2, row=2, columnspan=1, sticky='s')

# Pack the label widget
labely.pack()

# Start the mainloop
root.mainloop()