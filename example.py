import pyCandapter
import can
import signal
import csv
import os
import time
from datetime import datetime

#Port and baudrate for serial communication with the Candapter
PORT = input("enter port: ")
SERIALBAUDRATE = 9600
CANBAUDRATE = 500000

candapter = pyCandapter.pyCandapter(PORT, SERIALBAUDRATE)
candapter.openCANBus(CANBAUDRATE)

def signal_handler(sig, frame):
    candapter.closeCANBus()
    exit(0) 

def ensure_data_directory():
    """
    Ensures that the 'data' directory exists. If it does not exist,
    the directory is created.
    """
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created 'data' directory.")

# Function to create a new log file with a header
def create_log_file():
    """
    Creates a new CSV log file in the 'data' directory with a timestamped filename.
    The file contains headers: 'date', 'time', 'can_id', and 'value'.
    
    Returns:
        str: The filename of the created log file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_filename = f"orion_bms_data_{timestamp}.csv"
    
    # Open the file in write mode and add the CSV header
    with open(log_filename, 'w', newline='') as csvfile:
        log_writer = csv.writer(csvfile)
        log_writer.writerow(['date', 'time', 'can_id', 'value'])  # Write header
    print(f"Log file created: {log_filename}")
    
    return log_filename

def log_data_to_csv(log_filename, can_id, decoded_value):

    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H:%M:%S")

    # Append the new row of data to the CSV file
    with open(log_filename, 'a', newline='') as csvfile:
        log_writer = csv.writer(csvfile)
        log_writer.writerow([date_str, time_str, hex(can_id), decoded_value])
    print(f"Logged data: Date={date_str}, Time={time_str}, CAN_ID={hex(can_id)}, Value={decoded_value}")



signal.signal(signal.SIGINT, signal_handler)

#For receiving
#ensure_data_directory()
log_file = create_log_file()

while True:
    try:
        message = candapter.readCANMessage()
        if message is not None:
            #print(message)
            candapter.Information_from_BMS(message)
            for i in range(4):
                log_data_to_csv(log_file,message.arbitration_id,message.data[i])                
        
    except KeyboardInterrupt:
        print("closing Bus....")
        candapter.closeCANBus()
        candapter.closeDevice()

