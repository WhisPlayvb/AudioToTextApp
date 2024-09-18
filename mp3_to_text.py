import PySimpleGUI as sg
import speech_recognition as sr
import os
from pydub import AudioSegment
import io
import pyperclip
import yt_dlp

# Function to convert audio to text
def convert_audio_to_text(file_path, window):
    recognizer = sr.Recognizer()

    try:
        audio = AudioSegment.from_mp3(file_path)
    except Exception as e:
        return f"Error loading audio file: {e}"

    # Convert audio to wav format
    audio_file = io.BytesIO()
    audio.export(audio_file, format="wav")
    audio_file.seek(0)

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Could not understand the audio."
        except sr.RequestError:
            text = "Request to the speech recognition service failed."
    return text

# Function to handle download progress
def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        print("Download complete, now converting...")
    elif d['status'] == 'error':
        print("Error occurred during the download.")

# Function to download YouTube video as MP3 using yt-dlp
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

# Apply theme for a more realistic look
sg.theme('DarkBlue14')

# GUI Layout with improved design
layout = [
    [sg.Text("Audio to Text Converter", font=("Helvetica", 18), justification='center', expand_x=True, background_color="#1e1e1e")],
    [sg.Text("Select MP3 file or enter YouTube URL to download as MP3:", font=("Helvetica", 12), background_color="#1e1e1e")],
    [sg.Input(key="-FILE-", visible=False, enable_events=True), sg.FileBrowse("Browse MP3", file_types=(("MP3 Files", "*.mp3"),), button_color=('white', '#007ACC'))],
    [sg.Text("YouTube URL:", font=("Helvetica", 12), background_color="#1e1e1e")],
    [sg.Input(key="-YOUTUBE_URL-", size=(50, 1)), sg.Button("Download MP3", key="-DOWNLOAD-", font=("Helvetica", 12), button_color=('white', '#007ACC'))],
    [sg.Button("Convert", key="-CONVERT-", font=("Helvetica", 12), button_color=('white', '#3b83f6'))],
    [sg.Multiline("", key="-TEXT-", size=(60, 10), font=("Helvetica", 12), text_color='white', background_color='#2d2d2d', border_width=1)],
    [sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key='-PROGRESS-', bar_color=('white', '#007ACC'))],
    [sg.Button("Copy Text", key="-COPY-", font=("Helvetica", 10), button_color=('white', '#1f883e')), 
     sg.Button("Save Text", key="-SAVE-", font=("Helvetica", 10), button_color=('white', '#007ACC')), 
     sg.Button("Clear", key="-CLEAR-", font=("Helvetica", 10), button_color=('white', '#d73a49'))],
    [sg.Button("Exit", font=("Helvetica", 10), button_color=('white', '#c00'))]
]

# Create the window with custom icon and title
window = sg.Window(
    "Audio to Text Converter", 
    layout, 
    icon=None, 
    finalize=True, 
    background_color="#1e1e1e", 
    margins=(10, 10),
    element_justification='center',
)

# Event Loop
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Exit":
        break

    # File selected and conversion
    if event == "-CONVERT-":
        file_path = values["-FILE-"]
        if file_path and os.path.exists(file_path):
            sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, message='Converting audio...', time_between_frames=100)
            window['-PROGRESS-'].update_bar(0)
            text = convert_audio_to_text(file_path, window)
            window["-TEXT-"].update(text)
            window['-PROGRESS-'].update_bar(100)
            sg.popup_animated(None)  # Stop animation
        else:
            sg.popup("Please select a valid MP3 file.", title="Error", background_color='#1e1e1e')

    # Download YouTube video as MP3 using yt-dlp
    if event == "-DOWNLOAD-":
        url = values["-YOUTUBE_URL-"]
        if url:
            save_path = sg.popup_get_folder('Select Folder to Save MP3')
            if save_path:
                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, message='Downloading video...', time_between_frames=100)
                window['-PROGRESS-'].update_bar(0)
                download_youtube_as_mp3(url, save_path)
                sg.popup("Download Complete", "Video has been saved as MP3.", title="Success", background_color='#1e1e1e')
                window['-PROGRESS-'].update_bar(100)
                sg.popup_animated(None)  # Stop animation
        else:
            sg.popup("Please enter a valid YouTube URL.", title="Error", background_color='#1e1e1e')

    # Copy text to clipboard
    if event == "-COPY-":
        text_to_copy = values["-TEXT-"]
        if text_to_copy:
            pyperclip.copy(text_to_copy)
            sg.popup("Text copied to clipboard.", title="Success", background_color='#1e1e1e')
        else:
            sg.popup("No text to copy.", title="Error", background_color='#1e1e1e')

    # Save text to a file
    if event == "-SAVE-":
        text_to_save = values["-TEXT-"]
        if text_to_save:
            save_path = sg.popup_get_file("Save As", save_as=True, no_window=True, default_extension=".txt", file_types=(("Text Files", "*.txt"),))
            if save_path:
                with open(save_path, "w") as f:
                    f.write(text_to_save)
                sg.popup("File saved successfully.", title="Success", background_color='#1e1e1e')
        else:
            sg.popup("No text to save.", title="Error", background_color='#1e1e1e')

    # Clear text area
    if event == "-CLEAR-":
        window["-TEXT-"].update("")

# Close the window
window.close()
