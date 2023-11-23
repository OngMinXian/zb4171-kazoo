library(DESeq2)
library(ggplot2)

countData <- read.csv('train_set_2k.csv',header=TRUE,check.names=FALSE, row.names=1)
metadata <- read.csv('train_set_2k_metadata.csv', header=TRUE,check.names=FALSE)
metadata[c('condition')] <- lapply(metadata[c('condition')], factor)
countData = round(countData)

dds <- DESeq2::DESeqDataSetFromMatrix(
    countData = as.matrix(countData),
    colData = data.frame(metadata, row.names = 'sample_id'),
    design = ~condition)

dds <- DESeq(dds)
res <- results(dds)
head(results(dds))
summary(res)
res <- res[order(res$padj),]
write.table(res, file = "train_set_2k_deseq2.csv", sep = ",", quote = FALSE)


volcano_plot <- ggplot(as.data.frame(res), aes(x = log2FoldChange, y = -log10(pvalue))) +
  geom_point(aes(color = ifelse(padj < 0.01 & abs(log2FoldChange) > 2, "red", "blue")), pch = 20) +
  xlim(-3, 3) +
  labs(title = "Volcano plot")

ggsave("volcano_plot.png", plot = volcano_plot, width = 15, height = 8, dpi = 300)

d <- plotCounts(dds, gene=which.min(res$padj), intgroup="condition", 
                returnData=TRUE)
minpadj <- ggplot(d, aes(x=condition, y=count)) + 
  geom_point(position=position_jitter(w=0.1,h=0)) + 
  scale_y_log10(breaks=c(25,100,400))

ggsave("gene_with_min_padj.png", plot = minpadj, dpi = 300)


vsdata <- vst(dds, blind = FALSE)
df_vst=SummarizedExperiment::assay(vsdata)
write.table(df_vst, file = "train_set_2k_deseq2_vst.csv", sep = ",", quote = FALSE)

pcaData <- plotPCA(vsdata, intgroup="condition", returnData=TRUE)
percentVar <- round(100 * attr(pcaData, "percentVar"))
pca_vst <- ggplot(pcaData, aes(PC1, PC2, color=condition)) +
  geom_point() +
  xlab(paste0("PC1: ",percentVar[1],"% variance")) +
  ylab(paste0("PC2: ",percentVar[2],"% variance")) + 
  coord_fixed()
ggsave("pca_vst_2k.png", plot = pca_vst, dpi = 300)
