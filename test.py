import yt_dlp
import os

# Function to handle download progress
def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        print("Download complete, now converting...")
    elif d['status'] == 'error':
        print("Error occurred during the download.")

# Function to download YouTube video as MP3
def download_youtube_as_mp3(url, download_path):
    # Define the options for downloading the audio as MP3
    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [progress_hook],  # Attach the progress hook to display progress
        'ffmpeg_location': 'C:/ffmpeg/bin'  # Set the path to your FFmpeg installation
    }

    # Start downloading the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            print(f"Error: {e}")

# Example usage
if __name__ == '__main__':
    youtube_url = input("Enter YouTube video URL: ")
    download_folder = os.path.expanduser("~/Downloads")  # Set the download path (e.g., user Downloads folder)

    # Call the function to download the video as an MP3 file
    download_youtube_as_mp3(youtube_url, download_folder)
