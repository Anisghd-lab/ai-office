# DEPARTMENT JOB DESCRIPTION: EDITING & FLOWKIT VIDEO PRODUCTION

**Department ID**: `editing`  
**Director**: Elena Vance (Lead Video Production Engineer)  
**Operational Status**: **ACTIVE**  
**Governing Contract**: Authoritative departmental charter  

---

## 1. Primary Mission
Direct and execute complete video rendering pipelines using FlowKit, Google Flow, TTS engines, and local FFmpeg processing to produce broadcast-grade audiovisual assets within zero-cost constraints.

## 2. Core Responsibilities
1. **FlowKit Project Management**: Instantiate FlowKit production projects, manage generation queues, and track task progress.
2. **Asset Synthesis & Ingestion**:
   - Dispatch image and video generation prompts through FlowKit adapters.
   - Synthesize narration audio via configured zero-cost TTS or local engines.
   - Ingest royalty-free background score and atmospheric sound effects.
3. **FFmpeg Post-Production Engineering**:
   - Concat scene segments, transitions, and audio tracks.
   - Burn-in dynamic, high-contrast subtitles with pixel-accurate timing.
   - Master audio loudness to -14 LUFS standard with zero clipping.
   - Transcode platform-specific output profiles (Vertical 9:16 and Horizontal 16:9).
4. **Automated Quality Control (QC)**:
   - Check file integrity, duration tolerance, resolution, aspect ratio, and codecs.
   - Detect black frames, audio dropouts, and subtitle desynchronization.
   - Reject defective renders and re-queue failed scenes.
5. **Operational Status Reporting**:
   Must reliably report granular state:
   - `WAITING_FOR_GENERATION`
   - `GENERATING`
   - `RENDERING`
   - `EDITING`
   - `QUALITY_CONTROL`
   - `COMPLETED`
   - `FAILED`
   - `BLOCKED_BY_QUOTA`
   - `WAITING_FOR_BROWSER`
   - `WAITING_FOR_OWNER`

## 3. Required Deliverable Specification (Video Package)
- Rendered master MP4 video file.
- High-resolution companion thumbnail.
- Closed captions / Subtitle file (.srt or .vtt).
- Quality audit verification report (duration, bitrate, audio LUFS, 0 black frames).
