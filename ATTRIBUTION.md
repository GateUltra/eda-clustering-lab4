# Attribution and provenance

## Original course

- Author/source: Yongfu Li, **eda-learning**.
- Repository: https://github.com/yongfu-li/eda-learning
- Inspected revision: `4fb4083379d066325384023af074f7bf59e98e09` (retrieved 2026-10-20).
- Module: `courses/learn_clustering/module01-05-size-constrained-agglomerative/`.
- Browser lab: https://yongfu-li.github.io/eda-learning/courses/learn_clustering/labs/size-constrained-agglomerative/index.html
- Source files reviewed: module README, EXAMPLES, CHECKLIST, transcript, quiz and tiny graph; `platform/assets/clustering-core.js`; `courses/learn_clustering/common/solvers.py`; browser lab/tool files and course README.
- No AGENTS.md was present in the retrieved repository tree.

Reused: the five-node graph (AB=5, AC=1, BC=4, CD=2, CE=1, DE=5), unit node sizes, topic, and required parameter comparisons. The original media is linked externally as reference material, not repackaged as new work. No upstream source code or media file is redistributed in this delivery. No blanket upstream license is asserted.

## New work in this edition

- Sixteen English HTML slides and newly rendered graph diagrams.
- Newly authored English narration and newly synthesized per-slide English audio.
- Authored Simplified Chinese translations aligned to English speech, with English above Chinese in the video.
- New English handout and transcript, browser interaction, ten calculation challenges, six-question quiz, Python reference, learner exercise, and verification scripts.
- Two new counterexamples: feasible target missed by greedy; legal greedy result with suboptimal cutsize.

The tie-break compares sorted original member lists. Upstream generates names such as C0 and C1, so tied merge traces need not agree generally. The inspected upstream merge loop also does not explicitly filter nonpositive affinities; this edition requires affinity > 0. The original positive-weight example retains its specified outcomes.

The upstream module README described the browser track as planned even though the platform included an implemented lab. This delivery provides a working browser track and does not repeat that obsolete status.

## Peer deliveries consulted

- Lab 2: https://capeur.github.io/eda-clustering-module-lab2/ — consulted for the course navigation pattern (video, slides, lab, implementation, quiz, transcript).
- Lab 3: https://github.com/thy031/lab-03 — consulted via its index.html for walkthrough, implementation, capacity and quiz structure.

No peer code, narration or graphics were copied. The draft `Lab04_course_package.zip` was not found in the available files, so no draft reuse is claimed.

## Tools and fonts

- Narration: Microsoft `en-US-JennyNeural`, accessed through edge-tts 7.3.1, rate -5%. AI-generated voice, not a human recording.
- Video: FFmpeg, H.264 video and AAC audio; bilingual captions rendered with libass.
- Chinese caption font: Noto Sans CJK SC Regular, from https://github.com/notofonts/noto-cjk, licensed under the SIL Open Font License. See `assets/fonts/LICENSE-Noto.txt`.
- English captions: DejaVu Sans, from the rendering environment. HTML uses the system Arial/Helvetica/sans-serif stack.
- Automatic speech checks: faster-whisper with the base model. Automatic transcription can confuse spoken letter names; the source script and captions remain authoritative.

## Status

Prepared as a local course-maintenance deliverable. Not deployed to a destination repository, submitted to the teacher, or accepted by an instructor. Original-lab completion scores do not establish maintenance completion.
