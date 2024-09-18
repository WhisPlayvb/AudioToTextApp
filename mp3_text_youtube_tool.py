import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import speech_recognition as sr
import os
from pydub import AudioSegment
import io
import pyperclip
import yt_dlp
import re

# Function to convert audio to text
def convert_audio_to_text(file_path):
    recognizer = sr.Recognizer()
    try:
        audio = AudioSegment.from_mp3(file_path)
    except Exception as e:
        return f"Error loading audio file: {e}"

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
        percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).strip()
        speed_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_speed_str']).strip()
        progress_label.config(text=f"Downloading: {percent_str} at {speed_str}")
    elif d['status'] == 'finished':
        progress_label.config(text="Download complete, now converting...")
    elif d['status'] == 'error':
        progress_label.config(text="Error occurred during the download.")

# Function to download YouTube video as MP3 using yt-dlp
def download_youtube_as_mp3(url, download_path):
    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'progress_hooks': [progress_hook],
        'ffmpeg_location': 'C:/ffmpeg/bin'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            progress_label.config(text=f"Error: {e}")

# Function to browse and select MP3 file
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# Function to convert the selected audio file to text
def convert_audio():
    file_path = file_entry.get()
    if os.path.exists(file_path):
        text = convert_audio_to_text(file_path)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text)
        word_count = len(text.split())
        status_label.config(text=f"Word Count: {word_count}")
    else:
        messagebox.showerror("Error", "Please select a valid MP3 file.")

# Function to download YouTube video as MP3
def download_mp3():
    url = url_entry.get()
    if url:
        save_path = filedialog.askdirectory()
        if save_path:
            download_youtube_as_mp3(url, save_path)
            messagebox.showinfo("Success", "Download Complete: Video saved as MP3.")
    else:
        messagebox.showerror("Error", "Please enter a valid YouTube URL.")

# Function to copy text to clipboard
def copy_text():
    text_to_copy = text_area.get(1.0, tk.END).strip()
    if text_to_copy:
        pyperclip.copy(text_to_copy)
        messagebox.showinfo("Success", "Text copied to clipboard.")
    else:
        messagebox.showerror("Error", "No text to copy.")

# Function to save text to file
def save_text():
    text_to_save = text_area.get(1.0, tk.END).strip()
    if text_to_save:
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as file:
                file.write(text_to_save)
            messagebox.showinfo("Success", "Text saved to file.")
    else:
        messagebox.showerror("Error", "No text to save.")

# Function to clear the text area
def clear_text():
    text_area.delete(1.0, tk.END)
    status_label.config(text="Word Count: 0")

# Set up the main application window with dark mode
window = tk.Tk()
window.title("Audio & YouTube MP3 Downloader")
window.geometry("850x550")
window.configure(bg="#1e1e1e")
window.resizable(True, True)

# Responsive resizing for the window
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

# Set dark theme colors
bg_color = "#1e1e1e"
fg_color = "#ffffff"
entry_bg = "#404040"
btn_color = "#007ACC"
font_size = 14

# Increase tab size by customizing the style
style = ttk.Style()
style.configure('TNotebook.Tab', padding=[20, 10])  # Increase the padding around the tab label

# Create Notebook (Tabbed Interface)
tab_control = ttk.Notebook(window, style='TNotebook')
tab1 = tk.Frame(tab_control, bg=bg_color)
tab2 = tk.Frame(tab_control, bg=bg_color)

tab_control.add(tab1, text="Audio to Text")
tab_control.add(tab2, text="YouTube to MP3")
tab_control.pack(expand=1, fill="both")

# Centering the content in each tab
tab1.columnconfigure(0, weight=1)
tab1.columnconfigure(1, weight=1)
tab2.columnconfigure(0, weight=1)
tab2.columnconfigure(1, weight=1)

# Tab 1: Audio to Text Converter
tk.Label(tab1, text="Select MP3 File:", fg=fg_color, bg=bg_color, font=("Helvetica", font_size)).grid(row=0, column=0, padx=10, pady=10, sticky="E")
file_entry = tk.Entry(tab1, width=50, bg=entry_bg, fg=fg_color, relief="flat", font=("Helvetica", font_size))
file_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(tab1, text="Browse", command=browse_file, bg=btn_color, fg=fg_color, relief="flat", font=("Helvetica", font_size)).grid(row=0, column=2, padx=10, pady=10)

tk.Button(tab1, text="Convert Audio", command=convert_audio, bg=btn_color, fg=fg_color, relief="flat", font=("Helvetica", font_size)).grid(row=1, column=1, pady=10)

text_area = scrolledtext.ScrolledText(tab1, width=80, height=10, bg=entry_bg, fg=fg_color, insertbackground=fg_color, relief="flat", font=("Helvetica", font_size))
text_area.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Word Count and Status Bar
status_label = tk.Label(tab1, text="Word Count: 0", fg=fg_color, bg=bg_color, font=("Helvetica", font_size))
status_label.grid(row=3, column=0, columnspan=3, pady=10)

button_frame1 = tk.Frame(tab1, bg=bg_color)
button_frame1.grid(row=4, column=0, columnspan=3, pady=10)

tk.Button(button_frame1, text="Copy Text", command=copy_text, bg="#1f883e", fg=fg_color, relief="flat", font=("Helvetica", font_size)).grid(row=0, column=0, padx=5)
tk.Button(button_frame1, text="Save Text", command=save_text, bg=btn_color, fg=fg_color, relief="flat", font=("Helvetica", font_size)).grid(row=0, column=1, padx=5)
tk.Button(button_frame1, text="Clear", command=clear_text, bg="#d73a49", fg=fg_color, relief="flat", font=("Helvetica", font_size)).grid(row=0, column=2, padx=5)

# Tab 2: YouTube to MP3 Downloader
tk.Label(tab2, text="Enter YouTube URL:", fg=fg_color, bg=bg_color, font=("Helvetica", font_size)).grid(row=0, column=0, padx=10, pady=10, sticky="E")
url_entry = tk.Entry(tab2, width=50, bg=entry_bg, fg=fg_color, relief="flat", font=("Helvetica", font_size))
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Button(tab2, text="Download MP3", command=download_mp3, bg=btn_color, fg=fg_color, relief="flat", font=("Helvetica", font_size)).grid(row=1, column=1, pady=10)

progress_label = tk.Label(tab2, text="", fg=fg_color, bg=bg_color, font=("Helvetica", font_size))
progress_label.grid(row=2, column=0, columnspan=3, pady=10)

window.mainloop()
