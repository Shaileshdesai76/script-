## this script is useful for PCA plotting base on haplogroup frequency 
# Load required packages
install.packages("ggplot2")
library(ggplot2)

#your csv file, row should contain haplogroup number, and first column is your population name. 
## like this 
## pop  M R U H X
## pop1 0.2 0.3 0.4 0.7
## pop2 0.8 0.6 0.5 0.2
## pop3 0.2 0.3 0.4 0.5
## pop4 0.3 0.5 0.9 0.4
## pop5 0.7 0.3 0.3 0.7

# Read the CSV file
df <- read.csv("PCA_Frequency - Sheet1 - PCA_Frequency - Sheet1.csv", row.names = 1)

# Set ethnicity as row names and drop it from the matrix
rownames(df) <- df$Ethinicity
df$Ethinicity <- NULL

# Convert to numeric matrix
df <- as.data.frame(lapply(df, as.numeric))  # Ensure all columns are numeric

# Replace NA or Inf with 0 (or use imputation if preferred)
df[is.na(df)] <- 0
df[!is.finite(as.matrix(df))] <- 0

# Perform PCA
pca_result <- prcomp(df, scale. = TRUE)

# Summary of PCA
summary(pca_result)

# Extract PCA scores
pca_scores <- as.data.frame(pca_result$x)
pca_scores$Ethnicity <- rownames(pca_scores)

write.csv(pca_scores, "PCA_scores_srilanka.csv", row.names = FALSE)

#usually from this point, i do download file (above), and add new column as Regions.Language
#as second column, which we will just correspond to the population to its regions or language and using that we plot
# however using paste function in R, you can do automate, but i usually avoid this,
# because every time, i need to change population number so. 

pca_scores <- read.csv("PCA_scores_srilanka_for_R.csv")

#lets plot now 
library(ggplot2)
library(plotly)

p <- ggplot(
  pca_scores,
  aes(
    x = PC1,
    y = PC2,
    color = Regions.Language,
    text = Regions.Language   # hover label
  )
) +
  geom_point(size = 3) +
  theme_minimal() +
  theme(panel.grid = element_blank()) +
  labs(
    title = "PCA of Haplogroup Frequencies",
    x = "PC1",
    y = "PC3",
    color = "Region / Language"
  )

ggplotly(p, tooltip = "text")


### run this below if you want to only save as pdf. 

pdf("PCA_interactive_static.pdf", width = 7, height = 6)
print(p)
dev.off()

