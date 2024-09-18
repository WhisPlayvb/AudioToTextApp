python -m venv AudioToText
\AudioToText\Scripts\activate
pip install -r requirements.txt
pyinstaller --onefile --windowed --icon=teamfiles.ico mp3_text_youtube_tool.py
