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
- **Data Policy**: Temporary upload storage only for the active session, then cleanup.

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

The core privacy guarantee of this tool:

1. **Files are never stored.** The Excel is read into memory, processed, and discarded.
2. **Uploaded files are temporary.** They are held only long enough to validate and generate the download, then removed.
3. **Output is never persisted.** The PPTX is generated in memory and streamed back to the user.
4. **No logging of file contents.** Only operational metadata should be logged if needed.
5. **User auth doesn't touch file contents.** Auth and processing stay separate.

This means the tool can honestly be described as:
> "Your spreadsheet is only kept temporarily for validation and generation, then removed.
> The generated PowerPoint is returned directly to you and is not stored permanently."

That should be sufficient for most brokerage compliance requirements — but confirm
with the firm's compliance team before going live.

---

## Pricing Model Ideas (When Selling to the Team)

- **Per seat:** $X/user/month — simple, scales with team size
- **Per firm:** $X/month flat — easy to pitch, easy to invoice
- **One-time license:** $X — firm hosts it themselves (Option B2)
- **Usage-based:** $X per schematic generated — aligns cost to value

Recommended starting point: flat monthly per firm, priced below what one hour
of manual schematic work costs. If a schematic takes 1–2 hours at their billing
rate, the tool pays for itself on the first use.
