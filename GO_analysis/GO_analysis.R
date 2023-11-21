#Install packages
if (!require("BiocManager", quietly = TRUE))
  install.packages("BiocManager")

BiocManager::install("clusterProfiler", force = TRUE) #the package containing go_analysis

BiocManager::install("AnnotationDbi") #run in the background, required for the workflow

BiocManager::install("org.Hs.eg.db") #human genes database

if (!require("reshape2", quietly = TRUE))
  install.packages("reshape2")

#Load packages
library(clusterProfiler)
library(AnnotationDbi)
library(org.Hs.eg.db)
library(reshape2)

#Read DESeq2 results file
df <- read.csv("condition_cancer_results_filtered.csv")

#Remove rows with NA and set gene_id as the row names
df <- na.omit(df[df$gene_id != "", ])
rownames(df) <- df$gene_id
df <- df[, -which(names(df) == "gene_id")]

#Set log2FoldChange cut off for gene sets
up.genes <- rownames(df[df$log2FoldChange > 1, ])
down.genes <- rownames(df[df$log2FoldChange < 1, ])

#Enrich for terms, here we are searching for molecular function of the gene set "MF"
up_GO <- enrichGO(gene = up.genes, OrgDb = "org.Hs.eg.db", keyType = "SYMBOL", ont = "MF")
down_GO <- enrichGO(gene = down.genes, OrgDb = "org.Hs.eg.db", keyType = "SYMBOL", ont = "MF")

#Write out top 20 GO enrichment terms as a barplot
fit <- plot(barplot(up_GO, showCategory = 20))
png("up_MF.png", res = 250, width = 1200, height = 2000)
print(fit)
dev.off()

fit <- plot(barplot(down_GO, showCategory = 20))
png("down_MF.png", res = 250, width = 1200, height = 2000)
print(fit)
dev.off()
