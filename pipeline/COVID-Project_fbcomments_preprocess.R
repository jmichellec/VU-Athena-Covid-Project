#################################################################
#
# Facebook comments to news articles analysis
#
# Pre-processing of the texts & Keyword analysis 
# 
################################################################


setwd("C:/Users/jmich/1-VU-RA/pipeline")
fb <- read.csv(file = 'FB_NOS_NU_Telegraaf_NRC_all_endFeb.csv', 
               na.strings=c("", "NA"),encoding = "UTF-8", sep = ";")

library(quanteda)

#Adjust some meta data
colnames(fb)
names(fb)[names(fb) == 'like.summary.total_count'] <- 'like_count'
names(fb)[names(fb) == 'love.summary.total_count'] <- 'love_count'
names(fb)[names(fb) == 'haha.summary.total_count'] <- 'haha_count'
names(fb)[names(fb) == 'wow.summary.total_count'] <- 'wow_count'
names(fb)[names(fb) == 'sad.summary.total_count'] <- 'sad_count'
names(fb)[names(fb) == 'angry.summary.total_count'] <- 'angry_count'

#Change variable class
class(fb$like_count)
fb$like_count <- as.numeric(fb$like_count)

class(fb$comment_count)
fb$comment_count <- as.numeric(fb$comment_count)

#Keep only date not time
class(fb$created_time)
fb$created_time <- as.character(fb$created_time)
fb$created_time <- substr(fb$created_time, 0, 10)
#fb$created_time <- as.numeric(fb$created_time)
#fb$created_time <- as.Date(fb$created_time, format = "%y/%m/%d")
#doesn't work yet to transform in date

class(fb$message)
fb$message <- as.character(fb$message)

#Check for empty cells
sum(is.na(fb$message))
fb <- subset(fb, !is.na(message))

#Drop rows with very short comments
fb = fb[(which(nchar(fb$message) >= 10)),]

#Drop doubles
sum(duplicated(fb$message)) 
z <- duplicated(fb$message)
which(z==TRUE) 
length(unique(fb$message))
fb <- fb[!duplicated(fb$message), ]


#Save as csv file for python sentiment analysis
write.csv(fb, "Fb_data_forpy.csv", fileEncoding = "UTF-8" )

## Create a text corpus
quantedacorpus <- corpus(fb,
                         text_field = "message",
                         meta = list("id", "created_time", "comment_count","Like_count" ),
                         unique_docnames = TRUE)
#Prepare data
#Stopwords
stopwords('dutch')
#more extensive list of dutch stopwords:
mystopwords <- read.table("stop_words_dutch.txt", header = TRUE)
class(mystopwords)
stop_vec = as.vector(mystopwords$Custom_stopwords)
class(stop_vec)
#Also drop basic English stopwords
stopwords('english')
#List of emojis & symbols
emoji <- read.table("stop_words_emojis.txt", header=TRUE)
emoji_vec = as.vector(emoji$Emojis)


# Create document-frequency-matrix for topic model
dfm_fb <- dfm(quantedacorpus, 
                  tolower = TRUE, 
                  remove_numbers = TRUE, 
                  remove_punct = TRUE, 
                  remove_url = TRUE, 
                  remove_symbols = TRUE,
                  remove = c(stop_vec,emoji_vec, stopwords('dutch'),stopwords('english')),
                  stem = TRUE)

######Explore
#Get most frequent terms
topfeatures(
  dfm_fb,
  n = 200,
  decreasing = TRUE,
  scheme = c("count", "docfreq"),
  groups = NULL
)

#Look at keywords in context
head(kwic(quantedacorpus, pattern = "go*", window = 3, valuetype = "glob"))
head(kwic(quantedacorpus, pattern = "allergi*", window = 6, valuetype = "glob"), n=15)
allergy <- data.frame(head(kwic(quantedacorpus, pattern = "allergi*", window = 7, valuetype = "glob"), n=50))
allergy

head(kwic(quantedacorpus, pattern = "bloedverdunner*", window = 6, valuetype = "glob"), n=15)
head(kwic(quantedacorpus, pattern = "zwanger*", window = 6, valuetype = "glob"), n=15)
head(kwic(quantedacorpus, pattern = "kinderwens", window = 6, valuetype = "glob"), n=15)


#Read sample patient reports
options(max.print=1000)
print(as.character(quantedacorpus[30]))
print(as.character(quantedacorpus[152]))
print(as.character(quantedacorpus[1540]))

#most frequent bigrams
#install.packages("tidytext")
#library(tidytext)
#library(dplyr)
#?unnest_tokens()
#bifb <- fb %>% unnest_tokens(ngram,message,token = "ngrams", n = 2)
#bifb %>% count(ngram, sort = TRUE)

#***********************************************************************************************************
## Further NLP: POS tagging and most frequent NOUN / ADJ
# First clean quanteda corpus (similar to pre-processing steps as above for dfm)
qcorpus <- tokens(quantedacorpus)

qcorpus <- tokens_select(qcorpus, c(stop_vec,emoji_vec, stopwords('dutch'),stopwords('english')),selection='remove')

qcorpus <- tokens(qcorpus, remove_numbers = TRUE,  remove_punct = TRUE,remove_url = TRUE, 
                  remove_symbols = TRUE,remove_separators = FALSE)
      
######## POS tagging and keyword analysis with udpipe #####################


install.packages("udpipe")
library(udpipe)
dl <- udpipe_download_model(language = "dutch")
str(dl)

udmodel_dutch <- udpipe_load_model(file = "dutch-alpino-ud-2.5-191206.udpipe")

txt <- sapply(qcorpus, FUN=function(x){
  x <- gsub(" ", intToUtf8(160), x) ## replace space with no-break-space
  paste(x, collapse = " ")
})
x <- udpipe_annotate(udmodel_dutch, x = as.character(txt), tokenizer = "horizontal",parser = "none")
x <- as.data.frame(x)
str(x)
table(x$upos)

library(lattice)
stats <- subset(x, upos %in% c("NOUN")) 
stats <- txt_freq(stats$token)
stats$key <- factor(stats$key, levels = rev(stats$key))
barchart(key ~ freq, data = head(stats, 20), col = "cadetblue", 
         main = "Most occurring nouns", xlab = "Freq")

stats <- subset(x, upos %in% c("VERB")) 
stats <- txt_freq(stats$token)
stats$key <- factor(stats$key, levels = rev(stats$key))
barchart(key ~ freq, data = head(stats, 20), col = "cadetblue", 
         main = "Most occurring verbs", xlab = "Freq")

stats <- subset(x, upos %in% c("ADJ")) 
stats <- txt_freq(stats$token)
stats$key <- factor(stats$key, levels = rev(stats$key))
barchart(key ~ freq, data = head(stats, 20), col = "cadetblue", 
         main = "Most occurring adjectives", xlab = "Freq")


### Extract top keyword NOUN - ADJ / NOUN - VERB combinations
## Collocation (words following one another)
stats <- keywords_collocation(x = x, 
                              term = "token", group = c("doc_id", "paragraph_id", "sentence_id"),
                              ngram_max = 4)
collocs <- stats[order(-stats$freq),]
collocs$keyword <- factor(collocs$keyword, levels = rev(collocs$keyword))
barchart(keyword ~ freq, data = head(collocs, 20), col = "cadetblue", 
         main = "Most occurring collocations", xlab = "Freq")

## Co-occurrences: How frequent do words occur in the same sentence, in this case only nouns or adjectives
stats <- cooccurrence(x = subset(x, upos %in% c("NOUN", "ADJ")), 
                      term = "lemma", group = c("doc_id", "paragraph_id", "sentence_id"))

co_occur <- stats[order(-stats$cooc),]


## Co-occurrences: How frequent do words follow one another
stats <- cooccurrence(x = x$lemma, 
                      relevant = x$upos %in% c("NOUN", "ADJ"))

co_occur <- data.frame(stats[order(-stats$cooc),])
library(tidyr)
co_occur <- co_occur %>% unite("words", term1:term2, sep = " ", remove = FALSE)
co_occur$words <- factor(co_occur$words, levels = rev(co_occur$words))
barchart(words ~ cooc, data = head(co_occur, 20), col = "cadetblue", 
         main = "Most occurring co-occurences", xlab = "Freq")


## Co-occurrences: How frequent do words follow one another even if we would skip 2 words in between
stats <- cooccurrence(x = x$lemma, 
                      relevant = x$upos %in% c("NOUN", "ADJ"), skipgram = 2)
head(stats)

## Visualizations
library(igraph)
library(ggraph)
library(ggplot2)
wordnetwork <- head(stats, 70)
wordnetwork <- graph_from_data_frame(wordnetwork)
ggraph(wordnetwork, layout = "fr") +
  geom_edge_link(aes(width = cooc, edge_alpha = cooc), edge_colour = "pink") +
  geom_node_text(aes(label = name), col = "darkgreen", size = 4) +
  theme_graph(base_family = "Arial Narrow") +
  theme(legend.position = "none") +
  labs(title = "Cooccurrences within 3 words distance", subtitle = "Nouns & Adjective")

## Using RAKE
stats <- keywords_rake(x = x, term = "lemma", group = "doc_id", 
                       relevant = x$upos %in% c("NOUN", "ADJ"))
stats$key <- factor(stats$keyword, levels = rev(stats$keyword))
barchart(key ~ rake, data = head(subset(stats, freq > 3), 20), col = "red", 
         main = "Keywords identified by RAKE", 
         xlab = "Rake")

############################################################################### End