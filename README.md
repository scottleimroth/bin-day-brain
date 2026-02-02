# Bin Day Brain - Wollongong Smart Bin Reminders

Never miss bin day again! **Free and open source** - built for Illawarra/Wollongong residents.

## 🌐 Try It Live

**[Launch Web App →](https://bin-day-brain.pages.dev/)**

No installation required - works on any device with a browser.

---

## Available Platforms

| Platform | Location | Ready to Run |
|----------|----------|--------------|
| Windows Desktop | `desktop-app/dist/bin-day-brain.exe` | Yes |
| Web App | [Live Demo](https://bin-day-brain.pages.dev/) \| `web-app/dist/` | Yes (live or self-hosted) |
| Android | `android-app/dist/bin-day-brain.apk` | Yes |

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
│   ├── requirements.txt
│   └── dist/
│       └── bin-day-brain.exe
│
├── web-app/               # Web App (HTML/CSS/JS - PWA)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── dist/              # Ready to deploy
│
├── android-app/           # Android App (Flutter)
│   ├── lib/main.dart
│   ├── pubspec.yaml
│   └── dist/
│       └── bin-day-brain.apk
│
└── README.md
```

## Quick Start

### Windows Desktop
Just run `desktop-app/dist/bin-day-brain.exe`

### Web App
1. Upload `web-app/dist/` contents to any web server
2. Or host on GitHub Pages
3. Open in browser

### Android
1. Copy `android-app/dist/bin-day-brain.apk` to your phone
2. Enable "Install from unknown sources"
3. Install the APK

## Development

See README in each app folder for development instructions.

## APIs Used

- **Wollongong Waste API** - Collection schedules, materials guide, events
- **Open-Meteo** - Free weather forecasts (no API key required)

## License

© 2026 Scott Leimroth. All Rights Reserved.
