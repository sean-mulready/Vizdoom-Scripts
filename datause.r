
library(tidyr)
library(dplyr)


# Define the CSV file path
csv_file <- file.path("/home/seanm/_vizdoom/Ziege_game_data_block_1.csv")

# Read the CSV, filling empty cells with "-"
data <- read.csv(csv_file, header = TRUE, sep = ",", fill = TRUE, na.strings = "", row.names=NULL)

# Replace NA values with "-"
data[is.na(data)] <- "-"
data$Time <- as.numeric(data$Time)

data$time_diff <- c(0, diff(data$Time, lag = 1))
data$tic_diff <- c(0, diff(data$Tic, lag = 1))
data$rew_diff <- c(0, diff(data$Cumulative_Reward, lag = 1))
data$time_diff <- ifelse(data$time_diff < 0, NA, data$time_diff)

View(data)
barplot(
  table(
    round(
          data$time_diff, digits = 4)
  )
)