# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import re
import pandas as pd


def extract_class_features(file_name):
    # Read the text file
    with open(file_name, 'r') as file:
        data = file.read()

    # Initialize lists to store extracted information
    class_names = []
    feature_keys = []
    descriptions = []
    levels = []

    feature_key = None
    description = ""
    level = ""

    # Regular expressions to match relevant lines
    block_pattern = r'(?i)###Block: (.+) Class features'

    # Find all class feature blocks
    class_blocks = re.finditer(block_pattern, data)

    # Iterate through class feature blocks and extract information
    for match in class_blocks:
        class_name = match.group(1)
        block_start = match.start()
        next_block_match = re.search(r'\n\s*\n', data[block_start + len(class_name):])
        block_end = next_block_match.start() if next_block_match else None
        class_data = data[block_start:block_start + block_end] if block_end else data[block_start:]

        feature_lines = class_data.split('\n')

        for line in feature_lines:
            line = line.strip()
            # if line.startswith("###"):
                # Start of a new class feature block, save the extracted information
                # if feature_key:
                #     class_names.append(class_name.strip())
                #     feature_keys.append(feature_key.strip())
                #     descriptions.append(description.strip())
                #     levels.append(level)
                # Reset the variables for the next class feature
                # feature_key = None
                # description = ""
                # level = ""
            # else:

            # Split the line based on tab character or line end
            parts = line.split("\t")
            for part in parts:
                if part.startswith("KEY:"):
                    feature_key = part.split("KEY:")[1]
                elif part.startswith("DESC:"):
                    description = part.split("DESC:")[1]
                    # Extract the level from the description if present
                    for i in range(0, 3):
                        if i == 0:
                            level_match = re.search(r'(?i)At (\d+)s?t? level', description)
                            if level_match:
                                level = level_match.group(1)
                                break
                        if i == 1:
                            level_match = re.search(r'(?i)At (\d+)n?d? level', description)
                            if level_match:
                                level = level_match.group(1)
                                break
                        if i == 2:
                            level_match = re.search(r'(?i)At (\d+)r?d? level', description)
                            if level_match:
                                level = level_match.group(1)
                                break
                        if i == 3:
                            level_match = re.search(r'(?i)At (\d+)t?h? level', description)
                            if level_match:
                                level = level_match.group(1)
                                break

            if feature_key and description:
                class_names.append(class_name.strip())
                feature_keys.append(feature_key.strip())
                descriptions.append(description.strip())
                levels.append(level)

                # Reset the variables for the next class feature
                feature_key = None
                description = ""
                level = ""

    # Create a DataFrame
    data_dict = {
        'Class': class_names,
        'Feature Key': feature_keys,
        'Description': descriptions,
        'Level Learned': levels
    }
    df = pd.DataFrame(data_dict)

    # Save the DataFrame to an Excel file
    df.to_excel('class_features.xlsx')

def extract_archetype_info(file_path):
    archetypes = {}
    archetype_name = None
    archetype_parent_class_name = None

    new_archetype_potentially_starting = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()

            # Here we see that a new archetype is potentially starting, set flag accordingly.
            if line.startswith("# =============================="):
                new_archetype_potentially_starting = 1
                continue

            if new_archetype_potentially_starting:
                class_header_match = re.match(r'# (.+) Archetypes', line)
                if class_header_match:
                    new_archetype_potentially_starting = 0
                    archetype_name = class_header_match.group(1)
                    continue

            if not archetype_name:
                continue

            if re.search(r'(?i)CATEGORY:Special Ability', line) and re.search(r'(?i)TYPE:(.+) Class Feature\.(.+) Class Feature\.SpecialQuality', line):
                # Capture the archetype name between "TYPE:" and " Class"
                type_match = re.search(r'TYPE:(.*?) Class', line)
                if type_match:
                    archetype_name = type_match.group(1)

                # Capture the parent class name between "Class Feature." and " Class"
                class_feature_match = re.search(r'Class Feature\.(.*?) Class', line)
                if class_feature_match:
                    archetype_parent_class_name = class_feature_match.group(1)

                class_feature_name = re.search(r'~\t*([^\t]*)', line).group(1).strip()
                class_feature_description = re.search(r'DESC:(.+)', line)
                if class_feature_description:
                    # Todo: This level isn't correct and is not resetting to 0 when we are unable to find a match.
                    level_match = None
                    for i in range(0, 3):
                        if i == 0:
                            level_match = re.search(r'(?i)At (\d+)s?t? level', class_feature_description[0])
                            if level_match:
                                break
                        if i == 1:
                            level_match = re.search(r'(?i)At (\d+)n?d? level', class_feature_description[0])
                            if level_match:
                                break
                        if i == 2:
                            level_match = re.search(r'(?i)At (\d+)r?d? level', class_feature_description[0])
                            if level_match:
                                break
                        if i == 3:
                            level_match = re.search(r'(?i)At (\d+)t?h? level', class_feature_description[0])
                            if level_match:
                                break
                    if level_match:
                        class_feature_level = level_match.group(1)

                if class_feature_name:
                    class_feature_info = {
                        'Name': class_feature_name,
                        'Parent Class': archetype_parent_class_name,
                        'Archetype': archetype_name,
                        'Description': class_feature_description.group(1) if class_feature_description else '',
                        'Level': class_feature_level if class_feature_level else ''
                    }

                # Making sure the array doesn't get an exception by filling it with keys if they are not present.
                if archetype_parent_class_name not in archetypes:
                    archetypes[archetype_parent_class_name] = {}
                if archetype_name not in archetypes[archetype_parent_class_name]:
                    archetypes[archetype_parent_class_name][archetype_name] = []

                #Appending the actual data.
                archetypes[archetype_parent_class_name][archetype_name].append(class_feature_info)

    return archetypes


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_path = 'C:\\Users\Bram\\PycharmProjects\\ClassFeatureExtractor\\raw.githubusercontent.com_PCGen_pcgen_master_data_pathfinder_paizo_roleplaying_game_advanced_class_guide_acg_abilities_class.lst'
    extract_class_features(file_path)
    extract_archetype_info(file_path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
