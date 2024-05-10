import os
import json
from dataclasses import dataclass
from icecream import ic
import numpy as np
import pandas as pd

root_directory = "local\DATA - Test new format"

print("\n"*5)
if input(f"Are you sure tou want to execute this script on the folder '{root_directory}'? [y/n]\n> ") != "y":
    raise Exception("Script was not executed")

# ------

def find_final_subdirectories(root_dir: str) -> list[str]:
    final_subdirectories = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:  # If there are no subdirectories
            # jsonpath = os.path.join(dirpath, "measurement_info.json")
            # final_subdirectories.append((jsonpath, os.path.exists(jsonpath)))
            final_subdirectories.append(dirpath)
    return final_subdirectories


def correct_format(text: str) -> str:
    text = text.replace("user name", "user_name")
    return text

# -----------------




# ==========================
# Step 1: commentare il codice sotto questo step e controllare che il codice legge correttamente tutte le misure
# ==========================

meas_paths = find_final_subdirectories(root_directory)

flag = True
for i, path in enumerate(meas_paths):
   
    try:
        with open(os.path.join(path, "measurement_info.json"), "r") as f:
            metadata = json.load(f)

        field_sweep = metadata["field_sweep"]

    except FileNotFoundError:
        print(f"=== {path} does not have metadata\n")
        flag = False
        continue

    except KeyError:
        print(f"=== {path} has no field sweep\n")
        flag = False
        continue

    except json.JSONDecodeError:
        print(f"=== {path} is not a valid json\n")
        flag = False
        continue


    meas = path.split("\\")[-1]
    n_fields = len(field_sweep)

    files_old = list(filter(lambda x : ".csv" in x, os.listdir(path)))
    try:
        files_old.remove(f"{meas}.csv")
    except:
        pass
    files = [files_old[0].replace("(1)", f"({k+1})") for k in range(n_fields)]

    files_path = [os.path.join(path, file) for file in files]

    for f_path in files_path:
        if not(os.path.exists(f_path)):
            print(f"=== {f_path} does not exist\n")


# # ==========================
# # Step 2: scommentare il codice e rigirare tutto
# # ==========================

       
#     csvs = []
#     for j, file_path in enumerate(files_path):

#         # if i==0:
#         #     print(file_path)

#         with open(file_path, "r") as f:
#             csvs.append(pd.read_csv(f))
       
#         csvs[j].columns=["Frequency", "Amplitude", "Phase"]
#         csvs[j].insert(loc=1, column="Field", value=field_sweep[j])
   

#     final_csv = pd.concat(csvs)

#     final_csv.to_csv(os.path.join(path, f"{meas}.csv"), index=False)

#     for j, file_path in enumerate(files_path):
#         # ic(file_path)
#         os.remove(file_path)


    # # --- Moves png in plots folder

    # plots = list(filter(lambda x : ".png" in x, os.listdir(path)))
    # if len(plots) == 0:
    #     continue

    # os.mkdir(os.path.join(path, "Plots"))

    # plot_paths = [os.path.join(path, plot) for plot in plots]

    # for plot, plot_path in zip(plots, plot_paths):
    #     # ic(plot_path, os.path.join(path, "Plots", plot))
    #     os.rename(plot_path, os.path.join(path, "Plots", plot))
    
