import cv2
from tkinter import *
from PIL import Image, ImageTk

def start_camera():
    # Start the video capture
    global cap
    cap = cv2.VideoCapture(0)
    update_frame()


def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Optional: Enhance the contrast (Histogram Equalization)
        gray_frame = cv2.equalizeHist(gray_frame)

        # Optional: Denoise with Gaussian blur
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

        # Apply Canny edge detection
        edges = cv2.Canny(blurred_frame, 30, 100)

        # Convert edges to RGB for Tkinter
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        # Convert to ImageTk format
        img = Image.fromarray(edges_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the label
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)

    # Repeat the function
    lbl_video.after(1, update_frame)



def stop_camera():
    global cap
    cap.release()
    lbl_video.config(image="")

# Create the GUI window
window = Tk()
window.title("OpenCV GUI with Tkinter")

# Create a label to display the video
lbl_video = Label(window)
lbl_video.pack()

# Create start and stop buttons
btn_start = Button(window, text="Start Camera", command=start_camera)
btn_start.pack(side=LEFT, padx=10, pady=10)

btn_stop = Button(window, text="Stop Camera", command=stop_camera)
btn_stop.pack(side=RIGHT, padx=10, pady=10)

# Run the GUI event loop
window.mainloop()
