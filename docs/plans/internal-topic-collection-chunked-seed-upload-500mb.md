# Internal Topic Collection Seed Upload Plan (Chunked, 500MB)

## Summary
Replace the current single-request `custom_seeds_file` upload in Internal Topic Collection edit with `django-chunked-upload`, so large `.txt` seed imports are reliable on slow networks and do not require broad site-wide large upload allowances.

This plan keeps current import semantics:
- backup old `custom_seeds`
- replace with uploaded UTF-8 text
- do not auto-pair after file import

## Decisions Locked In
- `chunked_upload` is already installed and importable in container runtime.
- Maximum chunked upload size: **500MB** (`524288000` bytes), matching current nginx convention.
- `DATA_UPLOAD_MAX_MEMORY_SIZE` should be reduced to **10MB** by default, because chunked file payload is sent in `request.FILES` and this setting protects large non-file POST bodies.
- Checksum strategy is fixed to **MD5** (required by `django-chunked-upload` completion flow), computed client-side incrementally with **SparkMD5** and sent as `md5` in complete request payload.

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
- `CHUNKED_UPLOAD_MAX_BYTES = int(os.environ.get('CHUNKED_UPLOAD_MAX_BYTES', 524288000))`
- `CHUNKED_UPLOAD_EXPIRATION_DELTA = int(os.environ.get('CHUNKED_UPLOAD_EXPIRATION_DELTA', 86400))`
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
