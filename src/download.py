import requests

def download_file(url, local_filename):
    # Send a GET request to the URL
    with requests.get(url, stream=True) as r:
        # Raise an exception for any unsuccessful requests
        r.raise_for_status()
        # Open the local file in write-binary mode
        with open(local_filename, 'wb') as f:
            # Write the content in chunks to handle large files
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded file saved as {local_filename}")

# Example usage
url = 'https://ijapr.in/index.php/ijapr/article/download/3272/2875/'
local_filename = 'test.pdf'
download_file(url, local_filename)
