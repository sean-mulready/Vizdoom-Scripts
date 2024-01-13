
library(tidyr)
library(dplyr)


# Define the CSV file path
csv_file <- file.path("/home/seanm/_vizdoom/01__game_dataframe.csv")

# Read the CSV, filling empty cells with "-"
data <- read.csv(csv_file, header = TRUE, sep = ",", fill = TRUE, na.strings = "", row.names=NULL)


# Replace NA values with "-"
data[is.na(data)] <- "-"
#data$Time <- as.numeric(data$Time)

#data$time_diff <- c(0, diff(data$Time, lag = 1))
#data$tic_diff <- c(0, diff(data$Tic, lag = 1))
#data$rew_diff <- c(0, diff(data$Cumulative_Reward, lag = 1))
#data$time_diff <- ifelse(data$time_diff < 0 | NA, -1, data$time_diff)
#time_diff_only <- data$time_diff #|>
#filter(time_diff != -1)

#barplot(
  #table(
    #round(
          #time_diff_only, digits = 4)
  #)
#)
View(data)
#median(round(time_diff_only,digits = 4))
#mean(round(time_diff_only,digits = 4))
