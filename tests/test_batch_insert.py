import sqlite3

def insertTest(filtered_events):
    # Insert filtered events to SQLite DB
    conn = sqlite3.connect('sensor_events.db')
    cursor = conn.cursor()
    cursor.executemany('''
    INSERT INTO sensorEvents (receptionTs, idSensor, sensorType, sensorValue)
    VALUES (?, ?, ?, ?)
    ''', filtered_events)
    
    # # Insert backup -- Not implemented yet
    # backup_ts = int(time.time())
    # cursor.execute('''
    # INSERT INTO periodicBackups (idSensor, backupTs, mean, variance, stddev)
    # VALUES (?, ?, ?, ?, ?)
    # ''', (sensor_id, backup_ts, mean_val, variance_val, stddev_val))

    conn.commit()
    conn.close()

events_short = [
    (1716206530, 'sensor_10', 'type_3', 39.685437773123255),
    (1716206530, 'sensor_10', 'type_3', 7.320206397639484),
    (1716206531, 'sensor_10', 'type_1', 12.013880666130017),
    (1716206532, 'sensor_10', 'type_1', 89.54176143041083)
]
insertTest(events_short)


