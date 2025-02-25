import tkinter as tk
from App import App

# Create the main window and an instance of App
root = tk.Tk()
root.title('Satellite observation scheduler')
app = App(root)
root.mainloop()
