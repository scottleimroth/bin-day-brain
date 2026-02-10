# Bin Day Brain - Development Log & TODO

## Last Session

- **Date:** 2026-02-10
- **Summary:** Added standard repo files (CREDENTIALS.md, SECURITY_AUDIT.md, TODO.md, ARCHITECTURE.md)
- **Key changes:**
  - Created standard repo documentation files
  - Updated .gitignore with credentials entries
- **Stopped at:** Repo standardisation complete
- **Blockers:** None

---

## Current Status

### Working Features
- Smart Setup Wizard with Wollongong Waste API address lookup
- Color-coded dashboard (Green/Yellow/Red bins) with countdown
- Weather-smart alerts (wind warnings, rain advisory)
- Which Bin? A-Z search guide
- Event alerts for special collections
- Offline support with local caching
- Web app (Cloudflare Pages PWA)
- Windows desktop app (Python + CustomTkinter)
- Android app (Flutter)

### In Progress
- None currently

### Known Bugs
- None currently tracked

---

## TODO - Priority

1. [ ] Review and update dependencies across all three app versions
2. [ ] Add automated testing for web app
3. [ ] Verify Wollongong Waste API endpoints are still current

---

## TODO - Nice to Have

- [ ] iOS app build
- [ ] Push notifications for bin day reminders
- [ ] Widget support for Android home screen
- [ ] Dark mode for web app
- [ ] Multi-council support beyond Wollongong

---

## Completed

- [x] Web app deployed to Cloudflare Pages (2026)
- [x] Windows desktop app with PyInstaller packaging (2026)
- [x] Android app with Flutter (2026)
- [x] GitHub Releases for binary distribution (2026)
- [x] Repo standardisation - added required docs (2026-02-10)

---

## Architecture & Decisions

| Decision | Reason | Date |
|----------|--------|------|
| Three separate apps | Different platforms need different tooling (Python/HTML/Flutter) | 2026 |
| Cloudflare Pages for web hosting | Free, fast CDN, easy deployment | 2026 |
| GitHub Releases for binaries | Keep repo clean, private releases for private repo | 2026 |
| Public APIs only (no auth) | Wollongong Waste and Open-Meteo are free, no keys needed | 2026 |

---

## Notes

- Wollongong Waste API is a public council API - monitor for changes/deprecation
- Open-Meteo weather API is free with no key required
- Binaries distributed via GitHub Releases, never committed to repo
