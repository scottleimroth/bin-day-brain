# Bin Day Brain - Wollongong Smart Bin Reminders

[![Launch Web App](https://img.shields.io/badge/Launch-Web_App-blue?style=for-the-badge)](https://bin-day-brain.pages.dev/)
[![Download EXE](https://img.shields.io/badge/Download-Windows_EXE-green?style=for-the-badge)](https://github.com/scottleimroth/bin-day-brain/releases/latest/download/bin-day-brain.exe)
[![Download APK](https://img.shields.io/badge/Download-Android_APK-green?style=for-the-badge)](https://github.com/scottleimroth/bin-day-brain/releases/latest/download/BinDayBrain.apk)

Never miss bin day again! **Free and open source** - built for Illawarra/Wollongong residents.

---

## Available Platforms

| Platform | How to Get It |
|----------|---------------|
| Web App | [Launch in browser](https://bin-day-brain.pages.dev/) — no install needed |
| Windows Desktop | [Download EXE](https://github.com/scottleimroth/bin-day-brain/releases/latest/download/bin-day-brain.exe) — run directly |
| Android | [Download APK](https://github.com/scottleimroth/bin-day-brain/releases/latest/download/BinDayBrain.apk) — enable "Unknown sources" to install |

## Features

- **Smart Setup Wizard** - Find your address from the Wollongong Waste API
- **Color-coded Dashboard** showing days until next collection:
  - Green (FOGO - Food Organics Garden Organics)
  - Yellow (Recycling)
  - Red (Landfill)
- **Weather-Smart Alerts**:
  - Wind warnings when bins might blow over (40+ km/h)
  - Rain advisory for collection day
- **Which Bin? Search** - A-Z guide showing correct bin for each item
- **Event Alerts** - Upcoming special events (e-waste, chemical collection, etc.)
- **Offline Support** - Caches collection data locally

## Project Structure

```
bin-day-brain/
├── desktop-app/           # Windows Desktop (Python + CustomTkinter)
│   ├── main.py
│   └── requirements.txt
│
├── web-app/               # Web App (HTML/CSS/JS - PWA)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── dist/              # Ready to deploy
│
├── android-app/           # Android App (Flutter)
│   ├── lib/main.dart
│   └── pubspec.yaml
│
└── README.md
```

> Binaries (EXE, APK) are distributed via [GitHub Releases](https://github.com/scottleimroth/bin-day-brain/releases), not stored in the repo.

## Quick Start

### Windows Desktop
[Download the EXE](https://github.com/scottleimroth/bin-day-brain/releases/latest/download/bin-day-brain.exe) and run it — no installation needed.

### Web App
[Launch in your browser](https://bin-day-brain.pages.dev/) — no download needed.

### Android
1. [Download the APK](https://github.com/scottleimroth/bin-day-brain/releases/latest/download/BinDayBrain.apk) on your phone
2. Allow "Install from unknown sources" when prompted
3. Open and set up your address

## Development

See README in each app folder for development instructions.

## APIs Used

- **Wollongong Waste API** - Collection schedules, materials guide, events
- **Open-Meteo** - Free weather forecasts (no API key required)

## License

© 2026 Scott Leimroth. All Rights Reserved.
