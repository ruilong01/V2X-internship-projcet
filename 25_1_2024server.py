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

# Declare global variables for formatted data
formatted_lat = ""
formatted_lon = ""
traffic_notification = ""

led_state = False
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

            elif 'db' in current_data:
                # Extract the traffic notification
                traffic_info = current_data.split("db")[1].split("end")[0].strip()

                # Display traffic information in the console
                print("Traffic Information:", traffic_info)
                rx_text_traffic = f"Traffic Information: {traffic_info}"

                # Send the traffic information to socket_txrf3
                send_data_to_conn3(traffic_info)

                # Update the traffic notification frame
                gui_queue.put({'traffic': rx_text_traffic})

            elif 'available' in current_data:
                # Extract parking lot availability information
                parking_info = current_data.split("available")[0].strip()

                # Display parking lot availability information in the console
                print("Parking Lot Availability:", parking_info)
                rx_text_parking = f"Parking Lot Availability: {parking_info}"

                # Send parking lot availability information to socket_txrf3
                send_data_to_conn3(parking_info)

                # Update the parking lot availability frame
                gui_queue.put({'parking': rx_text_parking})

            # Reset current_data for the next set of data
            current_data = ""

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
        elif data.strip() == b'give me LED ON status':

            led_state = False
            print('LED State: ON')
            conn2.sendall(b'LED ON status received')

        elif data.strip() == b'give me LED OFF status':
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
        B.config(image=on_button_img)
    else:
        button_state = False
        B.config(image=off_button_img)
    print("Button  state is now", button_state)


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

def update_latitude_info(latitude_info):
    global lat_label, lat_frame
    # Check if lat_label and lat_frame are already defined
    if lat_label is not None and lat_frame is not None:
        # Update with the new information
        lat_label.config(text=latitude_info)
    else:
        # If lat_label or lat_frame is not defined, create a new Label and Frame
        lat_frame = Frame(top)
        lat_frame.pack()
        lat_label = Label(lat_frame, text=latitude_info)
        lat_label.pack()

# Function to update the longitude information
def update_longitude_info(longitude_info):
    global lon_label, lon_frame
    # Check if lon_label and lon_frame are already defined
    if lon_label is not None and lon_frame is not None:
        # Update with the new information
        lon_label.config(text=longitude_info)
    else:
        # If lon_label or lon_frame is not defined, create a new Label and Frame
        lon_frame = Frame(top)
        lon_frame.pack()
        lon_label = Label(lon_frame, text=longitude_info)
        lon_label.pack()

def update_traffic_notification(notification):
    global traffic_label, traffic_frame
    if traffic_label is not None:
        # Update with the new notification
        traffic_label.config(text=notification)
    else:
        # If traffic_label is not defined, create a new Label
        traffic_label = Label(traffic_frame, text=notification)
        traffic_label.pack()
# Function to clean up GPIO on program exit
def cleanup_gpio():
    GPIO.cleanup()

# Set up a function to run the GPIO cleanup on exit
atexit.register(cleanup_gpio)

# Create the tkinter root window
top = Tk()

# Initialize Pygame mixer after the tkinter root window is created
pygame.mixer.init()

# Update image file paths
off_led_img_path = "./01_nissan-maxima-aeb_off.gif"
on_led_img_path = "./02_nissan-maxima-aeb_on.gif"
on_button_img_path = "./03_push-brake_color.gif"
off_button_img_path = "./04_push-brake_white.gif"

# Convert the Pillow images to PhotoImage
on_led_img = ImageTk.PhotoImage(Image.open(on_led_img_path))
off_led_img = ImageTk.PhotoImage(Image.open(off_led_img_path))
on_button_img = ImageTk.PhotoImage(Image.open(on_button_img_path))
off_button_img = ImageTk.PhotoImage(Image.open(off_button_img_path))

button_state = False
led_state = False

# For the first connection on the local network
HOST1 = '192.168.1.1'
PORT1 = 50007

# For the local connection
HOST3 = '127.0.0.1'
PORT3 = 50007

## common
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s1.bind((HOST1, PORT1))
s1.listen(6)

# server 1 - PB
print("I am Server1")
conn1, addr1 = s1.accept()  # blocking
print('First connection to ', addr1)
update_thread1 = threading.Thread(target=socket_txrf1, args=(conn1,))
update_thread1.start()

B = Button(top, image=on_button_img, command=toggle_button)
B.pack()  # put button into window

# server 2 - LED
print("I am Server2")
conn2, addr2 = s1.accept()  # blocking
print('Second connection to ', addr2)
update_thread2 = threading.Thread(target=socket_txrf2, args=(conn2,))
update_thread2.start()

##socket 3
s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
s3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s3.bind((HOST3, PORT3))
s3.listen(8)

# Accept connection for the third client
print("I am Server3")
conn3, addr3 = s3.accept()  # blocking
print('Third connection to ', addr3)
update_thread3 = threading.Thread(target=socket_txrf3, args=(conn3,))
update_thread3.start()

# Start the music thread
music_thread = threading.Thread(target=play_music)
music_thread.start()

C = Canvas(top, width=220, height=160)
LED_img = C.create_image(0, 0, image=on_led_img, anchor=NW)
C.pack()

#rx_text_lat = "No message for now"
#L = Label(top, text=rx_text_lat)
#L.pack()

# Create a Tkinter frame for traffic notifications
traffic_frame = Frame(top)
traffic_frame.pack()

traffic_label = Label(traffic_frame, text="No traffic notification so far")
traffic_label.pack()

def process_gui_queue():
    gui_update = {}

    while not gui_queue.empty():
        update = gui_queue.get_nowait()
        gui_update.update(update)

    if 'latitude' in gui_update:
        update_latitude_info(gui_update['latitude'])

    if 'longitude' in gui_update:
        update_longitude_info(gui_update['longitude'])

    if 'traffic' in gui_update:
        update_traffic_notification(gui_update['traffic'])

    top.after(100, process_gui_queue)


top.after(100, process_gui_queue)
# Start the Tkinter main loop
top.mainloop()
