# Updated app.py

# Code to reposition select/deselect buttons to the top right of the pages grid section

# Assuming you have a function similar to this in your app.py

class PageGrid:
    def __init__(self):
        self.create_interface()

    def create_interface(self):
        # Previous layout code...

        # Repositioning buttons here
        self.button_container = tk.Frame(self.root)
        self.button_container.pack(side='top', anchor='ne')  # Top right position

        self.select_button = tk.Button(self.button_container, text='Select', command=self.select)
        self.deselect_button = tk.Button(self.button_container, text='Deselect', command=self.deselect)

        # Pack buttons to the button container
        self.select_button.pack(side='left')
        self.deselect_button.pack(side='left')

        # Continue with the rest of the interface...

    def select(self):
        # Logic for selecting
        pass

    def deselect(self):
        # Logic for deselecting
        pass
