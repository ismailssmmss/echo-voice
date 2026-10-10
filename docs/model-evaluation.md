# Voice model selection: evaluation gate

Do not designate a candidate as production-approved until the exact checkpoint, code, dependency stack, and commercial license have been reviewed for the planned use.

| Candidate | Role in evaluation | Required gate |
|---|---|---|
| OpenVoice V2 | Candidate for voice cloning/conversion | Verify checkpoint and code license, supported language behavior, deployment restrictions, GPU memory, and benchmark quality. |
| XTTS-v2 | Candidate for multilingual reference-conditioned generation | Verify current model card/license and commercial-use rights for the selected weights and service model; benchmark each advertised language. |
| F5-TTS | Research comparison candidate | Review the license attached to the exact code and weights. Do not assume commercial use is permitted. |

## Benchmark protocol
- Use only recordings with documented consent and rights.
- Record the exact model revision, runtime, GPU, dependency lock, language, and input duration.
- Measure real-time factor, wall-clock latency (median and p95), failure rate, peak VRAM, and output duration.
- Use blind human ratings for naturalness and speaker similarity; supplement with intelligibility and audio-quality measures. Do not use one metric as a proxy for all quality dimensions.
- Test language transfer separately from same-language cloning. Publish only languages that pass the quality gate.
- Keep a model registry and a rollback path; do not silently change voice output for existing projects.

This repository has not yet run these evaluations. The table is a plan, not a claim that any candidate has passed.
