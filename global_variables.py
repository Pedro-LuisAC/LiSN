import re
from pathlib import Path
file = open("editable_init_variables.txt").readlines()

def get_variable(variable_name):
    for line in file:
        name, val = line.split('=')
        if variable_name in name:
            return int(val)


def initialize():

    global calibration_factor
    calibration_factor = get_variable("dBRelPa_calibration_factor")
    global CHUNK
    CHUNK = get_variable("chunk_size")
    global noise_db
    noise_db = get_variable("noise_initial_volume")
    global phrase_db
    phrase_db = get_variable("phrase_initial_volume")
    global phrase_db_aux
    phrase_db_aux = phrase_db
    global srt_graph_aux
    srt_graph_aux = False
    global BASE_DIR
    BASE_DIR = Path(__file__).parent.resolve()


    # global value_db
    # value_db = 60
    # global CHUNK
    # CHUNK = 1024
    # global noise_db
    # noise_db = -30
    # global phrase_db
    # phrase_db = -25
    # global phrase_initalization_db
    # phrase_initalization_db = -25
if __name__ == '__main__':
    initialize()
    print(BASE_DIR)