# Does spoken speech teach imagined speech? Leakage-controlled linear baselines on three public datasets

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22441724.svg)](https://doi.org/10.5281/zenodo.22441724)

Small, reproducible baselines run before building a 16-channel EEG rig for imagined-speech repeatability.
The question: **can a decoder trained on spoken (or silently articulated) speech read imagined speech from the same person?**
And the prerequisite question: **does imagined speech even survive a change of session?**

Everything here is linear, CPU-only, and runs in minutes. This is a *transfer* test, not a state-of-the-art attempt.

## TL;DR

| dataset | modality | spoken → imagined/silent transfer | imagined/silent across sessions | imagined within session |
|---|---|---|---|---|
| Gaddy 2020 (sEMG, 8 ch, 1 subject, 1588 sentence pairs) | muscle | **yes, small**: top-10 retrieval on unseen sentences 6.0 % (all 81 features) / 7.1 % (duration feature removed) vs 3.2 % chance, permutation p < 0.01 in both. Spoken-teacher vs silent-teacher, paired on the same test items: +1.6 pp, 95 % CI [+0.6, +2.7] **without** the duration feature; +0.6 pp, CI [−0.4, +1.4], n.s. **with** it | silent speech (not imagined): 5.7 % top-10 vs 4.4 % chance, new session with electrodes reattached | — |
| Nieto 2022 (EEG, 128 wet ch, 4 Spanish words, 2 subjects × 3 same-day sessions) | brain | **null**: 29.2 % (p = 0.04) and 25.4 % (p = 0.50) vs 25 % chance | **collapses across same-day sessions**: 27.5 % / 26.7 % ≈ chance | present in 1 of 2 subjects: **32.4 ± 2.2 %** over 20 fold seeds with the 14-channel subset (the originally posted 34 % was a single seed), p = 0.001 with 1000 permutations; 31.2 % with 5 contiguous blocks (p = 0.006); 32.3 % with all 128 channels. Subject 1 at chance (≈ 22 %). |
| FEIS 2019 (EEG, 14 saline-felt ch Emotiv EPOC+, 16 English phonemes, 21 subjects) | brain | **null**: 6.7 % vs 6.25 % chance (group Wilcoxon p = 0.10); 1/21 subjects significant, as expected under the null | **at chance across the 3 same-visit sessions**: imagined → imagined 7.0 % (p = 0.09), leave-one-session-out on the protocol sessions recovered from the epoch index (see corrections); 4/21 subjects p < 0.05 | not computed separately (the three sessions are consecutive within one ~1 h visit) |

One methodological observation fell out of FEIS: with the *same* classifier and the *same* training-set size, spoken → imagined transfer is significant when the test trials are the **same trials** the spoken model was trained on (9.0 %, Wilcoxon p = 3e-5) and at chance when they come from a **held-out session** (6.7 %); paired difference +2.2 pp, 95 % CI [+1.4; +3.1], p = 0.0002. Training-set size does not explain it (−0.3 pp, p = 0.39). Nor does temporal proximity: a model trained on the even-numbered spoken trials scores 12.3 % on the *same* even imagined trials and 3.3 % — below chance — on the interleaved odd ones recorded ≤ 22 s away, and its errors on the odd trials land on the neighbouring even trial's label more often than expected (13.1 % vs 8.5 %). The gain comes from trial identity (a slow state memorised trial by trial), not from phonemic content. Any spoken → imagined result that pairs the same trials should be read with this in mind. *(Corrected 2026-09-07: the earlier text said "the only difference is temporal proximity"; there were two differences, and the mechanism is trial identity rather than proximity.)*

## Why these tests

The project hypothesis was "reading aloud can supervise imagined speech" (label imagined trials with a model trained on spoken ones). Before recording anything, I checked whether that holds on public data, and whether imagined speech is stable enough across days for a per-subject model to make sense.

## Method (same pipeline on the two EEG datasets; analysis windows differ)

- Features: log band-power (Welch, 1 s segments) in θ 4–8, α 8–13, β 13–30, γ 30–45 Hz, per channel. Analysis window: Nieto 0.5–3.0 s post-cue (2.5 s, the authors' own PSD window; the code indexes samples 1.0–3.5 s of an epoch that starts at −0.5 s), FEIS 0.25–5.0 s of the 5 s imagined epoch (4.75 s).
- Classifier: standardization + multinomial logistic regression, C = 0.05. No tuning on the test fold.
- Validation: **never** random window-level splits.
  - Nieto: leave-one-session-out (train on 2 sessions, test on the 3rd). **Correction (2026-09-06):** the three sessions of ds003626 were recorded on a *single day*, consecutively, with self-selected breaks ("Each individual participated in one single recording day comprising three consecutive sessions", Nieto et al. 2022, Methods). Earlier wording here said "recording days"; the split is across same-day sessions, not across days. Within-session numbers use 5-fold stratified CV inside each session. The channel subset is **14 channels** (one Biosemi-128 electrode nearest to each of the 14 sites listed below), not 16 as previously labelled.
  - FEIS: leave-one-session-out on the 3 protocol sessions. **Correction (2026-09-07):** the 2026-09-05 text said the sessions "cannot be recovered" from the timestamps and used contiguous thirds. That was wrong, and the answer was in the authors' own code: `merge_trial_csvs.py` concatenates the three recordings by adding +64/+112 to the epoch index and +1408/+2464 s to the time column, so session 1 = epochs 0–63 (64 trials), session 2 = 64–111 (48), session 3 = 112–159 (48); subject 12 has two sessions (112 trials). The three sessions are consecutive within one ~1 h visit. All FEIS numbers were recomputed with the real sessions.
- Null: label permutation of the training set — 100 permutations for Nieto leave-one-session-out, 200 for FEIS, 1000 for Nieto within-session (50 until 2026-09-07); p = (r + 1)/(N + 1) (Phipson & Smyth 2010), so p is never reported as 0.
- Channel subsets: a 14-channel subset of Nieto's Biosemi-128 (the electrode nearest to each of F7 FT7 T7 FC5 C5 C3 CP5 P7 F8 T8 C4 P8 Cz Pz; positions from MNE standard montages; the code label said "16ch" until 2026-09-06, the count was always 14); a 7-channel subset of FEIS at F7 FC5 T7 P7 F8 T8 P8. Reducing channels changed nothing in FEIS (SNR, not channel count, is the bottleneck there).

Gaddy (sEMG) uses a different design because the targets are sentences, not classes: Gaddy-style frame features pooled per utterance (81-d) → ridge regression into a TF-IDF character n-gram / SVD-128 text space → retrieval of the correct sentence among the test sentences (top-1, top-10, MRR). Conditions: voiced → silent on **unseen sentences** (5-fold), silent → silent, voiced → voiced, mixed teacher, plus a duration-only control (at chance: sentence length explains nothing) and a paired bootstrap between spoken-teacher and silent-teacher on the same test sentences.

Two feature sets are reported because they disagree on one point. The transfer itself (voiced → silent above the permutation null) holds with or without the utterance-duration feature. The *teacher duel* (is the spoken teacher better than a silent teacher for a silent target?) is significant only when duration is removed; with it, the difference shrinks to +0.6 pp and is not significant. A plausible reading is that duration shifts between voiced and silent utterances and acts as a domain-shift feature, but this is one subject and one linear model, so treat the duel as suggestive, not established.

## Results in detail

Full tables (in Portuguese, but self-explanatory) are in `results/`:

- `RESULTADO_GADDY_TRANSFER_SEM_DURACAO.md` — main sEMG table (duration feature removed) + paired teacher duel.
- `RESULTADO_GADDY_TRANSFER_SO_DURACAO.md` — duration-only control (chance).
- `RESULTADO_NIETO_TRANSFER_sub01.md`, `_sub02.md` — LOSO and within-session, 128 ch and 14 ch subset.
- `RESULTADO_FEIS_TRANSFER.md` — per-subject and group tables, 14 ch and 7 ch, with the same-trials vs held-out-session comparison (equalised training size) and the interleaved-trials control.

## What this does and does not show

- It shows that, with linear band-power decoders, spoken → imagined transfer in EEG is **not detectable** in these tests. For FEIS the group mean is 6.7 % with 95 % CI [6.1; 7.4] % against 6.25 % chance, so a *homogeneous* group effect larger than ≈ 1.2 pp is excluded; an effect concentrated in a few subjects is not (the per-subject detection floor with 160 trials is ≈ +2.7 pp at α = 0.05). *(Corrected 2026-09-07: the earlier text claimed "an effect ≥ 1.5 pp would have appeared", which only holds for a homogeneous effect.)*
- It shows that imagined-speech decodability in EEG is **session-bound** in Nieto: present within a session for one subject with good wet electrodes (80 imagined trials per session, 20 per class; ≈ 32 % vs 25 % chance, p = 0.001), gone across sessions recorded ~30 min apart on the same day. *(Corrected 2026-09-07: the earlier text said "~200 trials per condition" — 200/240 is the total imagined-trial count per subject across the three sessions, not the within-session volume — and quoted 34 %, which was one fold seed.)* Since the three sessions were consecutive, this says nothing yet about drift across days; that test has not been run on any dataset here.
- It does **not** test deep models, Riemannian/covariance features, or subject-pooled foundation models. Those are the obvious next steps and the conclusion may change.
- It does **not** replicate the FEIS authors' 69 % binary consonant/vowel result: with this pipeline the binary sits at chance both under leave-one-session-out (50.4 %) and under a random stratified 5-fold split like theirs (49.7 %), so the validation scheme does *not* explain the gap. *(Corrected 2026-09-07: the earlier text attributed it to the random split.)* What differs is the feature set (22,344-d windowed statistics vs 56-d band power), the classifier (SVM-RBF with grid search vs fixed-C logistic regression) and the sample (5 randomly drawn subjects vs 21); the authors' own 95 % CI is [52.6; 85.4] %.

Practical consequence for the hardware project: (1) physical repeatability across sessions (electrode position, impedance) comes first; (2) many repetitions per class within a session; (3) per-session calibration is a requirement, not a nicety; (4) "reading as supervision" stays a hypothesis without support in EEG so far. Muscle (sEMG) does transfer, and is the near-term route for silent speech.

## Corrections log

- **2026-09-06** — Nieto sessions are same-day, not different days; the channel subset is 14, not 16.
- **2026-09-07** — (1) FEIS sessions *are* recoverable from the epoch index; all FEIS numbers recomputed with leave-one-session-out on the real sessions instead of contiguous thirds. (2) "The only difference is temporal proximity" replaced by the equalised-training-size and interleaved-trials controls. (3) FEIS electrodes are saline-felt, not dry. (4) Nieto within-session: null raised from 50 to 1000 permutations and the point estimate averaged over 20 fold seeds (see `results/`). (5) All p-values use (r + 1)/(N + 1). (6) Power statement corrected. (7) The 69 % non-replication is no longer attributed to the validation split. (8) Gaddy cross-session cell relabelled *silent speech*. (9) FEIS subject 12 has 7 repetitions per class (two sessions). This log is the canonical list; each corrected sentence is also marked in place.

## Reproduce

```bash
pip install -r requirements.txt

# sEMG (Gaddy): runs from the pooled-feature cache, no raw download needed (seconds)
python3 scripts/gaddy_transfer.py --sem-duracao      # main table
python3 scripts/gaddy_transfer.py --so-duracao       # duration-only control
# to recompute features from raw: download emg_data.tar.gz from Zenodo 4064409 and set GADDY_RAW=/path/to/emg_data

# EEG (FEIS): runs from the feature cache (minutes); to recompute from raw, download FEIS-v1.1.zip
# from Zenodo 3554128 and set FEIS_ROOT=/path/to/scottwellington-FEIS-*/experiments
python3 scripts/feis_transfer.py                     # all 21 subjects
python3 scripts/feis_transfer.py 01 06               # a subset

# EEG (Nieto): needs the OpenNeuro ds003626 derivatives (sub-XX_ses-YY_eeg-epo.fif + _events.dat)
NIETO_RAW=/path/to/derivatives python3 scripts/nieto_transfer.py 01
NIETO_RAW=/path/to/derivatives python3 scripts/nieto_transfer.py 02
```

Caches under `cache/` contain pooled features only (per-utterance or per-epoch summaries), no raw signal.

## Data and licenses

- D. Gaddy & D. Klein, *Digital Voicing of Silent Speech* (EMNLP 2020). Data: Zenodo record 4064409 (see the record for license terms).
- N. Nieto et al., *Thinking out loud, an open-access EEG-based BCI dataset for inner speech recognition* (Scientific Data 2022). Data: OpenNeuro ds003626.
- S. Wellington & J. Clayton, *Fourteen-channel EEG with Imagined Speech (FEIS) dataset* (2019). Data: Zenodo record 3554128, ODC-BY 1.0.

Code: MIT. Derived caches: redistributed with attribution under the original data licenses.

## Cite

If you use this, cite the concept DOI (resolves to the latest version): Luporini, G. (2026). *Does spoken speech teach imagined speech? Leakage-controlled linear baselines on three public datasets (sEMG + EEG)*. Zenodo. https://doi.org/10.5281/zenodo.22441724

## Author

Gilberto Luporini, medical student, Faculdade São Leopoldo Mandic (Araras, Brazil). Independent project on non-invasive imagined-speech BCI. Questions and corrections: open an issue.
