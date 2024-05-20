import numpy as np
import time
import psutil
import os
from time import perf_counter

def filter_outliers(datos):
    '''
    Importante: 
    He modificado el codigo de filter_outliers para que en vez de generar una lista intermedia
    con los valores aceptables, me genere una lista con los indices de los valores que se posicionan fuera del 
    filtro. 
    He hecho esta modificación porque por una parte uso menos la memoria (ya que solo guardo los indices en vez de los valores float)
    y por otra, puedo más tarde usar estos indices para eliminar los valores fuera del filtro de una manera
    mucho más rápida y optimizada.
    '''
    mean = sum(datos) / len(datos)
    varianza = sum((x - mean) ** 2 for x in datos) / (len(datos) - 1)
    std = varianza ** 0.5
    
    low, high = mean - 3 * std, mean + 3 * std
    # low, high = mean - std, mean + std # for testing filter only
    
    # Get indices of outliers
    outlier_indices = [i for i, v in enumerate(datos) if v < low or v > high]
    return outlier_indices

def process_batch(events):
    # Extract values from the events
    values = [event[3] for event in events]
    
    # Get indices of outliers
    outlier_indices = filter_outliers(values)
    
    # Filter events to exclude outliers
    filtered_events = [event for index, event in enumerate(events) if index not in outlier_indices]
    
    # Return the values of the dictionary as the filtered event list
    return filtered_events

def get_memory_usage():
    # Get the current process
    process = psutil.Process(os.getpid())
    # Get the memory usage in bytes and convert to MB
    memory_usage = process.memory_info().rss / (1024 * 1024)
    return memory_usage

def initTest(events):
    print(f"Starting test with event num = {len(events)}")
    # Record start time and initial memory usage
    start_time = perf_counter()

    # Process the batch
    filtered_events = process_batch(events)
    
    # Record end time and final memory usage
    end_time = perf_counter()

    # Calculate elapsed time and memory usage
    elapsed_time = (end_time - start_time) * (10**6) # us

    # Output the results
    print(f"Original Events Len: {len(events)}")
    print(f"Filtered Events Len: {len(filtered_events)}")
    print(f"Elapsed Time: {elapsed_time} microseconds")

# Example events
events_short = [
    (1716206530, 'sensor_10', 'type_3', 39.685437773123255),
    (1716206530, 'sensor_10', 'type_3', 7.320206397639484),
    (1716206531, 'sensor_10', 'type_1', 12.013880666130017),
    (1716206532, 'sensor_10', 'type_1', 89.54176143041083)
]

events_long = [
    (1716206530, 'sensor_10', 'type_3', 39.685437773123255), (1716206530, 'sensor_10', 'type_3', 7.320206397639484), (1716206531, 'sensor_10', 'type_1', 12.013880666130017), (1716206532, 'sensor_10', 'type_1', 89.54176143041083), (1716206533, 'sensor_10', 'type_3', 3.169672718463179), (1716206533, 'sensor_10', 'type_3', 63.10851487944746), (1716206534, 'sensor_10', 'type_3', 66.14644358387712), (1716206535, 'sensor_10', 'type_3', 83.42455825571288), (1716206536, 'sensor_10', 'type_2', 82.94577819438811), (1716206536, 'sensor_10', 'type_1', 49.40299656595587), (1716206537, 'sensor_10', 'type_3', 14.098733002907604), (1716206537, 'sensor_10', 'type_1', 45.52718346884686), (1716206538, 'sensor_10', 'type_2', 31.202319474347284), (1716206538, 'sensor_10', 'type_2', 8.530517563134211), (1716206540, 'sensor_10', 'type_1', 86.7257878292727), (1716206542, 'sensor_10', 'type_3', 33.91589426067452), (1716206544, 'sensor_10', 'type_3', 16.991328281892336), (1716206549, 'sensor_10', 'type_1', 62.963505748666414), (1716206554, 'sensor_10', 'type_2', 61.88885238916182), (1716206555, 'sensor_10', 'type_3', 98.77105847897673), (1716206556, 'sensor_10', 'type_1', 15.21968413582262), (1716206557, 'sensor_10', 'type_2', 35.21202861638633), (1716206557, 'sensor_10', 'type_2', 76.40317105069741), (1716206560, 'sensor_10', 'type_2', 8.434278056254463), (1716206561, 'sensor_10', 'type_1', 79.9902495031215), (1716206563, 'sensor_10', 'type_2', 41.76271307086705), (1716206563, 'sensor_10', 'type_1', 16.673854862045722), (1716206564, 'sensor_10', 'type_2', 28.86346282779688), (1716206569, 'sensor_10', 'type_3', 99.52756157430962), (1716206570, 'sensor_10', 'type_1', 54.2597512833725)
]

initTest(events_short)
time.sleep(5)
initTest(events_long)

