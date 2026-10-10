# Third-party notices

## SILMA TTS v1

Echo Voice can download and load SILMA TTS v1 at runtime.

- Implementation/source package: [SILMA-AI/silma-tts](https://github.com/SILMA-AI/silma-tts). The upstream repository identifies the source code under the MIT License; retain the upstream copyright and license notice when redistributing source.
- Model weights: [silma-ai/silma-tts on Hugging Face](https://huggingface.co/silma-ai/silma-tts). The model card identifies the weights under Apache License 2.0; redistribute those weights only with the applicable license and notices.
- Package release used by the worker: `silma-tts==1.0.5`.
- The runtime loads weights from the upstream model repository into the configured model-cache volume. No model weights are bundled in the Android APK.

Before commercial production, re-check the exact license metadata and upstream terms for the source package, model weights, vocoder, normalizer, and all transitive dependencies. Voice sample performers may have rights separate from the software/model licenses; only use a reference voice you own or have explicit documented permission to use. Generated speech must be disclosed as AI-generated.
