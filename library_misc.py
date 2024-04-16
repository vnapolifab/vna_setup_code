import os
import numpy as np
import json

"""
This library contains general functions that are used throughout the program and are not related to a specific instrument or procedure.
"""

def saveData(x: list[float], y: list[float], p: list[float], user_folder: str, sample_folder: str, filename: str, index: int) -> str:
    """
    Saves data in as {root_folder}/{user_folder}/{sample_folder}/{filename} {suffix}", checks if existing measurements exist already and adds a suffix
    """

    rows = list(zip(x,y,p))

    root_folder = "DATA/"
    initialname = filename
    format = ".csv"

    if not(os.path.exists( f"{root_folder}/{user_folder}" )):   # Create user folder if it does not exist
        os.mkdir(f"{root_folder}/{user_folder}")

    if not(os.path.exists( f"{root_folder}/{user_folder}/{sample_folder}" )):   # Create sample folder if it does not exist
        os.mkdir(f"{root_folder}/{user_folder}/{sample_folder}")

    if not(os.path.exists( f"{root_folder}/{user_folder}/{sample_folder}/{filename}" )):
        os.mkdir(f"{root_folder}/{user_folder}/{sample_folder}/{filename}")
    elif index == 0:
        suffix = 2
        while os.path.exists( f"{root_folder}/{user_folder}/{sample_folder}/{filename} {suffix}" ):
            suffix = suffix+1
        filename = filename + f" {suffix}"
        sendWarning(f'Folder named "{initialname}" already exists, using "{filename}" instead')
        os.mkdir(f"{root_folder}/{user_folder}/{sample_folder}/{filename}")

    print("PATH:", f"{root_folder}/{user_folder}/{sample_folder}/{filename}/{filename} ({index+1}){format}")
    np.savetxt(f"{root_folder}/{user_folder}/{sample_folder}/{filename}/{filename} ({index+1}){format}", rows, delimiter=',')

    return filename


def load_and_convert(filename: str) -> tuple[list[float], list[float], list[float]]:
    """
    Reads data from txt file assuming 3 columns: frequency, amplitude, phase.
    Takes filename as input and returns relevant data.
    Use is deprecated and load_measurement should be used.
    """

    matrix = np.genfromtxt(filename, delimiter=",")
    freq = matrix[:, 0]
    # amp = 10 ** (matrix[:, 1] / 10)
    amp = matrix[:, 1]
    #phase = matrix[:, 2] * np.pi / 180
    phase = matrix[:, 2]

    return freq, amp, phase


def save_metadata(settings: object) -> None:
    user_folder = settings["user_name"]
    sample_name = settings["sample_name"]
    filename = settings["measurement_name"]

    # Save metadata:
    # settings["field_sweep"] = list(field_sweep.astype(float))  # updates field sweep with reference measurement, astype converts to float to avoid issues with int32 json formatting
    # settings["number_of_points"] = np.round(settings["number_of_points"])

    with open(f'DATA/{user_folder}/{sample_name}/{filename}/measurement_info.json', 'w') as f:
        json.dump(settings, f, indent=4)


def load_metadata(user_folder: str, sample_folder: str, measurement_name: str) -> object:
    """
    Loads the metadata file for a measurement.
    """

    with open(f"DATA/{user_folder}/{sample_folder}/{measurement_name}/measurement_info.json", "r") as f:
        metadata = json.load(f)
    return metadata


def load_measurement(user_folder: str, sample_folder: str, folder_name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Reads data from txt file assuming 3 columns: frequency, amplitude, phase.
    Takes filename as input and returns relevant data.
    Information about the measurement is given by the metadata.
    """

    with open(f"DATA/{user_folder}/{sample_folder}/{folder_name}/measurement_info.json", "r") as f:
        metadata = json.load(f)
    field_sweep = metadata["field_sweep"]
    measurement_name = metadata["measurement_name"]
    amps = []
    phases = []

    for i in range(len(field_sweep)):
        file = f"DATA/{user_folder}/{sample_folder}/{folder_name}/{measurement_name} ({i+1}).csv"
        f,a,p = load_and_convert(file)
        amps.append(a)
        phases.append(p)
    
    return np.array(f), np.array(field_sweep), np.array(amps), np.array(phases)


def sendWarning(s: str):
    # Function used for user interface
    print("WARNING: " + s)

def sendError(s: str):
    # Function used for user interface
    print("ERROR: " + s)

def sendLog(s: str):  
    # Function used for user interface
    print("LOG: " + s)



def update_log(settings: object):
    with open("log.txt", "r") as f:
        text = f.read()

    new_text = f"""
    Date-time: {settings["datetime"]}
    User: {settings["user_name"]}
    File name: {settings["measurement_name"]}
    Description: {settings["description"]}


    """

    file_content = text + new_text
    with open("log.txt", "w") as f:
        f.write(file_content)


    