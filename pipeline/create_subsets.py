import pandas as pd
import argparse
import os

def create_high_sent_subj_dataset(df, file_name, output_dir):
    """
    params:
    df: dataframe
    """

    # Get long comments with high sentiment (+/-) AND high subjectivity score
    sent_df = df[(df['sentiment'] >= 0.25) | (df['sentiment'] <= -0.25)]
    sent_subj_df = sent_df[sent_df['subjectivity'] >= 0.4]

    # Drop rows with very short comments
    df = sent_subj_df[(sent_subj_df['text'].apply(lambda x: len(x) >= 250))]

    outfile_name = output_dir + '/' + 'high_sent_subj' + file_name + '.csv'
    df.to_csv(outfile_name, index=False, sep='\t')

def create_pos_neg_dataset(df, file_name, output_dir):
    """
    params:
    df: dataframe
    file_name: preprocessed file
    output_dir: output directory
    """

    # Split up the corpus in positive and negative comments
    pos_df = df[df['sentiment'] >= 0.20]
    neg_df = df[df['sentiment'] <= -0.20]

    pos_outfile_name = output_dir + '/' + 'pos' + file_name + '.csv'
    neg_outfile_name = output_dir + '/' + 'neg' + file_name + '.csv'

    pos_df.to_csv(pos_outfile_name, index=False, sep='\t')
    neg_df.to_csv(neg_outfile_name, index=False, sep='\t')

def create_keywords_dataset(df, file_name, output_dir):
    """
    params:
    df: dataframe
    file_name: preprocessed file
    output_dir: output directory
    """
    bloodthinner = ['bloedverdunn', 'antistolling', 'coagulatie', 'bloedstolling', 'bloedproppen', 'stollingsprobleem', 'vwd']
    pregnancy = ['zwanger', 'kinderwens', 'borstvoeding', 'vruchtbaarheid', 'geboorte', 'bevallingsstoornissen', 'kinderen willen',
                 'kind willen', 'kind krijgen']
    immun = ['aandoening', 'hematologisch', 'maligniteit',
            'nierfalen', 'dialyse', 'orgaan', 'stamcel', 'transplantatie', 'immuun', 'hiv',
            'uitstellen', 'chemo', 'huid','psoriasis', 'hidradenitis',
            'suppurativa','eczeem', 'urticaria', 'auto-immuun', 'sle', 'dermato',
            'myositis','vasculitis', 'sclerodermie', 'kanker',
            'lymfom', 'melanom', 'hematolologie', 'long',
            'ild', 'cystic fibrosis', 'transplantatie',
            'multiple sclerosis', 'ms', 'nieren', 'maag', 'lever', 'darm', 'ibd', 'ibs',
            'gastro-intestinale', 'tumor', 'afweerstoornis', 'reuma', 'beperking',
            'chronisch', 'cfs']

    bt_df = df[df['clean_text'].str.contains('|'.join(bloodthinner))]
    pregnancy_df = df[df['clean_text'].str.contains('|'.join(pregnancy))]
    immun_df = df[df['clean_text'].str.contains('|'.join(immun))]

    bt_name = output_dir + '/' + 'bloodthinner' + file_name + '.csv'
    pregnancy_name = output_dir + '/' + 'pregnancy' + file_name + '.csv'
    immun_name = output_dir + '/' + 'immuno' + file_name + '.csv'

    bt_df.to_csv(bt_name, index=False, sep='\t')
    pregnancy_df.to_csv(pregnancy_name, index=False, sep='\t')
    immun_df.to_csv(immun_name, index=False, sep='\t')

def main():
    parser = argparse.ArgumentParser(description='List the content of a folder')

    # Add the arguments
    parser.add_argument('csv_file', help='preprocessed file for sentiment analysis')
    parser.add_argument('platform', help='platform of preprocessed file')

    # Execute the parse_args() method
    args = parser.parse_args()
    preprocessed_file = 'preprocessed_data/' + args.platform + '_preprocessed_' + args.csv_file

    # Create folder
    output_dir = 'preprocessed_data/data_subsets'
    os.makedirs(output_dir, exist_ok=True)

    # file paths
    file_name = args.csv_file.split('.')[0]

    # Sentiment statistics
    df = pd.read_csv(preprocessed_file, delimiter='\t')
    create_high_sent_subj_dataset(df, file_name, output_dir)
    create_pos_neg_dataset(df, file_name, output_dir)
    create_keywords_dataset(df, file_name, output_dir)

    print('Finished creating subsets.')

if __name__ == '__main__':
    main()
