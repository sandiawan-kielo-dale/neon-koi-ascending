# Neon Koi Ascending

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/sandiawan-kielo-dale/neon-koi-ascending/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/sandiawan-kielo-dale/neon-koi-ascending/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

Bounty: https://make.fun/bounty/ai-excited-01 — referral: https://make.fun/r/y5hkb35z

Entry for make.fun **"Make the AI judge excited" (ai-excited-01)** — one image
built to hit the judge with a jolt of energy on first sight.

## The image

A vivid orange-and-white koi leaps through a ring of gold fire over a
moonlit ocean, under aurora ribbons and a full moon, with cherry-blossom
petals drifting through the air. One unmistakable focal subject with a
visible eye, extreme warm-orange against deep-indigo contrast, glow from
the fire ring and the moon, and dense but organised detail: aurora, stars,
ripples, the moon's reflection on the water, and petals. The koi's arc,
the ring and the ripples all drive toward one thrilling moment, and the
big shapes — koi, ring, moon — still read clearly at ~300 pixels across.

## Files

- `main.py` — the generator program (Python 3, Pillow + numpy + stdlib only)
- `output/entry.png` — the generated 1024x1024 image (under 1 MiB)
- `LICENSE` — MIT
- `.makefun/owner.json` — repository ownership claim

## How to run

```sh
python3 main.py
```

That writes `output/entry.png` (or pass a path: `python3 main.py out.png`).
No network, no clock, no input files: a fixed seed makes the program fully
deterministic.

## Verification

Run it twice and compare — the two outputs are byte-identical:

```sh
python3 main.py output/entry.png && sha256sum output/entry.png
python3 main.py output/entry.png && sha256sum output/entry.png
```

The image is 1024x1024 RGB PNG and under the 1 MiB limit.
