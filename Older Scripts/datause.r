# R-Script for reading and some processing of data
# UNDER CONSTRUCTION
# for now simple and calculating the time based on tics

# loading libraries
library(tidyr)
library(dplyr)

# set wd to where .csv-files are stored
setwd("/home/seanm/_vizdoom/data")

# enter the number of blocks
block_num <- 4
# enter the number of subjects measured
subjects <- 1
# enter ticrate that is used during experiment
ticrate <- 50

for (sub_num in 1:subjects) {
  subject_data <- data.frame()
  subject_folder <- paste0("sub-", sub_num)
  if (!file.exists(subject_folder)) next  # Skip if the folder doesn't exist
  setwd(subject_folder)  # Move to the subject's folder
  for (b in 1:(block_num)) {
    current_file <- paste0(sub_num, "_block_", b, "_game_dataframe.csv")
    if (!file.exists(current_file)) next  # Skip if the file doesn't exist
    current_data <- read.csv(current_file,
                             header = TRUE,
                             sep = ",",
                             fill = TRUE,
                             na.strings = "", 
                             row.names = NULL)
    current_data <- current_data |>
      mutate(Block = b, .before = Episode)
    subject_data <- bind_rows(subject_data, current_data)

  }

  # Calculate ratios
  ratios <- list()
  for (b in 1:block_num) {
    block_data <- subject_data %>%
      filter(Block == b)

    left_monster <- block_data %>%
      filter(`X0_y` < -9)

    right_monster <- block_data %>%
      filter(`X0_y` > 75)

    left_inverted_movement <- left_monster %>%
      filter(Movement == 1)

    right_inverted_movement <- right_monster %>%
      filter(Movement == 1)

    left_ratio <- nrow(left_inverted_movement) / nrow(left_monster)
    right_ratio <- nrow(right_inverted_movement) / nrow(right_monster)

    ratios[[b]] <- list(Block = b,
                        Left_Ratio = left_ratio,
                        Right_Ratio = right_ratio)
  }

  cat("Subject", sub_num, "\n")
  for (i in 1:block_num) {
    cat("Block", ratios[[i]]$Block, "Left Ratio:", ratios[[i]]$Left_Ratio, "Right Ratio:", ratios[[i]]$Right_Ratio, "\n")
  }
  cat("\n")
  save(subject_data, file = paste0("combined_preprocessed_sub-", sub_num, ".csv"))

  setwd("..")  # Move back to the parent directory
  View(subject_data)
}




#was das ding machen soll: Es soll berechnen, wie häufig invertierte Steuerung verwendet wurde, wo das Monster war (links oder rechts) und welches Mu.
#Es muss also wissen: Monster links oder rechts (zählen) und steuerung dazu zählen
#also quasi Paare zählen: wie oft links + normal und links + invertiert und das gleiche für rechts
#dann die Quote über alle Trials aber muss das nochmal sortieren also in abhängigkeit von etwas ... genau, also steurungspaarung mit seite des monsters geteilt 
#durch gesamtzahl der seite des monsters
# movement-choice = 1 ist invertiert, 0 ist normal






# Initialisiere eine Variable, um die Summe der positiven "time"-Werte zu speichern
total_time_sum <- 0

# Iteriere über jede Episode
for (episode in unique(data$Episode)) {
  episode_data <- data[data$Episode == episode, ]
  
  # Extrahiere den maximalen numerischen Wert von Tic
  max_tic <- max(episode_data$Tic, na.rm = TRUE)
  
  # Überprüfe, ob max_tic größer als 0 ist und berechne die "time"
  if (max_tic > 0 && !grepl("^Time:", max_tic)) {
    time <- max_tic * (1/50)
    total_time_sum <- total_time_sum + time
    print(paste("Time for Episode", episode, ":", time))
  }
}

# Currently worked on

# Gib die Gesamtsumme der positiven "time"-Werte aus
#print(paste("Gesamtsumme der positiven Time-Werte:", total_time_sum))
#print(paste("korrigierte gesamtzeit:", (episodes*(1/35))+ total_time_sum))
#print(paste("Nochmal korrigierte Zeit:", ((episodes*14)*(1/35))+ total_time_sum))

#ratio_movements <- data %>%
  #group_by(Episode) %>%
  #summarize(ratio_0 = sum(Movement == 0) / n(),
            #ratio_1 = sum(Movement == 1) / n())

#print(ratio_movements)

#overall_ratio <- data %>%
  #summarize(ratio_0 = sum(Movement == 0) / n(),
            #ratio_1 = sum(Movement == 1) / n())

#print(overall_ratio)