import serial
ser = serial.Serial('/dev/ttyACM0', 115200)
while True:
    bytesToRead = ser.inWaiting()
    ser.read(bytesToRead)
    print ser.readline()
