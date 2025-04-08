import pandas as pd
import os
from io import StringIO
import numpy as np

# Column names and data type conversions as before
columns_needed = [
    "Subject", "Block", "Episode", "State", "Tic", "Time", "Action", 
    "Movement", "Variation", "Target_pos", "Target_name", "Reward"
]

convert_to_int = ["Subject", "Block", "Episode", "State", "Tic", "Movement", "Variation"]
convert_to_float = ["Time", "Target_pos", "Reward"]

# Subject data
subject_file = "subjects.tsv"
sub_data = pd.read_csv(subject_file, sep="\t")
sub_list = sub_data["sub_num"].unique()

root_dir = os.getcwd()

def movement_translation(movement):
    if movement == 0:
        return "normal"
    elif movement == 1:
        return "inverted"
    else:
        return "unknown"  # For other cases

def target_side(position):
    if position is None:
        return "unknown"
    
    position = round(float(position), 2)  # Round to 2 decimal places
    if position >= 75:
        return "left"
    elif position < -9:
        return "right"
    else:
        return "error"

def correct_choice(position, action):
    if position == "left" and action == "MOVE_LEFT":
        return True
    elif position == "right" and action == "MOVE_RIGHT":
        return True
    else:
        return False

def optimal_choice(variation, movement, first_action):
    if variation == 1 and movement == 0 and first_action == "MOVE_LEFT":
        return True
    elif variation == 1 and movement == 1 and first_action == "MOVE_RIGHT":
        return True
    elif variation == 2 and movement == 0 and first_action == "MOVE_RIGHT":
        return True
    elif variation == 2 and movement == 1 and first_action == "MOVE_LEFT":
        return True
    else:
        return False

def hit_logic(df):
    # Check if Reward is 1.0 at any point in the episode
    if "Reward" in df.columns:
        return df["Reward"].eq(1.0).any()
    return False

def process_data(needed_data):
    def first_non_na(series):
        return series.dropna().iloc[0] if not series.dropna().empty else np.nan
    
    processed_data = (
        needed_data.groupby("Episode").apply(lambda group: pd.Series({
            "Subject": group["Subject"].iloc[0],
            "Block": group["Block"].iloc[0],
            "Episode": group["Episode"].iloc[0],
            "State": group["State"].iloc[0],
            "Tic": group["Tic"].iloc[0],
            "Time": group["Time"].iloc[0],
            "Action": group["Action"].iloc[0],
            "Movement": group["Movement"].iloc[0],
            "Movement_Words": movement_translation(group["Movement"].iloc[0]),
            "Variation": group["Variation"].iloc[0],
            "Target_pos": first_non_na(group["Target_pos"]),
            "Target_name": first_non_na(group["Target_name"]),
            "first_non_na_index": group["Action"].first_valid_index(),
            "First_Action": first_non_na(group["Action"]),
            "Side": target_side(first_non_na(group["Target_pos"])),
            "correct_choice": correct_choice(target_side(first_non_na(group["Target_pos"])), first_non_na(group["Action"])),
            "optimal_choice": optimal_choice(
                group["Variation"].iloc[0], 
                group["Movement"].iloc[0], 
                first_non_na(group["Action"])
            ),
            "Time_of_Action": group.loc[group["Action"].first_valid_index(), "Time"], 
            "Time_of_Episode": group["Time"].max(),
            "Hit": hit_logic(group)  # Check Reward instead of Target_name
        }))
        .reset_index(drop=True)
    )
    return processed_data

# Process each subject
for subject in sub_list:
    subject_folder = os.path.join(root_dir, f"sub_{subject}")
    if not os.path.exists(subject_folder):
        continue
    
    processed_folder = os.path.join(subject_folder, "processed_data")
    os.makedirs(processed_folder, exist_ok=True)

    # Create a container to hold processed blocks for each subject
    all_processed_data = []
    
    for file in os.listdir(subject_folder):
        if file.endswith(".tsv"):
            file_path = os.path.join(subject_folder, file)
            
            df_list = []
            with open(file_path, "r") as f:
                header = None
                for line in f:
                    if header is None or not line.startswith(header[0]):
                        df_list.append(line)
                    if header is None:
                        header = line.strip().split("\t")
            
            df = pd.read_csv(StringIO("".join(df_list)), sep="\t", engine="python", on_bad_lines="skip")
            
            # Process and convert data types as before
            df = df[[col for col in columns_needed if col in df.columns]]
            for col in convert_to_int:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
            for col in convert_to_float:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='ignore')

            # Process each block and store in the all_processed_data container
            for block, block_df in df.groupby("Block"):
                processed_block_data = process_data(block_df)  # This is your data processing function
                all_processed_data.append(processed_block_data)
            
    # After processing all blocks for the subject, combine the results
    combined_data = pd.concat(all_processed_data, ignore_index=True)
    combined_data = combined_data.sort_values(by=["Block", "Episode"]).reset_index(drop=True)


    # Save the combined data to a single output file for this subject
    output_file = os.path.join(processed_folder, f"processed_data_subject_{subject}.tsv")
    combined_data.to_csv(output_file, sep="\t", index=False)
    
    print(f"Processed data saved for Subject {subject}: {output_file}")
