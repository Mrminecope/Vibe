# Vibe 5.0 — Music Player

A sleek, privacy-focused, ad-free Linux desktop music player whose **only music provider is YouTube / YouTube Music**.

## What changed

- Removed Jamendo, Apple/iTunes previews, MusicBrainz playback, generic URL playback, and other music providers from the active application.
- Search is powered by the official **YouTube Data API v3**.
- Full-song playback uses YouTube's **official embedded player** inside Vibe.
- No `yt-dlp`, raw YouTube stream extraction, DRM bypass, or downloaded audio files.
- Queue, previous/play/stop/next, seek timeline, and YouTube player remain inside the Vibe UI.
- API key is session-only and is not written to disk by Vibe.
- Vibe itself adds no advertising or behavioral tracking.

## Setup

Install system packages on Kali:

```bash
sudo apt update
sudo apt install python3 python3-venv
```

Then double-click `run.sh` (or create the desktop entry from `vibe.desktop`). On first launch, Vibe creates its Python environment and installs its dependencies.

Open **Settings → YouTube Data API key** and enter a Google Cloud API key with **YouTube Data API v3** enabled. The key remains in RAM for the current Vibe session only.

## Playback model

Vibe does not turn YouTube URLs into downloadable/raw audio URLs. Search results provide YouTube video IDs and playback is performed by YouTube's official embedded player. This is the supported approach for integrating YouTube playback without bypassing protected delivery mechanisms.

## Privacy boundary

Vibe does not add an advertising SDK, behavioral profile, local playback history, or media download cache. However, the embedded YouTube service is still a remote service: YouTube can process requests and playback activity according to its own service/privacy policies. Vibe cannot promise anonymity from YouTube.

This release also does not claim that application-level privacy features defeat operating-system swap/page-cache behavior or every network/host-level observer.

## Tests

```bash
pytest -q
```
