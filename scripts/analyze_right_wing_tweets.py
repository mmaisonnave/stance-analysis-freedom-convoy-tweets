import json
import sys
sys.path.append('..')

from src import io
from src.convoy_protest_dataset import DatasetType,ConvoyProtestDataset
from src.paths_handler import PathsHandler
from src.tweet import Tweet


io.info('Imports done.')

def main() -> None:
    """Main function to analyze right-wing tweets."""
    config = PathsHandler()

    hashtags = {
        '#FluTruxKlan',
        '#HoldTheLine',
        '#IStandWithTruckers',
        '#HonkHonk',
        '#TruckerConvoy2022'
    }

    # ========== Loading Tweet stances: ==========
    with open(config.get_path('tweet-evaluation-output'), 
            'r',
            encoding='utf-8'
            ) as file:
        tweet_id2stance = {tweet_stance_output['tweet_id']: tweet_stance_output['llm_response']
                        for tweet_stance_output in json.load(file)}

    io.info(f'Tweet with stances loaded, {len(tweet_id2stance):3,} tweet_ids found.')

    # ========== Loading Tweets: ==========
    hashtag2tweets = {}
    _, tweets,_  = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL, removed_repeated=True)
    io.info(f'Loaded {len(tweets):,} tweets from the dataset (repeated removed).')

    for hashtag in hashtags:
        hashtag_tweets = [tweet for tweet in tweets if hashtag.lower() in tweet.text.lower()]
        io.info(f'Hashtag: {hashtag:18} --- Tweets: {len(hashtag_tweets):6,}')
        hashtag2tweets[hashtag] = []  # Create the empty list here
        for tweet in hashtag_tweets:
            if tweet.id in tweet_id2stance and tweet_id2stance[tweet.id] == "right":
                hashtag2tweets[hashtag].append(tweet)
        
        io.info(f'Tweets with stance: {len(hashtag2tweets[hashtag]):,}')

    def most_relevant_tweets(tweets: list[Tweet]) -> dict[str,Tweet]:
        result = {}
        public_metrics = ['retweet_count', 
                        'reply_count', 
                        'like_count', 
                        'quote_count', 
                        'bookmark_count', 
                        'impression_count'
                        ]
        for public_metric in public_metrics:
            tweets.sort(key=lambda tweet: tweet.public_metrics['retweet_count'], 
                        reverse=True)
            if tweets[0].public_metrics[public_metric] > 0:
                most_important_tweet = {
                    'id': tweets[0].id,
                    'text': tweets[0].text,
                    'public_metrics': tweets[0].public_metrics,
                    'created_at': str(tweets[0].created_at),
                    'author_id': tweets[0].author_id,
                }
                result[public_metric] = most_important_tweet

        return result
    
    most_relevant_tweets_by_hashtag = {}
    for hashtag in hashtags:
        most_relevant_tweets_by_hashtag[hashtag] = most_relevant_tweets(hashtag2tweets[hashtag])
    
    with open(config.get_path('most_relevant_right_wing_tweets_per_hashtag'), 
            'w', 
            encoding='utf-8') as file:
        json.dump(most_relevant_tweets_by_hashtag, file, indent=4)

if __name__ == '__main__':
    # get name of the script
    script_name = sys.argv[0].split('/')[-1].split('.')[0]
    io.info(f'Starting script  "{script_name}".')
    main()
    io.info('Script completed successfully.')