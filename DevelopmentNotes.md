# 🚧 InsightPipe — Development Notes

## Ideas for Future Expansion

- Docker container for non-dev usage
- Dry-run simulation with image previews
- UI layer (local gallery or prompt editor)
- Remote Ollama support for lightweight clients
- Config templating with domain presets (e.g. wildlife, abstracts)

## Guiding Principles

- Minimal setup friction
- Modular structure
- Semantic clarity in outputs
- Respect for resource constraints
- Built for deliberate, thoughtful use—not speed

---

*Keep vision close, keep execution clean.*
### 🗂 Metadata Tag Mapping Rationale (InsightPipe)

To ensure cross-platform compatibility and searchability across tools like Adobe Bridge, Immich, and future indexing workflows, InsightPipe uses a dual-tagging strategy for keywords:

- **`IPTC:Keywords`**: Standard location recognized by Adobe Bridge and many DAM tools.
- **`XMP-dc:Subject`**: Dublin Core field interpreted as keyword set by Immich and other EXIF/XMP-aware tools.

This redundancy ensures that keywords remain accessible regardless of platform quirks or UI interpretations.

#### Classification Mode (`keywords=True`)
- Description is treated as list of keywords
- Tags written to:
  - `IPTC:Keywords`
  - `XMP-dc:Subject`
- Prompt (`keywordprompt`) is ignored due to verbosity and lack of semantic value.

#### Description Mode (`keywords=False`)
- Longform description stored in `XMP-dc:Description`
- Prompt stored in `XMP-dc:Title` for contextual reference

#### Both Modes
- InsightPipe Inference stored in `Headline`
- Model stored in `IPTC:Writer-Editor`


This structure avoids misuse of `UserComment`, preserves clarity, and maximizes metadata utility across search engines, image managers, and future InsightPipe extensions.

## ✨ Callable Module Support (v0.3)

InsightPipe now supports direct invocation as a Python module via:

### `keyword_file(fpath, model=None, max_keywords=None)`
- Auto-loads `config.yaml` if not already initialized
- Returns structured keywords from supported models
- Optional `max_keywords` to limit output size
- Keywords are inferred using the internal `keywordPrompt` from config
- Model availability is validated via `getAvailableModels()` using the Ollama backend

### `describe_file(fpath, prompt, model=None)`
- Uses arbitrary prompt provided by caller
- Supports flexible descriptive tasks (e.g. image summaries, alt text)
- Returns structured result with timestamp and description
- Model validation is enforced at runtime

### Runtime Behavior Notes
- `init_from_file(config_path)` is available for config override; defaults to `"config.yaml"`
- Keyword prompt is fixed via config to ensure consistency and parsing integrity
- Internal config, model, and Ollama endpoint are lazily initialized upon first call
- CLI execution remains unchanged and separated under `run_main_pipeline()` via `if __name__ == "__main__"`

InsightPipe can now be used cleanly by external scripts and containers without triggering CLI behavior unintentionally