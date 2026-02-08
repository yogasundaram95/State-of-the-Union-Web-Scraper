# Required Libraries
import requests
from requests.exceptions import RequestException
from lxml import html
from lxml import etree
import os
import re
import time
import logging
import pyodbc
from urllib.parse import urljoin
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; SOTUScraper/1.0)'}


def validate_sql_identifier(identifier, identifier_type="identifier"):
    """Validates that a SQL identifier contains only safe characters (alphanumeric and underscores)."""
    if not re.match(r'^[A-Za-z0-9_]+$', identifier):
        raise ValueError(f"Invalid SQL {identifier_type}: '{identifier}'. Only alphanumeric characters and underscores are allowed.")


def record_exists(cursor, table, name, date):
    """Checks if a record with the given president name and date already exists."""
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE NAME_OF_PRESIDENT = ? AND DATE_OF_UNION_ADDRESS = ?", (name, str(date)))
    return cursor.fetchone()[0] > 0


# Main program starts here
def main():
    """A web scraper that extracts State of the Union address speeches and stores them in a SQL Server table."""

    # setup SQL Server connection
    server = os.environ.get('SQL_SERVER', r'DHARMIK\SQLSERVER2022')
    database = os.environ.get('SQL_DATABASE', 'STATE_UNION_ADDRESSES')
    table = 'ADDRESS_TABLE'
    main_url = 'https://www.infoplease.com'
    speeches_url = 'https://www.infoplease.com/primary-sources/government/presidential-speeches/state-union-addresses'

    # Validate SQL identifiers before use
    try:
        validate_sql_identifier(database, "database name")
        validate_sql_identifier(table, "table name")
    except ValueError as e:
        logger.critical(str(e))
        return

    # Connect to SQL Server and create the database and table
    try:
        cursor = connect_to_sql_server(server, database, table)
    except Exception as e:
        logger.critical(f"Failed to connect to SQL Server: {e}")
        return

    # Get main page content to parse
    try:
        page = requests.get(speeches_url, headers=HEADERS, timeout=30)
        page.raise_for_status()
    except RequestException as e:
        logger.critical(f"Failed to fetch main speeches page: {e}")
        return

    tree = html.fromstring(page.content)
    html_etree = etree.ElementTree(tree)

    # Create output directory for speech text files
    output_directory = os.path.join(os.getcwd(), 'SpeechFiles')
    os.makedirs(output_directory, exist_ok=True)

    # Create the combined speeches file
    combined_speeches_file = os.path.join("CombinedStateOfUnionAddresses.txt")
    broken_links = []  # Track broken links
    with open(combined_speeches_file, 'w', encoding='utf-8') as combined_file:

        # Navigate Xpath to the tag with union addresses
        speech_links = html_etree.xpath('//*//div/dl/dt/span/a')

        # Iterate over each speech element and extract the information
        for speech in speech_links:
            # Extract president's name, date, and link to the speech
            full_speech_text = speech.text.strip()
            relative_link = speech.get('href')  # Get the relative URL for the speech
            full_link = urljoin(main_url, relative_link)  # Combine base URL with the relative link

            if '(' in full_speech_text and ')' in full_speech_text:
                # Split based on the last '(' to separate president and date
                president, date = full_speech_text.rsplit('(', 1)
                president = president.strip()
                date = date.strip(')')

                # Handle different date formats and convert to a standardized format
                try:
                    date = date.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '').strip()  # Remove suffixes
                    date = datetime.strptime(date, "%B %d, %Y").date()  # Convert to date object
                except ValueError:
                    continue  # Skip if the date format is incorrect
            else:
                continue

            # Check for duplicate before scraping
            try:
                if record_exists(cursor, table, president, date):
                    logger.warning(f"Duplicate skipped: {president} ({date})")
                    continue
            except Exception:
                pass  # If check fails, proceed with insertion

            # Log a processing message
            logger.info(f"Processing speech for {president} ({date})")

            # Extract the speech content from the speech link
            time.sleep(1)  # Rate limit between requests
            try:
                speech_response = requests.get(full_link, headers=HEADERS, timeout=30)
                speech_response.raise_for_status()
            except RequestException as e:
                logger.error(f"Failed to fetch speech for {president} ({date}): {e}")
                broken_links.append((president, date, full_link))
                continue

            speech_tree = html.fromstring(speech_response.content)

            # Find all <p> tags containing the speech text and join their content
            p_tags = speech_tree.xpath('//*/article/div/div/p')
            speech_text = '\n'.join([p.text_content().strip() for p in p_tags])

            # Check if the speech text is empty (broken link)
            if not speech_text.strip():
                logger.warning(f"No speech found for {president} ({date})")
                broken_links.append((president, date, full_link))

                # Insert NULL values for FILENAME_ADDRESS and TEXT_OF_ADDRESS
                insert_row_into_table(cursor, table, president, date, full_link, 'NULL', 'NULL')
                continue

            # Saving speech text to a local file
            filename = write_to_file(output_directory, f"{president} ({date})", speech_text)

            # Insert the data into the SQL Server database
            insert_row_into_table(cursor, table, president, date, full_link, filename, speech_text)

            # Append the speech to the combined speeches file
            combined_file.write(f"{president} ({date})\n\n{speech_text}\n\n{'-'*80}\n\n")

    # Success message for records stored in database
    logger.info("Records stored in the SQL database.")

    # Display broken links after processing
    display_broken_links(broken_links)


def connect_to_sql_server(server, database, table):
    """Connects to the SQL Server, creates the database and table if they don't exist."""
    # Validate identifiers
    validate_sql_identifier(database, "database name")
    validate_sql_identifier(table, "table name")

    # Connect to SQL Server
    odbc_conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';Trusted_Connection=yes;')
    odbc_conn.autocommit = True
    cursor = odbc_conn.cursor()

    # Create the database if it doesn't exist
    cursor.execute(f"""
    IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{database}')
    BEGIN
        CREATE DATABASE {database};
    END
    """)

    # Switch to the database
    cursor.execute(f"USE {database};")

    # Create the table if it doesn't exist (with UNIQUE constraint for duplicate prevention)
    cursor.execute(f"""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table}')
    BEGIN
        CREATE TABLE dbo.{table} (
            NAME_OF_PRESIDENT VARCHAR(100),
            DATE_OF_UNION_ADDRESS DATE,
            LINK_TO_ADDRESS VARCHAR(255),
            FILENAME_ADDRESS VARCHAR(255),
            TEXT_OF_ADDRESS NVARCHAR(MAX),
            UNIQUE (NAME_OF_PRESIDENT, DATE_OF_UNION_ADDRESS)
        );
    END
    """)

    return cursor

def insert_row_into_table(cursor, table, name, date, link, file, text):
    """Inserts a single union address into the SQL Server database. Returns True if inserted, False if skipped."""

    try:
        # Insert the speech data into the table using parameterized query
        cursor.execute(f"""
            INSERT INTO {table} (NAME_OF_PRESIDENT, DATE_OF_UNION_ADDRESS, LINK_TO_ADDRESS, FILENAME_ADDRESS, TEXT_OF_ADDRESS)
            VALUES (?, ?, ?, ?, ?);
            """, (name, str(date), link, file, text))
        return True
    except pyodbc.IntegrityError:
        logger.warning(f"Duplicate record skipped during insert: {name} ({date})")
        return False
    except Exception as e:
        logger.error(f"Failed to insert record for {name} ({date}): {e}")
        return False

def write_to_file(output_directory, file_name, text):
    """Writes the speech to a local file on disk and returns the file path."""
    # Clean up the file name and construct the full file path
    clean_file_name = file_name.replace(',', '').replace(' ', '_')
    full_file_path = os.path.join(output_directory, f"{clean_file_name}.txt")
    # Write the speech text to the file
    with open(full_file_path, "w", encoding='utf-8') as text_file:
        text_file.write(text)
    return full_file_path

def display_broken_links(broken_links):
    """Displays any broken links encountered while scraping."""
    if broken_links:
        for president, date, _ in broken_links:
            logger.warning(f"Broken link: {president} ({date})")
    else:
        logger.info("No broken links encountered.")

# Run the main function
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scraper interrupted by user.")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
