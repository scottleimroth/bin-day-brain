# Bin Day Brain - System Architecture

## Overview

Bin Day Brain is a multi-platform waste collection reminder app for Wollongong/Illawarra residents. It provides three independent client apps (web, desktop, Android) that each directly query public APIs for collection schedules and weather data. There is no backend server -- all logic runs client-side.

---

## Architecture Diagram

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    Web App       │  │  Desktop App     │  │  Android App     │
│  (HTML/CSS/JS)   │  │  (Python/CTk)    │  │  (Flutter/Dart)  │
│  PWA on CF Pages │  │  PyInstaller EXE │  │  APK via Release │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
         └─────────┬───────────┴──────────┬───────────┘
                   │                      │
                   ▼                      ▼
         ┌─────────────────┐    ┌─────────────────┐
         │ Wollongong      │    │ Open-Meteo       │
         │ Waste API       │    │ Weather API      │
         │ (schedules,     │    │ (forecasts,      │
         │  materials,     │    │  wind, rain)     │
         │  events)        │    │                  │
         └─────────────────┘    └─────────────────┘
```

---

## Technology Stack

### Web App
- **Framework:** Vanilla HTML/CSS/JS (PWA)
- **Hosting:** Cloudflare Pages
- **Key features:** Service worker for offline, localStorage for caching

### Desktop App
- **Framework:** Python + CustomTkinter
- **Packaging:** PyInstaller (single EXE)
- **Key libraries:** requests, customtkinter

### Android App
- **Framework:** Flutter/Dart
- **Key packages:** http, shared_preferences, path_provider

### External Services
- **Wollongong Waste API:** Collection schedules, materials guide, events
- **Open-Meteo API:** Weather forecasts (free, no key required)

---

## Component Structure

```
bin-day-brain/
├── web-app/               # Web App (HTML/CSS/JS - PWA)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── dist/              # Deployable build
│
├── desktop-app/           # Windows Desktop (Python + CustomTkinter)
│   ├── main.py
│   └── requirements.txt
│
├── android-app/           # Android App (Flutter)
│   ├── lib/main.dart
│   └── pubspec.yaml
│
├── README.md
├── ARCHITECTURE.md
├── TODO.md
├── SECURITY_AUDIT.md
├── CREDENTIALS.md          # .gitignored
└── .gitignore
```

---

## Data Models

### Collection Schedule
- Address: String - User's street address
- Bin type: Enum (FOGO/Recycling/Landfill)
- Next collection date: Date
- Days until: Integer (computed)

### Weather Alert
- Date: Date - Collection day
- Wind speed: Float (km/h)
- Rain probability: Float (%)
- Alert type: Enum (Wind/Rain/None)

---

## Key Workflows

### Address Setup
1. User enters suburb or street
2. App queries Wollongong Waste API for matching addresses
3. User selects their address from results
4. Collection schedule is fetched and cached locally

### Dashboard Refresh
1. App loads cached schedule on startup
2. Computes days until each bin type's next collection
3. Queries Open-Meteo for weather on collection days
4. Displays color-coded cards with weather alerts

---

## API Endpoints

**Wollongong Waste API (external):**
- Address search/lookup
- Collection schedule by address
- Materials guide (which bin for each item)
- Special events calendar

**Open-Meteo API (external):**
- 7-day weather forecast by coordinates
- Wind speed and rain probability

---

## Security Considerations

- **Authentication:** None required (all public APIs)
- **Data storage:** Local only (localStorage/SharedPreferences/config.json)
- **No PII transmitted:** Only suburb/address sent to council API
- **HTTPS:** All API calls use HTTPS

---

## Deployment

- **Web app:** Push to main triggers Cloudflare Pages deployment
- **Desktop:** Build with PyInstaller, upload EXE to GitHub Releases
- **Android:** Build with Flutter, upload APK to GitHub Releases

---

## Scalability Notes

- Fully client-side architecture means no server costs or scaling concerns
- Adding new councils would require adapting to each council's waste API
- Could add push notifications via Firebase if server-side component is added later

---

**Last Updated:** 2026-02-10
