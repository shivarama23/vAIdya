"""
A simple web parser to extract links from web pages and download files.

"""
import requests
from bs4 import BeautifulSoup
import os
import logging
import time
from datetime import datetime

# Set up logging
# Configure logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'./logs/link_parser_{timestamp}.log'
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LinkParser:
    """
    A class to parse web pages and download files.

    Attributes:
    url (str): The URL of the main page.
    issue_links (list): A list of issue links extracted from the main page.
    pdf_links (list): A list of PDF links extracted from each issue page.
    """

    def __init__(self, issues_url):
        self.issues_url = issues_url
        self.issue_links = []
        self.pdf_links = []

    def fetch_page(self, page_url):
        """
        Fetches the content of a web page using a GET request.

        Parameters:
        page_url (str): The URL of the page to fetch.

        Returns:
        bytes: The content of the page in bytes.
        """
        logging.info("Fetching page: %s", page_url)
        # Send a GET request to the page_url
        response = requests.get(page_url)
        # Raise an exception for any unsuccessful requests
        response.raise_for_status()
        # Return the page content
        return response.content

    def parse_issues(self, class_, extract):
        """
        Parses the main page to find all issue links.

        Parameters:
        class_ (str): The class attribute to look for in div elements.
        extract (str): The attribute to extract from the found elements.

        Returns:
        list: A list of extracted attributes (e.g., URLs).
        """
        logging.info("Parsing issues from main page: %s", self.issues_url)
        # Fetch the page content
        content = self.fetch_page(self.issues_url)
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        # Find all div elements with the specified class
        elements = soup.find_all('div', class_=class_)
        # Extract the specified attribute from each element
        self.issue_links = []
        for element in elements:
            # Find the tag with the specified attribute within the element
            tag = element.find(attrs={extract: True})
            if tag and extract in tag.attrs:
                self.issue_links.append(tag[extract])
                logging.info("Found issue link: %s", tag[extract])
        logging.info("Found %d issue links", len(self.issue_links))
        return self.issue_links

    def parse_pdfs(self, class_, extract):
        """
        Parses each issue page to find all PDF links.

        Parameters:
        class_ (str): The class attribute to look for in anchor elements.
        extract (str): The attribute to extract from the found elements.

        Returns:
        list: A list of extracted attributes (e.g., PDF URLs).
        """
        logging.info("Parsing PDF links from issue pages")
        self.pdf_links = []
        for issue_link in self.issue_links:
            # Fetch the content of each issue page
            content = self.fetch_page(issue_link)
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            # Find all anchor elements with the specified class
            elements = soup.find_all('a', class_=class_)
            # Extract the specified attribute from each element
            for element in elements:
                if extract in element.attrs and "PDF FULL TEXT" in element.text:
                    self.pdf_links.append(element[extract])
                    logging.info("Found PDF link: %s", element[extract])

        logging.info("Found %d PDF links", len(self.pdf_links))
        return self.pdf_links

    def download(self, pdf_link, local_filename):
        """
        Downloads a file from a given URL and saves it locally.

        Parameters:
        pdf_link (str): The URL of the file to download.
        local_filename (str): The name of the file to save locally.

        Returns:
        None
        """
        logging.info("Downloading file from %s", pdf_link)
        # Send a GET request to the pdf_link
        with requests.get(pdf_link, stream=True) as r:
            # Raise an exception for any unsuccessful requests
            r.raise_for_status()
            # Open the local file in write-binary mode
            with open(local_filename, 'wb') as f:
                # Write the content in chunks to handle large files
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info("Downloaded file saved as %s", local_filename)
        print(f"Downloaded file saved as {local_filename}")

    def download_all(self, download_folder='downloads'):
        """
        Downloads all PDF files from the extracted links.
    
        Parameters:
        download_folder (str): The folder to save the downloaded files.
    
        Returns:
        None
        """
        logging.info("Downloading all PDF files")
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        for pdf_link in self.pdf_links:
            # Extract the filename from the pdf_link
            pdf_link = pdf_link.replace('/view/', '/download/')
            filename = os.path.join(download_folder, pdf_link.split('/')[-1]+'.pdf')
            self.download(pdf_link, filename)
            time.sleep(1)
        logging.info("All files downloaded")

# Example usage
url = 'https://ijapr.in/index.php/ijapr/issue/archive'
parser = LinkParser(url)
# Parse the main page to get issue links
parser.parse_issues(class_='obj_issue_summary', extract='href')
# Parse each issue page to get PDF links
parser.parse_pdfs(class_='obj_galley_link pdf', extract='href')
for link in parser.pdf_links:
    print(link)
parser.download_all(download_folder='./data/downloads')
