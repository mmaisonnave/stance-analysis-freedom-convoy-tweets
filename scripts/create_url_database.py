import pandas as pd
import sys
sys.path.append('..')
from src.convoy_protest_dataset import ConvoyProtestDataset, DatasetType
from src import io
from collections import Counter
from src.paths_handler import PathsHandler
import os
import requests
from bs4 import BeautifulSoup, Comment
import time
import re
from urllib.parse import urlparse

headers = {'User-Agent': 'Mozilla/5.0'}


def compute_list_of_URLs():
    path_handler = PathsHandler()
    # OUTPUT:
    url_database_path = path_handler.get_path('url-database')
    unaccessible_domains = {
        't.co',
        't.c',
        't.',
        't',
        'twitter.com',
        'x.com',
        'bit.ly',
        'www.cbc.ca', # http://cbc.ca/1.6347862
        'nationalpost.com', # https://nationalpost.com/news/politics/senate-growing-frustrated-by-pressure-to-rubber-stamp-emergencies-act,
        'rumble.com', # https://rumble.com/vs4cua-vax-nation-show-me-your-papers.html?mc_cid=923a6baff1,
        'vm.tiktok.com', # https://vm.tiktok.com/ZMLSNAJdF/
        'torontosun.com', # http://torontosun.com/opinion/columnists/lilley-facing-pressure-trudeau-punts-on-chinese-election-interference-allegations
        'ino.to', # https://ino.to/fBCPRIH
        'buff.ly', # https://buff.ly/3VSUm5Y


    }

    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL,
                                                    removed_repeated=True
                                                    )
    
    urls_from_text = [url for tweet in tweets for url in tweet.urls]

    io.info(f"Number of URLs from text: {len(urls_from_text):,}")

    # Filter out URLs from unaccessible domains
    urls_from_text = [url 
                      for url in urls_from_text 
                      if _get_domain_from_url(url) not in unaccessible_domains]

    io.info(f"Number of URLs from text after filtering: {len(urls_from_text):,}")

    # Most common domains in URLs from text:
    common_domains = Counter([_get_domain_from_url(url) for url in urls_from_text]).most_common(20)
    io.info(f"Most common domains in URLs from text: {common_domains}")


    urls_from_metadata = [url['expanded_url']
                          for tweet in tweets
                          if tweet.entities and
                          'urls' in tweet.entities 
                          for url in tweet.entities['urls']]
    
    io.info(f"Number of URLs from metadata: {len(urls_from_metadata):,}")

    urls_from_metadata = [url for url in urls_from_metadata if _get_domain_from_url(url) not in unaccessible_domains]

    io.info(f"Number of URLs from metadata after filtering: {len(urls_from_metadata):,}")

    df = pd.DataFrame({
        'URL': list(set(urls_from_metadata + urls_from_text)),
        })
    
    df.to_csv(url_database_path, index=False)

def _get_domain_from_url(url: str) -> str:
    """
    Extract the domain from a URL.
    
    Args:
        url (str): The URL to extract the domain from.
    
    Returns:
        str: The domain of the URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc if parsed_url.netloc else parsed_url.path.split('/')[0]


def compute_filename_to_store():
    io.info('hello world')

    path_handler = PathsHandler()

    # INPUT:
    url_database_path = path_handler.get_path('url-database')

    # OUTPUT:
    output_folder = path_handler.get_path('url-database-folder')


    df = pd.read_csv(url_database_path)
    io.info(f"Number of URLs in database: {len(df):,}")

    if 'filename' in df.columns:
        del df['filename']

    domain_counter = Counter([_get_domain_from_url(url) for url in df['URL']])

    for domain, count in domain_counter.most_common(20):
        io.info(f"\tDomain: {domain}, Count: {count:,}")

    # How many domains?
    io.info(f"Number of unique domains: {len(set(domain_counter)):,}")

    df['index'] = range(1, len(df) + 1)

    # how many domains have a single URL?
    single_url_domains = [domain for domain, count in domain_counter.items() if count == 1]
    io.info(f"Number of domains with a single URL: {len(single_url_domains):,}")


    url2filename = {}

    
    for index,url in df.iterrows():
        domain = _get_domain_from_url( url['URL'])
        foldername = domain if domain_counter[domain] > 1 else 'misc'
        filename = f"{foldername}/{index+1}.html"

        if not os.path.exists(os.path.join(output_folder, foldername)):
            os.makedirs(os.path.join(output_folder, foldername), exist_ok=True)

        url2filename[url['URL']] = filename

    df['filename'] = df['URL'].map(url2filename)

    #check if filename contains characters outside the allowed ones (a-zA-Z0-9_.-)
    invalid_filenames = df[~df['filename'].str.match(r'^[a-zA-Z0-9_.\-/]+$')]
    for index, row in invalid_filenames.iterrows():
        io.warning(f"Invalid filename: {row['filename']} for URL: {row['URL']}")

    df.to_csv(url_database_path, index=False)
        


def _clean_html(html):
    """
    Clean HTML content to extract visible text.
    This function removes script, style, and other non-visible elements,
    and normalizes whitespace.

    Args:
        html (str): The HTML content to clean.
    Returns:
        str: Cleaned text content.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'aside', 'nav', 'form']):
        tag.decompose()

    # Optional: remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Get visible text
    text = soup.get_text(separator='\n', strip=True)

    # Normalize whitespace (except newlines)
    text = re.sub(r'[ \t]+', ' ', text)

    # remove 3+ new lines into 2:
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def _fetch_url_content(url: str):
    """
    Fetch the content of a URL and return the cleaned text.
    If the URL is not accessible or the content is empty, return an error message.

    Args:
        url (str): The URL to fetch.
    Returns:
        str: Cleaned text content or an error message.
    """
    status = 'OK'
    content = None
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text

        if content:
            content = _clean_html(content)

        else:
            content = "No content found at the URL."
        
    except requests.RequestException as e:
        status = 'Error'
        content = f"Error fetching {url}: {e}"

    return status, content

def clear_url_database_files():
    """
    Clear the URL database by updating the status of all URLs to 'pending'. In this way, the next time
    the script is run, it will fetch the content of all URLs again and overwrite the existing files.
    """
    path_handler = PathsHandler()
    url_database_path = path_handler.get_path('url-database')
    df = pd.read_csv(url_database_path)

    if 'status' in df.columns:
        df['status'] = 'pending'

    df.to_csv(url_database_path, index=False)

def fetch_content_all_urls():
    """
    Fetch the content of URLs in the database and save it to files.
    """
    io.info('Fetching content for URLs in the database...')

    path_handler = PathsHandler()
    url_database_path = path_handler.get_path('url-database')

    df = pd.read_csv(url_database_path)
    io.info(f"Number of URLs in database: {len(df):,}")

    if 'status' not in df.columns:
        df['status'] = 'pending'

    io.info(f"Number of URLs with status 'pending': {len(df[df['status'] == 'pending']):,}")
    io.info(f"Number of URLs with status 'fetched': {len(df[df['status'] == 'fetched']):,}")
    io.info(f"Number of URLs with status 'error':   {len(df[df['status'] == 'error']):,}")

    cap=5000
    io.info(f"Setting a limit of {cap} URLs to fetch in this run.")

    for idx, row in df.iterrows():
        url = row['URL']
        status = row['status']
        filename = os.path.join(path_handler.get_path('url-database-folder'), row['filename'])
        shortened_url = url[:30] + '...' if len(url) > 30 else url

        if status == 'pending':
            cap -= 1
            time.sleep(1)
            # ========== Fetch content from URL ==========
            status, content = _fetch_url_content(url)
            if status == 'OK':
                df.at[idx, 'status'] = 'fetched'
            elif status == 'Error':
                df.at[idx, 'status'] = 'error'
            
            io.info(f"Fetched  url {shortened_url:33} status={status} ")


            # ========== Save content to file ==========
            content = f"URL:{url}\nCONTENT:\n{content}"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content if content else '')
        else:
            io.info(f"Skipping url {shortened_url:33} (already fetched)")

        if cap <= 0:
            io.info("Reached the limit of URLs to fetch. Stopping.")
            break

    error_count = len(df[df['status'] == 'error'])
    fetched_count = len(df[df['status'] == 'fetched'])
    io.info(f"Number of URLs with status 'pending': {len(df[df['status'] == 'pending']):,}")
    io.info(f"Number of URLs with status 'fetched': {fetched_count:,}")
    io.info(f"Number of URLs with status 'error':   {error_count:,} ({error_count / (error_count + fetched_count) * 100:.2f}%)")
    
    df.to_csv(url_database_path, index=False)

if __name__ == '__main__':
    # compute_list_of_URLs()
    # compute_filename_to_store()
    # clear_url_database_files()
    fetch_content_all_urls()