import os
import numpy as np
import json
import pandas as pd
# from icecream import ic
from matplotlib import pyplot as plt

from logger import logger
import CONSTANTS as c

def create_measurement_path(settings):
    return os.path.join(c.DATA_FOLDER_NAME, settings["user_name"], settings["sample_name"], settings["measurement_name"])

    

def save_data(Ports: str, currents: list[float], currents1: list[float], currents2: list[float], freqs: list[float], fields: list[float], S1, S2, S3, S4, user_folder: str, sample_folder: str, measurement_name: str):
    """
    Saves data in as {root_folder}/{user_folder}/{sample_folder}/{measurement_name} {suffix}", checks if existing measurements exist already and adds a suffix
    """

    df = pd.DataFrame()
    df["Frequency"] = freqs
    df["Field"] = fields
    df["Current (dipole mode)"] = currents
    df["Current1 (quadrupole mode)"] = currents1
    df["Current2 (quadrupole mode)"] = currents2

    if (Ports == '12'):
        df["S11"] = S1
        df["S21"] = S2
        df["S12"] = S3
        df["S22"] = S4

    if (Ports == '13'):
        df["S11"] = S1
        df["S31"] = S2
        df["S13"] = S3
        df["S33"] = S4

    if (Ports == '14'):
        df["S11"] = S1
        df["S41"] = S2
        df["S14"] = S3
        df["S44"] = S4

    if (Ports == '23'):
        df["S22"] = S1
        df["S32"] = S2
        df["S23"] = S3
        df["S33"] = S4

    if (Ports == '24'):
        df["S22"] = S1
        df["S42"] = S2
        df["S24"] = S3
        df["S44"] = S4

    if (Ports == '34'):
        df["S33"] = S1
        df["S43"] = S2
        df["S34"] = S3
        df["S44"] = S4

    root_folder = f"{c.DATA_FOLDER_NAME}/"
    initialname = measurement_name
    format = ".csv"

    if not(os.path.exists( f"{root_folder}/{user_folder}" )):   # Create user folder if it does not exist
        os.mkdir(f"{root_folder}/{user_folder}")

    if not(os.path.exists( f"{root_folder}/{user_folder}/{sample_folder}" )):   # Create sample folder if it does not exist
        os.mkdir(f"{root_folder}/{user_folder}/{sample_folder}")

    if os.path.exists( f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}" ):
        #raise Exception("ERROR in saveData(): A measurement for this sample with this name already exist.")
        #print('This filename already exists')
        print('\n')
    else:
        os.mkdir(f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}")


    df.to_csv(f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}/{measurement_name}{format}", sep=',', index=False)



def load_measurement(measurement_path: str, Ports: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Reads data from txt file assuming 3 columns: frequency, amplitude, phase.
    Takes filename as input and returns relevant data.
    Information about the measurement is given by the metadata.
    """

    with open(os.path.join(measurement_path, "measurement_info.json"), "r") as f:
        metadata = json.load(f)

    fields = np.array(metadata["field_sweep"])
    n_field_points = len(fields)
    n_freq_points = metadata["number_of_points"]
    measurement_name = metadata["measurement_name"]

    df = pd.read_csv(os.path.join(measurement_path, f"{measurement_name}.csv"))
    freqs = (df.loc[ df["Field"] == fields[0] ])["Frequency"]

    S1 = np.zeros((n_field_points, n_freq_points), dtype = 'complex')
    amp1 = np.zeros((n_field_points, n_freq_points))
    phases1 = np.zeros((n_field_points, n_freq_points))

    S2 = np.zeros((n_field_points, n_freq_points), dtype = 'complex')
    amp2 = np.zeros((n_field_points, n_freq_points))
    phases2 = np.zeros((n_field_points, n_freq_points))

    S3 = np.zeros((n_field_points, n_freq_points), dtype = 'complex')
    amp3 = np.zeros((n_field_points, n_freq_points))
    phases3 = np.zeros((n_field_points, n_freq_points))

    S4 = np.zeros((n_field_points, n_freq_points), dtype = 'complex')
    amp4 = np.zeros((n_field_points, n_freq_points))
    phases4 = np.zeros((n_field_points, n_freq_points))
    
    for i, field in enumerate(fields):
        if (Ports == '12'):
            a = (df.loc[ df["Field"] == field ])["S11"]
            b = (df.loc[ df["Field"] == field ])["S21"]
            c = (df.loc[ df["Field"] == field ])["S12"]
            d = (df.loc[ df["Field"] == field ])["S22"]

        if (Ports == '13'):
            a = (df.loc[ df["Field"] == field ])["S11"]
            b = (df.loc[ df["Field"] == field ])["S31"]
            c = (df.loc[ df["Field"] == field ])["S13"]
            d = (df.loc[ df["Field"] == field ])["S33"]

        if (Ports == '14'):
            a = (df.loc[ df["Field"] == field ])["S11"]
            b = (df.loc[ df["Field"] == field ])["S41"]
            c = (df.loc[ df["Field"] == field ])["S14"]
            d = (df.loc[ df["Field"] == field ])["S44"]

        if (Ports == '23'):
            a = (df.loc[ df["Field"] == field ])["S22"]
            b = (df.loc[ df["Field"] == field ])["S32"]
            c = (df.loc[ df["Field"] == field ])["S23"]
            d = (df.loc[ df["Field"] == field ])["S33"]

        if (Ports == '24'):
            a = (df.loc[ df["Field"] == field ])["S22"]
            b = (df.loc[ df["Field"] == field ])["S42"]
            c = (df.loc[ df["Field"] == field ])["S24"]
            d = (df.loc[ df["Field"] == field ])["S44"]

        if (Ports == '34'):
            a = (df.loc[ df["Field"] == field ])["S33"]
            b = (df.loc[ df["Field"] == field ])["S43"]
            c = (df.loc[ df["Field"] == field ])["S34"]
            d = (df.loc[ df["Field"] == field ])["S44"]


        # Convert the Series of complex number strings into actual complex numbers
        complex_series = a.apply(lambda x: complex(x.strip()))
        complex_series = b.apply(lambda x: complex(x.strip()))
        complex_series = c.apply(lambda x: complex(x.strip()))
        complex_series = d.apply(lambda x: complex(x.strip()))

        # Convert the Pandas Series into a NumPy array
        S1[i,:] = np.array(complex_series, dtype = 'complex')
        amp1[i,:] = np.abs(S1[i,:])
        phases1[i,:] = np.angle(S1[i,:])

        S2[i,:] = np.array(complex_series, dtype = 'complex')
        amp2[i,:] = np.abs(S2[i,:])
        phases2[i,:] = np.angle(S2[i,:])

        S3[i,:] = np.array(complex_series, dtype = 'complex')
        amp3[i,:] = np.abs(S3[i,:])
        phases3[i,:] = np.angle(S3[i,:])

        S4[i,:] = np.array(complex_series, dtype = 'complex')
        amp4[i,:] = np.abs(S4[i,:])
        phases4[i,:] = np.angle(S4[i,:])


    return freqs, fields, amp1, phases1, amp2, phases2, amp3, phases3, amp4, phases4



def save_metadata(settings: object) -> None:
    user_folder = settings["user_name"]
    sample_name = settings["sample_name"]
    filename = settings["measurement_name"]

    temp = settings.pop("field_sweep")    
    settings["field_sweep"] = temp  # puts the field sweep at the end of the json for readability

    measurement_path = create_measurement_path(settings)
    with open(os.path.join(measurement_path, "measurement_info.json"), 'w') as f:
        json.dump(settings, f, indent=4)



# def load_metadata(user_folder: str, sample_folder: str, measurement_name: str) -> object:
def load_metadata(measurement_path: str) -> object:
    """
    Loads the metadata file for a measurement.
    """

    with open(os.path.join(measurement_path, "measurement_info.json"), "r") as f:
        metadata = json.load(f)
    return metadata



def save_settings(settings):    
    """
    Save the current settings to a file.
    """
    settings_file = os.path.join(os.path.dirname(__file__), "last_settings.json")
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)



def save_plot(path: str, name: str):
    folder_path = os.path.join(path, "Plots")
    if not(os.path.exists(folder_path)):
        os.mkdir(folder_path)
    plt.savefig(os.path.join(folder_path, name))












