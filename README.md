# YouTube Downloader Pro

A professional YouTube video downloader with a modern GUI interface.

## Download Location

Videos are saved in one of these locations (in order of preference):
1. User-selected folder (chosen on first run)
2. Default location: `~/Downloads/YouTube Downloads`

To change download location:
1. Go to File > Change Download Location
2. Select your preferred folder
3. All new downloads will go to the chosen location

## Features

- Clean and modern dark theme interface
- Progress bar with download speed
- Download status notifications
- High quality video downloads
- Automatic file organization

## Requirements

- Python 3.9+
- FFmpeg (for video processing)

## Installation

1. Clone or download this repository
2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Launch the application
2. Paste a YouTube URL into the input box
3. Click Download
4. Your video will be saved in the 'downloads' folder

## Building Executable

To create a standalone executable:
```bash
.\build.bat
```
The executable will be created in `dist/YouTube Downloader Pro/`

## Supported URLs

- Regular YouTube videos
- YouTube playlists
- YouTube Music

## Tips

- Videos are downloaded in the highest available quality
- Files are automatically named based on video title
- Progress bar shows download speed and completion percentage

## Author

Created by Ty

## License

MIT License