import sys
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt 
import seaborn as sns
import matplotlib.dates as mdates

from datetime import datetime, timedelta

sys.path.append('..')

from src import paths_handler
from src import io
from src.convoy_protest_dataset import DatasetType
from src.convoy_protest_dataset import ConvoyProtestDataset

def main():
    io.info('Starting script: create_hashtags_over_time_plot.py')
    paths = paths_handler.PathsHandler()

    # Getting all tweets from the dataset
    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL)
    io.info(f'Loaded {len(tweets):,} tweets from ConvoyProtestDataset')

    # Removing duplicates
    visited = set()
    unique_in_range_tweets = []
    for tweet in tweets:
        if tweet.id not in visited:
            unique_in_range_tweets.append(tweet)
            visited.add(tweet.id)
    io.info(f"Number of unique tweets: {len(unique_in_range_tweets):,}")


    # Filtering tweets to the date range of interest
    start = datetime(2022, 1, 1)
    end = datetime(2022, 3, 31)

    unique_in_range_tweets = [tweet for tweet in unique_in_range_tweets if start <= tweet.created_at <= end]
    io.info(f'Number of unique tweets in range: {len(unique_in_range_tweets):,}')



    all_hashtags = {hashtag for tweet in unique_in_range_tweets for hashtag in tweet.hashtags}

    frequency = defaultdict(int)
    tweet_counts_per_day = defaultdict(int)

    for tweet in unique_in_range_tweets:
        tweet_date = tweet.created_at.date()
        tweet_counts_per_day[tweet_date] += 1
        for hashtag in tweet.hashtags:
            frequency[(tweet_date, hashtag)] += 1

    dates = []
    hashtags = []
    counts = []
    total_tweets = []

    date = start
    while date <=end:
        current_date = date.date()
        day_total = tweet_counts_per_day[current_date]
        for hashtag in all_hashtags:
            dates.append(date)
            hashtags.append(hashtag)
            counts.append(frequency[(current_date, hashtag)])
            total_tweets.append(day_total)


        date = date + timedelta(days=1)


    # Filtering to hashtag of interests:
    hashtags_of_interest = [
        'flutruxklan', 
        'truckerconvoy2022',
        'holdtheline',
        'honkhonk',
        'istandwithtruckers'
    ]

    df = pd.DataFrame({
        'date': dates,
        'hashtag': hashtags,
        'count': counts,
        'total_tweets': total_tweets

    })
    df = df[df['hashtag'].isin(hashtags_of_interest)]

    # Create new data frame with one column for each hashtag of interest
    # Save total_tweets per date before pivot
    total_tweets_per_day = df.groupby('date')['total_tweets'].first()

    # Create new data frame with one column for each hashtag of interest
    df = df.pivot(index='date', columns='hashtag', values='count').fillna(0)

    # Add total_tweets back
    df['total_tweets'] = total_tweets_per_day

    df = df.reset_index()


    output_path = paths.get_path('hashtag_over_time_dataframe')
    io.info(f'Writing hashtags over time to {output_path}')


    # Normalizing by total tweets on each day.
    for hashtag in hashtags_of_interest:
        df[hashtag] = df[hashtag]/df['total_tweets']

    df.to_csv(
        output_path,
        index=False
    )

    # ploting

    # Convert to percentage
    for hashtag in hashtags_of_interest:
        df[hashtag] = df[hashtag] * 100

    # Seaborn style
    palette = sns.color_palette("tab10", n_colors=len(hashtags_of_interest))
    sns.set_style("whitegrid")

    # Increase font sizes
    title_fontsize = 20
    label_fontsize = 16
    tick_fontsize = 14
    legend_fontsize = 14

    important_dates = [
        datetime(2022, 1, 16),
        datetime(2022, 1, 24),
        # datetime(2022, 1, 30)
    ]

    # Create two subplots (one above the other)
    fig, (ax2, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(9.6, 9.6), sharex=True)

    # First plot: Hashtags usage over time
    for i, hashtag in enumerate(hashtags_of_interest):
        if hashtag in df.columns:
            ax1.plot(df['date'], df[hashtag], label=f'#{hashtag}', color=palette[i])
            ax1.fill_between(df['date'], 0, df[hashtag], alpha=0.2, color=palette[i])

    ax1.set_title('Hashtag Usage Over Time', fontsize=title_fontsize)
    ax1.set_ylabel('Percentage of Total Tweets (%)', fontsize=label_fontsize)

    ax1.set_xlabel('Date', fontsize=label_fontsize)
    ax1.legend(fontsize=legend_fontsize)
    ax1.grid(True)
    ax1.tick_params(axis='x', rotation=45, labelsize=tick_fontsize)
    ax1.tick_params(axis='y', labelsize=tick_fontsize)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))

    # Add vertical lines
    for date in important_dates:
        ax1.axvline(x=date, color='black', linestyle='--', linewidth=1.5)

    # Second plot: Total tweets over time
    ax2.plot(df['date'], df['total_tweets'], label='Total Tweets', color='purple')
    ax2.fill_between(df['date'], 0, df['total_tweets'], alpha=0.2, color='purple')

    ax2.set_title('Total Tweets Over Time', fontsize=title_fontsize)
    ax2.set_ylabel('Total Tweets', fontsize=label_fontsize)
    ax2.legend(fontsize=legend_fontsize)
    ax2.grid(True)
    ax2.tick_params(axis='x', rotation=45, labelsize=tick_fontsize)
    ax2.tick_params(axis='y', labelsize=tick_fontsize)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))




    important_dates = [
        datetime(2022, 1, 22),
        datetime(2022, 2, 23),
    ]
    # Add vertical lines (same important dates)
    for date in important_dates:
        ax2.axvline(x=date, color='black', linestyle='--', linewidth=1.5)


    for ax in [ax1,ax2]:
        # Get the current x-tick labels of the second subplot
        xticks = ax.get_xticklabels()

        # Remove the last x-tick label
        xticks[-1].set_text('')

    fig.canvas.draw()
    plt.tight_layout()

    # Save the figure
    plt.savefig(paths.get_path('hashtags_and_total_tweets_over_time'), dpi=300)



    io.ok('Done with script: create_hashtags_over_time_plot.py')


if __name__ == '__main__':
    main()