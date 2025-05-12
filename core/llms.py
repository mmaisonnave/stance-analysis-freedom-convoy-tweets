# from enum import Enum
import json
import sys
import numpy as np
sys.path.append('..')

from src.paths_handler import PathsHandler
import torch
from transformers import pipeline, AutoTokenizer
from src import io

from typing import List
from src.tweet import Tweet
from openai import OpenAI


# class TweetPoliticalAlignment(Enum):
#     NEUTRAL = "neutral"
#     LEFT = "left-wing"
#     RIGHT = "right-wing"

class StanceDetector:

    def __init__(self):
        config = PathsHandler()
        stance_detector_config = config.get_variable('stance-detector-configuration')
        model_name = stance_detector_config['model-name']
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        self.pipe = pipeline(
              "text-generation",
              model=model_name,
              tokenizer=self.tokenizer,
              pad_token_id= self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
              torch_dtype=torch.bfloat16,
              device_map="mps",
              )
        
        self.system_messages = {
              "role": "system", 
              "content": stance_detector_config['system-prompt']
              }

    def evaluate_batch(self, tweets: list[str]) -> list[int]:
        prompts = [
            {
                "role": "user",
                "content": f"Tweet: {tweet}\nOutput:"
            }
            for tweet in tweets
        ]
        
        # Repeat the system message for each input
        full_inputs = [[self.system_messages, prompt] for prompt in prompts]

        outputs = self.pipe(
            full_inputs,
            max_new_tokens=3,
            batch_size=8,  # Adjust based on your hardware
        )

        scores = []
        for out in outputs:
            try:
                score = int(out["generated_text"][-1]['content'])  # Ensure correct access pattern
                assert 0 <= score <= 10 or score == -1
            except Exception:
                score = -1  # Fallback for malformed outputs
            scores.append(score)

        return scores




class OpenAIStanceDetector:
    def __init__(self):
        self.config = PathsHandler()


        self.stance_detector_config = self.config.get_variable('openai-tweet-stance-detector-configuration')
        io.info(f'Using detector configuration={self.stance_detector_config}')

        # Retrieving vars from config:
        SEED = self.stance_detector_config['seed']
        self.max_tweet_count = self.stance_detector_config['user-timeline-max-tweet-count']
        which_key = self.stance_detector_config['openai-key']

        io.info(f'Using seed={SEED}')
        io.info(f'Using max tweet count= {self.max_tweet_count}')
        io.info(f'Using key= {which_key}')


        self.rng = np.random.default_rng(seed=SEED)

        self.client = OpenAI(api_key= self.config.get_api_key(which=which_key))

    @staticmethod
    def format_evaluate_tweet_prompt(tweet:Tweet) -> str:
        return f"<user_query>\nTweet: {tweet.sanitized_text}\n</user_query>\n"

    @staticmethod
    def format_evaluate_user_prompt(tweets: List[Tweet]) -> str:
        formated_tweet_list = [f"tweet {ix+1}: {tweet.sanitized_text}" for ix, tweet in enumerate(tweets)]
        return f"<user_query>\n{'\n'.join(formated_tweet_list)}\n</user_query>"


    def evaluate_user(self, tweets: List[Tweet]) -> str:
        assert len(tweets)>0, 'Trying to evaluate a user with no tweets.'
        assert len({tweet.author_id for tweet in tweets})==1, 'Trying to evaluate tweets of multiple users at the same time.'

        io.info(f'Randomly choosing {self.max_tweet_count} tweets out of {len(tweets)}')
        selected_tweets = self.rng.choice(
            a=tweets,
            size=self.max_tweet_count,
            replace=False
        )

        # Setting up system prompt
        developer_content = self.config.get_prompt(self.stance_detector_config['user-eval-developer-prompt-name'])

        # Formatting up user input
        user_content = OpenAIStanceDetector.format_evaluate_user_prompt(selected_tweets)

        io.info('User input formatted:')
        for line in user_content.splitlines():
            io.info(line)

        assert len(developer_content) + len(user_content) < 5000 + self.max_tweet_count*280, 'Call to API with suspiciously big payload.'

        llm_response = self.client.responses.create(
            model=self.stance_detector_config['model-name'],
            input=[
                {
                    "role": "developer",
                    "content": developer_content
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        )
        io.info(f'response:             {llm_response}')
        io.info(f'response.output_text: {llm_response}')

        full_response = {
            'llm_response': json.loads(llm_response.output_text),
            'author_id': tweets[0].author_id,
            'formatted_user_input': user_content,
            'tweet_ids': [tweet.id for tweet in selected_tweets]
        }        

        return full_response


    def evaluate_tweet(self, tweet: Tweet) -> dict:
        developer_content = self.config.get_prompt(self.stance_detector_config['tweet-eval-developer-prompt-name'])
        user_content = OpenAIStanceDetector.format_evaluate_tweet_prompt(tweet)
        assert len(developer_content) + len(user_content) < 5000 + 280


        io.info('Evaluating single tweet, calling API. With input:')
        for line in user_content.splitlines():
            io.info(line)

        llm_response = self.client.responses.create(
            model=self.stance_detector_config['model-name'],
            input=[
                {
                    "role": "developer",
                    "content": developer_content
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        )

        io.info(f'Response:             {llm_response}')
        io.info(f'Response.output_text: {llm_response.output_text}')

        llm_response = llm_response.output_text.replace('Assistant Response: ', '')

        
        if 'right' in llm_response.lower():
            normalized_llm_response = 'right'
        elif 'left' in llm_response.lower():
            normalized_llm_response = 'left'
        elif 'neutral' in llm_response.lower():
            normalized_llm_response = 'neutral'
        else:
            raise ValueError('Got wrong response from LLM. Problem with prompt?')

        full_response = {
            'llm_response': normalized_llm_response,
            'tweet_id': tweet.id,
            'author_id': tweet.author_id,
        }


        return full_response