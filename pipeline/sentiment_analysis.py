import pandas as pd
import argparse
import os
from plotnine import ggplot, ggsave, aes, geom_vline, geom_histogram


def sentiment_stats(df, file_name, output_dir):
    """
    params:
    df: dataframe
    """
    # Means of sentiment and subjectivity
    sent_mean = df['sentiment'].mean()
    subj_mean = df['subjectivity'].mean()

    # File names
    outfile_sent = file_name + 'sent_plot.jpg'
    outfile_subj = file_name + 'subj_plot.jpg'

    # Plot sentiment scores
    plt_sent = ggplot(df, aes(x='sentiment')) + geom_histogram(bins=30, color='black', fill='gray') + geom_vline(
        aes(xintercept=sent_mean),
        linetype='dashed', size=0.6)
    ggsave(plt_sent, filename=outfile_sent, path=output_dir)

    plt_subj = ggplot(df, aes(x='subjectivity')) + geom_histogram(bins=30, color='black', fill='gray') + geom_vline(
        aes(xintercept=subj_mean),
        linetype='dashed', size=0.6)
    ggsave(plt_subj, filename=outfile_subj, path=output_dir)

    mean_file_name = output_dir + '/' + 'means_' + file_name + '.txt'
    f = open(mean_file_name, mode='a', encoding='utf-8')
    f.write('sentiment mean: ' + sent_mean + '\n')
    f.write('subjectivity mean: ' + subj_mean + '\n')
    f.close()

def main(): 
    parser = argparse.ArgumentParser(description='List the content of a folder')

    # Add the arguments
    parser.add_argument('csv_file', help='preprocessed file for sentiment analysis')
    parser.add_argument('platform', help='platform of preprocessed file')

    # Execute the parse_args() method
    args = parser.parse_args()
    preprocessed_file = 'preprocessed_data/' + args.platform + '_preprocessed_' + args.csv_file

    # Create folder
    output_dir = 'sentiment_analysis_results'
    os.makedirs(output_dir, exist_ok=True)

    # file paths
    file_name = args.csv_file.split(".")[0]

    # Sentiment statistics
    df = pd.read_csv(preprocessed_file, delimiter='\t')
    sentiment_stats(df, file_name, output_dir)

    print("Finished sentiment statistics.")
    
if __name__ == '__main__':
    main()

