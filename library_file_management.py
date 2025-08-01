import os
import numpy as np
import json
import pandas as pd
from matplotlib import pyplot as plt

from logger import logger # Custom logging module
import CONSTANTS as c # Assuming CONSTANTS file defines paths, names, etc.

def create_measurement_path(settings):

    """
    Creates the path where measurement data will be stored, based on user, sample, and measurement names.
    """

    return os.path.join(c.DATA_FOLDER_NAME, settings["user_name"], settings["sample_name"], settings["measurement_name"])

    

def save_data(Ports: str, currents: list[float], currents1: list[float], currents2: list[float], freqs: list[float], fields: list[float], re1, im1, re2, im2, re3, im3, re4, im4, user_folder: str, sample_folder: str, measurement_name: str):
    """
    Saves measurement data to a CSV file. The file is saved under {root_folder}/{user_folder}/{sample_folder}/{measurement_name} with suffix handling if file already exists.
    """
    
    # Prepare the DataFrame with measurement data
    df = pd.DataFrame()
    df["Frequency"] = freqs
    df["Field"] = fields
    df["Current (dipole mode)"] = currents
    df["Current1 (quadrupole mode)"] = currents1
    df["Current2 (quadrupole mode)"] = currents2


    # Add the S-parameters based on the Ports value
    if (Ports == '12'):
        df["Re(S11)"] = re1
        df["Im(S11)"] = im1
        df["Re(S21)"] = re2
        df["Im(S21)"] = im2
        df["Re(S12)"] = re3
        df["Im(S12)"] = im3
        df["Re(S22)"] = re4
        df["Im(S22)"] = im4

    if (Ports == '13'):
        df["Re(S11)"] = re1
        df["Im(S11)"] = im1
        df["Re(S31)"] = re2
        df["Im(S31)"] = im2
        df["Re(S13)"] = re3
        df["Im(S13)"] = im3
        df["Re(S33)"] = re4
        df["Im(S33)"] = im4

    if (Ports == '14'):
        df["Re(S11)"] = re1
        df["Im(S11)"] = im1
        df["Re(S41)"] = re2
        df["Im(S41)"] = im2
        df["Re(S14)"] = re3
        df["Im(S14)"] = im3
        df["Re(S44)"] = re4
        df["Im(S44)"] = im4

    if (Ports == '23'):
        df["Re(S22)"] = re1
        df["Im(S22)"] = im1
        df["Re(S32)"] = re2
        df["Im(S32)"] = im2
        df["Re(S23)"] = re3
        df["Im(S23)"] = im3
        df["Re(S33)"] = re4
        df["Im(S33)"] = im4

    if (Ports == '24'):
        df["Re(S22)"] = re1
        df["Im(S22)"] = im1
        df["Re(S42)"] = re2
        df["Im(S42)"] = im2
        df["Re(S24)"] = re3
        df["Im(S24)"] = im3
        df["Re(S44)"] = re4
        df["Im(S44)"] = im4

    if (Ports == '34'):
        df["Re(S33)"] = re1
        df["Im(S33)"] = im1
        df["Re(S43)"] = re2
        df["Im(S43)"] = im2
        df["Re(S34)"] = re3
        df["Im(S34)"] = im3
        df["Re(S44)"] = re4
        df["Im(S44)"] = im4


    # Root directory path where the data will be saved
    root_folder = f"{c.DATA_FOLDER_NAME}/"
    initialname = measurement_name
    format = ".csv"

    # Create folders if they don't exist
    if not(os.path.exists( f"{root_folder}/{user_folder}" )):   # Create user folder if it does not exist
        os.mkdir(f"{root_folder}/{user_folder}")

    if not(os.path.exists( f"{root_folder}/{user_folder}/{sample_folder}" )):   # Create sample folder if it does not exist
        os.mkdir(f"{root_folder}/{user_folder}/{sample_folder}")


    # Check if the measurement already exists (it was used to add a suffix if that was the case, but this is no longer done, this will be deprecated in the future version of the code)
    if os.path.exists( f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}" ):
        print('\n')
    else:
        os.mkdir(f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}")

    # Save the DataFrame to a CSV 
    df.to_csv(f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}/{measurement_name}{format}", sep=',', index=False)



def load_measurement(measurement_path: str, Ports: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Reads and loads measurement data from the corresponding CSV file. Extracts frequency, amplitude, and phase information.
    Returns relevant measurement data such as frequency, field sweep, and S-parameters amplitudes and phase.
    """

    # Load metadata (e.g., field sweep, number of frequency points, etc.)
    with open(os.path.join(measurement_path, "measurement_info.json"), "r") as f:
        metadata = json.load(f)


    # Initializations
    fields = np.array(metadata["field_sweep"]) # Field sweep data
    n_field_points = len(fields)
    n_freq_points = metadata["number_of_points"] # Number of frequency points in the measurement
    measurement_name = metadata["measurement_name"]

    # Read the measurement data from CSV file
    df = pd.read_csv(os.path.join(measurement_path, f"{measurement_name}.csv"))
    freqs = (df.loc[ df["Field"] == fields[0] ])["Frequency"]

    # Initialize arrays to store complex S-parameters and their amplitudes/phases
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
    

    # Loop over field points and populate real and imaginary parts of the S-parameters associated with the ports used
    for i, field in enumerate(fields):
        if (Ports == '12'):
            re_a = (df.loc[ df["Field"] == field ])["Re(S11)"]
            im_a = (df.loc[ df["Field"] == field ])["Im(S11)"]
            re_b = (df.loc[ df["Field"] == field ])["Re(S21)"]
            im_b = (df.loc[ df["Field"] == field ])["Im(S21)"]
            re_c = (df.loc[ df["Field"] == field ])["Re(S12)"]
            im_c = (df.loc[ df["Field"] == field ])["Im(S12)"]
            re_d = (df.loc[ df["Field"] == field ])["Re(S22)"]
            im_d = (df.loc[ df["Field"] == field ])["Im(S22)"]

        if (Ports == '13'):
            re_a = (df.loc[ df["Field"] == field ])["Re(S11)"]
            im_a = (df.loc[ df["Field"] == field ])["Im(S11)"]
            re_b = (df.loc[ df["Field"] == field ])["Re(S31)"]
            im_b = (df.loc[ df["Field"] == field ])["Im(S31)"]
            re_c = (df.loc[ df["Field"] == field ])["Re(S13)"]
            im_c = (df.loc[ df["Field"] == field ])["Im(S13)"]
            re_d = (df.loc[ df["Field"] == field ])["Re(S33)"]
            im_d = (df.loc[ df["Field"] == field ])["Im(S33)"]

        if (Ports == '14'):
            re_a = (df.loc[ df["Field"] == field ])["Re(S11)"]
            im_a = (df.loc[ df["Field"] == field ])["Im(S11)"]
            re_b = (df.loc[ df["Field"] == field ])["Re(S41)"]
            im_b = (df.loc[ df["Field"] == field ])["Im(S41)"]
            re_c = (df.loc[ df["Field"] == field ])["Re(S14)"]
            im_c = (df.loc[ df["Field"] == field ])["Im(S14)"]
            re_d = (df.loc[ df["Field"] == field ])["Re(S44)"]
            im_d = (df.loc[ df["Field"] == field ])["Im(S44)"]

        if (Ports == '23'):
            re_a = (df.loc[ df["Field"] == field ])["Re(S22)"]
            im_a = (df.loc[ df["Field"] == field ])["Im(S22)"]
            re_b = (df.loc[ df["Field"] == field ])["Re(S32)"]
            im_b = (df.loc[ df["Field"] == field ])["Im(S32)"]
            re_c = (df.loc[ df["Field"] == field ])["Re(S23)"]
            im_c = (df.loc[ df["Field"] == field ])["Im(S23)"]
            re_d = (df.loc[ df["Field"] == field ])["Re(S33)"]
            im_d = (df.loc[ df["Field"] == field ])["Im(S33)"]

        if (Ports == '24'):
            re_a = (df.loc[ df["Field"] == field ])["Re(S22)"]
            im_a = (df.loc[ df["Field"] == field ])["Im(S22)"]
            re_b = (df.loc[ df["Field"] == field ])["Re(S42)"]
            im_b = (df.loc[ df["Field"] == field ])["Im(S42)"]
            re_c = (df.loc[ df["Field"] == field ])["Re(S24)"]
            im_c = (df.loc[ df["Field"] == field ])["Im(S24)"]
            re_d = (df.loc[ df["Field"] == field ])["Re(S44)"]
            im_d = (df.loc[ df["Field"] == field ])["Im(S44)"]

        if (Ports == '34'):
            re_a = (df.loc[ df["Field"] == field ])["Re(S33)"]
            im_a = (df.loc[ df["Field"] == field ])["Im(S33)"]
            re_b = (df.loc[ df["Field"] == field ])["Re(S43)"]
            im_b = (df.loc[ df["Field"] == field ])["Im(S43)"]
            re_c = (df.loc[ df["Field"] == field ])["Re(S34)"]
            im_c = (df.loc[ df["Field"] == field ])["Im(S34)"]
            re_d = (df.loc[ df["Field"] == field ])["Re(S44)"]
            im_d = (df.loc[ df["Field"] == field ])["Im(S44)"]


        # Convert to complex S-parameters and store the amplitudes and phases data
        S1[i,:] = np.array(re_a+1j*im_a, dtype = 'complex')
        amp1[i,:] = np.abs(S1[i,:])
        phases1[i,:] = np.angle(S1[i,:])

        S2[i,:] = np.array(re_b+1j*im_b, dtype = 'complex')
        amp2[i,:] = np.abs(S2[i,:])
        phases2[i,:] = np.angle(S2[i,:])

        S3[i,:] = np.array(re_c+1j*im_c, dtype = 'complex')
        amp3[i,:] = np.abs(S3[i,:])
        phases3[i,:] = np.angle(S3[i,:])

        S4[i,:] = np.array(re_d+1j*im_d, dtype = 'complex')
        amp4[i,:] = np.abs(S4[i,:])
        phases4[i,:] = np.angle(S4[i,:])


    return freqs, fields, amp1, phases1, amp2, phases2, amp3, phases3, amp4, phases4



def save_metadata(settings: object) -> None:
    """
    Saves metadata settings to a JSON file. This includes measurement info and configuration.
    """

    user_folder = settings["user_name"]
    sample_name = settings["sample_name"]
    filename = settings["measurement_name"]

    # Move the field_sweep key to the end for better readability
    temp = settings.pop("field_sweep")    
    settings["field_sweep"] = temp  # puts the field sweep at the end of the json for readability

    measurement_path = create_measurement_path(settings)
    with open(os.path.join(measurement_path, "measurement_info.json"), 'w') as f:
        json.dump(settings, f, indent=4)



def load_metadata(measurement_path: str) -> object:
    """
    Loads and returns the metadata for a given measurement.
    """

    with open(os.path.join(measurement_path, "measurement_info.json"), "r") as f:
        metadata = json.load(f)
    return metadata



def save_settings(settings):    
    """
    Save the current settings to a 'last_settings.json' file for future reference.
    """
    settings_file = os.path.join(os.path.dirname(__file__), "last_settings.json")
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)



def save_plot(path: str, name: str):
    """
    Saves the plot generated by matplotlib in a 'Plots' folder inside the specified path.
    Creates the 'Plots' folder if it does not exist.
    """

    folder_path = os.path.join(path, "Plots")
    if not(os.path.exists(folder_path)):
        os.mkdir(folder_path)
    plt.savefig(os.path.join(folder_path, name))












