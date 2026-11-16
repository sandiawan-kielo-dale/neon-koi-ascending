# Make the AI judge excited — "Neon Koi Ascending"

Entry for the make.fun bounty [ai-excited-01](https://make.fun/bounty/ai-excited-01)
($250, 20 places, ends Tue 17 Nov 2026 06:00 WIB / Mon 16 Nov 2026 23:00 UTC).
Entrant: Sandiawan (@sandiawan-kielo-dale on make.fun).

## The image

A single programmatically generated 1024×1024 PNG: a vivid orange-and-white
koi leaping through a ring of gold fire over a moonlit ocean, under aurora
ribbons and a full moon, with drifting cherry-blossom petals.

Designed to excite a vision judge in pairwise comparison: one unmistakable
focal subject with a visible eye, extreme warm-orange / deep-indigo colour
contrast, glow, and dense but organised detail (moon, aurora, stars, ripples,
moon reflection, petals).

## Files

- `main.py` — the generator. Pure Python 3 (Pillow + numpy, stdlib only).
  No network, no clock, fixed seed: two runs write byte-identical output.
  Writes to `/output/entry.png` by default, or to `sys.argv[1]` if given.
- `output/entry.png` — the generated image (1024×1024, RGB PNG, ~192 KB).
- `LICENSE` — MIT (required: the repo must carry an OSI-approved license).

## Verification (done 2026-11-16)

- Ran `python3 main.py output/entry.png` twice: identical SHA-256 both runs
  (`d76d2666ebf77b9b9cc88e329504085e145584b2363aceb33c5fb674c343941e`).
- Size 197,149 bytes — under the 1 MiB limit. Dimensions 1024×1024 — at
  the limit. Format PNG. Visually inspected: image opens correctly and the
  koi, ring, moon, aurora and petals all render as intended.

## How to run

```bash
python3 main.py            # writes /output/entry.png
python3 main.py out.png    # writes to out.png instead
```

Requires Python 3.12+ with Pillow and numpy installed
(`pip install pillow numpy`).

## How to submit (NOT done — build only)

> **Important:** this build was made by an agent session that make.fun's kit
> does not record. This bounty takes strict transcripts: an entry needs
> sealed recordings from the kit's `record` command, made while a recorded
> harness (Claude Code, Codex, Muse app, etc.) built it. A handed-over
> session ranks but takes no paid place by default. So before submitting,
> the build must be (re-)done inside a recorded session.

1. Fetch the kit and start recording **before** building:
   ```bash
   curl -sSL "https://make.fun/c/ai-excited-01/kit" | tar xz
   cd ai-excited-01-kit
   node cli/makefun.mjs record --competition ai-excited-01 --source <harness>
   ```
2. In the recorded session, create a **public** GitHub repo owned by
   Sandiawan's GitHub account with `main.py` and `LICENSE` at the root, and
   commit. The make.fun account has no GitHub login, so the commit must also
   carry `.makefun/owner.json` containing `{"wallet": "<account wallet>"}`.
   (Or submit as a source bundle instead of a repo.)
3. Make sure the account has a Solana wallet: add the payout wallet with
   `node cli/makefun.mjs wallet add --keypair <wallet-file>` from inside
   the kit. The entry is signed by an account wallet; that wallet is the
   payout wallet.
4. Submit from inside the kit (entry message is signed, valid 10 minutes):
   ```bash
   node cli/makefun.mjs submit --competition ai-excited-01 \
     --recording <recording-id> \
     --repo-url https://github.com/<owner>/<repo> \
     --commit <40-char-sha> --title "Neon Koi Ascending" \
     --keypair <wallet-file>
   ```
5. Deadline: 2026-11-16T23:00:00Z (Tue 17 Nov 2026 06:00 WIB). Max 10
   submissions per day, 20 total; the last submission before the deadline
   is the final entry.
