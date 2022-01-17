import pandas as pd
import datetime
import argparse
import os
from pattern.nl import sentiment
# python preprocessing.py FB_NOS_NU_Telegraaf_NRC_all_endFeb.csv fb

import nltk
from nltk.corpus import stopwords
import re
import spacy

import glob

def read_file(csv_file):
    """
    params:
    csv_file: file to be processed

    returns: dataframe
    """
    df = pd.read_csv(csv_file, delimiter=';').fillna('None')

    return df


def df_preprocessing(df, platform):
    """
    params:
    df: dataframe
    platform: type of platform (facebook, twitter, etc.)

    returns: dataframe
    """
    if (platform=='fb'):
        # Rename columns
        df = df.rename(columns={'like.summary.total_count': 'like_count',
                                'love.summary.total_count': 'love_count',
                                'haha.summary.total_count': 'haha_count',
                                'wow.summary.total_count': 'wow_count',
                                'sad.summary.total_count': 'sad_count',
                                'angry.summary.total_count': 'angry_count',
                                'message': 'text'
                                })

        # Reformat date
        df['query_time'] = df['query_time'].apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').date().strftime(
                '%Y-%m-%d') if x != 'None' else 'None')
        df['created_time'] = df['created_time'].apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S%z').date().strftime(
                '%Y-%m-%d') if x != 'None' else 'None')

    # Remove rows where messages are empty or character length smaller than 10
    df = df[(df['text'] != 'None') | (df['text'].apply(lambda x: len(x) >= 10))]

    # drop duplicates
    df = df.drop_duplicates(subset='text')

    return df

def stopwords_merged():
    """
    Merge all stopwords into one stopwords list
    returns list of stopwords
    """
    # Start with nltk
    stopwords_all = stopwords.words('dutch')

    # # Get paths with stopwords
    paths = glob.glob('stopwords/*.txt')
    for file in paths:
        with open(file, 'rb') as f:
            stopwords_list = f.read().splitlines()
            stopwords_all += stopwords_list

    unique_stopwords = list(set(stopwords_all))
    return unique_stopwords


def preprocess_text(text, nlp):
    """
    params:
    text: text string
    nlp: language model for tokenization and pos-tagging

    returns: list of tokenized words, clean text, sentiment and subjectivity
    """
    # Remove punctuations; if there is a letter attached, append to word before
    # there's -> theres
    no_urls = re.sub(r"http\S+", "", text)
    punctuations = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~’”“'
    text_clean = no_urls.translate(str.maketrans('', '', punctuations)).lower()

    # Tokenize sentence
    doc = nlp(text_clean)

    tokens_pos = []
    for token in doc:
        # if token.text not in stopwords_merged():
        #     pass
        # else:
        tokens_pos.append((token.text, token.pos_))
    text_clean = ' '.join(word[0] for word in tokens_pos)
    if text_clean == '':
        text_clean = 'None'

    sent = sentiment(text)[0]
    subj = sentiment(text)[1]
    return sent, subj, text_clean, tokens_pos

def create_preprocessed_file(df, outfile_name):
    """
    params:
    df: dataframe

    returns: None
    """
    # Each word in the lexicon has scores for:
    # 1)     polarity: negative vs. positive    (-1.0 => +1.0)
    # 2) subjectivity: objective vs. subjective (+0.0 => +1.0)
    # 3)    intensity: modifies next word?      (x0.5 => x2.0)
    nlp = spacy.load('nl_core_news_sm')

    # Add columns sentiment, subjectivity, tokens+POS
    df[['sentiment', 'subjectivity', 'clean_text', 'tokens_pos']] = df.apply(lambda x: preprocess_text(x.text, nlp),
                                                                                             1, result_type='expand')
    # Remove empties
    df = df[df['clean_text'] != 'None']

    df.to_csv(outfile_name, index=False, sep='\t', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description='List the content of a folder')

    # Add the arguments
    parser.add_argument('csv_file', help='file to be preprocessed')
    parser.add_argument('platform', help='which platform')

    # Execute the parse_args() method
    args = parser.parse_args()

    # Create folder
    output_dir = 'preprocessed_data'
    os.makedirs('preprocessed_data', exist_ok=True)

    # file paths
    csv_out = output_dir + '/' + args.platform + '_preprocessed_' + args.csv_file

    print("Starting preprocessing: might take awhile.")

    df = read_file(args.csv_file)
    df = df_preprocessing(df, args.platform)
    create_preprocessed_file(df, csv_out)

    print("Finished preprocessing data and saved file to preprocessed_data folder.")


if __name__ == '__main__':
    main()

