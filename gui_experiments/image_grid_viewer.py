import tkinter as tk
from PIL import Image, ImageTk
window = tk.Tk()
window.geometry('8000x6000')
window.title('Images')
window.columnconfigure((0,3), weight = 1, uniform = 'z')
window.rowconfigure(0, weight = 1) 
image_original = Image.open('IMG_20220107_221333.jpg')
image_ratio = image_original.size[0] / image_original.size[1]
print(image_ratio)
print(image_original.height)
print(image_original.width)

canvas = tk.Canvas(window,height=2231,width=4694,bg="black", border=0)
	
canvas.grid(columnspan=2)


def show_full_image(om):
	global resized_tk

	canvas_ratio = om.width / om.height
	print(canvas_ratio)
	if canvas_ratio > image_ratio:
		height = int(om.height)
		width = int(height * image_ratio) 
	else:
		width = int(om.width) 
		height = int(width / image_ratio)
	resized_image = image_original.resize((width, height))
	resized_tk = ImageTk.PhotoImage(resized_image)
	canvas.create_image(int(om.width/2),int(om.height/2),anchor = 'center',image = resized_tk)
canvas.bind('<Configure>', show_full_image)
window.mainloop()
  