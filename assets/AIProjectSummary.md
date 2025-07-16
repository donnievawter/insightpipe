# 📸 InsightPipe Project Summary

## 🧭 Purpose and Vision

**InsightPipe** is a modular AI-powered system designed to automate metadata enrichment for RAW image files, specifically ORF formats. It seamlessly integrates into a photographer's ingestion workflow, tagging each image with semantic keywords and descriptive prompts while preserving the original file structure and camera metadata.

Its guiding philosophy is:
- Zero manual intervention
- Maximum metadata insight
- Non-destructive enrichment
- Scalability through concurrency

This isn’t just a utility—it’s an intelligent co-pilot for image organization.

---

## 🔧 Technical Workflow

### 1. **Image Ingestion**

Files are imported either from SD cards or external drives via a custom script. Previously, these were sorted using ExifTool and timestamped folder structures. Now, the workflow introduces a staging directory:

```
ready_to_process/ ➞ InsightPipe ➞ processed/
```

### 2. **File Conversion**

Since LLMs can't interpret ORF files directly:
- InsightPipe converts `.ORF` → temporary `.JPG` using `rawpy` + `imageio`
- The JPG is stored in a dedicated temp directory: `/tmp/insightpipe_previews`
- No original files are overwritten

Conversion logic preserves filename casing and avoids accidental overwrites:
```python
os.path.splitext(orf_path)[0] + ".jpg"
```

### 3. **Metadata Inference and Tagging**

Each JPG is passed to an AI model along with a prompt:
- Descriptive prompt or keyword-specific
- Configurable via a simple interface or script call
- Model returns structured metadata

That metadata is then:
- **Embedded directly into the original ORF file** using ExifTool
- No sidecar files generated
- Camera info (Make, Model, DateTimeOriginal) remains intact

Optional: `job_id` is injected into the tagging call for traceability.

### 4. **Cleanup and Validation**

If a temporary JPG was created:
```python
if source_path != target_path and os.path.exists(target_path):
    os.remove(target_path)
```

This avoids filesystem clutter and ensures operational hygiene.

---

## 🕹️ Automation via Watchers

InsightPipe can run as a daemon via `launchd`, watching for new files:

- User-level LaunchAgent: `com.insightpipe.import.plist`
- Launchd commands used:
  ```bash
  launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.insightpipe.import.plist
  launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.insightpipe.import.plist
  ```

- Diagnostic script shows job status:
  ```bash
  check_insightpipe_jobs.sh
  ```

This enables passive enrichment on file drop.

---

## 🗃️ Post-Processing and Integration

Once metadata is embedded:
- Files are moved from `processed/` to archival folders (`bridge/YYYY/MM-DD`)
- Existing scripts handle structured backups via `rsync`
- Final backups contain enriched metadata

This means: the archive is search-ready and semantically enriched.

---

## 🧠 Future Possibilities

### Semantic Organization
InsightPipe’s enrichment opens paths for:
- Graph-based image browsing
- AI-curated “collections” by theme
- Metadata-driven image clustering

Instead of hierarchical folders, semantic pointers or indexes could reflect many-to-many relationships. Think:

```
Sunset ∩ Wildlife ∩ Silhouette → Semantic index
```

### Audit Trails and Observability
- Track last job per image via job_id
- Create visual dashboards with processed timestamps and keyword summaries
- Optional cron cleanup for `ready_to_process`

---

## 🎯 Summary of Contributions

✅ ORF-to-JPG conversion pipeline  
✅ Direct metadata embedding without sidecars  
✅ Watched folder ingestion and tagging  
✅ Safe temp file logic and cleanup  
✅ Job-level traceability via `job_id`  
✅ Web interface support (with alt fallback for raw previews)  
✅ Compatibility with multi-instance setups  
✅ Future-friendly for semantic organization  

InsightPipe isn’t just tagging—it’s quietly transforming how RAW archives are curated, searched, and scaled.
