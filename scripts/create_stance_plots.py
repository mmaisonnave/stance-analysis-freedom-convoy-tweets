"""
Create histogram of user stance and tweet stance plots (left, right, neutral).
"""
import pandas as pd
import os
import sys
from pathlib import Path
import json
from collections import Counter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Add the parent directory to sys.path in a more robust way
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.paths_handler import PathsHandler
from src.convoy_protest_dataset import ConvoyProtestDataset, DatasetType
from src.tweet import Tweet

from src import io
import argparse


def user_histogram() -> None:
    """
    Create a histogram of the user stance scores.
    """
    io.info("Initializing PathsHandler and loading output paths.")
    config: PathsHandler = PathsHandler()
    output_plot: str = config.get_path('user-stance-plot')
    json_file: str = config.get_path('user-evaluation-output')

    io.info(f"Loading user evaluation data from {json_file}")
    with open(json_file, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

    io.info(f"Loaded {len(data)} user evaluation records.")
    scores: list[int] = [int(results['llm_response']['score'])
                         for results in data
                         if results['llm_response']['score'] != 'Not enough information']

    io.info(f"Number of valid user scores (removing not enough information): {len(scores)}")
    # Create Histogram of scores
    sns.set_style(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 4))

    histogram: list[tuple[int, int]] = [(score, freq)
                                        for score, freq in Counter(scores).items()]

    histogram.sort(key=lambda x: x[0])
    io.info(f"Histogram bins: {histogram}")

    ax.bar([histogram[0] for histogram in histogram],
           [histogram[1] for histogram in histogram],
           color='blue',
           alpha=0.7)

    # add numbers on top of the bars
    for i, (score, freq) in enumerate(histogram):
        ax.text(i+1, freq + 0.5, str(freq), ha='center', va='bottom')

    ax.set_xlabel('Score')
    ax.set_ylabel('Number of Users')

    io.info(f"Saving user stance histogram plot to {output_plot}")
    fig.savefig(output_plot, dpi=300)



def full_tweet_plot() -> None:
    config: PathsHandler = PathsHandler()
    output_plot: str = config.get_path('tweet-stance-plot')
    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL, removed_repeated=True)

    tweet_plot(tweets=tweets, output_plot=output_plot)

def tweet_plot(tweets: list[Tweet], output_plot: str) -> None:
    """
    Create a plot of the number of right-wing, left-wing, and neutral tweets per day.
    """

    io.info("Initializing PathsHandler and loading output paths.")
    config: PathsHandler = PathsHandler()

    json_file: str = config.get_path('tweet-evaluation-output')

    io.info(f"Loading tweet evaluation data from {json_file}")
    with open(json_file, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

    io.info(f"Loaded {len(data)} tweet evaluation records.")


    io.info(f"Total tweets in dataset: {len(tweets):,}")

    computed_tweet_ids: set[str] = {item['tweet_id'] for item in data}
    tweets: list[Tweet] = [tweet for tweet in tweets if tweet.id in computed_tweet_ids]

    io.info(f"Tweets after filtering by evaluated IDs: {len(tweets):,}")

    id2stance: dict[str, str] = {item['tweet_id']: item['llm_response'] for item in data }

    neutral_tweet_counts_per_day: dict[datetime.date, int] = {}
    right_tweet_counts_per_day: dict[datetime.date, int] = {}
    left_tweet_counts_per_day: dict[datetime.date, int] = {}

    start: datetime = datetime(2022, 1, 1)
    end: datetime = datetime(2022, 3, 31)

    io.info(f"Initializing daily tweet counts from {start.date()} to {end.date()}.")
    for date in (start + timedelta(days=i) for i in range((end - start).days + 1)):
        neutral_tweet_counts_per_day[date.date()] = 0
        right_tweet_counts_per_day[date.date()] = 0
        left_tweet_counts_per_day[date.date()] = 0

    io.info("Counting tweets per day by stance.")
    for tweet in tweets:
        tweet_date = tweet.created_at.date()
        if start.date() <= tweet_date <= end.date():
            stance = id2stance.get(tweet.id)
            if stance == 'neutral':
                neutral_tweet_counts_per_day[tweet_date] += 1
            elif stance == 'right':
                right_tweet_counts_per_day[tweet_date] += 1
            elif stance == 'left':
                left_tweet_counts_per_day[tweet_date] += 1
            else:
                io.info(f"Unknown stance encountered: {stance}")
                raise ValueError(f"Unknown stance: {stance}")

    sorted_dates = sorted(neutral_tweet_counts_per_day.keys())

    io.info("Preparing data for plotting.")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    left_counts = [-left_tweet_counts_per_day[d] for d in sorted_dates]
    right_counts = [+right_tweet_counts_per_day[d] for d in sorted_dates]
    neutral_counts = [neutral_tweet_counts_per_day[d] for d in sorted_dates]
    # left_plus_right = [l + r for l, r in zip(left_counts, right_counts)]
    # total_counts = [l + r + n for l, r, n in zip(left_counts, right_counts, neutral_counts)]

    io.info("Plotting tweet stance counts per day.")

    ax.plot(sorted_dates, neutral_counts, marker='o', linestyle='-', label='Neutral', color='gray')
    ax.fill_between(sorted_dates, [0] * len(sorted_dates), neutral_counts, alpha=0.1, color='gray')

    ax.plot(sorted_dates, left_counts, marker='o', linestyle='-', label='Left')
    ax.fill_between(sorted_dates, [0] * len(sorted_dates), left_counts, alpha=0.3)

    ax.plot(sorted_dates, right_counts, marker='o', linestyle='-', label='Right')
    ax.fill_between(sorted_dates, [0] * len(sorted_dates), right_counts, alpha=0.3)

    # ax.plot(sorted_dates, total_counts, marker='o', linestyle='-', label='Neutral')
    # ax.fill_between(sorted_dates, left_plus_right, total_counts, alpha=0.3)

    ax.set_title('Number of Tweets per Day')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Tweets')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    fig.tight_layout()

    # Set y-tick labels to show positive values for both above and below the x axis
    yticks = ax.get_yticks()
    ax.set_yticklabels([str(abs(int(y))) for y in yticks])

    io.info(f"Saving tweet stance plot to {output_plot}")
    fig.savefig(output_plot, dpi=300)


# def proportion_left_right() -> None:
#     io.info("Initializing PathsHandler and loading output paths.")
#     config: PathsHandler = PathsHandler()

#     output_plot: str = config.get_path('tweet-proportion-stance-plot')
#     json_file: str = config.get_path('tweet-evaluation-output')

#     io.info(f"Loading tweet evaluation data from {json_file}")
#     with open(json_file, 'r', encoding='utf-8') as file:
#         data: dict = json.load(file)

#     io.info(f"Loaded {len(data)} tweet evaluation records.")

#     io.info("Loading dataset and filtering tweets.")
#     _, tweets, _ = ConvoyProtestDataset.get_dataset(
#         data_type=DatasetType.ALL,
#         removed_repeated=True)

#     io.info(f"Total tweets in dataset: {len(tweets):,}")

#     computed_tweet_ids: set[str] = {item['tweet_id'] for item in data}
#     tweets: list[Tweet] = [tweet for tweet in tweets if tweet.id in computed_tweet_ids]

#     io.info(f"Tweets after filtering by evaluated IDs: {len(tweets):,}")

#     id2stance: dict[str, str] = {item['tweet_id']: item['llm_response'] for item in data }

#     right_tweet_counts_per_day: dict[datetime.date, int] = {}
#     left_tweet_counts_per_day: dict[datetime.date, int] = {}

#     start: datetime = datetime(2022, 1, 1)
#     end: datetime = datetime(2022, 3, 31)

#     io.info(f"Initializing daily tweet counts from {start.date()} to {end.date()}.")
#     for date in (start + timedelta(days=i) for i in range((end - start).days + 1)):
#         right_tweet_counts_per_day[date.date()] = 0
#         left_tweet_counts_per_day[date.date()] = 0

#     io.info("Counting tweets per day by stance.")
#     for tweet in tweets:
#         tweet_date = tweet.created_at.date()
#         if start.date() <= tweet_date <= end.date():
#             stance = id2stance.get(tweet.id)
#             if stance == 'right':
#                 right_tweet_counts_per_day[tweet_date] += 1
#             elif stance == 'left':
#                 left_tweet_counts_per_day[tweet_date] += 1

#     sorted_dates = sorted(left_tweet_counts_per_day.keys())
#     io.info("Preparing data for plotting.")
#     fig, ax = plt.subplots(figsize=(12, 6))

#     left_counts = [left_tweet_counts_per_day[d] for d in sorted_dates]
#     right_counts = [right_tweet_counts_per_day[d] for d in sorted_dates]
#     proportion_left = [l / (l + r) if (l + r) > 0 else 0 for l, r in zip(left_counts, right_counts)]
#     right_plus_left_proportions = [(r + l) / (l + r) if (l + r) > 0 else 0 
#                                    for l, r in zip(left_counts, right_counts)]
    
#     total_counts = [l + r for l, r in zip(left_counts, right_counts)]
#     # remove from proprotion_left where total_counts is 0
#     proportion_left = [p for p, t in zip(proportion_left, total_counts) if t > 0]
#     # remove from sorted_dates where total_counts is 0
#     sorted_dates = [d for d, t in zip(sorted_dates, total_counts) if t > 0]
#     # remove from right_plus_left_proportions where total_counts is 0
#     right_plus_left_proportions = [p for p, t in zip(right_plus_left_proportions, total_counts) if t > 0]


#     io.info("Plotting tweet stance counts per day.")
#     ax.plot(sorted_dates, proportion_left, marker='o', linestyle='-', label='proportion left')
#     ax.fill_between(sorted_dates, [0] * len(sorted_dates), proportion_left, alpha=0.3)

#     ax.fill_between(sorted_dates, right_plus_left_proportions , proportion_left, alpha=0.3)



#     ax.set_title('Proportion of Tweets per Day')
#     ax.set_xlabel('Date')
#     ax.set_ylabel('Number of Tweets')
#     ax.tick_params(axis='x', rotation=45)
#     ax.legend()
#     fig.tight_layout()

#     io.info(f"Saving tweet stance plot to {output_plot}")
#     fig.savefig(output_plot, dpi=300)


def hashtag_plots() -> None:
    config: PathsHandler = PathsHandler()
    base_output: str = config.get_path('tweet-stance-plot')
    base, ext = os.path.splitext(base_output)


    for dataset_type in [DatasetType.FLUTRUXKLAN, 
                         DatasetType.HOLDTHELINE,
                         DatasetType.HONKHONK,
                         DatasetType.TRUCKERCONVOY2022,
                         DatasetType.ISTANDWITHTRUCKERS
                         ]:
        # _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=dataset_type, removed_repeated=True)
        tweets = ConvoyProtestDataset.get_hashtag_tweets(dataset_type)
        output_plot = f"{base}_{dataset_type.value}{ext}"
        tweet_plot(tweets=tweets, output_plot=output_plot)

def histogram_tweets_per_hashtag() -> None:
    config: PathsHandler = PathsHandler()

    json_file: str = config.get_path('tweet-evaluation-output')

    output_plot: str = config.get_path('hashtag-histogram-stance-plot')

    io.info(f"Loading tweet evaluation data from {json_file}")
    with open(json_file, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

    id2stance: dict[str, str] = {item['tweet_id']: item['llm_response'] for item in data}

    plot_data = {
        'count': [],
        'hashtag': [],
        'stance': []
    }
    for dataset_type in [DatasetType.FLUTRUXKLAN,
                         DatasetType.HOLDTHELINE,
                         DatasetType.HONKHONK,
                         DatasetType.TRUCKERCONVOY2022,
                         DatasetType.ISTANDWITHTRUCKERS
                         ]:
        _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=dataset_type, removed_repeated=True)

        tweets = [tweet for tweet in tweets if tweet.id in id2stance]

        right_count = len([tweet for tweet in tweets if id2stance[tweet.id] == 'right'])
        left_count = len([tweet for tweet in tweets if id2stance[tweet.id] == 'left'])
        neutral_count = len([tweet for tweet in tweets if id2stance[tweet.id] == 'neutral'])
        plot_data['count'].append(right_count)
        plot_data['count'].append(left_count)
        plot_data['count'].append(neutral_count)
        plot_data['hashtag'].append(dataset_type.value)
        plot_data['hashtag'].append(dataset_type.value)
        plot_data['hashtag'].append(dataset_type.value)
        plot_data['stance'].append('right')
        plot_data['stance'].append('left')
        plot_data['stance'].append('neutral')
    io.info("Preparing data for plotting.")
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_data = pd.DataFrame(plot_data)
    sns.set_style(style="whitegrid")
    sns.barplot(data=plot_data, x='hashtag', y='count', hue='stance', ax=ax)
    ax.set_title('Number of Tweets per Hashtag')
    ax.set_xlabel('Hashtag')
    ax.set_ylabel('Number of Tweets')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    io.info(f"Saving hashtag stance plot to {output_plot}")
    fig.savefig(output_plot, dpi=300)

def main() -> None:
    """
    Main function to create the plots.
    """
    parser = argparse.ArgumentParser(description="Create stance plots.")
    parser.add_argument('--user-plot', action='store_true', help='Create user stance histogram')
    parser.add_argument('--tweet-plot', action='store_true', help='Create tweet stance plot')
    parser.add_argument('--proportion-plot', action='store_true', help='Create tweet left/right proportion plot')  # Added argument
    parser.add_argument('--hashtag-plots', action='store_true', help='Create tweet stance plot')
    parser.add_argument('--hashtag-histogram', action='store_true', help='Create hashtag histogram plot')
    args = parser.parse_args()

    if args.user_plot:
        user_histogram()
    if args.tweet_plot:
        full_tweet_plot()
    if args.hashtag_plots:
        hashtag_plots()
    if args.hashtag_histogram:
        histogram_tweets_per_hashtag()



if __name__ == "__main__":
    main()
