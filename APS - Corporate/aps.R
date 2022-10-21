library("dplyr")
library("tidyr")
library("ggplot2")
aaa <- read.csv("C:/Users/Vitor Russomano/VsCodeProjects/Notes/APS - Corporate/AAA.csv")
bbb <- read.csv("C:/Users/Vitor Russomano/VsCodeProjects/Notes/APS - Corporate/BAA.csv")

merged <- as_tibble(merge(aaa, bbb))

merged %>%
    pivot_longer(cols = c("AAA", "BAA"), names_to = ("Rating"), values_to = ("Yield")) %>%
    mutate(DATE = as.Date(DATE, format = "%Y-%m-%d")) -> merged


ggplot(merged, aes(x = DATE, y = Yield, color = as.factor(Rating))) +
    geom_point(size = 1) +
    facet_wrap(~Rating, dir = "v") +
    theme(legend.position = "none") +
    scale_x_date(date_breaks = "6 month", date_labels = "%m-%Y") +
    theme(axis.text.x = element_text(angle = 60, hjust = 1))