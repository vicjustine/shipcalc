# Workada Calibration Runbook — VS Code

**Assigned app:** VS Code · **Tier:** Advanced · **Workflow category:** Refactor and add tests
**Target length:** 30 minutes · **Repo:** `~/dev/workada-calibration`

Direction from the manual, verbatim:

> Refactor a multi-module codebase and add unit tests for what you changed.
> Running the test suite at the end is a good final check.

---

## What you refactor and why

`src/shipcalc/batch.py` prices the 120-row shipment ledger. It works, but it has three
real design problems — all defensible to a reviewer, none of them lint errors:

| Problem | Why it matters | How you prove it |
| --- | --- | --- |
| One function does parsing, coercion, pricing and reporting | Untestable; you cannot price without printing | After the split, you unit-test pricing with no I/O |
| `except Exception` swallows the reason | Bad weight, bad postal code and bad period all become `skipped=3` | Show three distinct causes collapsing into one number |
| Totals accumulate as `float` | Money must not round-trip through binary float; the running sum carries error | `0.10+0.20+0.30` ×1000 → `600.0000000000113` |

> **Be accurate on camera.** At this dataset's size the float total still *rounds* to the
> correct cents — it is wrong in principle, not visibly corrupting today's output. Say it
> that way; do not claim a drift the numbers don't show.

**Target shape:** a `Shipment` value object, a pure `price_shipments()` returning results and
structured errors, and a thin `price_file()` that only does I/O.

---

## Hard rules

- **Never type a password on camera.** Bloom logs every keystroke.
- **No AI assistants.** **Disable Copilot before you start** — an inline suggestion appearing
  on camera is an instant reject. `Cmd+Shift+P` → "GitHub Copilot: Disable Completions".
- **Record `Entire screen`**, never a single window.
- **Stay in VS Code.** It is the assigned app; its integrated terminal counts as VS Code.
  Do *not* drift into the browser.
- **Idle under 15%** — 4.5 min of 30. No gap over 60s.
- Standard shortcuts only; no macros or custom keybindings.

---

## Pre-flight

```bash
cd ~/dev/workada-calibration && ./.venv/bin/python -m pytest && ./.venv/bin/python -m ruff check .
```

Expect `22 passed` and `All checks passed!`

Then, before recording:

- Open the folder in VS Code: `code ~/dev/workada-calibration`
- Bottom-right interpreter must read **`.venv`**. If not: `Cmd+Shift+P` →
  "Python: Select Interpreter" → `./.venv/bin/python`
- **Disable Copilot** and any other AI extension
- Close every unrelated editor tab and window
- Do Not Disturb on; quit Mail, Messages, Slack
- Zoom so code is readable in video: `Cmd+=` two or three times
- **Start the Workada timer**, then Bloom → New Recording → **Entire screen**

---

## Minutes 0–4 · Show the problem

1. Open `src/shipcalc/batch.py`. Scroll through it; let the docstring's three bullets sit on screen.
2. Open the integrated terminal (`` Ctrl+` ``) and run the module:
   ```
   ./.venv/bin/python -m shipcalc.batch
   ```
   It prints `priced=120 skipped=0 total=16889.00` and a zone breakdown.
3. Show the float problem concretely in the terminal:
   ```
   ./.venv/bin/python -c "t=0.0
   for _ in range(1000):
       t += 0.10; t += 0.20; t += 0.30
   print(repr(t))"
   ```
   Prints `600.0000000000113`.
4. Run the test suite (`Cmd+Shift+P` → "Tasks: Run Task" → **test**). 22 pass — your baseline.

## Minutes 4–9 · Prove errors are being swallowed

1. In the terminal, make a small broken ledger:
   ```
   head -1 data/shipments_fy2026.csv > /tmp/bad.csv && sed -n '2,6p' data/shipments_fy2026.csv >> /tmp/bad.csv
   ```
   ```
   printf 'SHP-9001,M5V 2T6,T,V6B 1A1,V,notanumber,30,60,true,2026-11\nSHP-9002,M5,T,V6B 1A1,V,2.0,30,60,true,2026-11\nSHP-9003,M5V 2T6,T,V6B 1A1,V,2.0,30,60,true,2099-01\n' >> /tmp/bad.csv
   ```
2. Run it:
   ```
   ./.venv/bin/python -c "from shipcalc.batch import price_file; price_file('data/rate_card_2026Q4.csv','/tmp/bad.csv')"
   ```
   Output: `priced=5 skipped=3`. **Three unrelated causes, one number, no reasons.**
3. Set a breakpoint on the `except Exception:` line and run **Debug: price the ledger** (`F5`)
   against the bad file to show the exception being discarded. Step once (`F10`), then stop.

## Minutes 9–22 · The refactor

Work in `batch.py`. Use real editor tooling — that is what is being recorded.

1. **Extract a `Shipment` dataclass** with a `from_row` classmethod doing the coercion.
   Use `F2` (Rename Symbol) rather than find-and-replace where you rename things.
2. **Add a `PricingError` dataclass** holding `shipment_id` and `reason`.
3. **Split the function in three:**
   - `load_shipments(path) -> list[Shipment]` — I/O only
   - `price_shipments(card, shipments) -> tuple[list[Quote], list[PricingError]]` — pure, no printing
   - `price_file(...)` — thin wrapper that loads, prices, prints
4. **Catch narrowly.** Replace `except Exception` with `except (ValueError, KeyError, InvalidOperation) as exc`
   and record `PricingError(row["shipment_id"], str(exc))`.
5. **Switch the total to `Decimal`**, seeded `sum(..., Decimal("0"))`.
6. Add type hints throughout.

Use `Cmd+Shift+O` to jump between symbols and the Problems panel (`Cmd+Shift+M`) to clear
anything Pylance flags. Save often — `formatOnSave` and import organizing are already on.

## Minutes 22–27 · Tests for what you changed

Create `tests/test_batch.py` and write tests covering the new seams:

- `Shipment.from_row` coerces a good row correctly
- A bad weight produces a `PricingError` naming that shipment, not a silent skip
- An unknown billing period produces a `PricingError`
- A short postal code produces a `PricingError`
- `price_shipments` on the real ledger returns 120 quotes and zero errors
- The total is a `Decimal` and equals the sum of the per-row totals

Run them as you go: `Cmd+Shift+P` → "Test: Run All Tests", or use the Testing sidebar so
the green ticks are visible on camera.

## Minutes 27–30 · Final check

1. **Tasks: Run Task → test.** Everything green, now more than 22.
2. **Tasks: Run Task → lint.** `All checks passed!`
3. **Tasks: Run Task → price ledger.** Confirm the total still reads **16889.00** — the
   refactor changed the structure, not the arithmetic. *That is your verification step.*
4. Re-run the bad-ledger command from minute 5. It now names each failure instead of
   printing `skipped=3`. **Before and after, same input — this is the deliverable.**

**Stop the Bloom recording.**

---

## Submit

```bash
cd ~/dev/workada-calibration && zip -r shipcalc-refactor-deliverable.zip src/shipcalc/batch.py tests/test_batch.py
```

- **Application:** `VS Code`
- **Description:**

> Refactored a monolithic batch-pricing function in a Python freight-rating codebase into a
> Shipment value object, a pure pricing function returning structured errors, and a thin I/O
> wrapper; replaced a blanket exception handler that hid failure reasons and switched money
> totals from float to Decimal, then added unit tests and confirmed the ledger total was
> unchanged. Workflow category: refactor and add tests. Tier: Advanced.

- Paste the Bloom session ID, **Attach recording**, attach the zip, submit, stop the timer.

---

## QC pass

- [ ] Real refactor with judgment, not formatting
- [ ] Ends in a check: same total before and after, plus new tests green
- [ ] Seeded data only; no credentials on screen
- [ ] No padded time; no gap over 60s
- [ ] **VS Code in the foreground the whole session** (its terminal counts)
- [ ] Copilot and all AI assistants disabled
- [ ] One continuous recording, Entire screen
- [ ] All three Bloom files attached
