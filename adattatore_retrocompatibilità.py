import os
import json
from icecream import ic
from CONSTANTS import *


def find_all_measurements(root_dir: str) -> list[str]:
    final_subdirectories = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:  # If there are no subdirectories
            jsonpath = os.path.join(dirpath, "measurement_info.json")
            final_subdirectories.append((jsonpath, os.path.exists(jsonpath)))
    return final_subdirectories


def correct_format(text: str) -> str:
    # Perform replacements
    text = text.replace("name", "measurement_name")
    text = text.replace("user", "user_name")
    text = text.replace("dipole mode", "dipole_mode")
    text = text.replace("S parameter", "s_parameter")
    text = text.replace("field sweep", "field_sweep")
    text = text.replace("Angle", "angle")
    text = text.replace("Start frequency", "start_frequency")
    text = text.replace("Stop frequency", "stop_frequency")
    text = text.replace("Number of points", "number_of_points")
    text = text.replace("Bandwith", "bandwith")
    text = text.replace("Power", "power")
    return text


root_directory = DATA_FOLDER_NAME
json_files = find_all_measurements(root_directory)

for i, file in enumerate(json_files):
    print(f"{i:3}) {str(file[1]).upper():5} {file[0]}")

for json_file in json_files:
    if json_file[1]:
        with open(json_file[0], "r") as f:
            content = f.read()
        new_content = correct_format(content)

    else:
        new_content = "{}"

    with open(json_file[0], "w") as f:
        f.write(new_content)