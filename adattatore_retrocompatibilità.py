def replace_in_file(file_path):
    try:
        # Open the file for reading
        with open(file_path, 'r') as file:
            file_data = file.read()

        # Perform replacements
        file_data = file_data.replace("name", "measurement_name")
        file_data = file_data.replace("user", "user_name")
        file_data = file_data.replace("dipole mode", "dipole_mode")
        file_data = file_data.replace("S parameter", "s_parameter")
        file_data = file_data.replace("field sweep", "field_sweep")
        file_data = file_data.replace("Angle", "angle")
        file_data = file_data.replace("Start frequency", "start_frequency")
        file_data = file_data.replace("Stop frequency", "stop_frequency")
        file_data = file_data.replace("Number of points", "number_of_points")
        file_data = file_data.replace("Bandwith", "bandwith")
        file_data = file_data.replace("Power", "power")

        # Open the file for writing
        with open(file_path, 'w') as file:
            file.write(file_data)

        print("Replacements successfully made in the file.")

    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")

# Example usage:
file_path = input("Enter the path of the text file: ")
replace_in_file(file_path)