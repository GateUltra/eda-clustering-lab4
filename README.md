# Clustering for EDA — Lab 4 maintainer edition

Module: `module01-05-size-constrained-agglomerative`

This package contains a **new English-narrated teaching video with burned-in English/Simplified Chinese subtitles**, 16 editable HTML slides (full video: 7 minutes 19 seconds), an English handout and transcript, per-slide narration, interactive exercises, a quiz, and reproducible Python/JavaScript implementations. The upstream video is not embedded or substituted for this new lesson.

## Open the course

From this directory, run:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/`. The site is static and has no build-time or runtime CDN dependencies. All local links are relative, including the video, subtitle downloads and exercises. `slides.html` also works directly as a local file; use Left/Right arrow keys or the navigation buttons. Click Listen to play the current slide’s English audio. For the synchronized bilingual experience, play the MP4.

## Files

| Path | Purpose |
| --- | --- |
| `media/lab04-lesson.mp4` | Finished H.264/AAC teaching video, 1280×720, 25 fps, bilingual captions burned in |
| `slides.html` | Editable English slides with no external JS dependencies |
| `handout.html` | English lesson handout, printable with the browser |
| `transcript.html`, `transcript.txt` | Final English narration text and per-slide audio players |
| `media/audio/slide-01.mp3` … `slide-16.mp3` | English synthesized narration, separately per slide |
| `media/audio/slide-*.json` | Final script and raw speech-service boundary timestamps |
| `media/captions/lab04-lesson.{en,zh,bilingual}.{srt,vtt}` | Separate English, Chinese and combined editable caption tracks |
| `media/captions/lab04-lesson.ass` | Styled bilingual caption source used for rendering |
| `media/lab04-lesson.timings.json` | Actual slide start/end times and audio durations |
| `source/make_lesson.py`, `source/lesson.json` | English slide content, narration and authored Chinese translations |
| `source/slides-template.html` | Editable slide layout and exact graph diagrams |
| `lab.html`, `quiz.html`, `assets/` | Interactive site and browser algorithm |
| `source/reference.py`, `source/exercise.py` | Completed Python reference and learner exercise stub |
| `source/graphs.json`, `source/goldens.json` | Original example, counterexamples and verified traces |
| `qa/` | Algorithm, media and browser verification evidence |
| `downloads/` | Convenient ZIP downloads for site visitors |

`media/sample-two-slides.mp4` is the early two-slide pipeline test, not the completed lesson. `media/segments/` is generated temporary build output and is excluded from the distribution. The deliberately incomplete `source/exercise.py` is a learner exercise; the completed solution is `source/reference.py`.

## Regenerate

Requirements: Python 3.10+, Node.js for cross-language tests, FFmpeg/ffprobe with libx264 and libass, and a Chromium browser for rendering. Install the media dependencies:

```bash
python -m pip install -r requirements-media.txt
python -m playwright install chromium
```

The distributed audio, frames and MP4 are already complete. Regeneration does not require a speech service unless you change narration or deliberately replace the cached audio.

```bash
# 1. Edit the authoring source, then regenerate content.
python source/make_lesson.py
python source/build_slides.py
python source/build_text.py

# 2. Generate changed narration (requires speech-service network access).
python source/synthesize.py --slides 1,2
# Verify a short sample before generating a new full lesson.
python source/render.py --slides 1,2
python source/build_video.py --slides 1,2 --output sample-two-slides.mp4
python source/synthesize.py

# 3. Render and assemble the full lesson from actual audio durations.
python source/render.py
python source/build_video.py

# 4. Verify and refresh download archives.
python source/verify.py
python source/verify_media.py
python source/verify_browser.py
python source/package_downloads.py
```

Set `CHROME_PATH` to an existing Chromium executable if Playwright’s bundled browser is unavailable. On Windows PowerShell: `$env:CHROME_PATH='C:\path\to\chrome.exe'`. On Linux: `CHROME_PATH=/path/to/chrome python source/render.py`.

Narration uses `en-US-JennyNeural`, rate `-5%`, via edge-tts. The script respects `HTTPS_PROXY`; if supplied, it adds the environment’s `SSL_CERT_FILE` to normal trusted roots. It does not disable TLS verification. Service availability and future voice output are not guaranteed. The frozen MP3 files make this delivery usable without regenerating speech.

Sentence boundaries come from the synthesized speech. The video builder clamps tiny overlapping boundary intervals, burns English above Chinese at fixed positions, and leaves a 0.45-second or slightly longer frame-aligned pause after each slide. Slide duration equals the decoded MP3 duration plus that pause, rounded up to a 25-fps frame. Original boundary metadata remains available. The website intentionally adds no `<track>` element to the already-captioned MP4.

## Algorithm checks

```bash
python source/verify.py
python source/reference.py --k 2 --capacity 2
python source/reference.py --k 2 --capacity 3
python source/reference.py --k 2 --capacity none
python source/reference.py --k 3 --capacity 2
python source/check_exercise.py --impl source/reference.py
```

The verifier checks the four required results, cutsize reduction per merge, capacity and stopping invariants, 47 complete Python/JavaScript trace comparisons, and independent exhaustive partition checks for the examples. See the handout for the exact member-list tie-break and its difference from upstream synthetic cluster IDs.

## GitHub Pages deployment

The destination repository has **not been supplied**, so this package has not been pushed or deployed.

1. Choose your destination repository and upload the **contents of the package directory** to its root. Keep `index.html`, `assets/`, `media/`, `source/` and `downloads/` together. Include `.nojekyll`.
2. In GitHub repository Settings → Pages, choose **Deploy from a branch**, then the desired branch (usually `main`) and `/(root)`.
3. Wait for GitHub Pages to report success. Open the published project URL and test the video, slides, lab, quiz and download links.
4. For integration into the original course instead of a standalone Pages project, place these files under `courses/learn_clustering/module01-05-size-constrained-agglomerative/` and update the parent course links through a reviewed change.

No comments have been posted to the teacher, no issue has been closed, and no instructor acceptance is claimed. Completed original browser challenges (10/10) and quiz (4/4) are prior review evidence only.

## Attribution and limitations

See `ATTRIBUTION.md`. The original five-node data and module topic are reused. The teaching text, video, narration, bilingual translations, diagrams, implementations, quizzes and counterexamples are new. The earlier draft ZIP was not available in this session and could not be reused. Speech has been checked with automated transcription and boundary/length checks; this does not substitute for the maintainer’s final subjective listening review. Browser QA covers a local project subpath, not a live GitHub Pages deployment.
