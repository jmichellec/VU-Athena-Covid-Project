#************************************************************************************

########################## Sentiment analysis using pattern.nl ###################

#************************************************************************************

setwd("C:/Users/jmich/1-VU-RA/pipeline")
fb_s <- read.csv(file = 'FB_sent_sub.csv',na.strings=c("", "NA"),encoding = "UTF-8", sep = ",")

mean(fb_s$Sentiment) #0.0494207
mean(fb_s$Subjectivity) # 0.3860997

#Drop first two rows
fb_s = subset(fb_s, select = -c(X,Unnamed..0) )
colnames(fb_s)

# plot sentiment scores
library(ggplot2)
a <- ggplot(fb_s, aes(x = Sentiment))
#histogram
a + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Sentiment)), 
             linetype = "dashed", size = 0.6)

# Plot Subjectivity Scores
b <- ggplot(fb_s, aes(x = Subjectivity))
#histogram
b + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Subjectivity)), 
             linetype = "dashed", size = 0.6)

#*************************************************************************
## Split up the corpus in positive and negative comments
#
# --> maybe rather one corpus with most positive and negative comments?!
#
#fb_s.POSITIVE <- subset(fb_s, Sentiment >= 0.20)
#fb_s.NEGATIVE <- subset(fb_s, Sentiment <= -0.20)

#fb_s.POSITIVE$message <- as.character(fb_s.POSITIVE$message)
#fb_s.NEGATIVE$message <- as.character(fb_s.NEGATIVE$message)
##
#*********************************************************************************************************************
#              High Subjectivity Comments
#*********************************************************************************************************************
# Get long comments with high sentiment (+/-) AND high subjectivity score

fb_subjective <- fb_s[(fb_s$Sentiment >= 0.25) | (fb_s$Sentiment <= -0.25), ]

fb_subjective <- subset(fb_subjective, Subjectivity >= 0.4)

#Drop rows with very short comments
fb_subjective$message <- as.character(fb_subjective$message)
fb_subjective = fb_subjective[(which(nchar(fb_subjective$message) >= 250)),]

#Drop less important columns
fb_subjective = subset(fb_subjective, select = -c(X.U.FEFF.level, object_type,query_status,query_time, 
                                                  query_type) )

#Sort by Subjectivity decreasing before start reading comments
fb_subjective <-fb_subjective[order(fb_subjective$Subjectivity, decreasing = TRUE),]
head(fb_subjective)

#Subset for Teun for intercoder reliability 
fb_subset <-fb_subjective[121:250,]

install.packages("writexl")
library("writexl")
write_xlsx(fb_subset, "Fb_long-high-sent_subset130.xlsx")

#######################################################################################
# Selection of longer, higher sentiment and subjectivity comments related to sub-topics:

#****************************************************************************
#               Blood Thinners
#***************************************************************************

#Subset Corpus with keywords 
bloodthinner <- c("bloedverdunn*", "bloedverdunnend", "bloedverdunnerrt", "bloedverdunner*",
                  "antistollingsmiddel*", "antistolling*", "antistollingsmedicijnen", "coagulatie*",
                  "bloedstolling*", "bloedproppen", "bloedstollingsstoornis*", "stollingsprobleem", "vwd" )
subset_bloodth <- fb_s[with(fb_s, grepl(paste0("\\b(?:",paste(bloodthinner, collapse="|"),")\\b"), message)),]

#Keep only high sentiment-subjectivity longer comments
subset_bloodth <- subset_bloodth[(subset_bloodth$Sentiment >= 0.05) | (subset_bloodth$Sentiment <= -0.05), ]

subset_bloodth <- subset(subset_bloodth, Subjectivity >= 0.3)

#Drop rows with very short comments
subset_bloodth$message <- as.character(subset_bloodth$message)
subset_bloodth = subset_bloodth[(which(nchar(subset_bloodth$message) >= 150)),]


mean(subset_bloodth$Sentiment) #0.0110936
mean(subset_bloodth$Subjectivity) #0.4800054

# plot sentiment scores
library(ggplot2)
a <- ggplot(subset_bloodth, aes(x = Sentiment))
#histogram
a + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Sentiment)), 
             linetype = "dashed", size = 0.6)

# Plot Subjectivity Scores
b <- ggplot(subset_bloodth, aes(x = Subjectivity))
#histogram
b + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Subjectivity)), 
             linetype = "dashed", size = 0.6)


#****************************************************************************
#               Pregnancy
#***************************************************************************
pregnancy <- c("zwanger*", "zwangerschap*", "zwangerschappen*", "kinderwens*",
               "borstvoeding*", "zwangere*", "vruchtbaarheid*", "geboorte*",
               "bevallingsstoornissen", "kinderen willen", "kind willen","kind krijgen") 

subset_preg <- fb_s[with(fb_s, grepl(paste0("\\b(?:",paste(pregnancy, collapse="|"),")\\b"), message)),]

#Keep only high sentiment-subjectivity longer comments
subset_preg <- subset_preg[(subset_preg$Sentiment >= 0.075) | (subset_preg$Sentiment <= -0.075), ]

subset_preg <- subset(subset_preg, Subjectivity >= 0.4)

#Drop rows with very short comments
subset_preg$message <- as.character(subset_preg$message)
subset_preg = subset_preg[(which(nchar(subset_preg$message) >= 150)),]


mean(subset_preg$Sentiment) #0.04464674
mean(subset_preg$Subjectivity) #0.4841187


# plot sentiment scores
library(ggplot2)
a <- ggplot(subset_preg, aes(x = Sentiment))
#histogram
a + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Sentiment)), 
             linetype = "dashed", size = 0.6)

# Plot Subjectivity Scores
b <- ggplot(subset_preg, aes(x = Subjectivity))
#histogram
b + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Subjectivity)), 
             linetype = "dashed", size = 0.6)

#******************************************************************************
#             Immunocompromised People
#******************************************************************************
Immun <- c("immuungecompromitteerd*", "aandoening","hematologisch", "maligniteit*", 
           "nierfalen", "dialyse", "orgaan*", "stamcel*","transplantatie", "immuundefici?nties",
           "immuun*", "hiv", "uitstellen", "chemo", "huid*","Psoriasis*","Hidradenitis*", 
           "Suppurativa*","Eczeem*", "urticaria*", "auto-immuunziekte*","SLE*", "dermato*", 
           "myositis","vasculitis", "sclerodermie", "auto-immuun-blaarziekte*", "*kanker*", 
           "lymfom*", "melanom*", "hematolologie*", "*long*", "longkanker", 
           "interstiti?le longziekte", "ILD", "cystic fibrosis", "transplantatie", 
           "multiple sclerosis", "MS", "nieren", "maag", "lever", "darm", "IBD", "ibs", 
           "gastro-intestinale", "tumor*", "tumoren", "afweerstoornis", "reuma*", "beperking", 
           "chronisch*", "ME", "CFS")

subset_immun <- fb_s[with(fb_s, grepl(paste0("\\b(?:",paste(Immun, collapse="|"),")\\b"), message)),]

#Keep only high sentiment-subjectivity longer comments
subset_immun <- subset_immun[(subset_immun$Sentiment >= 0.075) | (subset_immun$Sentiment <= -0.075), ]

subset_immun <- subset(subset_immun, Subjectivity >= 0.3)

#Drop rows with very short comments
subset_immun$message <- as.character(subset_immun$message)
subset_immun = subset_immun[(which(nchar(subset_immun$message) >= 150)),]

 

mean(subset_immun$Sentiment) #0.02104047
mean(subset_immun$Subjectivity) #0.5153681

# plot sentiment scores
library(ggplot2)
a <- ggplot(subset_immun, aes(x = Sentiment))
#histogram
a + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Sentiment)), 
             linetype = "dashed", size = 0.6)

# Plot Subjectivity Scores
b <- ggplot(subset_immun, aes(x = Subjectivity))
#histogram
b + geom_histogram(bins = 30, color = "black", fill = "gray") +
  geom_vline(aes(xintercept = mean(Subjectivity)), 
             linetype = "dashed", size = 0.6)
