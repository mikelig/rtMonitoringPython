import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter, MinuteLocator

# Get the directory of the current script
current_dir = os.path.dirname(__file__)

# Construct the path to the data file
data_file_path = os.path.join(current_dir, 'data', 'record_2k_events_30min_23052024.txt')

# Read data from file
data = pd.read_csv(data_file_path, header=None, names=['Time', 'CPU Usage', 'Memory Usage'])

# Clean and convert data
data['Time'] = pd.to_datetime(data['Time'], format='%H:%M:%S')
data['CPU Usage'] = data['CPU Usage'].str.rstrip('%').astype(float)
data['Memory Usage'] = data['Memory Usage'].astype(float)

# Plot the data
plt.figure(figsize=(10, 5))

# Plot CPU usage
plt.plot(data['Time'], data['CPU Usage'], label='CPU Usage (%)', color='blue')

# Plot Memory usage
plt.plot(data['Time'], data['Memory Usage'], label='Memory Usage (MiB)', color='red')

# Set plot title and labels
plt.title('CPU and Memory Usage Over Time')
plt.xlabel('Time')
plt.ylabel('Usage')

# Set the major locator for x-axis to 1 minute
plt.gca().xaxis.set_major_locator(MinuteLocator(interval=1))
plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

# Rotate time labels for better readability
plt.xticks(rotation=45)

# Add a legend
plt.legend()

# Adjust layout to make room for the rotated x-axis labels
plt.tight_layout()

# Show the plot
plt.show()
