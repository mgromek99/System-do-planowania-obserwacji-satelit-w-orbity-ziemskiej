from datetime import datetime, timedelta
import itertools
from generate_plan import generate_plan
import tkinter as tk
import re
from tkinter import filedialog
import os
from observatory_visibility import observatory_visibility
from satellite_visibility import satellite_visibility
from skyfield.api import EarthSatellite
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class PlanViewer:
    def __init__(self, parent, json_viewer_obs, json_viewer_tle, error_textbox):
        self.parent = parent
        self.json_viewer_obs = json_viewer_obs
        self.json_viewer_tle = json_viewer_tle
        self.json_viewer_tle_get_copy = []
        self.json_viewer_obs_get_copy = []

        self.error_textbox = error_textbox  # Text widget for displaying errors
        self.plan = []
        self.sorted_observations = []
        self.selected_folder_path = ""  # Variable to store the selected folder path
        self.plan_iteration = 0
        self.export_string = "Object"

        self.display_textbox = tk.Text(self.parent, height=15, width=80, wrap="none")
        self.scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=self.display_textbox.yview)
        self.display_textbox.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.display_textbox.pack(side="left", fill="both", expand=True)

        # Button to open the JSON file and create plan
        self.generate_plan_button = tk.Button(self.parent, text="[Re]Generate Plan", command=self.create_plan, width=20)
        self.generate_plan_button.pack()

        # Button to show plan
        self.show_plan_button = tk.Button(self.parent, text="Show Plan", command=self.show_plan, width=20)
        self.show_plan_button.pack()

        # Button to show satellite visibility
        self.show_sat_vis_button = tk.Button(self.parent, text="Show Satellite Passes",
                                             command=self.display_all_satellite_visibility, width=20)
        self.show_sat_vis_button.pack()

        # Button to show observatory visibility
        self.show_obs_vis_button = tk.Button(self.parent, text="Show Nautical Twilights",
                                             command=self.display_all_observatory_visibility, width=20)
        self.show_obs_vis_button.pack()

        # Button to choose a folder
        self.choose_folder_button = tk.Button(self.parent, text="Choose Folder", command=self.choose_folder, width=20)
        self.choose_folder_button.pack()

        # Button to export the content of the textbox to a file
        self.export_button = tk.Button(self.parent, text="Export Content", command=self.export_content, width=20)
        self.export_button.pack()

        # Button to export the content of the textbox to a file
        self.export_gantt = tk.Button(self.parent, text="Export as Gantt Chart", command=self.export_gantt, width=20)
        self.export_gantt.pack()

        # Frame for start datetime input
        self.start_datetime_frame = tk.Frame(self.parent)
        self.start_datetime_frame.pack(pady=(5, 0))  # Adjust padding as needed

        # Start date label and entry
        tk.Label(self.start_datetime_frame, text="Start Date\n(YYYY-MM-DD HH:MM):").pack()
        self.start_date_entry = tk.Entry(self.start_datetime_frame, width=20)
        self.start_date_entry.pack()

        # Frame for end datetime input
        self.end_datetime_frame = tk.Frame(self.parent)
        self.end_datetime_frame.pack(pady=(5, 10))  # Adjust padding as needed

        # End date label and entry
        tk.Label(self.end_datetime_frame, text="End Date\n(YYYY-MM-DD HH:MM):").pack()
        self.end_date_entry = tk.Entry(self.end_datetime_frame, width=20)
        self.end_date_entry.pack()

        # Initialize with default values
        now = datetime.now()
        self.start_date_entry.insert(0, now.strftime("%Y-%m-%d %H:%M"))
        self.end_date_entry.insert(0, (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))

    def get_datetime_input(self):
        """Parse datetime input from entries."""
        start_str = self.start_date_entry.get()
        end_str = self.end_date_entry.get()

        try:
            start = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            end = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            if end < start:
                self.log_error("Start time must be earlier than end time.")
                return None, None
            return start, end
        except ValueError as e:
            self.log_error(f"Invalid date format: {e}")
            return None, None

    def choose_folder(self):
        """Open a dialog to choose a folder and store its path."""
        self.selected_folder_path = filedialog.askdirectory()
        if self.selected_folder_path:
            self.log_error(f"Selected folder: {self.selected_folder_path}")  # Utilize error_textbox for logging

    def export_content(self):
        """Export the textbox's content to a file in the selected folder."""
        if not self.selected_folder_path:
            self.log_error("Please choose a location first.")
            return

        # Define the file path
        file_path = os.path.join(self.selected_folder_path, f"{self.export_string}_{self.plan_iteration}.txt")


        try:
            # Open the file for writing and export the textbox content
            with open(file_path, 'w') as file:
                content = self.display_textbox.get("1.0", tk.END)
                file.write(content)
            self.log_error("Content exported successfully.")
        except Exception as e:
            self.log_error(f"Failed to export content. Error: {e}")

    def validate_unsigned_int(self, value):
        return re.match('^[0-9]*$', value) is not None

    def clear_display(self):
        self.display_textbox.delete('1.0', tk.END)

    def log_error(self, message):
        """Display error messages in the provided error_textbox widget."""
        self.error_textbox.configure(state='normal')  # Ensure the textbox is writable
        self.error_textbox.delete('1.0', tk.END)  # Clear previous content
        self.error_textbox.insert(tk.END, message)
        self.error_textbox.configure(state='disabled')  # Prevent further user edits

    def display_error(self, message):
        self.clear_display()  # Clear previous content
        self.display_textbox.insert(tk.END, message)

    def prepare_data(self):
        if (self.json_viewer_obs is not None and self.json_viewer_obs.data_ready) and (
                self.json_viewer_tle is not None and self.json_viewer_tle.data_ready):
            self.export_string = "Observation_Plan"
            self.json_viewer_tle_get_copy.clear()
            self.json_viewer_tle_get_copy = self.json_viewer_tle.get_data_with_priority()
            self.json_viewer_obs_get_copy.clear()
            self.json_viewer_obs_get_copy = self.json_viewer_obs.get_data_with_priority()
            start, end = self.get_datetime_input()
            if not start or not end:
                self.log_error("Invalid datetime input.")
                return
            self.plan = generate_plan(self.json_viewer_obs_get_copy,
                                      self.json_viewer_tle_get_copy,
                                      start, end, 0, 2)
            self.sorted_observations = self.create_sorted_observations()
            self.plan_iteration = self.plan_iteration + 1
        else:
            self.display_error("One or both JsonFileViewer instances either do not exist or their data is not ready.")

    # Function to create sorted observations
    def create_sorted_observations(self):
        sorted_observations = []
        for satellite_plan in self.plan:
            satellite_data, satellite_name = satellite_plan
            for observation in satellite_data:
                datetime_list, location = observation
                for datetime_pair in datetime_list:
                    start_time, end_time = datetime_pair
                    sorted_observations.append((location, satellite_name, start_time, end_time))
        sorted_observations.sort(key=lambda x: (x[0], x[2]))
        return sorted_observations

    # Function to display the sorted observations in the Text widget
    def print_sorted_observations(self):
        self.clear_display()  # Clear previous content
        for location, group in itertools.groupby(self.sorted_observations, key=lambda x: x[0]):
            observation_info = f"Observatory: {location}\n"
            for _, satellite_name, start_time, end_time in group:
                observation_info += f"    Start Time: {start_time}, End Time: {end_time}, Satellite: {satellite_name}\n"
            self.display_textbox.insert(tk.END, observation_info)

    def create_plan(self):
        self.prepare_data()
        if self.plan:
            self.sorted_observations = self.create_sorted_observations()
            if self.sorted_observations:
                self.print_sorted_observations()
            else:
                self.display_error("Failed to sort plan.")
        else:
            self.display_error("Failed to create plan.")

    def show_plan(self):
        if self.sorted_observations:
            self.export_string = "Observation_Plan"
            self.print_sorted_observations()
        else:
            self.display_error("The plan is not yet generated.")

    def display_all_satellite_visibility(self):
        # Check if both viewers exist and their data_ready is True
        if (self.json_viewer_obs_get_copy is not None and self.json_viewer_obs_get_copy != []) and (
                self.json_viewer_tle_get_copy is not None and self.json_viewer_tle_get_copy != []):
            self.clear_display()
            self.export_string = "Satellite_Visibility"
            for observatory in self.json_viewer_obs_get_copy:
                observation_info = f"Observatory: {observatory['COMMENT']}\n"
                for satellite in self.json_viewer_tle_get_copy:
                    tsat = EarthSatellite(satellite['TLE_LINE1'], satellite['TLE_LINE2'])
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
                            observation_info += f"    Start: {p[0]}, End: {p[2]}, Satellite: {tsat.model.satnum_str}\n"
                        else:
                            observation_info += f"    Start: {p[0]}, End: {p[1]}, Satellite: {tsat.model.satnum_str}\n"
                self.display_textbox.insert(tk.END, observation_info)
        else:
            self.display_error("Generate plan first.")

    def display_all_observatory_visibility(self):
        # Check if both viewers exist and their data_ready is True
        if self.json_viewer_obs_get_copy is not None and self.json_viewer_obs_get_copy != []:
            self.clear_display()
            self.export_string = "Observatory_Visibility"
            for observatory in self.json_viewer_obs_get_copy:
                observation_info = f"Observatory: {observatory['COMMENT']}\n"
                observation_times = observatory_visibility(observatory['START_TIME'], observatory['END_TIME'],
                                                           observatory['LATITUDE'], observatory['LONGITUDE'],
                                                           observatory['TIMEZONE_OFFSET'], 2)
                for start_time, end_time in observation_times:
                    observation_info += f"  Start time: {start_time}, End time: {end_time}\n"
                self.display_textbox.insert(tk.END, observation_info)
        else:
            self.display_error("Generate plan first.")

    def export_gantt(self):
        """
        Create a Gantt chart with x-axis labels for each unique start and end datetime and save it to a specified location.
        """
        if self.selected_folder_path:
            if self.sorted_observations:
                self.export_string = "gantt_chart"
                file_path_join = os.path.join(self.selected_folder_path,
                                              f"{self.export_string}_{self.plan_iteration}.svg")

                # Setting up the figure and axis for the plot
                fig, ax = plt.subplots(figsize=(10, 8))  # Adjusted size for better visibility

                # Collect all unique datetimes
                unique_datetimes = set()
                for _, _, start, end in self.sorted_observations:
                    # Assuming the datetimes are already in UTC, if not convert them to UTC
                    unique_datetimes.add(start.replace(tzinfo=None))
                    unique_datetimes.add(end.replace(tzinfo=None))

                # Sort the unique datetimes
                sorted_datetimes = sorted(list(unique_datetimes))

                # Generating the Gantt chart
                for i, task in enumerate(self.sorted_observations):
                    city, description, start, end = task
                    # Remove timezone info for consistent comparison and plotting
                    start = start.replace(tzinfo=None)
                    end = end.replace(tzinfo=None)
                    duration = (end - start).total_seconds() / 3600
                    ax.barh(city, duration, left=start, height=0.4)

                # Set the x-axis to have a tick for each unique datetime and rotate labels for readability
                ax.set_xticks(sorted_datetimes)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
                plt.xticks(rotation=90)

                # Adding labels and grid
                plt.xlabel('Date and Time')
                plt.ylabel('City')
                plt.title('Observation Schedule')
                plt.grid(True)

                # Adjust layout to prevent overlapping of x-axis labels
                plt.tight_layout()

                # Save the plot to file
                plt.savefig(file_path_join)
                plt.close()
            else:
                self.log_error("Failed to use sorted plan.")
        else:
            self.log_error("First select export path")
    def export_gantt(self):
        if self.selected_folder_path:
            if self.sorted_observations:
                self.export_string = "gantt_chart"
                file_path_join = os.path.join(self.selected_folder_path,
                                              f"{self.export_string}_{self.plan_iteration}.svg")

                # Setting up the figure and axis for the plot
                fig, ax = plt.subplots(figsize=(20, 15))  # Adjusted size for better visibility

                # Collect all unique datetimes
                unique_datetimes = set()
                for _, _, start, end in self.sorted_observations:
                    # Assuming the datetimes are already in UTC, if not convert them to UTC
                    unique_datetimes.add(start.replace(tzinfo=None))
                    unique_datetimes.add(end.replace(tzinfo=None))

                # Sort the unique datetimes
                sorted_datetimes = sorted(list(unique_datetimes))

                # Generating the Gantt chart
                for i, task in enumerate(self.sorted_observations):
                    city, description, start, end = task
                    # Convert start and end times to Matplotlib's date format
                    start_num = mdates.date2num(start.replace(tzinfo=None))
                    end_num = mdates.date2num(end.replace(tzinfo=None))
                    duration = end_num - start_num  # Duration in Matplotlib's date format
                    ax.barh(city, duration, left=start_num, height=0.4)

                # Set the x-axis to have a tick for each unique datetime and format them
                ax.set_xticks([mdates.date2num(dt) for dt in sorted_datetimes])
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
                plt.xticks(rotation=90)
                plt.tick_params(axis='x', which='major', labelsize=8)  # Adjust font siz                )



                # Adding labels and grid
                plt.xlabel('Date and Time')
                plt.ylabel('City')
                plt.title('Observation Schedule')
                plt.grid(True)

                # Adjust layout to prevent overlapping of x-axis labels
                plt.tight_layout()

                # Save the plot to file
                plt.savefig(file_path_join)
                plt.close()
            else:
                self.log_error("Failed to use sorted plan.")
        else:
            self.log_error("First select export path")


