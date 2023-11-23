library(AnnotationDbi)
library(org.Hs.eg.db)

expression_matrix <- read.delim('/home/ec2-user/data/GSE120795_total_norms_raw_counts.tsv', header = TRUE, row.names = 1, check.names = FALSE)
ensembl_ids <- rownames(expression_matrix)

expression_matrix$symbol <- mapIds(org.Hs.eg.db, keys=ensembl_ids, keytype="ENSEMBL", column="SYMBOL")

# remove row with no symbol
expression_matrix <- expression_matrix[!is.na(expression_matrix$symbol),]

unique_gene_names <- unique(expression_matrix$symbol)

# create new matrix
aggregated_matrix <- matrix(0, nrow = length(unique_gene_names), ncol = ncol(expression_matrix)-1)
rownames(aggregated_matrix) <- unique_gene_names
colnames(aggregated_matrix) <- colnames(expression_matrix)[-length(colnames(expression_matrix))]

# create a copy without symbol for colsum operation
expression_df <- as.matrix(expression_matrix[, -length(colnames(expression_matrix))]) 

for (i in seq_along(unique_gene_names)) {
  gene_name <- unique_gene_names[i]
  rows_with_gene <- expression_matrix$symbol == gene_name
  aggregated_matrix[i, ] <- colSums(expression_df[rows_with_gene, , drop = FALSE])
}
write.table(aggregated_matrix, file = "ANTE_normal_counts_converted.csv", sep = ",", quote = FALSE)
