# Voice model selection: evaluation gate

Do not mark a candidate as production-approved until the exact checkpoint, code, dependency stack, and commercial license have been reviewed for the intended use.

| Candidate | Evaluation role | Required gate |
|---|---|---|
| OpenVoice V2 | Candidate for voice cloning/conversion | Verify exact code/checkpoint license, supported language behavior, deployment restrictions, GPU memory, and benchmark quality. |
| XTTS-v2 | Candidate for reference-conditioned multilingual speech | Review the current code and weights license for the exact artifacts and commercial use; benchmark each advertised language. |
| F5-TTS | Research comparison candidate | Review the license for exact code and weights before any commercial use. |

## Benchmark protocol
- Use only recordings with documented consent and rights.
- Record exact model revision, runtime, GPU, dependency lock, language, and input duration.
- Measure real-time factor, latency median/p95, failure rate, peak VRAM, and output duration.
- Combine blind human ratings for naturalness/speaker similarity with intelligibility and audio-quality measures; no single score represents all quality.
- Evaluate cross-language transfer separately from same-language cloning and publish only languages that pass the quality gate.
- Maintain a model registry and rollback path.

No such evaluations have been run by this repository change. This document defines a process, not passing results.
