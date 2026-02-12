# Internal Topic Collection Seed Upload Plan (Chunked, 500MB)

## Summary
Replace the current single-request `custom_seeds_file` upload in Internal Topic Collection edit with `django-chunked-upload`, so large `.txt` seed imports are reliable on slow networks and do not require broad site-wide large upload allowances.

This plan keeps current import semantics:
- backup old `custom_seeds`
- replace with uploaded UTF-8 text
- do not auto-pair after file import

## Decisions Locked In
- `chunked_upload` is already installed and importable in container runtime.
- Maximum logical chunked upload size: **500MB** (`524288000` bytes).
  - this is enforced by Django chunked-upload settings, not by raising nginx
    request body limits globally.
- `FILE_UPLOAD_MAX_MEMORY_SIZE` default should be **10MB** so regular file
  uploads do not buffer excessively in process memory.
- `DATA_UPLOAD_MAX_MEMORY_SIZE` should be reduced to **10MB** by default, because chunked file payload is sent in `request.FILES` and this setting protects large non-file POST bodies.
- Checksum strategy is fixed to **MD5** (required by `django-chunked-upload` completion flow), computed client-side incrementally with **SparkMD5** and sent as `md5` in complete request payload.

## Initial Code Review Stage (2026-02-12)
This stage captures post-implementation fixes required after initial code review.

### Critical Tasks
1. Fix stale `seeds_frozen` after upload-import fast path:
   - Problem:
     - Upload-import currently writes `custom_seeds` via queryset `update(...)`,
       bypassing model `save()` and `pre_save` signal (`freeze_tc_urls`).
     - Result: `seeds_frozen` can stay stale and `get_seeds()` may return old data.
   - Required implementation:
     - In upload-import branch, always handle `seeds_frozen` explicitly so it can
       never remain stale.
     - Keep submit latency bounded: do not reintroduce expensive
       `model.save()`/reversion path for large imports.
     - Current chosen mitigation: invalidate cache (`seeds_frozen=""`) during
       upload consume so runtime `get_seeds()` recomputes from current data.
   - Required tests:
     - Regression proving old frozen data is not returned after upload import.

2. Remove partial-write risk on failed upload consume:
   - Problem:
     - M2M/attachment writes could happen before upload-id validation/decode,
       allowing partial state changes on early-return errors.
   - Required implementation:
     - Validate/consume upload within transactional logic.
     - Reorder side-effecting writes (`save_m2m`, attachments) to happen only
       after upload has passed validation and decode checks.
   - Required tests:
     - Invalid upload id must not persist unrelated form edits or attachment
       deletes.

### High Tasks
1. Make upload consume race-safe / one-time:
   - Problem:
     - Two near-simultaneous submits with same `upload_id` can race.
   - Required implementation:
     - Use transactional row locking (`select_for_update`) for upload consume.
     - Keep delete-on-success semantics and session binding cleanup.
   - Required tests:
     - Reuse of consumed upload id is rejected and does not persist edits.

2. Remove avoidable memory amplification during upload submit:
   - Problem:
     - Submit path decodes full file to text and then re-encodes full string
       just for logging size.
   - Required implementation:
     - Do not call `len(new_custom_seeds.encode("utf-8"))` in timing logs.
     - Use upload metadata (`offset`/stored size) for logged byte count.

3. Harden backup file path generation:
   - Problem:
     - Backup filename used raw title characters; slash/path segments could lead
       to writes outside intended backup directory.
   - Required implementation:
     - Sanitize title segment (slug-safe), enforce absolute-path containment
       under `MEDIA_ROOT/SEEDS_BACKUP_DIR`, and write file with explicit UTF-8.
   - Required tests:
     - Backup filename/path sanitization regression.

### Reversion Performance Guardrails
- Keep `TopicCollection` reversion exclusions for large fields:
  - `custom_seeds`
  - `seeds_frozen`
  - `last_changed`
- Goal:
  - avoid large `reversion_version` rows and submit-time overhead when importing
    large custom seed files.
- Verification:
  - upload-import branch must avoid model save where large fields would be
    serialized into reversion history.
  - no stale seed behavior despite avoiding model save.

## Post-Review Follow-up Stage (2026-02-12, Storage & Throughput)
### Ingress policy decision (2026-02-12)
- Decision:
  - keep nginx `client_max_body_size` at **10MB** globally and for `/seeder/`.
  - do not use `500MB` nginx body limits for chunked seed upload.
- Context:
  - chunk upload requests are sent in ~4MB parts; each request stays well below
    10MB.
  - raising nginx to 500MB for `/seeder/` increases unauthenticated edge abuse
    surface without being required for chunked workflow correctness.
- Timeouts for `/seeder/`:
  - set broad request/response timeouts to **300s** for authenticated app area
    (`client_body_timeout`, `proxy_connect_timeout`,
    `proxy_send_timeout`, `proxy_read_timeout`).
  - scope is path-level (`/seeder/`), not endpoint-specific.

### Daily stale upload cleanup
- Problem:
  - Users may upload chunks and never submit the form.
  - Temp files/rows then remain until explicitly removed and can exhaust disk.
- Implemented approach:
  - Daily cron job: `harvests.cron.cleanup_expired_chunked_uploads`.
  - Deletes every `ChunkedUpload` older than `CHUNKED_UPLOAD_EXPIRATION_DELTA`
    and removes associated temp files.
  - Added to `CRONJOBS` in settings:
    - `('5 1 * * *', 'harvests.cron.cleanup_expired_chunked_uploads')`
- Expected behavior:
  - stale partial/complete uploads are automatically reclaimed at least once/day.

### Proactive cleanup on replacement upload
- Problem:
  - Uploading another file for the same topic/session could keep old upload
    artifacts around until cron window.
- Implemented approach:
  - On first chunk of a new upload, remove older same-topic/same-user upload
    bindings from session and delete corresponding upload artifacts.
- Expected behavior:
  - repeated re-uploads do not accumulate within active editing sessions.

### Throughput optimization (submit path)
- Implemented:
  - Move UTF-8 decode outside the DB transaction and row-lock window.
  - Keep transactional section focused on validation, update, and consume.
  - Keep reversion-heavy model save path avoided for large imports.
- Note:
  - Writing 100MB text into DB is still inherently expensive; the optimization
    removes avoidable lock/coordination overhead but does not remove database
    I/O cost itself.

### No-op save fast path for large collections (2026-02-12)
- Problem:
  - Editing a TC with very large `custom_seeds` could still take tens of
    seconds even when no meaningful field was changed.
- Root cause:
  - no-upload edit branch still called `topic.save(...)` for large collections,
    and `TopicCollection` pre-save seed-freezing logic could do expensive work.
- Implemented approach:
  - In `InternalCollectionEdit.form_valid`, detect "no real changes"
    (`changed_data` + m2m/attachment deltas) and skip topic save entirely.
  - For large-seed no-upload edits, save only actually changed concrete model
    fields (`update_fields=changed_model_fields`) instead of broad field sets.
  - In `freeze_tc_urls` pre-save signal, skip freeze recalculation when
    `update_fields` does not include seed-related fields.
  - Keep full freeze behavior for seed-related saves.
- Expected behavior:
  - Saving unchanged large TCs should return quickly (seconds, not tens of
    seconds) because no large seed write/freeze path is executed.

## Prerequisites (must be done before coding)
- Verify chunked upload migrations are applied:
  - `./drun showmigrations chunked_upload`
  - `./drun migrate`
- Confirm runtime model/table for chunk uploads exists before implementing endpoint logic.

## Current Flow (to replace)
- Form field is direct file upload: `Seeder/harvests/forms.py:206`
- Edit handler reads full uploaded file in one request: `Seeder/harvests/views.py:516`
- Replace logic is in:
  - backup call: `Seeder/harvests/views.py:518`
  - decode + replace: `Seeder/harvests/views.py:520`
  - warning "not paired automatically": `Seeder/harvests/views.py:530`

## Target Flow
1. User opens Internal TC edit form.
2. User selects a `.txt` file.
3. Browser uploads chunks asynchronously to dedicated Django endpoints.
4. Browser sends completion request (with checksum) and gets `upload_id`.
5. Browser stores `upload_id` in hidden field.
6. User submits the normal edit form.
7. Server resolves `upload_id`, decodes uploaded file as UTF-8, performs backup+replace, and deletes temporary chunk upload data.

## File-by-File Implementation

### 1) `Seeder/harvests/views.py`
Add dedicated chunked upload views and wire them to Internal TC context:
- `InternalCollectionCustomSeedsChunkUploadView`
- `InternalCollectionCustomSeedsChunkCompleteView`

Requirements:
- authenticated access only
- only for valid Internal TC `pk`
- endpoint-level validation: `.txt` file only, `text/plain` or `application/octet-stream`
- max bytes enforced by chunked upload settings (500MB)

Update `InternalCollectionEdit.form_valid`:
- replace `custom_seeds_file` handling with hidden `custom_seeds_upload_id`
- when upload id is present:
  - validate upload exists and is complete
  - decode UTF-8; on decode failure show existing error message and abort replacement
  - call `backup_custom_seeds()`
  - assign decoded text to `topic.custom_seeds` and save
  - preserve current success/warning messages
  - remove consumed temp upload artifact
- keep existing non-upload edit branches unchanged (`custom_seeds_too_large`, pair behavior when no file import)
- explicitly update `topic.save(update_fields=...)` exclusion set to also exclude `custom_seeds_upload_id` (non-model form field), otherwise Django will raise on save.

### 2) `Seeder/harvests/forms.py`
In `InternalTopicCollectionEditForm`:
- remove direct `custom_seeds_file = forms.FileField(...)` from server-handled upload path
- add `custom_seeds_upload_id = forms.CharField(required=False, widget=forms.HiddenInput())`
- update help text to explain chunked upload behavior and overwrite semantics
- keep `files_to_delete` and other existing fields unchanged
- update `__init__` logic that currently references `self.fields["custom_seeds_file"]`; retarget it to the new upload UI/help field path (or guard the access) so form init does not break when `custom_seeds_file` is removed.

### 3) `Seeder/harvests/urls.py`
Add two URL patterns under internal collections:
- `collections/internal/<int:pk>/custom-seeds/chunk-upload`
- `collections/internal/<int:pk>/custom-seeds/chunk-upload/complete`

Use explicit URL names for template JS wiring.

Effective routed endpoints (including global prefixes) will be:
- `/seeder/harvests/collections/internal/<int:pk>/custom-seeds/chunk-upload`
- `/seeder/harvests/collections/internal/<int:pk>/custom-seeds/chunk-upload/complete`

### 4) New template for Internal TC edit
Create `Seeder/harvests/templates/internal_tc_edit_form.html` and set:
- `InternalCollectionEdit.template_name = 'internal_tc_edit_form.html'`

Template responsibilities:
- render existing form fields
- add file picker UI for chunk upload
- add progress/status UI
- include hidden `custom_seeds_upload_id`
- disable submit while upload is active
- block submit if file selected but upload not completed

### 5) New JS file for chunk upload client
Create `Seeder/static/harvests/internal_tc_chunked_upload.js`.

Responsibilities:
- split selected file into chunks (recommended 4MB each)
- POST chunks sequentially with required fields (`file`, `filename`, `offset`, optional `upload_id`)
- compute incremental MD5 with SparkMD5 during chunk iteration and send final `md5` on complete request
- fill hidden `custom_seeds_upload_id` on success
- update progress UI and lock/unlock submit button
- report failures clearly and keep submit blocked until fixed/retried

Concrete implementation decision:
- add SparkMD5 as a static vendor asset (for deterministic behavior across browsers), include it only on `internal_tc_edit_form.html`, and keep upload logic in `Seeder/static/harvests/internal_tc_chunked_upload.js`.

### 6) `Seeder/settings/env.py`
Add/update env-driven settings:
- `FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('FILE_UPLOAD_MAX_MEMORY_SIZE', 10485760))`
- `CHUNKED_UPLOAD_MAX_BYTES = int(os.environ.get('CHUNKED_UPLOAD_MAX_BYTES', 524288000))`
- `CHUNKED_UPLOAD_EXPIRATION_DELTA = int(os.environ.get('CHUNKED_UPLOAD_EXPIRATION_DELTA', 21600))`
- `CHUNKED_UPLOAD_PATH = os.environ.get('CHUNKED_UPLOAD_PATH', 'chunked_uploads')`

Lower non-file POST memory ceiling:
- `DATA_UPLOAD_MAX_MEMORY_SIZE` default from `524288000` to `10485760` (10MB)

Note:
- Keep env override support so deployment can raise if another legitimate large non-file POST endpoint exists.

## Data and Security Constraints
- Upload endpoints must require login.
- Upload id must not be accepted blindly:
  - verify completion state
  - verify it belongs to current authenticated context (at least current session/user + TC binding)
  - enforce one-time consumption (after successful import, upload record/file must be deleted and upload id cannot be reused)
- Accept only `.txt` imports for this workflow.
- Keep large upload capability scoped to dedicated upload endpoints.

## Potential Issues and Mitigations
- Interrupted uploads / slow network:
  - chunk retries + resumable offset behavior; clear client status on mismatch.
- Orphaned temporary chunk files:
  - delete on successful consume; add cleanup for expired uploads.
- UTF-8 decode failure:
  - retain current behavior: show error, do not replace `custom_seeds`.
- Large text replacement memory spikes:
  - avoid duplicate full in-memory copies where possible; keep worker limits monitored.
- Hidden upload id tampering:
  - server-side ownership/context checks before consuming upload.
- Lower `DATA_UPLOAD_MAX_MEMORY_SIZE` side effect:
  - if any endpoint depends on huge non-file POST bodies, that endpoint must get explicit handling or higher env value.
- Slow submit after upload (large `custom_seeds`):
  - avoid `model.save()` in the upload-consume branch because revision middleware
    can serialize huge `custom_seeds` into `reversion_version` rows.
  - persist edited scalar fields + `custom_seeds` via a single queryset
    `update(...)` in that branch to keep submit latency bounded.
  - keep `pair_custom_seeds()` out of the upload-import path.

## Testing Plan

### Automated tests (harvests tests module)
- authenticated chunk upload happy path
- unauthenticated upload denied
- invalid extension rejected
- >500MB rejected
- completion checksum mismatch rejected
- form submit with valid `custom_seeds_upload_id` performs backup+replace
- upload decode error preserves old `custom_seeds`
- existing edit behavior without file upload remains unchanged

### Manual checks
- upload 300MB+ txt over throttled link
- verify progress + final save
- confirm warning: uploaded seeds are not auto-paired
- verify backup file exists in `media/seeds/backup`

## Acceptance Criteria
- Internal TC edit supports `.txt` seed uploads up to 500MB reliably.
- Upload no longer depends on a single long multipart request.
- Current backup/replace/not-auto-pair semantics are preserved.
- Default `DATA_UPLOAD_MAX_MEMORY_SIZE` is 10MB unless overridden by env.
- Change is isolated to Internal TC edit workflow and dedicated upload endpoints.

## Rollout Notes
- This plan is Django-centric and does not require global nginx/traefik changes.
- If edge proxy adjustments are needed later, restrict them to the new upload endpoint paths only.

## Implementation Notes (2026-02-12)
- User-reported issue after initial rollout:
  - In browser testing, clicking "Send" after a fully completed upload could
    still take ~28s for a ~15MB file.
- Investigation outcome:
  - `pair_custom_seeds()` is not called in the upload-import branch.
  - Main expensive work during submit is large `custom_seeds` persistence and
    (previously) model `save()` side effects under `reversion` middleware.
  - Some requests still had non-`custom_seeds` field changes (`date_from`)
    in `form.changed_data`, which could trigger `topic.save(update_fields=...)`
    and extra revision serialization cost.
- Mitigation implemented:
  - In upload-import branch, avoid model `save()` entirely.
  - Persist both edited scalar fields and `custom_seeds` through a single
    queryset `update(...)`, while keeping backup/replace semantics unchanged.
  - Keep one-time upload consumption and context ownership checks unchanged.
- Observability added:
  - Upload-import submit logs detailed timings in
    `Internal TC upload consume timings (...)` including:
    `decode`, `backup`, `save`, `cleanup`, `total`.
- Current known behavior:
  - Submit path no longer runs seed pairing for upload-import.
  - Remaining latency depends mostly on DB/storage performance for writing large
    `custom_seeds` and backup file I/O.
