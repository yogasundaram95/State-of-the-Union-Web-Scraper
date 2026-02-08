"""
Demo script for the State of the Union Web Scraper.

Scrapes 3 speeches from The American Presidency Project (UCSB) and saves them
to local text files. No SQL Server required — demonstrates the scraping logic standalone.

Source: https://www.presidency.ucsb.edu
"""

import requests
from requests.exceptions import RequestException
from lxml import html
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; SOTUScraper/1.0)'}

# Demo targets: 3 speeches spanning US history
DEMO_SPEECHES = [
    {
        'president': 'George Washington',
        'date': 'January 8, 1790',
        'url': 'https://www.presidency.ucsb.edu/documents/first-annual-address-congress-0',
    },
    {
        'president': 'Abraham Lincoln',
        'date': 'December 1, 1862',
        'url': 'https://www.presidency.ucsb.edu/documents/second-annual-message-9',
    },
    {
        'president': 'John F. Kennedy',
        'date': 'January 11, 1962',
        'url': 'https://www.presidency.ucsb.edu/documents/annual-message-the-congress-the-state-the-union-4',
    },
]


def scrape_speech(url):
    """Fetches and extracts speech text from a UCSB Presidency Project page."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    p_tags = tree.xpath('//div[contains(@class,"field-docs-content")]//p')
    return '\n'.join([p.text_content().strip() for p in p_tags])


def save_speech(output_dir, president, date, text):
    """Saves a speech to a text file and returns the file path."""
    clean_name = f"{president} ({date})".replace(',', '').replace(' ', '_')
    file_path = os.path.join(output_dir, f"{clean_name}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return file_path


def main():
    logger.info("State of the Union Web Scraper — Demo Mode")
    logger.info(f"Scraping {len(DEMO_SPEECHES)} speeches (no SQL Server needed)\n")

    # Output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_output')
    os.makedirs(output_dir, exist_ok=True)

    results = []

    for speech_info in DEMO_SPEECHES:
        president = speech_info['president']
        date_str = speech_info['date']
        url = speech_info['url']

        logger.info(f"Scraping: {president} ({date_str})")

        time.sleep(1)  # Rate limit
        try:
            text = scrape_speech(url)
        except RequestException as e:
            logger.error(f"Failed to fetch speech for {president}: {e}")
            continue

        if not text.strip():
            logger.warning(f"No speech content found for {president}")
            continue

        file_path = save_speech(output_dir, president, date_str, text)
        preview = text[:200].replace('\n', ' ') + '...'
        results.append((president, date_str, len(text), file_path, preview))
        logger.info(f"Saved to {file_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("DEMO RESULTS SUMMARY")
    print("=" * 70)
    for president, date_str, length, file_path, preview in results:
        print(f"\nPresident:  {president}")
        print(f"Date:       {date_str}")
        print(f"Length:     {length:,} characters")
        print(f"Saved to:   {os.path.basename(file_path)}")
        print(f"Preview:    {preview}")
        print("-" * 70)

    print(f"\nTotal speeches scraped: {len(results)}")
    print(f"Output directory: {output_dir}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user.")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
