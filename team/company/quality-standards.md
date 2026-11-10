# AI OFFICE — AUDIOVISUAL QUALITY STANDARDS

## 1. Technical Video Benchmarks
- **Container Format**: MP4 (H.264 / AVC video codec, AAC audio codec).
- **Short-Form Frame Rate & Dimensions**: 1080 × 1920 (9:16 vertical), 30 fps or 60 fps, minimum video bitrate 6 Mbps.
- **Long-Form Frame Rate & Dimensions**: 1920 × 1080 (16:9 horizontal), 30 fps or 60 fps, minimum video bitrate 10 Mbps.
- **Color Space**: Rec.709, standard sRGB gamut, clean black levels (no corrupted macroblocks or green frames).

## 2. Technical Audio Benchmarks
- **Sampling Rate**: 44.1 kHz or 48.0 kHz, stereo, minimum audio bitrate 192 kbps.
- **Loudness Standards**: Target integrated loudness of -14 LUFS (integrated) with maximum true peak of -1.0 dBTP.
- **Audio Cleanliness**: Zero clipping, zero unmastered harsh spikes, clear voiceover separation from background music.

## 3. Subtitles & Typography
- **Format**: Hardcoded burned-in subtitles (via FFmpeg `subtitles` filter) or WebVTT/SRT sidecar.
- **Legibility**: High-contrast outline/shadow, centered lower-third placement, maximum 2 lines per short-form frame, rhythmic synchronization with spoken voice.

## 4. Editorial & Content Quality
- **Hook Effectiveness**: Opening 3 seconds must create immediate curiosity or visual intrigue.
- **Factual Integrity**: Every empirical statistic or historical claim must have a verified source in the research dossier.
- **Pacing**: Short-form cuts every 2.0 to 4.0 seconds; dynamic transitions without visual clutter.
