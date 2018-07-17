import sys
from functions import *

port = '/dev/ttyUSB0'
user_input = [0]
print("\nWelcome to the TEAL Ultrasonic PCBA calibration and test application.")
print("To begin, first specify the communication port:  e.g. `port com15`")
print_usage()

while(user_input[0] != 'q'):

    print('\n------------------------------------------------------')
    print('Enter a command... (enter `q` to quit or `h` for help)')

    user_input=list(map(str,input().split(' ')))

    command  = user_input[0]

    if command == 'port':
        try:
            port = user_input[1]
            print("Port set to: ", port)
        except:
            print("Unexpected error:", sys.exc_info()[0])
        finally:
            pass

    elif command == 'read':
        try:
            result = read_reg(port, int(user_input[1]))
            print("Value %d read from register %d" % (result[1], int(user_input[1])))
        except:
            print("Unexpected error:", sys.exc_info()[0])

    elif command == 'write':
        try:
            write_reg(port, int(user_input[1]), int(user_input[2]))
            result = read_reg(port, int(user_input[1]))
            if int(result[1]) != int(user_input[2]):
                print("Write failed.")
                sys.exit()
            else:
                print("Value %d written to register %d" % (result[1], int(user_input[1])))
        except:
            print("Unexpected error:", sys.exc_info()[0])

    elif command == 'params':
        try:
            result = write_parameters(port, 'golden_file.txt')
            # First measurement after writing parameters is always bad for some strange reason. Flush the sensor.
            take_measurement(port)
            if result >= 1:
                print("Wrote: %7d   Register(s)" % result)
                print("Success! Run `save` to store eeprom settings.")
            elif result < 0:
                print("Failed!.")
            elif result == 0:
                print("Already has settings.")
        except:
            print("Unexpected error:", sys.exc_info()[0])

    elif command == 'save':
        try:
            save_eeprom(port)
            print("Saved.")
        except:
            print("Unexpected error:", sys.exc_info()[0])

    elif command == 'measure':
        try:
            results = take_measurement(port)
            print("Distance: %2.3f   Amplitude: %3d   Width:%3d" % (results[0], results[1], results[2]))
        except:
            print("Unexpected error:", sys.exc_info()[0])

    elif command == 'diag':
        try:
            results = get_resonant_frequency(port)
            print("Frequency: %2.2f   Register Value: %2d" % (results[0], results[1]))
        except:
            print("Unexpected error:", sys.exc_info()[0])

    elif command == 'sweep':
        sweep_for_best_frequency(port)
    elif command == 'q':
        print("Exiting program.")

    elif command == 'h':
        print_usage()
    else:
        print("Command not recognized.")