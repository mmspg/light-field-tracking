import tkinter as tk
from PIL import ImageTk, Image

root = tk.Tk()
root.title("lf-tracking")

img = ImageTk.PhotoImage(Image.open("img.jpg"))

tk.Label(root, image=img).grid(column=0, row=0)
tk.Label(root, image=img).grid(column=1, row=0)
tk.Label(root, text="Image 1").grid(column=0, row=1)
tk.Label(root, text="Image 2").grid(column=1, row=1)

root.mainloop()