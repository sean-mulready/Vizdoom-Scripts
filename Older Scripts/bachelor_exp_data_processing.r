
# So this is the next attempt
# what it should do:
# 1. Take the preprocessed tsv-file (should be somehow sorted)
# - regroup so first group by ptp_num, then by block, then by episode for further processing
# -look about relations between what was balance and therefore,
#  what the probabilties where, and check if the it was indeed that in 70% it was 
#  normal or inverted when the monster was on that side 
#  (because I am looking, if ptp has matched probability of their movement to the game)
# - Check, what the first movement was in each episode so need to filter or more likely
#   go through the lines of each episode and skip until the MOVEMENT is not "NONE" (as a string!)
# - Make some awesome descriptive statistics
# - idea for the statistics: comparing the correct key vs. the statistically optimal key
# (there is an optimal movement key for balance being 0 or 1)

# loading libraries
library(tidyr)
library(dplyr)

raw_data <- read.csv("preprocessed_data_all.tsv", sep="\t")

raw_data <- raw_data %>%
  select(Participant, Block, Episode,State,Tic, Time, Action, Movement, Balance, X0_y)  # Only keep relevant columns

raw_data$Participant <- as.integer(raw_data$Participant) #ptp number
raw_data$Block <- as.integer(raw_data$Block) #block number
raw_data$Episode <- as.integer(raw_data$Episode) #episode as int
raw_data$State <- as.integer(raw_data$State) #state as int
raw_data$Balance <- as.integer(raw_data$Balance) #balance as int
raw_data$Movement <- as.integer(raw_data$Movement) #movement as int
raw_data$Tic <- as.integer(raw_data$Tic)# tic as int
raw_data$Time <- as.numeric(raw_data$Time)# time as numeric
raw_data$X0_y <- as.numeric(raw_data$X0_y)# X0_y as numeric

raw_data <- raw_data %>%
  filter(if_all(everything(), ~ . != "invalid number"))


View(raw_data)
str(raw_data)

# function to translate if movement was inverted or normal

movement_translation <- function(movement){
  if (movement == 0) {
    return("normal")
  } else if (movement == 1) {
    return("inverted")
  } else {
    return("unknown")  # You can handle other cases if needed
  }
}

monster_side <- function(position){
  if (is.numeric(position)) {
    position <- round(as.numeric(position), 2)
    }  # Round to 2 decimal places
  if (position >= (75)) {
    return("left")
  }else if (position < (-9)){
    return("right")
  }else{
    return("error")
  }
}

#function to check if the movement was correct

correct_movement <- function(movement,position, action){
  if (movement == 0 && position == "left" && action == "MOVE_LEFT"){ #normal, left side, MOVE_LEFT is correct
  return("correct")
  }else if (movement == 0 && position == "right" && action == "MOVE_RIGHT"){ # normal, right side, MOVE_RIGHT is correct
    return("correct")
  }else if (movement == 1 && position == "left" && action == "MOVE_RIGHT"){ # inverted, left side, MOVE_RIGHT is correct
    return("correct")
  } else if (movement == 1 && position == "right" && action == "MOVE_LEFT"){  # inverted, right side, MOVE_LEFT is correct
    return("correct")
  }else{   # everything else is incorrect
    return("incorrect")
  }

}

#function to check, if the movement was the optimal choice (choice with the overall highest probability)
# if balance is 0 or 1 either MOVE_LEFT or MOVE_RIGHT is the optimal choice 
# So e.g. TRUE if balance == 0 and action = MOVE_LEFT optimal

optimal_movement <- function(balance,first_action){
  if (balance == 0 && first_action == "MOVE_LEFT"){
    return(TRUE)
  }else if (balance == 1 && first_action == "MOVE_RIGHT"){
    return(TRUE)
  }else{
    return(FALSE)
  }
}

# Group the data by ptp_num, block_num, and episode
processed_data <- raw_data %>%
  group_by(Participant, Block, Episode) %>%
  
  # Filter to get the first non-NA Action in each group
  summarize(
    First_Action = first(na.omit(Action)),
    
    # Get the index of the first non-NA Action
    first_non_na_index = which(!is.na(Action))[1],
    
    Movement = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      Movement[first_non_na_index]
    } else {
      NA
    },
    
    Movement_Words = if (!is.na(Movement) && !is.na(first_non_na_index)) {
      movement_translation(Movement)
    } else {
      NA
    },
    
    Balance = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      Balance[first_non_na_index]
    } else {
      NA
    },
    
    X0_y = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      X0_y[first_non_na_index]
    } else {
      NA
    },
    
    side = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      monster_side(X0_y[first_non_na_index])
    } else {
      NA
    },

    correct_key = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      correct_movement(Movement, side, First_Action)
    } else {
      NA
    },

    optimal_key = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      optimal_movement(Balance, First_Action)
    } else {
      NA
    },
    
    Tic = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      Tic[first_non_na_index]
    } else {
      NA
    },
    
    Time = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
      Time[first_non_na_index]
    } else {
      NA
    }
  ) %>%
  ungroup()

# View the processed data
View(processed_data)


summary_data <- raw_data %>%
  group_by(Participant, Block) %>%
  summarise(count = n()) %>%
  arrange(Participant, Block)

print(summary_data)

summary_data <- processed_data %>%
  group_by(Participant, Block, side, Balance) %>%
  summarise(
    total_episodes = n(),  # Total count of episodes
    inverted_count = sum(Movement == "inverted"),  # Count of inverted movement
    normal_count = sum(Movement == "normal"),      # Count of normal movement
    inverted_ratio = inverted_count / total_episodes,  # Ratio of inverted movement
    normal_ratio = normal_count / total_episodes    # Ratio of normal movement
  ) %>%
  arrange(Participant, Block, side, Balance)

View(summary_data)

# If the balance is 0 there's a probability of .7, the movement is
# inverted if the monster spawns on the right side (optimal key A/left)
# and a probability of .7 that the movement is normal 
# if the monster spawns on the left side (optimal key A/left)
# so if the balance for a block of episodes is 0, the optimal key is A/left
# for every episode
# so for each block I want to know what the blance was and I want to know, how many
# times the movement was inverted/normal per side of the cacodemon


# Summarizing the data
summary_data <- processed_data %>%
  group_by(Participant, Block) %>%
  summarise(
    Balance = first(Balance),  # Assuming balance is constant for each block
    optimal_side = ifelse(Balance == 0, "left is optimal", "right is optimal"),
    total_episodes = n(),  # Total count of episodes in the block
    inverted_count_left = sum(Movement == 1 & side == "left"),
    normal_count_left = sum(Movement == 0 & side == "left"),
    inverted_count_right = sum(Movement == 1 & side == "right"),
    normal_count_right = sum(Movement == 0 & side == "right"),
    
    # Ratios for each side
    inverted_ratio_left = inverted_count_left / total_episodes,
    normal_ratio_left = normal_count_left / total_episodes,
    inverted_ratio_right = inverted_count_right / total_episodes,
    normal_ratio_right = normal_count_right / total_episodes,

    # Counts of how many times the monster spawned on each side
    spawn_count_left = sum(side == "left"),
    spawn_count_right = sum(side == "right")
  ) %>%
  arrange(Participant, Block)

View(summary_data)