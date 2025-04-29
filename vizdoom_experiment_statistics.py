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
    # Check if Reward is 1 at any point in the episode as indicator that target has been hit
    if "Reward" in df.columns:
        return df["Reward"].eq(1.0).any()
    return False

def process_data(needed_data):
    def first_non_na(series):
        return series.dropna().iloc[0] if not series.dropna().empty else np.nan

    # how many episodes where recorded and replayed
    original_counts = (
        needed_data.groupby(["Subject", "Block", "Episode"]).size()
        .reset_index()
        .groupby(["Subject", "Block"])
        .size()
        .reset_index(name="Original_Episode_Count")
    )

    # only process valid episodes (excludes episodes where neither action nor target_pos have at least 1 value)
    valid_episodes = needed_data.groupby("Episode").filter(
        lambda g: g["Action"].notna().any() and g["Target_pos"].notna().any()
    )

    # processing of valid episodes
    processed_data = (
        valid_episodes.groupby("Episode").apply(lambda group: pd.Series({
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
            "Hit": hit_logic(group)
        }))
        .reset_index(drop=True)
    )

    # counts valid episodes
    valid_counts = processed_data.groupby(["Subject", "Block"]).size().reset_index(name="Valid_Episode_Count")

    # merging
    overview = pd.merge(original_counts, valid_counts, on=["Subject", "Block"], how="left").fillna(0)
    overview["Valid_Episode_Count"] = overview["Valid_Episode_Count"].astype(int)
    overview["Excluded_Episodes"] = overview["Original_Episode_Count"] - overview["Valid_Episode_Count"]

    return processed_data, overview


all_subjects_combined = []
all_overviews = []  # episodecount

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
                processed_block_data, overview_df = process_data(block_df)  
                all_processed_data.append(processed_block_data)
                all_overviews.append(overview_df)
            
    # After processing all blocks for the subject, combine the results
    combined_data = pd.concat(all_processed_data, ignore_index=True)
    combined_data = combined_data.sort_values(by=["Block", "Episode"]).reset_index(drop=True)


    # Save the combined data to a single output file for this subject
    output_file = os.path.join(processed_folder, f"processed_data_subject_{subject}.tsv")
    combined_data.to_csv(output_file, sep="\t", index=False)
    
    print(f"Processed data saved for Subject {subject}: {output_file}")

    all_subjects_combined.append(combined_data)

# Combine all subjects' data into one file
if all_subjects_combined:
    grand_combined_data = pd.concat(all_subjects_combined, ignore_index=True)
    grand_combined_data = grand_combined_data.sort_values(by=["Subject", "Block", "Episode"]).reset_index(drop=True)
    
    final_output_file = os.path.join(root_dir, "all_subjects_combined.tsv")
    grand_combined_data.to_csv(final_output_file, sep="\t", index=False)
    print(f"All subject data combined into one file: {final_output_file}")

# Combine overview over all Subjects and Blocks
if all_overviews:
    combined_overview = pd.concat(all_overviews, ignore_index=True)
    combined_overview = combined_overview.sort_values(by=["Subject", "Block"]).reset_index(drop=True)

    print("\n📊 Episodecount pro Subject & Block:")
    print(combined_overview)

# Calculate the movement ratios for each variation to check if there was an overall ratio of .8/.2 
ratio_statistics = grand_combined_data.groupby("Variation").apply(lambda df: pd.Series({
    "normal_right": ((df["Side"] == "right") & (df["Movement"] == 0)).sum() / len(df),
    "inverted_right": ((df["Side"] == "right") & (df["Movement"] == 1)).sum() / len(df),
    "normal_left": ((df["Side"] == "left") & (df["Movement"] == 0)).sum() / len(df),
    "inverted_left": ((df["Side"] == "left") & (df["Movement"] == 1)).sum() / len(df),
})).reset_index()

print("\n✅ Ratio statistics:")
print(ratio_statistics)

# save ratio-statistics and episode-overview in one file

#  axis=1 for horizontal merge
combined_data = pd.concat([combined_overview, ratio_statistics], axis=1)

combined_data.to_csv("combined_statistics_overview.tsv", sep="\t", index=False)



import matplotlib.pyplot as plt

# Add a trial index per block (0-based within each Subject/Block)
grand_combined_data["Trial_Index"] = (
    grand_combined_data
    .groupby(["Subject", "Block"])
    .cumcount()
)

# Group by trial index and get mean optimal choice rate
trial_avg_optimal = (
    grand_combined_data
    .groupby("Trial_Index")["optimal_choice"]
    .mean()
)

# Add a Trial counter per block so we can align episodes across blocks
grand_combined_data["Trial"] = grand_combined_data["Episode"]


# Now compute the average proportion of optimal choices per trial
optimal_per_trial = (
    grand_combined_data
    .groupby("Trial")
    .agg(Optimal_Proportion=("optimal_choice", "mean"))
    .reset_index()
)




# plotting
plt.figure(figsize=(12, 6))
plt.plot(optimal_per_trial["Trial"], optimal_per_trial["Optimal_Proportion"], marker='o')
plt.xlabel("Trial")
plt.ylabel("Proportion of Optimal Choices")
plt.title("Average Optimal Choices per Trial")

# Fix x-axis ticks to show only integers
plt.xticks(ticks=range(1, optimal_per_trial["Trial"].max() + 1))

plt.grid(True)
plt.tight_layout()
plt.savefig("Average_optimal_choices_by_trial.pdf", dpi=300)
plt.close()


import matplotlib.pyplot as plt
import numpy as np

# Compute subject-level proportions
subject_trial_optimal = (
    grand_combined_data
    .groupby(["Subject", "Trial"])
    .agg(
        Optimal_Count=("optimal_choice", "sum"),
        Trial_Count=("optimal_choice", "count")
    )
    .reset_index()
)

subject_trial_optimal["Optimal_Proportion"] = (
    subject_trial_optimal["Optimal_Count"] / subject_trial_optimal["Trial_Count"]
)

# Compute trial-level means (already in your code)
optimal_per_trial = (
    grand_combined_data
    .groupby("Trial")
    .agg(Optimal_Proportion=("optimal_choice", "mean"))
    .reset_index()
)


# Set up plot
plt.figure(figsize=(12, 6))

# Plot subject dots with manual jitter
np.random.seed(0)  # for reproducibility
jitter_strength = 0.15

for _, row in subject_trial_optimal.iterrows():
    x = row["Trial"] + np.random.uniform(-jitter_strength, jitter_strength)
    y = row["Optimal_Proportion"]
    plt.plot(x, y, 'o', markerfacecolor=None,markeredgecolor='black', alpha=0.5, markersize=3)

# Plot average line
plt.plot(
    optimal_per_trial["Trial"],
    optimal_per_trial["Optimal_Proportion"],
    marker='o',
    color="blue",
    label="Mean Optimal Choice",
    zorder=2
)

# Final touches
plt.xlabel("Trial")
plt.ylabel("Proportion of Optimal Choices")
plt.title("Average Optimal Choices per Trial (with Subject Data)")
plt.xticks(ticks=range(1, optimal_per_trial["Trial"].max() + 1))
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.savefig("Average_optimal_choices_by_trial_with_subjects_matplotlib.pdf", dpi=300)
plt.close()



# Count datapoints per trial
trial_counts = grand_combined_data.groupby("Trial").size().reset_index(name="Count")

# Plot with matplotlib
plt.figure(figsize=(12, 6))
plt.bar(trial_counts["Trial"], trial_counts["Count"], color="steelblue")
plt.title("Number of Data Points per Trial (Episode)")
plt.xlabel("Trial (Episode Number)")
plt.ylabel("Number of Data Points")
plt.xticks(trial_counts["Trial"], rotation=90)
plt.tight_layout()
plt.savefig("datapoints_per_trial.pdf", dpi=300)
plt.close()





# Count total and optimal per movement type
movement_group = grand_combined_data.groupby("Movement_Words")["optimal_choice"].agg(
    total='count', optimal='sum'
).reset_index()

# Calculate proportion
movement_group["optimal_rate"] = movement_group["optimal"] / movement_group["total"]

# Plot
plt.figure(figsize=(6, 5))
plt.bar(movement_group["Movement_Words"], movement_group["optimal_rate"], color=["skyblue", "salmon"])
plt.xlabel("Movement Type")
plt.ylabel("Proportion of Optimal Choices")
plt.title("Optimal Choice Rate by Movement Type")
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("Optimal_choice_by_movement_type.pdf", dpi=300)
plt.close()

# Count total and optimal per block
block_group = grand_combined_data.groupby("Block")["optimal_choice"].agg(
    total='count', optimal='sum'
).reset_index()

# Calculate proportion
block_group["optimal_rate"] = block_group["optimal"] / block_group["total"]

# Plot
plt.figure(figsize=(8, 5))
plt.bar(block_group["Block"], block_group["optimal_rate"], color="mediumseagreen")
plt.xlabel("Block")
plt.ylabel("Proportion of Optimal Choices")
plt.title("Optimal Choice Rate by Block")
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("Optimal_choice_by_block.pdf", dpi=300)
plt.close()

