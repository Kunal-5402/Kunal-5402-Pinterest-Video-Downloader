import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
import os
import re

# Function to download the video
def download_file(url, filename):
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    full_path = os.path.join(downloads_path, filename)
    
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues

        file_size = int(response.headers.get('Content-Length', 0))
        progress = tqdm(response.iter_content(1024), f'Downloading {filename}', total=file_size, unit='B', unit_scale=True, unit_divisor=1024)

        with open(full_path, 'wb') as f:
            for chunk in progress:
                f.write(chunk)
                progress.update(len(chunk))

        print(f"Download completed!")

    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")

# Function to expand shortened Pinterest URLs
def expand_short_url(short_url):
    try:
        response = requests.get(short_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        href_link = soup.find("link", rel="alternate")['href']
        match = re.search(r'url=(.*?)&', href_link)
        return match.group(1) if match else None
    except Exception as e:
        print(f"Error expanding short URL: {e}")
        return None

# Function to fetch video URL
def get_video_url(page_url):
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        video_tag = soup.find("video", class_="hwa kVc MIw L4E")

        if not video_tag or 'src' not in video_tag.attrs:
            print("Error: Video URL not found.")
            return None

        extract_url = video_tag['src']
        return extract_url.replace("hls", "720p").replace("m3u8", "mp4")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch video URL: {e}")
        return None

# Main function
def main():
    page_url = input("Enter page URL: ").strip()

    if "pinterest.com/pin/" not in page_url and "https://pin.it/" not in page_url:
        print("Entered URL is invalid.")
        return

    # Expand short URL if needed
    if "https://pin.it/" in page_url:
        print("Expanding shortened URL...")
        page_url = expand_short_url(page_url)
        if not page_url:
            print("Failed to expand short URL.")
            return

    print("Fetching video URL...")
    video_url = get_video_url(page_url)
    if video_url:
        print("Downloading video...")
        filename = datetime.now().strftime("%d_%m_%H_%M_%S") + ".mp4"
        download_file(video_url, filename)
    else:
        print("Failed to find a valid video URL.")

if __name__ == "__main__":
    while True:
        choice = input("Press X to exit, or any other key to continue: ")
        if choice.lower() == "x":
            print("Exiting the program...")
            break
        main()