import time
import os
from _models.Brain import Brain
from _models.RingDetectorYOLO import RingDetector

# Constants indicating if a message was sent from the
# brain or the jetson
BRAIN_IDENTIFIER = "B"
JETSON_IDENTIFIER = "J"

previous_data_received = []
data_received = []

# Loads in the model and weights
rl_brain = Brain("./_models/weights/04-27-2022.onnx")
detector = RingDetector("./_models/weights/best.pt", camera_pitch=30)

def write_to_brain(str):
    # Open up serial port and send string to 
    # jetson with JETSON_IDENTIFIER
    str = JETSON_IDENTIFIER + " " + str + "\n"
    f = open("/dev/ttyACM1", "w")
    f.write(str)
    f.close()

def read_from_brain():
    # Read data from brain

    f = open("brain_output", "r")

    global previous_data_received

    # Read the last line in the brain_output buffer
    data_received = f.readlines()[-1].rstrip().split()

    # If the data is unique, this means the brain is sending
    # new data
    if previous_data_received != data_received:
        print(data_received)
        previous_data_received = data_received
        return True, data_received

    return False, data_received

def __main__():
    i = 0
    time.sleep(0.5)
    f = open("testfile", "a+")
    print("-----", file=f)

    while True:
        try:

            # output indicates wether or not to output the calculated
            # result to the brain
            # data recieved has the data we need to pass into our reinforcement
            # learning model
            output, data_received = read_from_brain()

            # Converts items in the list of paramaters to floats
            # removes BRAIN_IDENTIFIER
            data_received = [float(x) for x in data_received[1:-1]]

            # Detect all rings in frame, add closest 10 ring
            # positions to the rest of the data we recieved 
            # from the brain
            data_received.extend(detector.inference(10))

            # Debugging/logging
            print(data_received)
            print(data_received, file=f)

            # Time normailization
            data_received[0] = data_received[0]/105

            # Run an inference on the reinforcement learning model
            # to find which way to move
            res = rl_brain.inference(data_received)

            # Logging
            print(res, file=f)

            velocity, rotation = str(res[0]), str(res[1])

            # Logging
            print(f'{velocity} {rotation}', file=f)

            # If this data is unique, send the results to the 
            # brain
            if output:
               string_to_send = velocity + " " + rotation + " " + str(i)
               write_to_brain(string_to_send)
               i += 1

        # Ctrl + C on this program closes the entire pipeline
        except KeyboardInterrupt:
            print("Closing and Cleaning up...")
            os.system("./stop.sh")
            exit()


if __main__:
    __main__()
