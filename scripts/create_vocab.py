import spacy
import sys
sys.path.append('..')

from collections import defaultdict
from src import io
from src.convoy_protest_dataset import ConvoyProtestDataset, DatasetType
from src.paths_handler import PathsHandler

def main():
    config = PathsHandler()
    io.info('Running script: create_vocab.py')
    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL, removed_repeated=True)

    io.info(f'{len(tweets):,} tweets retrieved.')


    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner', 'textcat'])

    freq = defaultdict(int)

    io.info('Processing documents using spaCy...')
    docs = nlp.pipe([tweet.text for tweet in tweets])
    io.info('Ffinished processing docs with spaCy.')

    io.info('Computing vocab...')
    for doc in docs:
        for token in doc:
            if token.text.isalpha() and  not (token.is_stop or len(token.text)<=2):
                freq[token.text.lower()]+=1


    threshold = config.get_variable('vocab-threshold')
    io.info(f'Finished computing tokens. Total tokens: {len(freq):,}')
    freq = {lemma:count for lemma, count in freq.items() if count>threshold}

    io.info(f'Total lemmas after filtering > {threshold}: {len(freq):,}')

    with open(config.get_path('vocab-filename'), 'w', encoding='utf-8') as writer:
        writer.write('\n'.join(sorted(freq)))


if __name__ == "__main__":
    main()