import PySimpleGUI as sg
import speech_recognition as sr
import os
from pydub import AudioSegment
import io
import pyperclip
from pytube import YouTube

# Function to convert audio to text
def convert_audio_to_text(file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_mp3(file_path)
    
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

# Function to download YouTube video and extract MP3 audio
def download_youtube_video(url, output_path):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(only_audio=True).first()  # Get the audio stream only
        output_file = video_stream.download(output_path)  # Download the file
        base, ext = os.path.splitext(output_file)
        mp3_file = base + '.mp3'
        
        # Convert the file to MP3 using pydub
        audio = AudioSegment.from_file(output_file)
        audio.export(mp3_file, format="mp3")
        
        # Optionally, remove the original file
        os.remove(output_file)
        
        sg.popup('Download Complete', f'Video has been saved as MP3: {mp3_file}', title="Success", background_color='#1e1e1e')
        return mp3_file
    except Exception as e:
        sg.popup('Error', f'Failed to download video: {e}', title="Error", background_color='#1e1e1e')
        return None

# Apply theme for more realistic look
sg.theme('DarkBlue14')  # Choosing a dark, professional-looking theme

# GUI Layout with improved design
layout = [
    [sg.Text("Audio to Text Converter", font=("Helvetica", 18), justification='center', expand_x=True, background_color="#1e1e1e")],
    [sg.Text("Select MP3 file or enter YouTube URL to download as MP3:", font=("Helvetica", 12), background_color="#1e1e1e")],
    [sg.Input(key="-FILE-", visible=False, enable_events=True), sg.FileBrowse("Browse MP3", file_types=(("MP3 Files", "*.mp3"),), button_color=('white', '#007ACC'))],
    [sg.Text("YouTube URL:", font=("Helvetica", 12), background_color="#1e1e1e")],
    [sg.Input(key="-YOUTUBE_URL-", size=(50, 1)), sg.Button("Download MP3", key="-DOWNLOAD-", font=("Helvetica", 12), button_color=('white', '#007ACC'))],
    [sg.Button("Convert", key="-CONVERT-", font=("Helvetica", 12), button_color=('white', '#3b83f6'))],
    [sg.Multiline("", key="-TEXT-", size=(60, 10), font=("Helvetica", 12), text_color='white', background_color='#2d2d2d', border_width=1)],
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
            text = convert_audio_to_text(file_path)
            window["-TEXT-"].update(text)
        else:
            sg.popup("Please select a valid MP3 file.", title="Error", background_color='#1e1e1e')

    # Download YouTube video as MP3
    if event == "-DOWNLOAD-":
        url = values["-YOUTUBE_URL-"]
        if url:
            save_path = sg.popup_get_folder('Select Folder to Save MP3')
            if save_path:
                mp3_file = download_youtube_video(url, save_path)
                if mp3_file:
                    window["-FILE-"].update(mp3_file)
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
