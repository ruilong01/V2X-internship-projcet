import socket
import threading
from tkinter import *
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import time
import atexit
import pygame
import queue

# Add this line at the beginning of your code to initialize the queue
gui_queue = queue.Queue()

# Variable to store the previous console message
prev_console_message = ""
# Variable to store the previous message in the message box
prev_message_box_message = ""

top = Tk()

# Declare global variables for formatted data
formatted_lat = ""
formatted_lon = ""
traffic_notification = ""

def socket_txrf1(conn1):
    while True:
        data = conn1.recv(100)
        print('Rx from client 1 ->', data)
        if not data:
            break
        elif data == b'no need give me PB status':
            break
        elif data == b'give me PB status':
            if button_state == False:
                conn1.sendall(b'warning issue')
            else:
                conn1.sendall(b'no warning issue')
    conn1.close()

def socket_txrf2(conn2):
    global led_state
    global rx_text_lat

    current_data = ""

    while True:
        data = conn2.recv(100)
        print('Rx from client 2 ->', data)

        # Append the received data to the current data
        current_data += data.decode('utf-8')

        # Check if the received data contains "end"
        if 'end' in current_data:
            # Split the data and extract the value
            value_str = current_data.split("end")[0]

            # Check if the received data contains "lat" or "long" as prefixes
            if 'lat' in current_data:
                # Extract the latitude value
                value = float(value_str.split(":")[1])

                # Format the value with 7 decimal places
                formatted_data = "{:.7f}".format(value / 10**7)

                # Print and display the formatted data
                print("Formatted remote Latitude:", formatted_data)
                rx_text_lat = f"Latitude: {formatted_data}"

                # Update the latitude frame
                gui_queue.put({'latitude': rx_text_lat})

                # Send the formatted latitude to conn3
                send_data_to_conn3(f'lat: {formatted_data} end')

            elif 'long' in current_data:
                # Extract the longitude value
                value = float(value_str.split(":")[1])

                # Format the value with 7 decimal places
                formatted_data = "{:.7f}".format(value / 10**7)

                # Print and display the formatted data
                print("Formatted remote Longitude:", formatted_data)
                rx_text_lon = f"Longitude: {formatted_data}"

                # Update the longitude frame
                gui_queue.put({'longitude': rx_text_lon})

                # Send the formatted longitude to conn3
                send_data_to_conn3(f'long: {formatted_data} end')

            # Reset current_data for the next set of data
            current_data = ""

        elif data.startswith(b'db'):
            # Display "Traffic" information in a separate line in the console
            print("Traffic Information:", data.decode('utf-8'))
            rx_text = f"Traffic Information: {data.decode('utf-8')}"

            # Send the traffic information to socket_txrf3
            send_data_to_conn3(data.decode('utf-8'))

            # Update the traffic notification frame
            gui_queue.put({'traffic': data.decode('utf-8')})

        else:
            # Display all received data
            print(f"Received: {data.decode('utf-8')}")
            rx_text = f"Received: {data.decode('utf-8')}"

            # Send the received data to socket_txrf3
            send_data_to_conn3(data.decode('utf-8'))

        # Acknowledge the receipt of data
        conn2.sendall(b'Data received')

        if not data:
            break
        elif data == b'no need give me LED status':
            break
        elif data == b'give me LED ON status':
            led_state = False
            print('LED State: ON')
            conn2.sendall(b'LED ON status received')
        elif data == b'give me LED OFF status':
            led_state = True
            print('LED State: OFF')
            conn2.sendall(b'LED OFF status received')

    conn2.close()

def send_data_to_conn3(data):
    global conn3
    try:
        conn3.sendall(data.encode('utf-8'))
    except Exception as e:
        print(f"Error sending data to conn3: {e}")

def socket_txrf3(conn3):
    global formatted_lat
    global formatted_lon
    global traffic_notification

    while True:
        # Send the formatted data to socket_txrf3
        if formatted_lat:
            conn3.sendall(formatted_lat.encode('utf-8'))
            formatted_lat = ""  # Reset formatted_lat after sending

        if formatted_lon:
            conn3.sendall(formatted_lon.encode('utf-8'))
            formatted_lon = ""  # Reset formatted_lon after sending

        if traffic_notification:
            conn3.sendall(traffic_notification.encode('utf-8'))
            traffic_notification = ""  # Reset traffic_notification after sending

        # Receive data from conn3
        data_from_conn3 = conn3.recv(100)
        print('Rx from conn3 ->', data_from_conn3)

        # Process and display the received data from conn3
        print(f"Data from conn3: {data_from_conn3.decode('utf-8')}")
        rx_text = f"Data from conn3: {data_from_conn3.decode('utf-8')}"

        # Acknowledge the receipt of data to the client connected through conn3
        conn3.sendall(b'Data received')

        if not data_from_conn3:
            break

    conn3.close()

def toggle_button():
    global button_state
    if button_state == False:
        button_state = True
    else:
        button_state = False
    print("Button state is now", button_state)

# Function to play music
def play_music():
    music_file = "/home/student/Downloads/notification_sound.mp3"

    # Check if the LED state is on
    while True:
        if led_state:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        else:
            time.sleep(1)

def write_LED():
    global led_state
    global rx_text_lat

    if led_state == False:
        C.itemconfig(LED_img, image=off_led_img)  # turn LED off
    else:
        C.itemconfig(LED_img, image=on_led_img)  # turn LED on

    L.config(text=rx_text_lat)
    print('inside write_led')
    top.after(300, write_LED)  # schedule the function read...exec after 300ms

# Declare global variables for frames
lat_frame = None
lon_frame = None
traffic_frame = None

# Declare global variables for labels
lat_label = None
lon_label = None
traffic_label = None

# Modify update_latitude_info and update_longitude_info functions
def update_info(label, frame, info):
    if label is not None and frame is not None:
        # Clear previous information
        label.config(text="")
        # Update with the new information
        label.config(text=info)
    else:
        # If label or frame is not defined, create a new Label and Frame
        frame = Frame(top)
        frame.pack()
        label = Label(frame, text=info)
        label.pack()

# Function to update the latitude information
def update_latitude_info(latitude_info):
    global lat_label, lat_frame
    if lat_label is not None and lat_frame is not None:
        # Update with the new information
        lat_label.config(text=latitude_info)
    else:
        # If label or frame is not defined, create a new Label and Frame
        lat_frame = Frame(top)
        lat_frame.pack()
        lat_label = Label(lat_frame, text=latitude_info)
        lat_label.pack()

# Function to update the longitude information
def update_longitude_info(longitude_info):
    global lon_label, lon_frame
    if lon_label is not None and lon_frame is not None:
        # Update with the new information
        lon_label.config(text=longitude_info)
    else:
        # If label or frame is not defined, create a new Label and Frame
        lon_frame = Frame(top)
        lon_frame.pack()
        lon_label = Label(lon_frame, text=longitude_info)
        lon_label.pack()

# Function to update the traffic notification
def update_traffic_notification(notification):
    global traffic_label, traffic_frame
    if traffic_label is not None and traffic_frame is not None:
        # Update with the new notification
        traffic_label.config(text=notification)
    else:
        # If label or frame is not defined, create a new Label and Frame
        traffic_frame = Frame(top)
        traffic_frame.pack()
        traffic_label = Label(traffic_frame, text=notification)
        traffic_label.pack()

    # Print traffic notification to console
    print(f"Traffic Information: {notification}")

def process_gui_queue():
    while not gui_queue.empty():
        gui_update = gui_queue.get()
        update_latitude_info(gui_update.get('latitude', ''))
        update_longitude_info(gui_update.get('longitude', ''))
        update_traffic_notification(gui_update.get('traffic', ''))

    top.after(100, process_gui_queue)

top.after(100, process_gui_queue)
# Start the Tkinter main loop

top.mainloop()
