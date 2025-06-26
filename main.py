import argparse
import requests
import logging
from bs4 import BeautifulSoup
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="Detects if directory listing is enabled on a web server.")
    parser.add_argument("url", help="The URL to check (e.g., http://example.com/directory/).  Include trailing slash for directory listing check.")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout for the HTTP request in seconds. Default is 5.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging for debugging.")
    parser.add_argument("-o", "--output", type=str, help="Output file to save results (optional).")

    return parser


def is_directory_listing_enabled(url, timeout=5):
    """
    Checks if directory listing is enabled at the given URL.

    Args:
        url (str): The URL to check.
        timeout (int): Timeout for the HTTP request in seconds.

    Returns:
        bool: True if directory listing is likely enabled, False otherwise.
    """
    try:
        # Validate URL (very basic check - could be improved with regex)
        if not url.startswith(('http://', 'https://')):
            logging.error("Invalid URL format.  Must start with http:// or https://")
            return False

        logging.info(f"Checking URL: {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Check if the response is HTML
        if 'text/html' not in response.headers.get('Content-Type', '').lower():
            logging.info("Content type is not HTML.  Directory listing might not be the issue.")
            return False

        soup = BeautifulSoup(response.content, 'html.parser')

        # Common indicators of directory listing:
        # 1. Presence of "Index of" in the title
        # 2. Presence of specific tags like <a> tags linking to files/directories
        if "Index of" in soup.title.string:
            logging.info("Found 'Index of' in title, likely directory listing enabled.")
            return True

        # Check for links that look like files or directories
        links = soup.find_all('a')
        if links:
            file_like_links = 0
            for link in links:
                href = link.get('href')
                if href and href not in ['.', '..', '/']: # Ignore parent directory links
                    file_like_links +=1

            if file_like_links > 3: # Heuristic: if many links, likely directory listing. Adjust as needed.
                logging.info(f"Found {file_like_links} file-like links. Directory listing is likely enabled")
                return True


        logging.info("Directory listing likely not enabled.")
        return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False

def main():
    """
    Main function to execute the directory listing detector.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG) # Set log level to DEBUG

    url = args.url
    timeout = args.timeout
    output_file = args.output

    if not url:
        print("Please provide a URL to check.")
        return

    try:
        # Input validation: check if timeout is a positive integer
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        # Input validation: Check if URL is a string
        if not isinstance(url, str):
            raise TypeError("URL must be a string.")
    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        sys.exit(1)  # Exit the program with an error code
    except TypeError as e:
        logging.error(f"Invalid input type: {e}")
        sys.exit(1)

    try:
        result = is_directory_listing_enabled(url, timeout)

        if result:
            message = f"Directory listing is likely enabled at {url}"
            print(message)

            if output_file:
                try:
                    with open(output_file, "w") as f:
                        f.write(message + "\n")
                    logging.info(f"Results saved to {output_file}")
                except Exception as e:
                    logging.error(f"Error writing to output file: {e}")
        else:
            message = f"Directory listing is likely not enabled at {url}"
            print(message)
            if output_file:
                try:
                    with open(output_file, "w") as f:
                        f.write(message + "\n")
                    logging.info(f"Results saved to {output_file}")
                except Exception as e:
                    logging.error(f"Error writing to output file: {e}")


    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()