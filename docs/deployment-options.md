# Deployment Options

Two viable paths. The right one depends on how much IT access the brokerage
team has and how fast you want to move.

---

## Option A — Production Web Application (FastAPI + React)

This is the recommended path for end-users. It provides a password-protected web portal with validation feedback before any PowerPoint is rendered.

### Architecture
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React + Vite single-page app
- **Container**: Docker (Debian-slim)
- **Data Policy**: Uploads are written to the system temp directory for the active session and deleted after generation or expiry. See Data Privacy Considerations for the exact paths and the cases where a file can remain.

### How to Run Locally (Docker)
1. Ensure Docker is installed.
2. From the project root:
   ```bash
   docker build -t schematic-builder .
   docker run -p 8000:8000 \
     -e ADMIN_USERNAME=admin \
     -e ADMIN_PASSWORD=yourpassword \
     -e ALLOWED_ORIGINS=http://localhost:8000 \
     schematic-builder
   ```
3. Open `http://localhost:8000` in your browser.

### Cloud Deployment (Vercel / Railway / Render)
The app is designed to stay operational without a database.
- **Railway/Render**: Connect your GitHub repo and use the `Dockerfile`.
- **Environment Variables**:
    - `ADMIN_USERNAME`: Username for the admin login
    - `ADMIN_PASSWORD`: The password users must enter to access the tool.
    - `ALLOWED_ORIGINS`: Frontend origins allowed to call the API
    - `SESSION_TTL_SECONDS`: Session lifetime in seconds
    - `UPLOAD_TTL_SECONDS`: Temporary upload retention window in seconds

---

## Option B — Internal Deploy (If the firm has IT infrastructure)

Run entirely inside the firm's environment. Nothing goes to an external server.

### Option B1 — Local Python script
Simplest possible. User installs Python, runs the script from command line.
- Zero hosting cost
- Zero security risk (never leaves the machine)
- Friction: requires Python knowledge, not user-friendly

### Option B2 — Internal web app
Same as Option A but hosted on the firm's internal servers or SharePoint/Azure.
- Ideal if the firm already has Azure/Microsoft 365 infrastructure
- IT department runs it, not you
- Harder to sell as a product — firm owns it once deployed

### Option B3 — Excel macro / Office add-in
Run the generation directly from Excel via a button.
- Feels native to the workflow
- Complex to build and maintain
- Requires Microsoft Office add-in distribution

---

## Recommended Path

```
Now:     Validate the existing spreadsheets and confirm the generated PPTX format
Week 1:  Run internal testing against sample files and edge cases
Week 2:  Deploy a password-protected preview for stakeholder review
Week 3:  Decide whether to keep hosted externally or move to firm-managed infrastructure
```

---

## Data Privacy Considerations

This section describes what `backend/main.py` does with uploaded files. It is not a
claim that files are never written to disk.

### When files are written

1. **Validation copy.** `POST /api/validate` writes the upload to
   `UPLOAD_DIR/validate-<uuid>.xlsx`, where `UPLOAD_DIR` is
   `tempfile.gettempdir()/schematic_uploads` (`backend/main.py:52`). The copy is
   needed because `run_pipeline` takes a file path (`backend/main.py:167-170`).
2. **Session copy.** If validation is not blocked, the same bytes are written again
   to `UPLOAD_DIR/<uuid>.xlsx` and tracked in the in-memory `upload_sessions` map
   (`backend/main.py:85-97, 185-186`). Blocked uploads do not get a session copy.

### When files are deleted

1. **Validation copy** is removed in a `finally` block immediately after validation,
   including when validation raises (`backend/main.py:172-176`).
2. **Session copy** is removed in a `finally` block at the end of `POST /api/generate`,
   including when generation returns an error such as a missing title or an
   unanswered carrier merge (`backend/main.py:219-221`).
3. **Expired session copies** are removed by `_cleanup_expired_state`, which runs on
   login, validate, generate and authenticated requests (`backend/main.py:67-82`).
   Expiry uses `UPLOAD_TTL_SECONDS`, default 1800 seconds (`backend/main.py:27`).
   Cleanup is lazy: it runs on the next request, not on a timer.

### Paths that can leave files behind

1. **Restart or process kill.** `upload_sessions` is in memory only. After a restart
   the map is empty, so files written before the restart are no longer tracked and are
   never deleted by the application. There is no startup sweep of `UPLOAD_DIR`.
2. **Kill before a `finally` block runs.** If the process is killed during validation
   or generation, the cleanup block does not run, so the validation copy or the
   session copy remains.
3. **Write failure in `_create_upload_session`.** The write at
   `backend/main.py:88-89` has no cleanup around it, so a failed write can leave a
   partial file.

Files left by the first two paths stay in the system temp directory until the
operating system or an operator removes them.

### What is not written

- **Output deck.** `POST /api/generate` renders to an in-memory `BytesIO` and streams
  it back (`backend/main.py:212-218`; `scripts/run_pipeline.py:145-156`). The API
  never writes a `.pptx` to disk.
- **Auth state.** Bearer tokens and expiry times are held in the `auth_sessions`
  dictionary only (`backend/main.py:50, 144-146`).
- **File contents in logs.** The application does not log file contents. Uvicorn
  access logs record request lines such as method, path and status, not request bodies.

This means the tool can be described as:
> "Your spreadsheet is written to the server's temporary directory for validation and generation.
> It is deleted after generation or after the upload window expires.
> If the server restarts before that cleanup, the temporary copy can remain in the system temp directory.
> The generated PowerPoint is streamed back to you and is not written to disk."

Confirm this description with the firm's compliance team before going live.

---

## Pricing Model Ideas (When Selling to the Team)

- **Per seat:** $X/user/month — simple, scales with team size
- **Per firm:** $X/month flat — easy to pitch, easy to invoice
- **One-time license:** $X — firm hosts it themselves (Option B2)
- **Usage-based:** $X per schematic generated — aligns cost to value

Recommended starting point: flat monthly per firm, priced below what one hour
of manual schematic work costs. If a schematic takes 1–2 hours at their billing
rate, the tool pays for itself on the first use.
