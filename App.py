import tkinter as tk
from JsonFileViewer import JsonFileViewer
from satellite_visibility import satellite_visibility
from generate_plan import generate_plan
from datetime import datetime
import itertools
from PlanViewer import PlanViewer

class App:

    def __init__(self, root):
        self.debug = False
        self.schemaTLE = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ORDINAL": {"type": "integer", "minimum": 0, "maximum": 255},
                    "COMMENT": {"type": "string", "maxLength": 32},
                    "ORIGINATOR": {"type": "string", "maxLength": 7},
                    "NORAD_CAT_ID": {"type": ["integer", "null"], "minimum": 0},
                    "OBJECT_NAME": {"type": "string", "maxLength": 25},
                    "OBJECT_TYPE": {"type": ["string", "null"], "maxLength": 12},
                    "CLASSIFICATION_TYPE": {"type": "string", "minLength": 1, "maxLength": 1},
                    "INTLDES": {"type": ["string", "null"], "maxLength": 8},
                    "EPOCH": {"type": "string", "format": "date-time"},
                    "EPOCH_MICROSECONDS": {"type": "integer", "minimum": 0},
                    "MEAN_MOTION": {"type": "number"},
                    "ECCENTRICITY": {"type": "number"},
                    "INCLINATION": {"type": "number"},
                    "RA_OF_ASC_NODE": {"type": "number"},
                    "ARG_OF_PERICENTER": {"type": "number"},
                    "MEAN_ANOMALY": {"type": "number"},
                    "EPHEMERIS_TYPE": {"type": "integer", "minimum": 0, "maximum": 255},
                    "ELEMENT_SET_NO": {"type": "integer", "minimum": 0},
                    "REV_AT_EPOCH": {"type": "number"},
                    "BSTAR": {"type": "number"},
                    "MEAN_MOTION_DOT": {"type": "number"},
                    "MEAN_MOTION_DDOT": {"type": "number"},
                    "FILE": {"type": "integer", "minimum": 0},
                    "TLE_LINE0": {"type": "string", "maxLength": 27},
                    "TLE_LINE1": {"type": "string", "minLength": 69, "maxLength": 69},
                    "TLE_LINE2": {"type": "string", "minLength": 69, "maxLength": 69},
                    "OBJECT_ID": {"type": ["string", "null"], "maxLength": 11},
                    "OBJECT_NUMBER": {"type": ["integer", "null"], "minimum": 0},
                    "SEMIMAJOR_AXIS": {"type": "number"},
                    "PERIOD": {"type": ["number", "null"]},
                    "APOGEE": {"type": "number"},
                    "PERIGEE": {"type": "number"},
                    "DECAYED": {"type": ["integer", "null"], "minimum": 0, "maximum": 255}
                },
                "required": [
                    "TLE_LINE1", "TLE_LINE2"
                ]
            }
        }
        self.schemaObs = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "PRIORITY": {"type": "integer"},
                    "COMMENT": {"type": ["string", "null"]},
                    "START_TIME": {"type": "string", "format": "date-time"},
                    "END_TIME": {"type": "string", "format": "date-time"},
                    "ANGLE": {"type": "number"},
                    "LATITUDE": {"type": "number"},
                    "LONGITUDE": {"type": "number"},
                    "TIMEZONE_OFFSET": {"type": "integer"}
                },
                "required": [
                    "START_TIME", "END_TIME", "LATITUDE", "LONGITUDE", "ANGLE", "TIMEZONE_OFFSET"
                ]
            }
        }

        self.root = root
        self.root.geometry("800x600")

        label1 = tk.Label(root, text="Application feedback:")
        label1.pack(side="top", anchor="ne")

        self.textbox_error = tk.Text(self.root, height=4, width=40)  # Adjust height and width as needed
        self.textbox_error.pack(side="top", anchor="ne", fill="both", expand=False)

        label2 = tk.Label(root, text="Buttons:")

        label2.pack(side="top", anchor="ne")

        # Create a frame for the TLE JsonFileViewer
        self.json_viewer_tle_frame = tk.Frame(root)
        # self.json_viewer_tle_frame.pack(fill="both", expand=True)

        # Initialize JsonFileViewer in its frame
        self.json_viewer_tle = JsonFileViewer(self.json_viewer_tle_frame, self.schemaTLE, "Open TLE JSON", self.textbox_error)

        # Create a frame for the Obs JsonFileViewer
        self.json_viewer_obs_frame = tk.Frame(root)
        # self.json_viewer_obs_frame.pack(fill="both", expand=True)

        # Initialize JsonFileViewer in its frame
        self.json_viewer_obs = JsonFileViewer(self.json_viewer_obs_frame, self.schemaObs, "Open Observatory JSON", self.textbox_error)

        # Create a frame for the PlanViewer
        self.plan_viewer_frame = tk.Frame(root)

        # Initialize PlanViewer in its frame
        self.plan_viewer = PlanViewer(self.plan_viewer_frame, self.json_viewer_obs, self.json_viewer_tle, self.textbox_error)
        # Create another frame for different content
        #self.other_frame = tk.Frame(root, bg='blue')
        #tk.Label(self.other_frame, text="This is another Frame").pack()

        # Buttons to switch between frames
        self.btn_json_viewer_tle = tk.Button(
            root,
            text="Show TLE JSON Viewer",
            command=lambda: self.show_frame_and_refresh(self.json_viewer_tle_frame, self.json_viewer_tle)
        )
        self.btn_json_viewer_tle.pack(side="top", anchor="ne", fill="both", expand=False)

        self.btn_json_viewer_obs = tk.Button(
            root,
            text="Show Observatory JSON Viewer",
            command=lambda: self.show_frame_and_refresh(self.json_viewer_obs_frame, self.json_viewer_obs)
        )
        self.btn_json_viewer_obs.pack(side="top", anchor="ne", fill="both", expand=False)

        #self.btn_other_frame1 = tk.Button(
        #    root,
        #    text="Show Other Frame",
        #    command=lambda: self.show_frame(self.other_frame)
        #)
        #self.btn_other_frame1.pack(side="top", anchor="ne", fill="both", expand=False)

        if self.debug:
            self.btn_other_frame2 = tk.Button(
                root,
                text="Test TLE getter",
                command=lambda: self.process_and_display_json_data(
                    self.json_viewer_tle,
                    "TLE data")
            )
            self.btn_other_frame2.pack(side="top", anchor="ne", fill="both", expand=False)

            self.btn_other_frame3 = tk.Button(
                root,
                text="Test observatory getter",
                command=lambda: self.process_and_display_json_data(
                    self.json_viewer_obs,
                    "Observatory data")
            )
            self.btn_other_frame3.pack(side="top", anchor="ne", fill="both", expand=False)

            self.btn_other_frame4 = tk.Button(
                root,
                text="Test satellite visibility",
                command=lambda: self.process_and_display_satellite_visibility()
            )
            self.btn_other_frame4.pack(side="top", anchor="ne", fill="both", expand=False)

            self.btn_other_frame5 = tk.Button(
                root,
                text="Test plan",
                command=lambda: self.process_data_and_create_plan()
            )
            self.btn_other_frame5.pack(side="top", anchor="ne", fill="both", expand=False)

        self.btn_other_frame6 = tk.Button(
            root,
            text="Show Plan Viewer",
            command=lambda: self.show_frame(self.plan_viewer_frame)
        )
        self.btn_other_frame6.pack(side="top", anchor="ne", fill="both", expand=False)

    def show_frame(self, frame):
        # Hide all frames
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.pack_forget()
        # Show the chosen frame
        frame.pack(fill='both', expand=True)

    def show_frame_and_refresh(self, frame, obj_to_refresh):
        # Hide all frames
        obj_to_refresh.refresh_entry_fields()
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.pack_forget()
        # Show the chosen frame
        frame.pack(fill='both', expand=True)

    def print_json_data(data):
        for item in data:
            print("Satellite Data:")
            for key, value in item.items():
                print(f"  {key}: {value}")
            print("\n")

    def process_and_display_tle_data(self):
        if self.json_viewer_tle.data_ready:  # Check if data is ready
            data_with_priority = self.json_viewer_tle.get_data_with_priority(max_on_none=True)
            for item in data_with_priority:
                print("Satellite Data:")
                for key, value in item.items():
                    print(f"  {key}: {value}")
                print("\n")
        else:
            print("Data not loaded or ready")

    def process_and_display_json_data(self, json_data, message):
        if json_data.data_ready:  # Check if data is ready
            data_with_priority = json_data.get_data_with_priority(max_on_none=True)
            for idx, item in enumerate(data_with_priority):
                print(message+f" {idx}")
                for key, value in item.items():
                    print(f"  {key}: {value}")
                print("\n")
        else:
            print("Data not loaded or ready")

    def process_and_display_satellite_visibility(self):
        # Check if both viewers exist and their data_ready is True
        if (self.json_viewer_obs is not None and self.json_viewer_obs.data_ready) and (
                self.json_viewer_tle is not None and self.json_viewer_tle.data_ready):
            print("Both JsonFileViewer instances exist and their data is ready.\nSatellite visibility:")
            for satellite in self.json_viewer_tle.get_data_with_priority():
                print(f"    Satellite {satellite['NORAD_CAT_ID']}, {satellite['TLE_LINE0']}")
                for observatory in self.json_viewer_obs.get_data_with_priority():
                    print(f"        Observatory {observatory['COMMENT']}")
                    passes = satellite_visibility(
                        satellite['TLE_LINE1'],
                        satellite['TLE_LINE2'],
                        observatory['START_TIME'],
                        observatory['END_TIME'],
                        observatory['ANGLE'],
                        observatory['LATITUDE'],
                        observatory['LONGITUDE']  # ,
                        # observatory['TIMEZONE_OFFSET']
                    )
                    for p in passes:
                        if len(p) in {4, 5}:
                            print(f"            Start: {p[0]}, End: {p[2]}")
                        else:
                            print(f"            Start: {p[0]}, End: {p[1]}")
        else:
            print("One or both JsonFileViewer instances either do not exist or their data is not ready.")

    def process_data_and_create_plan(self):
        if (self.json_viewer_obs is not None and self.json_viewer_obs.data_ready) and (
                self.json_viewer_tle is not None and self.json_viewer_tle.data_ready):
            print("Both JsonFileViewer instances exist and their data is ready.\nGenerated observation plan:")
            s = datetime(2024, 1, 29, 0, 0)
            e = datetime(2024, 2, 4, 23, 0)
            plan = generate_plan(self.json_viewer_obs.get_data_with_priority(),
                                 self.json_viewer_tle.get_data_with_priority(),
                                 s, e, 0, 2
                                 )

            # Flatten the data to include satellite name with each observation
            flattened_observations = []
            for satellite_plan in plan:
                satellite_data, satellite_name = satellite_plan
                for observation in satellite_data:
                    datetime_list, location = observation
                    for datetime_pair in datetime_list:
                        start_time, end_time = datetime_pair
                        flattened_observations.append((location, satellite_name, start_time, end_time))

            # Sort the flattened observations by observatory first, then by start time
            sorted_observations = sorted(flattened_observations, key=lambda x: (x[0], x[2]))

            # Group by observatory for printing
            for location, group in itertools.groupby(sorted_observations, key=lambda x: x[0]):
                print(f"Observatory: {location}")
                for _, satellite_name, start_time, end_time in group:
                    print(f"    Start Time: {start_time}, End Time: {end_time}, Satellite: {satellite_name}")
        else:
            print("One or both JsonFileViewer instances either do not exist or their data is not ready.")