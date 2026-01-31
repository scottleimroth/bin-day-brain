# FOGI App - Wollongong Bin Collection Tracker

A simple, offline-first desktop utility for tracking Wollongong bin collection days.

## Features

- Simple setup wizard to find your address
- Color-coded dashboard showing days until next collection:
  - Green (FOGO - Food Organics Garden Organics)
  - Yellow (Recycling)
  - Red (Landfill)
- Offline-first design - caches collection data locally
- Modern, flat GUI using CustomTkinter

## Installation

1. Download the latest `fogi-app.exe` from Releases
2. Run the executable - no installation needed!

## Development Setup

### Requirements

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run from Source

```bash
python main.py
```

### Build Executable

To create a standalone `.exe` file:

```bash
python build_exe.py
```

Or manually:

```bash
pyinstaller --onefile --windowed --icon=app_icon.ico main.py
```

The executable will be created in the `dist/` folder.

## How It Works

The app uses the Wollongong Waste Info API:
- On first launch, a wizard helps you find your property
- Collection dates are fetched and cached locally
- The app works offline using the cached data
- Click "Refresh" to update collection dates when online

## Tech Stack

- Python 3
- CustomTkinter (Modern GUI)
- requests (API calls)
- json (Local data persistence)

## License

Private - All Rights Reserved
