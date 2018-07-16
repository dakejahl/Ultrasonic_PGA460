import sys
from functions import *

port = ''
user_input = [0]

print('\nCommands:')
print('    port(path)                    e.g: port COM15')
print('    read(addr)                    e.g: read 0')
print('    write(addr, val)              e.g: write 0 55')
print('    write_eeprom(file_name)       e.g: write_eeprom golden_file')
print('')

while(user_input[0] != 'q'):

    print('---------------------------------------')
    print('Enter a command... (enter `q` to quit)')

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

    elif command == 'write_eeprom':
        # try:
        result = write_eeprom(port, 'golden_file.txt')
        if result == 1:
            print("All eeprom data has been successfully written and burned.")
        else:
            print("Failed to write to eeprom.")
        # except:
        #     print("Unexpected error:", sys.exc_info()[0])

    elif command == 'q':
        print("Exiting program.")
    else:
        print("Command not recognized.")