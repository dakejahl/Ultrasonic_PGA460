import sys
from functions import *

port = ''
user_input = [0]

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
                print("Write failed!")
                sys.exit()
            else:
                print("Value %d written to register %d" % (result[1], int(user_input[1])))
        except:
            print("Unexpected error:", sys.exc_info()[0])

    elif command == 'params':
        try:
            result = write_parameters(port, 'golden_file.txt')
            if result >= 1:
                print("Wrote: %3d register(s)" % result)
                print("All parameter data has been successfully written. Run `save` to store eeprom settings.")
            elif result < 0:
                print("Failed to write to eeprom.")
            elif result == 0:
                print("Nothing to write, eeprom already has settings")
        except:
            print("Unexpected error:", sys.exc_info()[0])
    elif command == 'save':
        save_eeprom(port)
    elif command == 'q':
        print("Exiting program.")
    elif command == 'h':
        print_usage()
    else:
        print("Command not recognized.")