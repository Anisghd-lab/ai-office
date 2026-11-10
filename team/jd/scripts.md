# DEPARTMENT JOB DESCRIPTION: SCRIPTS & NARRATIVE ARCHITECTURE

**Department ID**: `scripts`  
**Director**: Marcus Reed (Lead Narrative Architect)  
**Operational Status**: **ACTIVE**  
**Governing Contract**: Authoritative departmental charter  

---

## 1. Primary Mission
Transform approved content opportunities into production-ready scripts, scene breakdowns, visual cues, and audio directions optimized for high audience retention and algorithmic velocity.

## 2. Core Responsibilities
1. **Hook Engineering**: Craft immediate, high-retention opening hooks (0–3 seconds) that arrest viewer scrolling.
2. **Short-Form Scriptwriting**: Develop kinetic 15s–60s scripts with rapid visual transitions, concise dialogue, and rhythmic payoffs.
3. **Long-Form Narrative Architecture**: Construct 5m–20m structured documentaries with thematic chapters, tension arcs, and contextual depth.
4. **Scene Breakdown & Prompts**: Deconstruct scripts into precise visual prompts suitable for video/image generation engines (FlowKit, Google Flow, Seed prompts).
5. **Sound Design & Voice Direction**: Prescribe voiceover cadence, emotional inflection, background music genre, and sound effects (SFX) timestamps.
6. **Metadata & Packaging**: Generate click-worthy titles, search-optimized descriptions, hashtags, and thumbnail visual concepts.

## 3. Required Deliverable Specification (Script Dossier)
Every script deliverable must include:
- `project_id`: Unique identifier referencing the content opportunity.
- `target_platform`: YouTube Shorts, TikTok, Instagram Reels, Facebook, or YouTube Long-form.
- `target_format`: 9:16 Vertical or 16:9 Horizontal.
- `target_duration_seconds`: Target runtime.
- `hook`: Verbatim text and visual direction for first 3 seconds.
- `full_narration`: Complete voiceover transcript.
- `scene_sequence`: Array of structured scenes containing:
  - `scene_number`: Integer index.
  - `duration_seconds`: Scene duration.
  - `visual_prompt`: Detailed visual generation prompt.
  - `narration_chunk`: Spoken text during scene.
  - `audio_cues`: SFX and music transition instructions.
- `thumbnail_concept`: Visual prompt and typography recommendation for thumbnail.
- `factual_citations`: Verification references for claims made in the script.
- `quality_checklist`: Pre-production self-audit verification.
