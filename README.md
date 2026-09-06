# Does spoken speech teach imagined speech? Leakage-controlled linear baselines on three public datasets

Small, reproducible baselines run before building a 16-channel EEG rig for imagined-speech repeatability.
The question: **can a decoder trained on spoken (or silently articulated) speech read imagined speech from the same person?**
And the prerequisite question: **does imagined speech even survive a change of session?**

Everything here is linear, CPU-only, and runs in minutes. This is a *transfer* test, not a state-of-the-art attempt.

## TL;DR

| dataset | modality | spoken → imagined/silent transfer | imagined across sessions | imagined within session |
|---|---|---|---|---|
| Gaddy 2020 (sEMG, 8 ch, 1 subject, 1588 sentence pairs) | muscle | **yes, small**: top-10 retrieval on unseen sentences 6.0 % (all 81 features) / 7.1 % (duration feature removed) vs 3.2 % chance, permutation p < 0.01 in both. Spoken-teacher vs silent-teacher, paired on the same test items: +1.6 pp, 95 % CI [+0.6, +2.7] **without** the duration feature; +0.6 pp, CI [−0.4, +1.4], n.s. **with** it | 5.7 % vs 4.4 % chance (new session) | — |
| Nieto 2022 (EEG, 128 wet ch, 4 Spanish words, 2 subjects × 3 sessions) | brain | **null**: 29.2 % (p = 0.03) and 25.4 % (p = 0.50) vs 25 % chance | **collapses**: 27.5 % / 26.7 % ≈ chance | present in 1 of 2 subjects: 34 % with a 16-channel subset (p < 0.01) |
| FEIS 2019 (EEG, 14 dry ch Emotiv, 16 English phonemes, 21 subjects) | brain | **null**: 6.4 % vs 6.25 % chance (p = 0.38); 1/21 subjects significant, as expected under the null | — (timestamps not recoverable) | **null at group level**: 6.3 %; 4/21 subjects significant |

One methodological observation fell out of FEIS: with the *same* classifier, spoken → imagined transfer is significant when train and test come from the **same trials** (8.7 %, p = 0.0002) and at chance when they come from **different temporal blocks** (6.4 %). The only difference is temporal proximity, so the gain is shared drift/state, not phonemic content. Any spoken → imagined result that pairs the same trials should be read with this in mind.

## Why these tests

The project hypothesis was "reading aloud can supervise imagined speech" (label imagined trials with a model trained on spoken ones). Before recording anything, I checked whether that holds on public data, and whether imagined speech is stable enough across days for a per-subject model to make sense.

## Method (identical across the two EEG datasets)

- Features: log band-power (Welch, 1 s segments) in θ 4–8, α 8–13, β 13–30, γ 30–45 Hz, per channel.
- Classifier: standardization + multinomial logistic regression, C = 0.05. No tuning on the test fold.
- Validation: **never** random window-level splits.
  - Nieto: leave-one-session-out (train on 2 recording days, test on the 3rd). Within-session numbers use 5-fold stratified CV inside each day.
  - FEIS: leave-one-block-out on 3 contiguous temporal blocks of trials (the dataset's timestamps were rewritten by the authors at a fixed 22 s interval, so the original 3 sessions cannot be recovered; contiguous thirds are the honest fallback).
- Null: label permutation of the training set (100–200 permutations), p = fraction of null accuracies ≥ observed.
- Channel subsets: a 16-channel subset of Nieto's Biosemi-128 nearest to F7 FT7 T7 FC5 C5 C3 CP5 P7 F8 T8 C4 P8 Cz Pz (positions from MNE standard montages); a 7-channel subset of FEIS at F7 FC5 T7 P7 F8 T8 P8. Reducing channels changed nothing in FEIS (SNR, not channel count, is the bottleneck there).

Gaddy (sEMG) uses a different design because the targets are sentences, not classes: Gaddy-style frame features pooled per utterance (81-d) → ridge regression into a TF-IDF character n-gram / SVD-128 text space → retrieval of the correct sentence among the test sentences (top-1, top-10, MRR). Conditions: voiced → silent on **unseen sentences** (5-fold), silent → silent, voiced → voiced, mixed teacher, plus a duration-only control (at chance: sentence length explains nothing) and a paired bootstrap between spoken-teacher and silent-teacher on the same test sentences.

Two feature sets are reported because they disagree on one point. The transfer itself (voiced → silent above the permutation null) holds with or without the utterance-duration feature. The *teacher duel* (is the spoken teacher better than a silent teacher for a silent target?) is significant only when duration is removed; with it, the difference shrinks to +0.6 pp and is not significant. A plausible reading is that duration shifts between voiced and silent utterances and acts as a domain-shift feature, but this is one subject and one linear model, so treat the duel as suggestive, not established.

## Results in detail

Full tables (in Portuguese, but self-explanatory) are in `results/`:

- `RESULTADO_GADDY_TRANSFER_SEM_DURACAO.md` — main sEMG table (duration feature removed) + paired teacher duel.
- `RESULTADO_GADDY_TRANSFER_SO_DURACAO.md` — duration-only control (chance).
- `RESULTADO_NIETO_TRANSFER_sub01.md`, `_sub02.md` — LOSO and within-session, 128 ch and 16 ch subset.
- `RESULTADO_FEIS_TRANSFER.md` — per-subject and group tables, 14 ch and 7 ch, with the same-trials vs different-blocks comparison.

## What this does and does not show

- It shows that, with linear band-power decoders, spoken → imagined transfer in EEG is **below the detection floor** of these tests. For FEIS the group 95 % CI half-width is ≈ 0.7 pp, so a true transfer effect larger than ≈ 1.5 pp over chance would have appeared. Absence of evidence at this level, not evidence of absence.
- It shows that imagined-speech decodability in EEG is **session-bound** in Nieto: present within a day for one subject with good wet electrodes and ~200 trials per condition, gone across days.
- It does **not** test deep models, Riemannian/covariance features, or subject-pooled foundation models. Those are the obvious next steps and the conclusion may change.
- It does **not** replicate the FEIS authors' 69 % binary consonant/vowel result (random split) or the 40 % 16-class figure reported elsewhere; under temporal-block validation, both classes of result sit at chance here.

Practical consequence for the hardware project: (1) physical repeatability across sessions (electrode position, impedance) comes first; (2) many repetitions per class within a session; (3) per-session calibration is a requirement, not a nicety; (4) "reading as supervision" stays a hypothesis without support in EEG so far. Muscle (sEMG) does transfer, and is the near-term route for silent speech.

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

## Author

Gilberto Luporini, medical student, Faculdade São Leopoldo Mandic (Araras, Brazil). Independent project on non-invasive imagined-speech BCI. Questions and corrections: open an issue.
