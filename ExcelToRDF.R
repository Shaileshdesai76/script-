library(readxl)

# ----------------------------
# USER INPUTS
# ----------------------------
input_xlsx <- "input.xlsx"
sheet_name <- 1
output_rdf <- "output.rdf"

# ----------------------------
# 1. READ XLSX
# ----------------------------
dat <- read_excel(input_xlsx,
                  sheet = sheet_name,
                  col_names = TRUE,
                  .name_repair = "minimal")

dat <- as.data.frame(dat, stringsAsFactors = FALSE)

# ----------------------------
# 2. FILL MISSING VALUES WITH 0
# ----------------------------
for (j in 2:ncol(dat)) {
  dat[[j]][is.na(dat[[j]]) | dat[[j]] == ""] <- 0
}

# Convert to character (RDF expects characters)
for (j in 2:ncol(dat)) {
  dat[[j]] <- as.character(dat[[j]])
}

# ----------------------------
# 3. EXTRACT SAMPLE NAMES AND MATRIX
# ----------------------------
samples <- dat[[1]]
mat <- as.matrix(dat[,-1])
rownames(mat) <- samples
sites <- colnames(mat)

cat("Total sites written:", length(sites), "\n")
cat("Total samples:", nrow(mat), "\n")

# ----------------------------
# 4. WRITE RDF HEADER
# ----------------------------
write("  ;1.0", output_rdf)

write(paste0(paste(sites, collapse = ";"), ";"),
      output_rdf,
      append = TRUE)

write(paste(rep("10;", length(sites)), collapse = ""),
      output_rdf,
      append = TRUE)

# ----------------------------
# 5. WRITE SAMPLES
# ----------------------------
for (i in seq_len(nrow(mat))) {
  write(paste0(">", rownames(mat)[i], ";1;;;;;;;"),
        output_rdf,
        append = TRUE)

  write(paste(mat[i, ], collapse = ""),
        output_rdf,
        append = TRUE)
}
