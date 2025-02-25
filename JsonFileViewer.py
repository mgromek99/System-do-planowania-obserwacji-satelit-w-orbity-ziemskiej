import tkinter as tk
from tkinter import filedialog
import json
#from jsonschema import validate, ValidationError
import re
import datetime
from UniquePriorityPicker import UniquePriorityPicker
import copy
class JsonFileViewer:

    def __init__(self, parent, schema, btn_string, err_textbox):
        self.error_textbox = err_textbox
        self.button_string = btn_string
        self.parent = parent
        self.schema = schema  # JSON schema is now a parameter
        self.data_ready = False
        # Initialize JSON data
        self.data = None
        self.casted_data = None
        self.entry_widgets = {}

        # Create scrollbars
        self.v_scroll = tk.Scrollbar(self.parent, orient="vertical")
        self.h_scroll = tk.Scrollbar(self.parent, orient="horizontal")

        # Create a canvas
        self.canvas = tk.Canvas(self.parent, yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set, highlightthickness=0)
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

        # Layout the scrollbars and canvas
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a frame inside the canvas
        self.display_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.display_frame, anchor="nw")

        # Create a button to open the JSON file
        open_button = tk.Button(self.parent, text=self.button_string, command=self.open_json_file, width=20)
        open_button.pack()

    def log_error(self, message):
        """Display error messages in the error_textbox widget."""
        self.error_textbox.configure(state='normal')  # Ensure the textbox is writable
        self.error_textbox.delete('1.0', tk.END)  # Clear previous content
        self.error_textbox.insert(tk.END, message)
        self.error_textbox.configure(state='disabled')  # Prevent further user edits

    def open_json_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.data_ready = False
            try:
                with open(file_path, 'r') as file:
                    self.data = json.load(file)
                    self.display_json()
            except Exception as e:
                self.clear_display()
                self.display_error(f"Error: {e}")

    def cast_value(self, key, value):
        """Cast a value to the correct type based on the schema provided."""
        if key in self.schema['items']['properties']:
            prop = self.schema['items']['properties'][key]
            if 'type' in prop:
                if prop['type'] == 'integer':
                    return int(value) if value is not None else None
                elif prop['type'] == 'number':
                    return float(value) if value is not None else None
                elif prop['type'] == 'string' and 'format' in prop and prop['format'] == 'date-time':
                    try:
                        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value is not None else None
                    except ValueError:
                        self.log_error(f"Error parsing date-time: {value}")
                        return None
        return value

    def cast_json_data(self, data):
        """Recursively cast all values in the JSON data."""
        if isinstance(data, list):
            return [self.cast_json_data(item) for item in data]
        elif isinstance(data, dict):
            return {k: self.cast_value(k, v) for k, v in data.items()}
        return data

    def display_json(self):
        self.clear_display()
        if isinstance(self.data, list):
            self.casted_data = self.cast_json_data(self.data)
            for index, item in enumerate(self.casted_data):
                # Convert datetime objects to string for display
                item_for_display = {k: v.isoformat() if isinstance(v, datetime.datetime) else v for k, v in
                                    item.items()}
                self.create_single_element_frame(f"Item {index}", item_for_display, index)
            self.refresh_entry_fields()
            self.data_ready = True
        else:
            self.display_error("Unsupported JSON format")
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_single_element_frame(self, key, value, index):
        frame = self.create_element_frame(key, index)
        self.create_toggle_and_inner_frame(frame, value)

    def create_element_frame(self, label_text, index):
        frame = tk.Frame(self.display_frame, pady=5)
        frame.pack(fill='x', expand=True)
        label = tk.Label(frame, text=label_text)

        label.pack(side='left', padx=5)
        entry = tk.Entry(frame, width=5, validate="key", validatecommand=(self.parent.register(self.validate_unsigned_int), '%P'))
        entry.pack(side='left', padx=5)
        self.entry_widgets[index] = entry  # Store the entry widget with index as key
        return frame

    def create_toggle_and_inner_frame(self, outer_frame, value):
        inner_frame = tk.Frame(outer_frame, pady=5)
        text_widget = tk.Text(inner_frame, wrap='word', height=5, width=50)

        # Set initial background color for the text widget
        text_widget.config(bg="#dcdcdc")  # Darker grey background when not focused

        # Configure a tag for focused style
        text_widget.tag_configure('focused', background='#000000', borderwidth=0)

        # Event binding for focus in - change background to white
        text_widget.bind('<FocusIn>', lambda event: text_widget.config(bg="white"))

        # Event binding for focus out - change background to darker grey
        text_widget.bind('<FocusOut>', lambda event: text_widget.config(bg="#dcdcdc"))

        text_widget.insert('end', json.dumps(value, indent=4))
        text_widget.pack()
        toggle_button = tk.Button(outer_frame, text='Toggle', command=lambda: self.toggle_visibility(inner_frame))
        toggle_button.pack(side='left', padx=5)

    def toggle_visibility(self, frame):
        if frame.winfo_viewable():
            frame.pack_forget()
            # Set focus to the parent window to remove focus from the text widget
            self.parent.focus_set()
        else:
            frame.pack(fill='both', expand=True)
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def validate_unsigned_int(self, value):
        return re.match('^[0-9]*$', value) is not None

    def clear_display(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def display_error(self, message):
        error_label = tk.Label(self.display_frame, text=message, fg='red')
        error_label.pack()

    def get_data_with_priority(self, max_on_none=True):
        """Retrieve casted_data with an additional 'PRIORITY' field."""
        # Check if casted_data is not None and is a list
        if self.casted_data is None or not isinstance(self.casted_data, list):
            return []

        # First, assign priorities from entry widgets to each item in casted_data
        for index, item in enumerate(self.casted_data):
            priority_value = self.entry_widgets.get(index, tk.Entry()).get()
            if priority_value.isdigit():
                item['PRIORITY'] = int(priority_value)

        # Find the maximum priority assigned
        max_priority = max((item.get('PRIORITY', 0) for item in self.casted_data), default=0)

        # Then, assign default priority to items without a priority
        for item in self.casted_data:
            if 'PRIORITY' not in item or item['PRIORITY'] is None:
                item['PRIORITY'] = max_priority + 1 if max_on_none else 0

        get_val = copy.deepcopy(self.casted_data)

        randomizer = UniquePriorityPicker(len(get_val))
        for item in get_val:
            random_priority, multiplier = randomizer.get_random_integer_and_multiplier()
            item['PRIORITY'] *= multiplier
            item['PRIORITY'] += random_priority
        get_val.sort(key=lambda x: (x['PRIORITY']))
        return get_val

    def refresh_entry_fields(self):
        """
        Refresh the entry fields to match the 'PRIORITY' value in the casted_data.
        """
        if not self.casted_data or not isinstance(self.casted_data, list):
            return  # Do nothing if casted_data is empty or not a list

        for index, item in enumerate(self.casted_data):
            # Get the current priority from the casted_data
            current_priority = item.get('PRIORITY', '')

            # Get the entry widget for the current item
            entry_widget = self.entry_widgets.get(index)

            # Check if entry widget exists and the priority value is different
            if entry_widget and entry_widget.get() != str(current_priority):
                # Update the entry widget with the current priority
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, str(current_priority))

