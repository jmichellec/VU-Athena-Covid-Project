import pandas as pd
import argparse
import matplotlib.pyplot as plt
import os
from collections import Counter
from yellowbrick.text import FreqDistVisualizer
# import rake
import numpy as np
from ast import literal_eval
from nltk import ngrams


from sklearn.feature_extraction.text import CountVectorizer


def read_file(csv_file):
    """
    params:
    csv_file: file to be processed

    returns: dataframe
    """
    df = pd.read_csv(csv_file, delimiter='\t')

    return df

def flatten(texts):
    """
    Flattens list of lists
    params:
    texts: list of lists

    return: flattened list

    """
    flattened_list = [item for items in texts for item in items]
    return flattened_list

def texts_list(df):
    """ Turn string of list into list and append to bigger list
    params:
    df: preprocessed dataframe
    returns: list of lists (tokenized)

    """
    texts = []
    for text in df['tokens_pos']:
        texts.append(literal_eval((text)))
    return texts

def create_corpus(flatten_tokenized_texts):
    """
    params:
    tokenized_texts: list of tokenized sentences

    returns:
    dictionary with words as keys and frequency as values
    dictionary with pos as keys and frequency as values
    dictionary with (token, pos) as keys and frequency as values
    """
    corpus = []
    pos_corpus = []
    token_pos_corpus = []
    for token, pos in flatten_tokenized_texts:
        corpus += token
        pos_corpus += pos
        token_pos_corpus += (token, pos)
    corpus = Counter(corpus)
    pos_corpus = Counter(pos_corpus)
    token_pos_corpus = Counter(token_pos_corpus)

    return corpus, pos_corpus, token_pos_corpus

def most_frequent(corpus, file_name, corpus_type):
    """
    saves plot of 20 most frequent words to folder

    params:
    corpus: count word dictionary
    file_name: name of file to be processed
    """

    if corpus_type == 'token':
        outfile_name = 'keyword_analysis_results/mf_token_' + file_name + '.png'
    elif corpus_type == 'pos':
        outfile_name = 'keyword_analysis_results/mf_pos_' + file_name + '.png'
    elif corpus_type == 'token_pos':
        outfile_name = 'keyword_analysis_results/mf_token_pos_' + file_name + '.png'

    plot_counter(corpus, 'most frequent words', outfile_name)

def kwic(corpus, word):
    """
    params:
    corpus: corpus
    word: word for the context

    returns: list of keywords in context
    """
    kwic_list = list(corpus.concordance(word, width=5, lines=5))
    return kwic_list

def ngrams_list(tokenized_texts, n):
    """
    params:
    tokenized_texts: list of lists containing tokenized texts
    n: number of words for gram

    returns: list consisting of n-grams
    """
    ngram_tokens_list = []
    ngram_pos_list = []
    for text in tokenized_texts:

        tokens_list = []
        pos_list = []

        for token, pos in text:
            tokens_list.append(token)
            pos_list.append(pos)
        ngram_tokens = list(ngrams(tokens_list, n))
        ngram_pos = list(ngrams(pos_list, n))

        ngram_tokens_list.append(ngram_tokens)
        ngram_pos_list.append(ngram_pos)

    return ngram_tokens_list, ngram_pos_list

def plot_counter(counter_object, title, outfile_name):
    keys = []
    values = []
    for item in counter_object.most_common(20):
        keys.append(item[0])
        values.append(item[1])

    keys = list(reversed(keys))
    values = list(reversed(values))

    df = pd.DataFrame({'freq': values}, index=keys)
    df.plot.barh(align='center')
    plot_ttl = 'Top 20 word ' + title
    plt.title(plot_ttl)
    plt.xlabel('Frequency')
    plt.tight_layout()
    plt.savefig(outfile_name, bbox_inches='tight')

def word_collocation(tokenized_texts, n, file_name):
    """
    Save plot of top 20 word collocations (word following each other)

    params:
    tokenized_texts: list of lists containing tokenized texts
    n: number of ngrams
    file_name:
    """

    ngram_tokens, ngram_pos = ngrams_list(tokenized_texts, n)

    flat_ngram_tokens = flatten(ngram_tokens)
    flat_ngram_pos = flatten(ngram_pos)

    ngram_count_tokens = Counter(flat_ngram_tokens)
    ngram_count_pos = Counter(flat_ngram_pos)

    outfile_tokens = 'keyword_analysis_results/colloc_tokens' + file_name + '.png'
    outfile_pos = 'keyword_analysis_results/colloc_pos' + file_name + '.png'

    plot_counter(ngram_count_tokens, 'collocation', outfile_tokens)
    plot_counter(ngram_count_pos, 'collocation', outfile_pos)

def word_cooccurence(df, filename):
    docs = df.clean_text.tolist()
    counter = CountVectorizer(ngram_range=(1, 1))
    X = counter.fit_transform(docs)
    # X[X > 0] = 1 # run this line if you don't want extra within-text cooccurence (see below)
    Xc = (X.T * X)  # this is co-occurrence matrix in sparse csr format
    Xc.setdiag(0)  # sometimes you want to fill same word cooccurence to 0
    print(docs)
    print(Xc.todense())
    print(counter.vocabulary_)

    # cv = CountVectorizer(ngram_range=(2, 2))
    # docs = cv.fit_transform(df.clean_text)
    # # d = cv.vocabulary_
    # keys = cv.get_feature_names()
    # visualizer = FreqDistVisualizer(
    #     features=keys, size=(1080, 720)
    # )
    # visualizer.fit(docs)
    # visualizer.show()
    #
    # outfile_name = 'keyword_analysis_results/cooc_' + filename + '.png'
    # plt.barh(keys, values, align='center')
    # plt.title('Top word cooccurrences')
    # plt.xlabel('Frequency')
    # plt.tight_layout()
    # plt.savefig(outfile_name, bbox_inches='tight')


def main():
    parser = argparse.ArgumentParser(description='List the content of a folder')

    # Add the arguments
    parser.add_argument('csv_file', help='preprocessed file for sentiment analysis')
    parser.add_argument('platform', help='platform of preprocessed file')

    # Execute the parse_args() method
    args = parser.parse_args()
    preprocessed_file = 'preprocessed_data/' + args.platform + '_preprocessed_' + args.csv_file
    df = pd.read_csv(preprocessed_file, delimiter='\t').head(5)

    # Create folder
    output_dir = 'keyword_analysis_results'
    os.makedirs(output_dir, exist_ok=True)

    # file paths
    file_name = args.csv_file.split('.')[0]
    tokenized_texts = texts_list(df)
    flatten_tokenized_texts = flatten(tokenized_texts)
    corpus, pos_corpus, token_pos_corpus = create_corpus(flatten_tokenized_texts)

    # words = []
    # for word in words:
    #     kwic(corpus, word)

    # word_collocation(tokenized_texts, 2, file_name)
    # most_frequent(corpus, file_name, 'token')
    # word_cooccurence(df, file_name)

if __name__ == '__main__':
    main()

