import sys
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

    plt.figure(figsize=(6.4, 4.8))

    for i, hashtag in enumerate(hashtags_of_interest):
        if hashtag in df.columns:
            plt.plot(df['date'], df[hashtag], label=f'#{hashtag}', color=palette[i])
            plt.fill_between(df['date'], 0, df[hashtag], alpha=0.2, color=palette[i])

    # Increase font sizes
    title_fontsize = 20
    label_fontsize = 16
    tick_fontsize = 14
    legend_fontsize = 14


    plt.title('Hashtag Usage Over Time', fontsize=title_fontsize)
    plt.xlabel('Date', fontsize=label_fontsize)
    plt.ylabel('Percentage of Total Tweets (%)', fontsize=label_fontsize)

    plt.legend(fontsize=legend_fontsize)
    plt.grid(True)
    plt.xticks(rotation=45, fontsize=tick_fontsize)
    plt.yticks(fontsize=tick_fontsize)


    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))


    # Add vertical lines
    important_dates = [
        datetime(2022, 1, 16),
        datetime(2022, 1, 24),
        datetime(2022, 1, 30)
    ]

    for date in important_dates:
        plt.axvline(x=date, color='darkgray', linestyle='--', linewidth=1.5)

    plt.tight_layout()
    plt.savefig(paths.get_path('hashtag_over_time_plot'), dpi=300)




    # Plotting total tweets over time
    plt.figure(figsize=(6.4, 4.8))
    plt.plot(df['date'], df['total_tweets'], label='Total Tweets', color='purple')
    plt.fill_between(df['date'], 0, df['total_tweets'], alpha=0.2, color='purple')

    # Increase font sizes
    plt.title('Total Tweets Over Time', fontsize=title_fontsize)
    plt.xlabel('Date', fontsize=label_fontsize)
    plt.ylabel('Total Tweets', fontsize=label_fontsize)

    plt.legend(fontsize=legend_fontsize)
    plt.grid(True)
    plt.xticks(rotation=45, fontsize=tick_fontsize)
    plt.yticks(fontsize=tick_fontsize)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))

    # Add vertical lines (same important dates)
    for date in important_dates:
        plt.axvline(x=date, color='darkgray', linestyle='--', linewidth=1.5)

    plt.tight_layout()

    # Save the second plot to a different file
    plt.savefig(paths.get_path('tweets_over_time_plot'), dpi=300)

    io.ok('Done with script: create_hashtags_over_time_plot.py')


if __name__ == '__main__':
    main()