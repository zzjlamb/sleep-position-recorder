# RPi Pico software for reading and recording sleep positions
# from a MPU6050 6 axis IMU
# We are not interested in gyroscope data, only the gravity vector,
# as it is assumed that the subject is not accelerating during the reading, apart from
# gravitational acceleration.
# This software will not work in a zero G environment :)

import machine
import time

# MPU6050 driver at
# https://github.com/TimHanewich/MicroPython-Collection/blob/master/MPU6050/MPU6050.py
import MPU6050
import math as m

debug=False

_ISO_FORMAT_STRING = const("{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.{:03d}Z")

last_position="Unknown"

# Name the log file
now=time.localtime()
dfileName=f"SM{now[3]:02d}{now[4]:02d}{now[5]:02d}.csv"
if debug:
    print(dfileName)
    
# Set up the I2C interface
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))

# Set up the MPU6050 class 
mpu = MPU6050.MPU6050(i2c)

# Setup the onboard LED
led=machine.Pin(25,machine.Pin.OUT)
led.off()

# Convert a timestamp to text
def timestamp_iso8601():
    time_tuple = time.localtime()
    return _ISO_FORMAT_STRING.format(
        time_tuple[0],
        time_tuple[1],
        time_tuple[2],
        time_tuple[3],
        time_tuple[4],
        time_tuple[5],
        0,
    )

# Log an entry
def record_data(position):
    #date and time
    line=f"{timestamp_iso8601()},{position}"
    if debug:
        print(line)
    with open(dfileName,'a') as f:
        f.write(line+'\n')

# wake up the MPU6050 from sleep
mpu.wake()
time.sleep(0.1)  # Wait for the MPU to wake up


#Setup data file
f=open(dfileName,"w")
f.close()

# Measure linear acceleration every one second
# The MPU returns a tuple with three values:
#  x, y and z. Gravitational acceleration is 1 unit.
while True:
    position="Unknown"
    
    try:
        accel = mpu.read_accel_data()
        
        #  Calculate the roll angle from the gravity direction
        deg=m.degrees(m.atan2(accel[0],accel[2]))
        if debug:
            print (f"{deg:.1f} degrees")

        # If the gravity vector is in the general direction of the Y axis, record Standing
        # (Could also be standing on head, but unlikely!
        if abs(accel[1])>0.9:
                position="Standing"
                
        # Here if not Standing, otherwise ignore the roll angle and record Standing
        elif deg>-50 and deg <50:
            position="Supine"
        elif deg >120 or deg <-120:
                position="Prone"
        else:
            if deg>0:
                position="Right"
            else:
                position="Left"
        # Update the last position
        # We only write a log entry if it has changed
        if position != last_position:
            last_position = position
            record_data(position)
        # Light the onboard LED if standing (confirms the unit is working)
        if position=="Standing":
            led.on()
        else:
            led.off()
    except:
        record_data("IMU read error")
    time.sleep(1)
