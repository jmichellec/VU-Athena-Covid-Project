import pandas as pd
import numpy as np
import argparse
import os

from ast import literal_eval
import pyLDAvis.gensim
from gensim import corpora, models
from gensim.models import Phrases
from gensim.models import CoherenceModel
from pprint import pprint
import glob
from nltk.corpus import stopwords

def stopwords_merged():
    """
    Merge all stopwords into one stopwords list
    returns list of stopwords
    """
    # Start with nltk
    stopwords_all = stopwords.words('dutch')

    # # Get paths with stopwords
    # paths = glob.glob('stopwords/*.txt')
    paths = ['stopwords/voornamen.txt', 'stopwords/stop_words_emojis.txt']
    for file in paths:
        with open(file, 'rb') as f:
            stopwords_list = f.read().splitlines()
            stopwords_all += stopwords_list

    unique_stopwords = list(set(stopwords_all))
    return unique_stopwords


def texts_list(df):
    """ Turn string of list into list and append to bigger list
    params:
    df: preprocessed dataframe
    returns: list of lists (tokenized)

    """
    texts = []
    for text in df['tokens_pos']:

        # list string to list
        token_pos_list = literal_eval(text)

        text = []
        for token, pos in token_pos_list:
            # if pos.startswith('J') or pos.startswith('NO') or pos.startswith('V'):
            if token not in stopwords_merged():
                text.append(token)
        texts.append(text)
    return texts

def doc_term_matrix(data):
    """ Create Bag-of-Words model and dictionary for gensim
    params:
    data: list of lists (tokenized)
    returns: corpus and dictionary
    """
    # bigram = Phrases(data, min_count=20)
    # for idx in range(len(data)):
    #     for token in bigram[data[idx]]:
    #         if '_' in token:
    #             # Token is a bigram, add to document.
    #             data[idx].append(token)

    dictionary = corpora.Dictionary(data)
    bow_corpus = [dictionary.doc2bow(token) for token in data]
    tfidf = models.TfidfModel(bow_corpus)
    corpus = tfidf[bow_corpus]
    return corpus, dictionary


def evaluation_lda(model, data, dictionary, corpus):
    """ Compute coherence score and perplexity.
    params:
    model: lda model
    data: list of lists (tokenized)
    dictionary
    corpus

    returns: coherence score, perplexity score
    """
    coherence_model_lda = CoherenceModel(model=model, texts=data, dictionary=dictionary, coherence='c_v')
    coherence = coherence_model_lda.get_coherence()
    perplexity = model.log_perplexity(corpus)
    return coherence, perplexity


def hyperparameter_tuning(data, dictionary, corpus):
    """ Test different number of topics and get coherence and perplexity scores. """

    # Change depending on models one wants to check
    lda_models = [
        models.ldamodel.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=20, random_state=np.random.seed(123)),
        models.ldamodel.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=20, random_state=np.random.seed(123)),
        models.ldamodel.LdaModel(corpus, num_topics=20, id2word=dictionary, passes=20, random_state=np.random.seed(123)),
        models.ldamodel.LdaModel(corpus, num_topics=40, id2word=dictionary, passes=20, random_state=np.random.seed(123)),
        ]
    coherences = []
    perplexities = []
    for model in lda_models:
        coherence, perplexity = evaluation_lda(model, data, dictionary, corpus)
        coherences.append(coherence)
        perplexities.append(perplexity)
    return coherences, perplexities, lda_models

def format_topics_sentences(lda_model, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(lda_model[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = lda_model.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return sent_topics_df


def main():
    """ Function to run gensim LDA"""
    parser = argparse.ArgumentParser(description='List the content of a folder')

    # Add the arguments
    parser.add_argument('csv_file', help='preprocessed file for sentiment analysis')
    parser.add_argument('platform', help='platform of preprocessed file')

    # Execute the parse_args() method
    args = parser.parse_args()
    file_path = 'preprocessed_data/' + args.platform + '_preprocessed_' + args.csv_file

    df = pd.read_csv(file_path, delimiter='\t')
    texts = texts_list(df.head(100))

    print("Creating doc-term matrix...")
    corpus, dictionary = doc_term_matrix(texts)
    print("Doc-term matrix created!")

    # Hyperparameter tune the number of topics using coherence
    print("Starting hyperparameter tuning...")
    coherences, _, lda_models = hyperparameter_tuning(texts, dictionary, corpus)

    # Get index of highest coherence value, can also be changed to perplexity
    best_model_index = np.argmax(coherences)
    lda_model = lda_models[best_model_index]

    print("Retrieved the best model.")

    # Show topics
    topics = lda_model.print_topics()

    print("Saving results...")

    # Create folder
    csv_name = args.csv_file.split(".")[0]
    os.makedirs('lda_results', exist_ok=True)
    vis_name = 'lda_results/' + csv_name + 'no_stops_jnv.html'
    topics_name = 'lda_results/' + csv_name + 'no_stops_jnv.txt'

    with open(topics_name, 'w', encoding='utf-8') as f:
        pprint(topics, f)

    df_topic_sents_keywords = format_topics_sentences(lda_model, corpus, texts)
    # Format
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']
    df_dominant_topic.to_csv('lda_results/' + csv_name + '.tsv', sep='\t')
    # Show
    print(df_dominant_topic.head(10))

    pyLDAvis.enable_notebook()
    vis = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary, mds='mmds', n_jobs=1)
    pyLDAvis.save_html(vis, vis_name)

    print("Finished LDA!")
    # pyLDAvis.show(vis)

if __name__ == "__main__":
    main()
