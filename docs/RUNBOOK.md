# Workada Computer Use — Calibration Runbook

**Repo:** github.com/vicjustine/shipcalc (private) · **Tier:** Advanced · **Workflow category:** Set up CI/CD from scratch
**Target length:** 30 minutes (calibration sample) · **Repo:** `~/dev/workada-calibration`

> Calibration rule from the manual: pick **one** direction, work it for **about 30 minutes**,
> upload the Bloom recording. (Full production tasks target 1 hour, 30 min min, 2 hr max.)

---

## The direction being followed

From the manual's **Development → GitHub → Advanced** suggestions, verbatim:

> Build a GitHub Actions pipeline with a test matrix, caching and deployment.
> A push and a tagged release are good ways to show it running.

Mapped to this repo:

| Advanced requirement | What you build on camera | How it's proven |
| --- | --- | --- |
| Test matrix | Python 3.10 / 3.11 / 3.12 × ubuntu | 3 green jobs in Actions |
| Caching | `cache: pip` in setup-python | 2nd run logs a cache hit |
| Deployment | Build artifact + release on tag | Release page shows the `.whl` |
| **Test case that passes** | Push a deliberately broken commit → CI red → fix → CI green | Two contrasting runs |

The last row is the **validation step** the QC checklist demands. Do not skip it.

---

## Hard rules (these get tasks rejected)

- **Never type a password while recording.** Bloom logs every keystroke. Log in to GitHub *before* you press record.
- **No AI assistants during the recording.** No Copilot, no Claude, no ChatGPT. Disable Copilot in VS Code before you start.
- **Record `Entire screen`**, never a single window. Single-window recordings can fail to convert to MP4.
- **Never a work account.** Your personal GitHub with a private throwaway repo is fine.
- **Idle time under 15%.** For a 30-min recording that's 4.5 minutes total. No gap over 60s counts as active.
- **Stay in the assigned app.** Time is credited to whatever is in the foreground. GitHub in the browser is the assigned app; the terminal and editor are supporting apps. Keep the browser in front as much as the work allows.
- **No macros or custom shortcuts.** Standard app shortcuts only.

---

## Phase 0 — One-time setup (not counted in task time)

### 0.1 Install Bloom

1. Open your **Workada dashboard → Settings**. Download the **Mac** installer.
2. Open the `.dmg` and **drag Bloom into Applications**.
3. Open Bloom → **Sign in with Workada** → in the browser page that opens, click **Connect Bloom**.
4. Confirm Bloom shows your account as **Connected**.
5. Grant all three permissions when Bloom asks:
   - **Screen & System Audio Recording** (called *Screen Recording* on older macOS)
   - **Accessibility**
   - **Input Monitoring**
   In System Settings → **Privacy & Security**, toggle Bloom **on** under each of the three.
6. **Quit Bloom completely with `Cmd+Q`** and reopen it. If you skip this, **New Recording stays grayed out**.
7. Make a **1-minute test recording** on **Entire screen**.
8. Confirm the saved folder holds all three files: `recording.mp4`, `events.jsonl`, `manifest.json`.

**If macOS says "Bloom is damaged and can't be opened":** click **Cancel** (*not* Move to Trash). Then open Terminal (`Cmd+Space`, type `Terminal`, Enter) and run:

```bash
xattr -dr com.apple.quarantine /Applications/Bloom.app
```

No output means it worked. Reopen Bloom.

### 0.2 Install the Workada timer

1. Download from the **Workada timer download page** (no sign-in needed).
2. On Mac, check your chip: ** menu → About This Mac**. Safari and Firefox always suggest the
   Apple-silicon build, so **on an Intel Mac pick the Intel build manually**.
3. Drag the timer into **Applications**, open it, sign in with your Workada account.
4. Confirm the timer shows **Computer Use** as the project.

### 0.3 Sign the consent form

In Workada, **sign the recording consent form**. Required before your first task.

---

## Phase 1 — Pre-flight (do this before pressing record)

Run this check script to confirm the repo baseline is green:

```bash
cd ~/dev/workada-calibration && ./.venv/bin/python -m pytest && ./.venv/bin/python -m ruff check .
```

Expect: `22 passed` and `All checks passed!`

### The repo is already pushed

Live at **github.com/vicjustine/shipcalc** — private, 10 commits, Actions enabled and empty.
Nothing to set up. To remove it after you submit:

```bash
gh repo delete vicjustine/shipcalc --yes
```

### Screen prep

- Browser **full-screen** on the GitHub tab, zoom so text is comfortably readable in video.
- **Do Not Disturb ON** (Control Centre → Focus → Do Not Disturb).
- **Quit** Mail, Messages, Slack, Discord, personal apps.
- **Disable GitHub Copilot** in VS Code if installed.
- Close every tab that isn't this work. **Don't open your profile or repo list on camera.**
- Already signed in to the new GitHub account in the `workada` browser profile.

### Final pre-record checklist

- [ ] Signed in to GitHub already — no password typing on camera
- [ ] `pytest` green, `ruff` clean
- [ ] Repo live at `vicjustine/shipcalc`, Actions tab empty
- [ ] Do Not Disturb on, personal apps quit
- [ ] Copilot / all AI assistants disabled
- [ ] **Workada timer started**
- [ ] Bloom open, ready to record **Entire screen**

---

## Phase 2 — The 30-minute recording

**Start the Workada timer first, then Bloom → New Recording → Entire screen.**

Work at a natural pace. The minute markers are a pacing guide, not a script — reviewers want
real decisions, not a performance. Never pause longer than 60 seconds.

### Minutes 0–3 · Establish the starting state

Show the reviewer where you're beginning, all in the browser:

1. Open the repo on GitHub.
2. Click the **Actions** tab — show it's empty. *This is your "before" state.*
3. Click into `src/shipcalc/rates.py`, scroll briefly to show real code exists.
4. Open `pyproject.toml`, point at the `[project.optional-dependencies] dev` line (pytest, ruff).

### Minutes 3–12 · Build the workflow with a matrix and caching

Create the workflow **in the GitHub web editor** (keeps you in the assigned app):

1. **Actions** tab → **set up a workflow yourself**.
2. Name the file `ci.yml`.
3. Type the workflow out. Don't paste it in one shot — typing shows the work:

```yaml
name: CI

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest -q
```

> 23 lines, tested on real runners. `cache: pip` inside `setup-python@v5` replaces the
> eight-line `actions/cache` block. Keep this open on a second screen and type it across —
> the manual bans AI assistants and macros while recording, not working from your own notes.
> Don't paste all 23 lines in one keystroke.


4. **Commit changes…** → commit message `Add CI workflow with test matrix and pip caching` → **Commit directly to main**.
5. Go to **Actions** and watch the run. Narrate nothing — just let it run.
6. **Open each of the three matrix jobs** (3.10, 3.11, 3.12) and show them green.
7. Expand **Post Run actions/setup-python@v5** — the first run logs *Cache saved with the key*, meaning nothing was there to restore. This matters for step 2 of the proof.

### Minutes 12–19 · Prove the pipeline actually catches failures

This is the **test case** — the single most important part for Advanced tier.

1. In the browser, open `src/shipcalc/surcharges.py` → click the **pencil (Edit)** icon.
2. Break the fuel calculation deliberately. Change:
   ```python
   return (base * FUEL_INDEX[period]).quantize(Decimal("0.01"))
   ```
   to:
   ```python
   return (base + FUEL_INDEX[period]).quantize(Decimal("0.01"))
   ```
   (`*` → `+` — a plausible real bug, not obvious vandalism.)
3. Commit to a **new branch** named `fix/fuel-surcharge-rounding`, and **open a pull request**.
4. On the PR, watch the checks run and **go red**. Open the failing job and show the assertion:
   `AssertionError: assert Decimal('100.16') == Decimal('16.10')` — 2 failed, 20 passed.
5. **Now show the cache working:** expand **Run actions/setup-python@v5** — it logs *Cache restored from key*, restored from the first run. That's your caching evidence.
6. Edit the file again **on the branch**, restore `*`, commit `Restore multiplicative fuel surcharge`.
7. Checks re-run and go **green**. Merge the PR.

> You have now shown a case that **should fail** and one that **should pass** — exactly what the
> manual asks for ("try a case that should work and one that shouldn't").

### Minutes 19–26 · Add branch protection and deployment

1. **Settings → Branches → Add branch ruleset** (or *Add rule* on older UI).
2. Target `main`. Enable **Require status checks to pass** and select the `test` checks.
3. Save. This makes the CI meaningful rather than decorative.
4. Back in **Actions**, edit `ci.yml` and append a release job:

```yaml
  release:
    needs: test
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Build wheel
        run: |
          python -m pip install --upgrade pip build
          python -m build
      - name: Publish release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*
```

5. Commit it to `main` (through a PR if protection now blocks direct pushes — **that itself demonstrates
   the protection working**, which is a bonus proof point).

### Minutes 26–30 · Tag a release and verify the deliverable

1. **Releases → Draft a new release** → tag `v0.3.0` → **Publish release**.
   (Or in terminal: `git tag v0.3.0 && git push origin v0.3.0`.)
2. **Actions** → the `release` job runs. Show it green.
3. Open the **Releases** page → confirm the `.whl` artifact is attached. **This is your deliverable.**
4. Final sweep in the browser: Actions history showing red → green → release, and the ruleset page.

**Stop the Bloom recording.** Keep the folder it saves.

---

## Phase 3 — Submit (about 5 minutes)

### Collect the output file

Download the built wheel from the Releases page, and zip it with the workflow file:

```bash
cd ~/dev/workada-calibration && mkdir -p out && cp .github/workflows/ci.yml out/ 2>/dev/null; cd out && zip -r ../shipcalc-ci-deliverable.zip . && cd ..
```

> The manual says: **if your output is multiple files, zip them.** Include `ci.yml` and the
> downloaded `.whl`. A link to the repo is not a substitute for the file.

### Fill in the Workada task page

1. Workada → **Computer Use** project → **Tasks**.
2. Open your claimed **Record your work** task, or click **Start** next to *Start a recording task*.
3. **Application:** `GitHub`
4. **Describe your work** — one or two sentences, naming the workflow category and tier:

> Built a GitHub Actions CI pipeline for a Python freight-rating library with a 3-version test
> matrix and pip caching, proved it by pushing a broken fuel-surcharge commit that failed the
> checks and fixing it to green, then added branch protection and a tag-triggered release job that
> publishes a built wheel. Workflow category: set up CI/CD from scratch. Tier: Advanced.

5. **Bloom session ID:** in Bloom, click **Copy session ID** next to your recording, paste it, then
   click **Attach recording**. Workada pulls the three files Bloom uploaded automatically.
6. If an upload failed, upload manually from your Bloom folder (250 MiB per file cap):
   `recording.mp4`, `events.jsonl`, `manifest.json` — **all three are required**.
7. **Work file or export:** attach `shipcalc-ci-deliverable.zip`.
8. **Submit.**
9. **Stop the Workada timer** after submitting.

### Post-submit check

Workada compares the recording against your timer time and shows a **coverage report**. It's
informational only and doesn't change pay.

---

## Final QC pass (from the manual's checklist)

- [ ] **Not a toy exercise** — real CI config, matrix, caching, protection, release
- [ ] **Deliverable + check** — published release with a wheel; red-then-green proves the test case
- [ ] **Seeded data only** — fake carrier rates and shipments; no real client data, no credentials on screen
- [ ] **No padded time** — no waiting on long runs; CI runs are ~1 min each
- [ ] **Assigned app in front** — GitHub in the browser dominates the recording
- [ ] **No AI while recording** — Copilot disabled, no assistants used
- [ ] **Idle under 15%** — no gap over 60s; under 4.5 min total for a 30-min session
- [ ] **Tagged and new** — Advanced tier genuinely matches (build-level features, passing test case)
- [ ] **One continuous recording**, Entire screen
- [ ] **All three Bloom files** attached

---

## If something goes wrong

| Problem | What to do |
| --- | --- |
| Bloom crashes mid-session | Start a **new recording** and **submit all of them** |
| `New Recording` grayed out | Toggle all three privacy permissions on, `Cmd+Q` Bloom, reopen |
| "Bloom is damaged" | Click **Cancel**, run the `xattr -dr` command above, reopen |
| CI run queues forever | Private repos have Actions minutes limits — make the repo public, or note it and continue |
| Captured something sensitive | Email **support@workada.co within 24 hours** |
| Done with the repo | `gh repo delete vicjustine/shipcalc --yes` |
