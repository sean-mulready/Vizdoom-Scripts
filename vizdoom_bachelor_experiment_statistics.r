# import packages
library(dplyr)
library(tidyr)
library(ggplot2)





# 1. I need to have the information like a list of the Subject numbers in the one file
# 2. Then it needs to do something for every number in that list 
    # 3. it should go into the corresponding folder
        # 4. it should do everything following for each blockfile
            # 5. only select the needed data
            # 6. make some descriptive Statistics (first action, correct action, optimal key, RT)
#7. have overall statistics

# 1. get the list of Subject numbers
sub_data <- read.csv("Subjects.tsv", sep = "\t") #maybe work on avoiding duplicates in Subject.tsv

sub_list <- sub_data$sub_num
print(sub_list)
# do something for every number in that list

for (s in sub_list){
  # 3. navigate to the corresponding folder
  current_filepath <- file.path(getwd(), paste0("sub_",s))
  #print(current_filepath)
  setwd(current_filepath) #setting the current working directory to access the files
  print(paste("Current working directory for sub_num", s, ":", getwd()))
  # do everything for each blockfile
  block_files <- list.files(pattern = "\\.tsv")

  for (file in block_files){
    current_blockfile <- read.csv(file, sep = "\t") #read the tsv-file
    needed_data <- current_blockfile %>%
      select(Subject, Block, Episode,State,Tic, Time, Action, Movement, Variation, X0_y)  # Only keep relevant columns
    needed_data$Subject <- as.integer(needed_data$Subject) #sub number
    needed_data$Block <- as.integer(needed_data$Block) #block number
    needed_data$Episode <- as.integer(needed_data$Episode) #episode as int
    needed_data$State <- as.integer(needed_data$State) #state as int
    needed_data$Variation <- as.integer(needed_data$Variation) #variation as int
    needed_data$Movement <- as.integer(needed_data$Movement) #movement as int
    needed_data$Tic <- as.integer(needed_data$Tic)# tic as int
    needed_data$Time <- as.numeric(needed_data$Time)# time as numeric
    needed_data$X0_y <- as.numeric(needed_data$X0_y)# X0_y as numeric
    needed_data <- needed_data %>%
      filter(Subject != "invalid number" | is.na(X0_y))
    #View(needed_data)

    #all the functions needed for further processing
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
      if (is.na(position)){
        return ("unkown")
      }
      #if (is.numeric(position)) {
      position <- round(as.numeric(position), 2)
      #}  # Round to 2 decimal places
      if (position >= (75)) {
        return("left")
      }else if (position < (-9)){
        return("right")
      }else{
        return("error")
      }
    }

    #function to check if the movement choice was correct

    correct_choice <- function(movement,position, action){
      if (movement == 0 && position == "left" && action == "MOVE_LEFT"){ #normal, left side, MOVE_LEFT is correct
        return(TRUE)
      }else if (movement == 0 && position == "right" && action == "MOVE_RIGHT"){ # normal, right side, MOVE_RIGHT is correct
        return(TRUE)
      }else if (movement == 1 && position == "left" && action == "MOVE_RIGHT"){ # inverted, left side, MOVE_RIGHT is correct
        return(TRUE)
      } else if (movement == 1 && position == "right" && action == "MOVE_LEFT"){  # inverted, right side, MOVE_LEFT is correct
        return(TRUE)
      }else {   # everything else is incorrect
        return(FALSE)
      }

    }

    #function to check, if the movement was the optimal choice (choice with the overall highest probability)
    # if variation is 1 or 2 either MOVE_LEFT or MOVE_RIGHT is the optimal choice 
    # So e.g. TRUE if variation == 1 and action = MOVE_LEFT optimal

    optimal_choice <- function(variation,first_action){
      if (variation == 1 && first_action == "MOVE_LEFT"){
        return(TRUE)
      }else if (variation == 2 && first_action == "MOVE_RIGHT"){
        return(TRUE)
      }else {
        return(FALSE)
      }
    }

    # Group the blockfiles by episode
    processed_data <- needed_data %>%
      group_by(Episode) %>%
  
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
    
        Variation = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
          Variation[first_non_na_index]
        } else {
          NA
        },
    
        X0_y = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
          X0_y[first_non_na_index]
        } else {
          NA
        },
    
        side = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
          monster_side(X0_y)
        } else {
          NA
        },

        correct_choice = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
          correct_choice(Movement, side, First_Action)
        } else {
          NA
        },

        optimal_choice = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
          optimal_choice(Variation, First_Action)
        } else {
          NA
        },
    
        Tic = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
          Tic[first_non_na_index]
        } else {
          NA
        },
    
        Time_of_Action = if (!is.na(first_non_na_index) && first_non_na_index > 0) {
          Time[first_non_na_index]
        } else {
          NA
        },
        Time_of_Episode = max(Time)
      ) %>%
      filter(if_all(everything(), ~ . != "invalid number")) %>% #kick out all the rows with invalid numbers
      ungroup()
    # Reorder the columns so Subject and Block come before Episode
    processed_data <- processed_data %>%
      mutate(Subject = s, Block = as.numeric(gsub("\\D", "", file))) %>%
      select(Subject, Block, everything())
    # View the processed data
    # create folders for processed data if they don't exist and setwd()
    processed_folder <- "processed data"
    if (!file.exists(processed_folder)){
      dir.create(file.path(getwd(),processed_folder))
    }
    setwd(file.path(getwd(),processed_folder))
    
    
    write.table(processed_data, paste0("processed_data_",file), row.names = FALSE, sep = "\t")
    
    setwd("..")
  }

  #at the very end set the working directory back to the original
  setwd("..")
  print(paste("Returned to original working directory:", getwd()))
}

# now I have files that are processed and so far contain the data I need for 
# my descriptive statistics
# what I want to have is:
# RT
# optimal choices and relations
# correct choices
# episode length:Time_of_Episode mean (per block, per sub, overall)
# basically I have to store all the data of the files in one file at least for the numbers I want overall 
# 1. for all the Subjects go to the folder of the processed data
# 2. for each file
# 3. read the file
# 4. append it to a dataframe
# 5. save that dataframe 


# create dataframe for all data

descriptive_statistics_overall <- data.frame()
for (s in sub_list){
  folderpath <- file.path(getwd(),paste0("sub_",s),"processed data")
  setwd(folderpath)
  print(paste("current path: ", getwd()))
  s_files <- list.files(full.names = TRUE)
  print(s_files)

  for (f in s_files){
    current_f <- read.table(f, header = TRUE)
    #print(paste("Processing file: ", f))  MAYBE DELETE THIS PRINTS?
    #print(paste("mean Time of Episode: ", mean(current_f$Time_of_Episode)))
    #print(paste("SD Time of Episode: ", sd(current_f$Time_of_Episode)))
    #print(paste("mean RT (first action): ", mean(current_f$Time_of_Action)))
    #print(paste("sd RT (first action): ", sd(current_f$Time_of_Action)))
    descriptive_statistics_overall <- rbind(descriptive_statistics_overall,current_f)
  }

  #at the end set back to basic directory
  setwd("../..")
}

descriptive_statistics_overall <- descriptive_statistics_overall %>%
  group_by(Subject, Block) %>%
    mutate(cum_opt = cumsum(as.numeric(optimal_choice)), .after = optimal_choice)
View(descriptive_statistics_overall)

#get the overall statistics

overall_statistics <- descriptive_statistics_overall %>%
  ungroup() %>%
  summarize(
    mean_time_episode = mean(Time_of_Episode),
    sd_time_episode = sd(Time_of_Episode),
    mean_RT_first_action = mean(Time_of_Action),
    sd_RT_first_action = sd(Time_of_Action),
    optimal_choice_count = (sum(optimal_choice == TRUE)/n()),
    correct_choice_count = (sum(correct_choice == TRUE)/n())
  )

View(overall_statistics)

# Get the overall ratio statistics

ratio_statistics <- descriptive_statistics_overall %>%
  group_by(Variation) %>%
    summarize(
      normal_right = sum(side == "right" & Movement == 0)/n(),
      inverted_right = sum(side == "right" & Movement == 1)/n(), 
      normal_left = sum(side == "left" & Movement == 0)/n(), 
      inverted_left = sum(side == "left" & Movement == 1)/n()

    )
View(ratio_statistics)


# Get Block statistics for each Subject
block_statistics <- descriptive_statistics_overall %>%
  group_by(Subject, Block, Variation) %>%
  summarize(
    episodes = n(),
    mean_time_episode = mean(Time_of_Episode),
    sd_time_episode = sd(Time_of_Episode),
    mean_RT_first_action = mean(Time_of_Action),
    sd_RT_first_action = sd(Time_of_Action),
    optimal_key_count = (sum(optimal_key == TRUE)/n()),
    correct_key_count = (sum(correct_key == "correct")/n())
  )

View(block_statistics)

# If the variation is 1 there's a probability of .8, the movement is
# inverted if the monster spawns on the right side (optimal choice A/left)
# and a probability of .8 that the movement is normal 
# if the monster spawns on the left side (optimal choice A/left)
# If variation 2 prob of .8 that normal if right and prob .8
# that inv if left 

#to check the ratios and also if on a total it was close to
#the goal (.8/.2) the ratios of the .8 should be checked so 
#4 conditions (2 per balance value) should be summed and ratioed

# Get block-wise ratio statistics for each Subject
ratio_blockwise <- descriptive_statistics_overall %>%
  group_by(Subject, Block) %>%
  summarize(
    Variation = first(Variation),  # Assuming Balance is the same for each Subject-Block combination
    normal_right = sum(side == "right" & Movement == 0) / n(),
    inverted_right = sum(side == "right" & Movement == 1) / n(),
    normal_left = sum(side == "left" & Movement == 0) / n(),
    inverted_left = sum(side == "left" & Movement == 1) / n(),
    times_left = sum(side=="left"),
    times_right = sum(side=="right"),
    Episodes = n()
    #.groups = 'drop'  # Optional: This prevents grouping in the output
  )

View(ratio_blockwise)




##### Plots

#plot Episode time (do they get faster within and over blocks?)
#to consider: the cacodemon spawns in random places therefore the distance changes
#which then changes the time necessary to finish the episode
#maybe there's a way to normalize it (set it in relation to distance)?

# mean Episode times for each Subject and block
time_data <- descriptive_statistics_overall %>%
  group_by(Subject, Block) %>%
  summarise(
    mean_ep_time_sub = mean(Time_of_Episode, na.rm = TRUE), # mean ep-time per block for each Subject
    .groups = "drop"
  )

#  mean Episode times for each block
mean_times_all <- time_data %>%
  group_by(Block) %>%
  summarise(
    mean_ep_time_all = mean(mean_ep_time_sub, na.rm = TRUE),
    .groups = "drop"
  )

# plot for Episode times per block, mean and individual
episode_time_plot <- ggplot() +
  # Individual proportions
  geom_point(data = time_data, 
             aes(x = Block, y = Time_of_Episode, colour = factor(Subject)), 
             alpha = 0.6, size = 2) + 
  # Mean proportions
  geom_line(data = mean_times_all, 
            aes(x = Block, y = mean_ep_time_all, group = 1), 
            colour = "black", size = 1) +
  geom_point(data = mean_times_all, 
             aes(x = Block, y = mean_ep_time_all), 
             colour = "black", size = 3) +
  labs(
    x = "Block", 
    y = "Episode Time", 
    colour = "Subject",
    title = "Individual and overall mean times of episodes per Block"
  ) +
  theme_minimal() 
  +
  # Customize text sizes using `theme()`
  theme_minimal(base_size = 12) +  # Adjust overall base text size
  theme(
    plot.title = element_text(size = 18, face = "bold"),  # Title size and style
    axis.title = element_text(size = 14),  # Axis labels size
    axis.text = element_text(size = 12),  # Axis tick labels size
    legend.text = element_text(size = 12),  # Legend text size
    legend.title = element_text(size = 14)  # Legend title size
  )

#Save it
ggsave("Episode_Times.pdf", plot = episode_time_plot,
        width = 210, height = 210, units = "mm")


# plot for the RT (time of first movement)

# mean reaction times for each Subject and block
RT_data <- descriptive_statistics_overall %>%
  group_by(Subject, Block) %>%
  summarise(
    mean_RT_sub = mean(Time_of_Action, na.rm = TRUE), # mean RT per block for each Subject
    .groups = "drop"
  )

# Calculate mean Episode times for each block
mean_RT_all <- RT_data %>%
  group_by(Block) %>%
  summarise(
    mean_RT_all = mean(mean_RT_sub, na.rm = TRUE),
    .groups = "drop"
  )

# RT-plot

RT_plot <- ggplot() +
  # Individual means
  geom_point(data = RT_data, 
             aes(x = Block, y = Time_of_Action, colour = factor(Subject)), 
             alpha = 0.6, size = 2) + 
  # Means for all
  geom_line(data = mean_RT_all, 
            aes(x = Block, y = mean_RT_all, group = 1), 
            colour = "black", size = 1) +
  geom_point(data = mean_RT_all, 
             aes(x = Block, y = mean_RT_all), 
             colour = "black", size = 3) +
  labs(
    x = "Block", 
    y = "Reaction Time", 
    colour = "Subject",
    title = "Individual and overall Reaction Times per Block"
  ) +
  theme_minimal() 
  +
  # Customize text sizes using `theme()`
  theme_minimal(base_size = 12) +  # Adjust overall base text size
  theme(
    plot.title = element_text(size = 18, face = "bold"),  # Title size and style
    axis.title = element_text(size = 14),  # Axis labels size
    axis.text = element_text(size = 12),  # Axis tick labels size
    legend.text = element_text(size = 12),  # Legend text size
    legend.title = element_text(size = 14)  # Legend title size
  )


#Save it
ggsave("RT_A4.pdf", plot = time_change_plot,
        width = 210, height = 210, units = "mm")




# Calculate proportions for each Subject and block
proportions_data <- descriptive_statistics_overall %>%
  group_by(Subject, Block) %>%
  summarise(
    prop_opt = mean(optimal_key, na.rm = TRUE), # Proportion for each Subject
    .groups = "drop"
  )

# Calculate mean proportions for each block
mean_proportions <- proportions_data %>%
  group_by(Block) %>%
  summarise(
    mean_prop_opt = mean(prop_opt, na.rm = TRUE),
    .groups = "drop"
  )

# plot for optimal choice proportion per block, mean and individual
proportion_plot <- ggplot() +
  # Individual proportions
  geom_point(data = proportions_data, 
             aes(x = Block, y = prop_opt, colour = factor(Subject)), 
             alpha = 0.6, size = 2) + # , position = position_jitter(width = 0.2) Jitter to avoid overlap
  # Mean proportions
  geom_line(data = mean_proportions, 
            aes(x = Block, y = mean_prop_opt, group = 1), 
            colour = "black", size = 1) +
  geom_point(data = mean_proportions, 
             aes(x = Block, y = mean_prop_opt), 
             colour = "black", size = 3) +
  labs(
    x = "Block", 
    y = "Proportion of Optimal Choices", 
    colour = "Subject",
    title = "Proportion of Optimal Choices by Block"
  ) +
  theme_minimal() 
  +
  # Customize text sizes using `theme()`
  theme_minimal(base_size = 12) +  # Adjust overall base text size
  theme(
    plot.title = element_text(size = 18, face = "bold"),  # Title size and style
    axis.title = element_text(size = 14),  # Axis labels size
    axis.text = element_text(size = 12),  # Axis tick labels size
    legend.text = element_text(size = 12),  # Legend text size
    legend.title = element_text(size = 14)  # Legend title size
  )
# Save

# Save the plot
ggsave("Proportion_Optimal_Choices.pdf", 
       plot = proportion_plot, 
       width = 210, height = 210, units = "mm")



# Calculate proportions for each Subject and block (correct key)
proportions_data2 <- descriptive_statistics_overall %>%
  group_by(Subject, Block) %>%
  summarise(
    prop_cor = mean(correct_key, na.rm = TRUE), # Proportion for each Subject
    .groups = "drop"
  )

# Calculate mean proportions for each block
mean_proportions_cor <- proportions_data2 %>%
  group_by(Block) %>%
  summarise(
    mean_prop_cor = mean(prop_cor, na.rm = TRUE),
    .groups = "drop"
  )

# plot for correct choice proportion per block, mean and individual
proportion_plot_cor <- ggplot() +
  # Individual proportions
  geom_point(data = proportions_data2, 
             aes(x = Block, y = prop_cor, colour = factor(Subject)), 
             alpha = 0.6, size = 2) + # , position = position_jitter(width = 0.2) Jitter to avoid overlap
  # Mean proportions
  geom_line(data = mean_proportions_cor, 
            aes(x = Block, y = mean_prop_cor, group = 1), 
            colour = "black", size = 1) +
  geom_point(data = mean_proportions_cor, 
             aes(x = Block, y = mean_prop_cor), 
             colour = "black", size = 3) +
   # Labels and title
  labs(
    x = "Block", 
    y = "Proportion of Correct Choices", 
    colour = "Subject",
    title = "Proportion of Correct Choices by Block"
  ) +
  # Customize text sizes using `theme()`
  theme_minimal(base_size = 12) +  # Adjust overall base text size
  theme(
    plot.title = element_text(size = 18, face = "bold"),  # Title size and style
    axis.title = element_text(size = 14),  # Axis labels size
    axis.text = element_text(size = 12),  # Axis tick labels size
    legend.text = element_text(size = 12),  # Legend text size
    legend.title = element_text(size = 14)  # Legend title size
  )
# Save the plot
ggsave("Proportion_Correct_Choices.pdf", 
       plot = proportion_plot_cor, 
       width = 210, height = 210, units = "mm")