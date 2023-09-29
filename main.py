# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import re
import pandas as pd


def extract_class_features(file_name, output_file_name, source_book_name):
    # Read the text file
    with open(file_name, 'r') as file:
        data = file.read()

    # Initialize lists to store extracted information
    class_names = []
    feature_keys = []
    descriptions = []
    levels = []
    sources = []

    feature_key = None
    description = ""
    level = 0

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

            # Split the line based on tab character or line end
            parts = line.split("\t")
            for part in parts:
                if part.startswith("KEY:"):
                    feature_key = part.split("KEY:")[1]
                    feature_key = re.search(r'~(.+)', feature_key).group(1).strip()
                elif part.startswith("DESC:"):
                    description = part.split("DESC:")[1]
                    # Extract the level from the description if present
                    for i in range(0, 4):
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
                elif part.startswith("PREVARGTEQ:"):
                    # Get ability level
                    ability_power_level_match = re.search(r'(?i)(.*?)LVL,(\d{0,2})', part.split("PREVARGTEQ:")[1])
                    if ability_power_level_match:
                        level = ability_power_level_match.group(2)

            if feature_key and description:
                class_names.append(class_name.strip())
                feature_keys.append(feature_key.strip())
                descriptions.append(description.strip())
                levels.append(level)
                sources.append(source_book_name)

                # Reset the variables for the next class feature
                feature_key = None
                description = ""
                level = 0

    # Create a DataFrame
    data_dict = {
        'Class': class_names,
        'Sub Feature Of': '',
        'Class Feature': feature_keys,
        'Description': descriptions,
        'Level': levels,
        'Source': sources
    }
    df = pd.DataFrame(data_dict)

    # Save the DataFrame to an Excel file
    df.to_excel(output_file_name)

def extract_class_features_cr(file_name, output_file_name, source_book_name):
    class_features = {}
    class_name = None
    class_feature_name = None
    sub_feature_name = None
    class_feature_description = None
    class_feature_level = None

    is_valid_class_feature = 1

    # Regular expressions to match relevant lines
    block_pattern = r'(?i)###Block: (.+) Class features'

    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            is_valid_class_feature = 1
            line = line.strip()

            class_header_match = re.match(block_pattern, line)
            if class_header_match:
                class_name = class_header_match.group(1)
                continue

            # Split the line based on tab character or line end
            parts = line.split("\t")
            for part in parts:
                if is_valid_class_feature:
                    if part.startswith("KEY:"):
                        feature_key = part.split("KEY:")[1]
                        class_name_key = re.search(r'(.+)~', feature_key)
                        if class_name_key and len(class_name_key.groups()) > 0:
                            class_name = class_name_key.group(1).strip()
                        class_feature_key = re.search(r'~(.+)', feature_key)
                        if class_feature_key and len(class_feature_key.groups()) > 0:
                            class_feature_name = class_feature_key.group(1).strip()
                    elif part.startswith("CATEGORY:"):
                        if not part.split("CATEGORY:")[1] == "Special Ability":
                            is_valid_class_feature = 0
                    elif part.startswith("TYPE:"):
                        class_feature_type = part.split("TYPE:")[1]
                        # TYPE:{Classname}ClassFeatures.(SpecialQuality/SpecialAttack)
                        if re.search(r'(?i)SpecialQuality\.SuperNatural\.DomainPower', class_feature_type) or re.search(r'(?i)SpecialAttack\.SpellLike\.DomainPower', class_feature_type):
                            # Dealing with cleric domain power, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Cleric"
                        elif re.search(r'(?i)(.+)ClassFeatures\.SpecialAttack.Supernatural.BardicPerformance(.+)', class_feature_type) or re.search(r'(?i)(.+)ClassFeatures\.SpecialQuality.Supernatural.BardicPerformance(.+)', class_feature_type) or re.search(r'(?i)(.+)ClassFeatures\.SpecialAttack.Extraordinary.VersatilePerformance(.+)', class_feature_type):
                            # Dealing with bardic/versatile performance, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Bard"
                        elif re.search(r'(?i)(.+)ClassFeatures\.SpecialAttack(.+)', class_feature_type) or re.search(r'(?i)(.+)ClassFeatures\.SpecialQuality(.+)', class_feature_type):
                            # Dealing with different formatting of class features
                            type_match = re.search(r'(?i)ClassFeatures\.(.+)ClassFeatures\.Special(.+)', class_feature_type)
                            if type_match:
                                if class_name and class_name != type_match.group(1):
                                    # Class name was already set and differs from picked up key. Set key as sub_feature_name
                                    sub_feature_name = class_name
                                class_name = type_match.group(1)
                            else:
                                # Capture the parent class name between "ClassFeatures." and " ClassFeatures"
                                type_match = re.search(r'(?i)(.+)ClassFeatures\.Special', class_feature_type)
                                if type_match:
                                    if class_name and class_name != type_match.group(1):
                                        # Class name was already set and differs from picked up key. Set key as sub_feature_name
                                        sub_feature_name = class_name
                                    class_name = type_match.group(1)
                        elif re.search(r'(?i)(.+)ClassFeatures\.RagePower(.+)', class_feature_type):
                            # Dealing with a barbarian rage power, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Barbarian"
                        elif re.search(r'(?i)Class Feature\.Sorcerer Class Feature\.(.+) ~ Power LVL (.+).Sorcerer', class_feature_type):
                            # Dealing with wizard school, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Sorcerer"
                            # Capture the bloodline level
                            bloodline_ability_level_match = re.search(r'~ Power LVL (.+).Sorcerer', class_feature_type)
                            if bloodline_ability_level_match:
                                class_feature_level = bloodline_ability_level_match.group(1)
                        elif re.search(r'(?i)WizardClassFeatures\.SpecialQuality\.SuperNatural', class_feature_type) or re.search(r'(?i)WizardClassFeatures\.SpecialQuality\.SpellLike', class_feature_type):
                            # Dealing with sorcerer bloodline, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Wizard"
                        else:
                            is_valid_class_feature = 0
                    elif part.startswith("DESC:"):
                        description_match = part.split("DESC:")[1]
                        if description_match:
                            if not class_feature_description:
                                class_feature_description = ""
                            class_feature_description += description_match
                            if not class_feature_level:
                                # Extract the level from the description if present
                                for i in range(0, 4):
                                    if i == 0:
                                        level_match = re.search(r'(?i)At (\d+)s?t? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 1:
                                        level_match = re.search(r'(?i)At (\d+)n?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 2:
                                        level_match = re.search(r'(?i)At (\d+)r?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 3:
                                        level_match = re.search(r'(?i)At (\d+)t?h? level', class_feature_description)
                                        if level_match:
                                            break
                                if level_match:
                                    class_feature_level = level_match.group(1)
                                else:
                                    class_feature_level = 0
                    elif part.startswith("PREVARGTEQ:"):
                        # Get ability level
                        ability_power_level_match = re.search(r'(?i)(.*?)LVL,(\d{0,2})', part.split("PREVARGTEQ:")[1])
                        if ability_power_level_match:
                            class_feature_level = ability_power_level_match.group(2)
            if is_valid_class_feature and class_feature_name and class_feature_description:
                class_feature_info = {
                    'Class': class_name,
                    'Name': class_feature_name,
                    'SubName': sub_feature_name,
                    'Description': class_feature_description if class_feature_description else '',
                    'Level': class_feature_level if class_feature_level else 0
                }

                # Making sure the array doesn't get an exception by filling it with keys if they are not present.
                if class_name not in class_features:
                    class_features[class_name] = {}
                if class_feature_name not in class_features[class_name]:
                    class_features[class_name][class_feature_name] = []

                # Appending the actual data.
                class_features[class_name][class_feature_name].append(class_feature_info)

            class_name = None
            class_feature_name = None
            class_feature_description = None
            class_feature_level = None
            sub_feature_name = None

        # Convert the archetypes dictionary to a pandas DataFrame
        archetype_data = []
        for parent_class, archetypes_dict in class_features.items():
            for archetype, features in archetypes_dict.items():
                for feature in features:
                    archetype_data.append({
                        'Class': parent_class,
                        'Sub Feature Of': feature['SubName'],
                        'Class Feature': feature['Name'],
                        'Description': feature['Description'],
                        'Level': feature['Level'],
                        'Source': source_book_name
                    })

        df = pd.DataFrame(archetype_data)

        # Write the DataFrame to an Excel file
        df.to_excel(output_file_name)

def extract_class_features_uc(file_name, output_file_name, source_book_name):
    class_features = {}
    class_name = None
    class_feature_name = None
    sub_feature_name = None
    class_feature_description = None
    class_feature_level = None

    is_valid_class_feature = 1

    # Regular expressions to match relevant lines
    block_pattern = r'(?i)###Block: (.+) Class features'

    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            is_valid_class_feature = 1
            line = line.strip()

            class_header_match = re.match(block_pattern, line)
            if class_header_match:
                class_name = class_header_match.group(1)
                continue

            # Split the line based on tab character or line end
            parts = line.split("\t")
            for part in parts:
                if is_valid_class_feature:
                    if part.startswith("KEY:"):
                        feature_key = part.split("KEY:")[1]
                        class_name_key = re.search(r'(.+)~', feature_key)
                        if class_name_key and len(class_name_key.groups()) > 0:
                            class_name = class_name_key.group(1).strip()
                        class_feature_key = re.search(r'~(.+)', feature_key)
                        if class_feature_key and len(class_feature_key.groups()) > 0:
                            class_feature_name = class_feature_key.group(1).strip()
                    elif part.startswith("CATEGORY:"):
                        if not part.split("CATEGORY:")[1] == "Special Ability":
                            is_valid_class_feature = 0
                    elif part.startswith("TYPE:"):
                        class_feature_type = part.split("TYPE:")[1]
                        # TYPE:{Classname}ClassFeatures.(SpecialQuality/SpecialAttack)
                        if re.search(r'(?i)SpecialQuality\.SuperNatural\.DomainPower', class_feature_type) or re.search(r'(?i)SpecialAttack\.SpellLike\.DomainPower', class_feature_type):
                            # Dealing with cleric domain power, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Cleric"
                        elif re.search(r'(?i)(.+)ClassFeatures\.SpecialAttack.Supernatural.BardicPerformance(.+)', class_feature_type) or re.search(r'(?i)(.+)ClassFeatures\.SpecialQuality.Supernatural.BardicPerformance(.+)', class_feature_type) or re.search(r'(?i)(.+)ClassFeatures\.SpecialAttack.Extraordinary.VersatilePerformance(.+)', class_feature_type):
                            # Dealing with bardic/versatile performance, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Bard"
                        # Todo: I might have to apply the (.*) instead of (.+) in other docs too.
                        elif re.search(r'(?i)(.*)ClassFeatures\.SpecialAttack(.*)', class_feature_type) or re.search(r'(?i)(.*)ClassFeatures\.SpecialQuality(.*)', class_feature_type):
                            # Dealing with different formatting of class features
                            type_match = re.search(r'(?i)ClassFeatures\.(.+)ClassFeatures\.Special(.+)', class_feature_type)
                            if type_match:
                                if class_name and class_name != type_match.group(1):
                                    # Class name was already set and differs from picked up key. Set key as sub_feature_name
                                    sub_feature_name = class_name
                                class_name = type_match.group(1)
                            else:
                                # Capture the parent class name between "ClassFeatures." and " ClassFeatures"
                                type_match = re.search(r'(?i)(.+)ClassFeatures\.Special', class_feature_type)
                                if type_match:
                                    if class_name and class_name != type_match.group(1):
                                        # Class name was already set and differs from picked up key. Set key as sub_feature_name
                                        sub_feature_name = class_name
                                    class_name = type_match.group(1)
                        elif re.search(r'(?i)(.+)ClassFeatures\.RagePower(.+)', class_feature_type):
                            # Dealing with a barbarian rage power, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Barbarian"
                        elif re.search(r'(?i)Class Feature\.Sorcerer Class Feature\.(.+) ~ Power LVL (.+).Sorcerer', class_feature_type):
                            # Dealing with wizard school, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Sorcerer"
                            # Capture the bloodline level
                            bloodline_ability_level_match = re.search(r'~ Power LVL (.+).Sorcerer', class_feature_type)
                            if bloodline_ability_level_match:
                                class_feature_level = bloodline_ability_level_match.group(1)
                        elif re.search(r'(?i)WizardClassFeatures\.SpecialQuality\.SuperNatural', class_feature_type) or re.search(r'(?i)WizardClassFeatures\.SpecialQuality\.SpellLike', class_feature_type):
                            # Dealing with sorcerer bloodline, set sub_feature_name to class name
                            sub_feature_name = class_name
                            class_name = "Wizard"
                        else:
                            is_valid_class_feature = 0
                    elif part.startswith("DESC:"):
                        description_match = part.split("DESC:")[1]
                        if description_match:
                            if not class_feature_description:
                                class_feature_description = ""
                            class_feature_description += description_match
                            if not class_feature_level:
                                # Extract the level from the description if present
                                for i in range(0, 4):
                                    if i == 0:
                                        level_match = re.search(r'(?i)At (\d+)s?t? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 1:
                                        level_match = re.search(r'(?i)At (\d+)n?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 2:
                                        level_match = re.search(r'(?i)At (\d+)r?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 3:
                                        level_match = re.search(r'(?i)At (\d+)t?h? level', class_feature_description)
                                        if level_match:
                                            break
                                if level_match:
                                    class_feature_level = level_match.group(1)
                                else:
                                    class_feature_level = 0
                    elif part.startswith("PREVARGTEQ:"):
                        # Get ability level
                        ability_power_level_match = re.search(r'(?i)(.*?)LVL,(\d{0,2})', part.split("PREVARGTEQ:")[1])
                        if ability_power_level_match:
                            class_feature_level = ability_power_level_match.group(2)
            if is_valid_class_feature and class_feature_name and class_feature_description:
                class_feature_info = {
                    'Class': class_name,
                    'Name': class_feature_name,
                    'SubName': sub_feature_name,
                    'Description': class_feature_description if class_feature_description else '',
                    'Level': class_feature_level if class_feature_level else 0
                }

                # Making sure the array doesn't get an exception by filling it with keys if they are not present.
                if class_name not in class_features:
                    class_features[class_name] = {}
                if class_feature_name not in class_features[class_name]:
                    class_features[class_name][class_feature_name] = []

                # Appending the actual data.
                class_features[class_name][class_feature_name].append(class_feature_info)

            class_name = None
            class_feature_name = None
            class_feature_description = None
            class_feature_level = None
            sub_feature_name = None

        # Convert the archetypes dictionary to a pandas DataFrame
        archetype_data = []
        for parent_class, archetypes_dict in class_features.items():
            for archetype, features in archetypes_dict.items():
                for feature in features:
                    archetype_data.append({
                        'Class': parent_class,
                        'Sub Feature Of': feature['SubName'],
                        'Class Feature': feature['Name'],
                        'Description': feature['Description'],
                        'Level': feature['Level'],
                        'Source': source_book_name
                    })

        df = pd.DataFrame(archetype_data)

        # Write the DataFrame to an Excel file
        df.to_excel(output_file_name)

def extract_archetype_info(file_path, output_file_name, source_book_name):
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
                    for i in range(0, 4):
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
                    else:
                        class_feature_level = 0
                class_feature_level_match = re.search(r'(?i)\tPREVARGTEQ:(.*?)LVL,(.{0,2}?)\t', line)
                if class_feature_level_match:
                    # Get ability level
                    if class_feature_level_match.group(2).strip():
                        class_feature_level = class_feature_level_match.group(2).strip()
                if class_feature_name:
                    class_feature_info = {
                        'Name': class_feature_name,
                        'Parent Class': archetype_parent_class_name,
                        'Archetype': archetype_name,
                        'Description': class_feature_description.group(1) if class_feature_description else '',
                        'Level': class_feature_level if class_feature_level else 0
                    }

                # Making sure the array doesn't get an exception by filling it with keys if they are not present.
                if archetype_parent_class_name not in archetypes:
                    archetypes[archetype_parent_class_name] = {}
                if archetype_name not in archetypes[archetype_parent_class_name]:
                    archetypes[archetype_parent_class_name][archetype_name] = []

                #Appending the actual data.
                archetypes[archetype_parent_class_name][archetype_name].append(class_feature_info)

        # Convert the archetypes dictionary to a pandas DataFrame
        archetype_data = []
        for parent_class, archetypes_dict in archetypes.items():
            for archetype, features in archetypes_dict.items():
                for feature in features:
                    archetype_data.append({
                        'Parent Class': parent_class,
                        'Archetype': archetype,
                        'Class Feature': feature['Name'],
                        'Description': feature['Description'],
                        'Level': feature['Level'],
                        'Source': source_book_name
                    })

        df = pd.DataFrame(archetype_data)

        # Write the DataFrame to an Excel file
        df.to_excel(output_file_name)

def extract_archetype_info_apg(file_path, output_file_name, source_book_name):
    archetypes = {}
    archetype_name = None
    sub_feature_name = None
    archetype_parent_class_name = None
    class_feature_name = None
    class_feature_description = None
    class_feature_level = None

    is_valid_archetype_feature = 1

    new_archetype_potentially_starting = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            is_valid_archetype_feature = 1
            line = line.strip()

            # Here we see that a new archetype is potentially starting, set flag accordingly.
            if line.startswith("#------------------"):
                new_archetype_potentially_starting = 1
                continue

            if new_archetype_potentially_starting:
                class_header_match = re.match(r'##	(.+)	', line)
                if class_header_match:
                    new_archetype_potentially_starting = 0
                    archetype_parent_class_name = class_header_match.group(1)
                    continue

            if not archetype_parent_class_name:
                continue

            # Split the line based on tab character or line end
            parts = line.split("\t")
            for part in parts:
                if is_valid_archetype_feature:
                    if part.startswith("KEY:"):
                        feature_key = part.split("KEY:")[1]
                        archetype_key = re.search(r'(.+)~', feature_key)
                        if archetype_key and len(archetype_key.groups()) > 0:
                            archetype_name = archetype_key.group(1).strip()
                        class_feature_key = re.search(r'~(.+)', feature_key)
                        if class_feature_key and len(class_feature_key.groups()) > 0:
                            class_feature_name = class_feature_key.group(1).strip()
                    elif part.startswith("CATEGORY:"):
                        if not part.split("CATEGORY:")[1] == "Special Ability":
                            is_valid_archetype_feature = 0
                    elif part.startswith("TYPE:"):
                        class_feature_type = part.split("TYPE:")[1]
                        if re.search(r'(?i)ClassFeatures\.(.+)ClassFeatures\.SpecialQuality(.+)', class_feature_type) or re.search(r'(?i)ClassFeatures\.(.+)ClassFeatures\.Archetype(.+)\.SpecialQuality(.+)', class_feature_type):
                            # Capture the parent class name between "ClassFeatures." and " ClassFeatures"
                            type_match = re.search(r'(?i)ClassFeatures\.(.+)ClassFeatures', class_feature_type)
                            if type_match:
                                archetype_parent_class_name = type_match.group(1)
                        elif re.search(r'(?i)Class Feature\.Sorcerer Class Feature\.(.+) ~ Power LVL (.+).Sorcerer', class_feature_type):
                            # Dealing with wizard school, set sub_feature_name to archetype name
                            sub_feature_name = archetype_name
                            archetype_name = None
                            archetype_parent_class_name = "Sorcerer"
                            # Capture the bloodline level
                            bloodline_ability_level_match = re.search(r'~ Power LVL (.+).Sorcerer', class_feature_type)
                            if bloodline_ability_level_match:
                                class_feature_level = bloodline_ability_level_match.group(1)
                        elif re.search(r'(?i)WizardClassFeatures\.SpecialQuality\.SuperNatural', class_feature_type) or re.search(r'(?i)WizardClassFeatures\.SpecialQuality\.SpellLike', class_feature_type):
                            # Dealing with sorcerer bloodline, set sub_feature_name to archetype name
                            sub_feature_name = archetype_name
                            archetype_name = None
                            archetype_parent_class_name = "Wizard"
                        elif re.search(r'(?i)SpecialQuality\.SuperNatural\.DomainPower', class_feature_type):
                            # Dealing with cleric domain power, set sub_feature_name to archetype name
                            sub_feature_name = archetype_name
                            archetype_name = None
                            archetype_parent_class_name = "Cleric"
                        else:
                            is_valid_archetype_feature = 0
                    elif part.startswith("DESC:"):
                        description_match = part.split("DESC:")[1]
                        if description_match:
                            if not class_feature_description:
                                class_feature_description = ""
                            class_feature_description += description_match
                            if not class_feature_level:
                                # Extract the level from the description if present
                                for i in range(0, 4):
                                    if i == 0:
                                        level_match = re.search(r'(?i)At (\d+)s?t? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 1:
                                        level_match = re.search(r'(?i)At (\d+)n?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 2:
                                        level_match = re.search(r'(?i)At (\d+)r?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 3:
                                        level_match = re.search(r'(?i)At (\d+)t?h? level', class_feature_description)
                                        if level_match:
                                            break
                                if level_match:
                                    class_feature_level = level_match.group(1)
                                else:
                                    class_feature_level = 0
                    elif part.startswith("PREVARGTEQ:"):
                        # Get ability level
                        ability_power_level_match = re.search(r'(?i)(.*?)LVL,(\d{0,2})', part.split("PREVARGTEQ:")[1])
                        if ability_power_level_match:
                            class_feature_level = ability_power_level_match.group(2)
            if is_valid_archetype_feature and class_feature_name:
                class_feature_info = {
                    'Name': class_feature_name,
                    'SubName': sub_feature_name,
                    'Parent Class': archetype_parent_class_name,
                    'Archetype': archetype_name,
                    'Description': class_feature_description if class_feature_description else '',
                    'Level': class_feature_level if class_feature_level else 0
                }

                # Making sure the array doesn't get an exception by filling it with keys if they are not present.
                if archetype_parent_class_name not in archetypes:
                    archetypes[archetype_parent_class_name] = {}
                if archetype_name not in archetypes[archetype_parent_class_name]:
                    archetypes[archetype_parent_class_name][archetype_name] = []

                # Appending the actual data.
                archetypes[archetype_parent_class_name][archetype_name].append(class_feature_info)

            archetype_name = None
            class_feature_name = None
            class_feature_description = None
            class_feature_level = None
            sub_feature_name = None

        # Convert the archetypes dictionary to a pandas DataFrame
        archetype_data = []
        for parent_class, archetypes_dict in archetypes.items():
            for archetype, features in archetypes_dict.items():
                for feature in features:
                    archetype_data.append({
                        'Parent Class': parent_class,
                        'Sub Feature Of': feature['SubName'],
                        'Archetype': archetype,
                        'Class Feature': feature['Name'],
                        'Description': feature['Description'],
                        'Level': feature['Level'],
                        'Source': source_book_name
                    })

        df = pd.DataFrame(archetype_data)

        # Write the DataFrame to an Excel file
        df.to_excel(output_file_name)

def extract_archetype_info_uc(file_path, output_file_name, source_book_name):
    archetypes = {}
    archetype_name = None
    sub_feature_name = None
    archetype_parent_class_name = None
    class_feature_name = None
    class_feature_description = None
    class_feature_level = None

    is_valid_archetype_feature = 1

    new_archetype_potentially_starting = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            is_valid_archetype_feature = 1
            line = line.strip()

            # Here we see that a new archetype is potentially starting, set flag accordingly.
            if line.startswith("###Block:"):
                class_header_match = re.match(r'###Block: (.*) Archetype', line)
                if class_header_match:
                    new_archetype_potentially_starting = 0
                    archetype_parent_class_name = class_header_match.group(1)
                    continue

            if not archetype_parent_class_name:
                continue

            # Split the line based on tab character or line end
            parts = line.split("\t")
            for part in parts:
                if is_valid_archetype_feature:
                    if part.startswith("KEY:"):
                        feature_key = part.split("KEY:")[1]
                        archetype_key = re.search(r'(.+)~', feature_key)
                        if archetype_key and len(archetype_key.groups()) > 0:
                            archetype_name = archetype_key.group(1).strip()
                        class_feature_key = re.search(r'~(.+)', feature_key)
                        if class_feature_key and len(class_feature_key.groups()) > 0:
                            class_feature_name = class_feature_key.group(1).strip()
                    elif part.startswith("CATEGORY:"):
                        if not part.split("CATEGORY:")[1] == "Special Ability":
                            is_valid_archetype_feature = 0
                    elif part.startswith("TYPE:"):
                        class_feature_type = part.split("TYPE:")[1]
                        if not re.search(r'(.*)ArchetypeAbility.Special(.*)', part.split("TYPE:")[1]):
                            # Capture the parent class name between "ClassFeatures." and " ClassFeatures"
                                is_valid_archetype_feature = 0
                    elif part.startswith("DESC:"):
                        description_match = part.split("DESC:")[1]
                        if description_match:
                            if not class_feature_description:
                                class_feature_description = ""
                            class_feature_description += description_match
                            if not class_feature_level:
                                # Extract the level from the description if present
                                for i in range(0, 4):
                                    if i == 0:
                                        level_match = re.search(r'(?i)At (\d+)s?t? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 1:
                                        level_match = re.search(r'(?i)At (\d+)n?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 2:
                                        level_match = re.search(r'(?i)At (\d+)r?d? level', class_feature_description)
                                        if level_match:
                                            break
                                    if i == 3:
                                        level_match = re.search(r'(?i)At (\d+)t?h? level', class_feature_description)
                                        if level_match:
                                            break
                                if level_match:
                                    class_feature_level = level_match.group(1)
                                else:
                                    class_feature_level = 0
                    elif part.startswith("PREVARGTEQ:"):
                        # Get ability level
                        ability_power_level_match = re.search(r'(?i)(.*?)LVL,(\d{0,2})', part.split("PREVARGTEQ:")[1])
                        if ability_power_level_match:
                            class_feature_level = ability_power_level_match.group(2)
            if is_valid_archetype_feature and class_feature_name:
                class_feature_info = {
                    'Name': class_feature_name,
                    'SubName': sub_feature_name,
                    'Parent Class': archetype_parent_class_name,
                    'Archetype': archetype_name,
                    'Description': class_feature_description if class_feature_description else '',
                    'Level': class_feature_level if class_feature_level else 0
                }

                # Making sure the array doesn't get an exception by filling it with keys if they are not present.
                if archetype_parent_class_name not in archetypes:
                    archetypes[archetype_parent_class_name] = {}
                if archetype_name not in archetypes[archetype_parent_class_name]:
                    archetypes[archetype_parent_class_name][archetype_name] = []

                # Appending the actual data.
                archetypes[archetype_parent_class_name][archetype_name].append(class_feature_info)

            archetype_name = None
            class_feature_name = None
            class_feature_description = None
            class_feature_level = None
            sub_feature_name = None

        # Convert the archetypes dictionary to a pandas DataFrame
        archetype_data = []
        for parent_class, archetypes_dict in archetypes.items():
            for archetype, features in archetypes_dict.items():
                for feature in features:
                    archetype_data.append({
                        'Parent Class': parent_class,
                        'Sub Feature Of': feature['SubName'],
                        'Archetype': archetype,
                        'Class Feature': feature['Name'],
                        'Description': feature['Description'],
                        'Level': feature['Level'],
                        'Source': source_book_name
                    })

        df = pd.DataFrame(archetype_data)

        # Write the DataFrame to an Excel file
        df.to_excel(output_file_name)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Todo: Include alchemist discoveries?
    # Todo: Include samurai/cavalier orders?
    # Todo: Remove garbage characters like '%' and '*' from descriptions

    # Code specific to the ACG:
    # Todo: Make a special "Sub Class Feature" field for wizard schools (and other future features),
    file_path = 'raw.githubusercontent.com_PCGen_pcgen_master_data_pathfinder_paizo_roleplaying_game_advanced_class_guide_acg_abilities_class.lst'
    extract_class_features(file_path, "acg_class_features.xlsx", "Pathfinder Roleplaying Game: Advanced Class Guide")
    extract_archetype_info(file_path, "acg_archetype_features.xlsx", "Pathfinder Roleplaying Game: Advanced Class Guide")

    # Code specific to the APG:
    # Todo: The APG uses a different key for class features, it looks like this: KEY:{ArchetypeName} ~ {ClassFeatureName} CATEGORY:Special Ability TYPE:ClassFeatures.{Classname}ClassFeatures.SpecialQuality. The code will have to be changed accordingly.
    # Todo: Exclude TYPE:{Classname}ClassFeatures.SpecialQuality.ClassSpecialization
    # Adds sub class feature from key in case of wizard schools: KEY:Air School ~ Air Supremacy
    # Adds cleric domain abilities to the same "Sub Class Feature" field
    # Adds sorcerer bloodline abilities to the same "Sub Class Feature" field. Bloodline ability template: TYPE:Class Feature.Sorcerer Class Feature.{BloodlineName} ~ Power LVL {level}.Sorcerer
    file_path = 'raw.githubusercontent.com_PCGen_pcgen_master_data_pathfinder_paizo_roleplaying_game_advanced_players_guide_apg_abilities_class.lst'
    extract_archetype_info_apg(file_path, "apg_archetype_features.xlsx", "Pathfinder Roleplaying Game: Advanced Player's Guide")
    extract_class_features_uc(file_path, "apg_class_features.xlsx", "Pathfinder Roleplaying Game: Advanced Player's Guide")

    # Code specific to the CR:
    # Todo: The CR uses a different key for class features, it looks like this: CATEGORY:Special Ability TYPE:{Classname}ClassFeatures.(SpecialQuality/SpecialAttack). The code will have to be changed accordingly.
    # Sorcerer bloodlines are handled the same way as the APG
    # Cleric domains are handled the same way as the APG
    # Todo: RogueClassFeatures.Ranger (among others) are showing up in the class field.
    file_path = 'raw.githubusercontent.com_PCGen_pcgen_master_data_pathfinder_paizo_roleplaying_game_core_rulebook_cr_abilities_class.lst'
    extract_class_features_cr(file_path, "cr_class_features.xlsx", "Pathfinder Roleplaying Game: Core Rulebook")

    # Code specific to the Ultimate Combat Guide:
    # Todo: The CR uses a different key for class features, it looks like this: TYPE:{Classname}ClassFeatures.SpecialQuality. The code will have to be changed accordingly.
    # Todo: The CR uses a different key for archetype class features, it looks like this: KEY:{archetype_name} ~ {class_feature_name} CATEGORY:Special Ability TYPE:{Classname}ClassFeatures.SpecialQuality. The code will have to be changed accordingly.
    file_path = 'uc_abilities_class.lst'
    extract_class_features_uc(file_path, "uc_class_features.xlsx", "Pathfinder Roleplaying Game: Ultimate Combat")
    # Todo: Add a search key for "ArchetypeAbility" instead of "ClassFeature"
    extract_archetype_info_uc(file_path, "uc_archetype_features.xlsx", "Pathfinder Roleplaying Game: Ultimate Combat")
