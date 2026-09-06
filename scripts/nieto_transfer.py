#!/usr/bin/env python3
"""PROFESSOR-GABARITO em EEG (Nieto/Thinking Out Loud, espanhol, 4 palavras, 128ch @256 Hz).
Pergunta central do projeto: treinar em fala PRONUNCIADA lê fala IMAGINADA (inner) em EEG?
Leave-one-session-out (3 sessões): (I) inner→inner · (P) pron→pron · (T) PRON→INNER (transfer) ·
(M) pron+inner→inner. Features: log-bandpower Welch (θ α β γ) por canal, janela 1,0–3,5 s.
Montagens: 128ch e subconjunto 16ch ≈ nossa coroa (mais próximo por posição 3D). Nulo: permutação.
Uso: python3 nieto_transfer.py [01|02]"""
import sys, os, numpy as np, pandas as pd, mne, warnings; warnings.filterwarnings('ignore')
from scipy.signal import welch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
mne.set_log_level('ERROR'); rng = np.random.default_rng(0)
SUB = sys.argv[1] if len(sys.argv) > 1 else '01'; RAW = os.environ.get('NIETO_RAW', 'data/nieto')   # OpenNeuro ds003626 derivatives: sub-XX_ses-YY_eeg-epo.fif + _events.dat
OUT = f'results/RESULTADO_NIETO_TRANSFER_sub{SUB}.md'; os.makedirs('results', exist_ok=True)
FS, T0, T1 = 256, 1.0, 3.5; BANDS = [(4,8),(8,13),(13,30),(30,45)]
NOSSA = ['F7','FT7','T7','FC5','C5','C3','CP5','P7','F8','T8','C4','P8','Cz','Pz']
X_all, Y_all, S_all, info = [], [], [], None
for ses in ('01','02','03'):
    f = f'{RAW}/sub-{SUB}_ses-{ses}_eeg-epo.fif'
    if not os.path.exists(f): continue
    ep = mne.read_epochs(f, preload=True); info = info or ep.info
    ev = np.asarray(pd.read_pickle(f'{RAW}/sub-{SUB}_ses-{ses}_events.dat'))
    x = ep.get_data()[:, :, int(T0*ep.info['sfreq']):int(T1*ep.info['sfreq'])]
    n = min(len(x), len(ev)); X_all.append(x[:n]); Y_all.append(ev[:n]); S_all.append(np.full(n, int(ses)))
X = np.concatenate(X_all); Y = np.concatenate(Y_all); S = np.concatenate(S_all)
cls, cond = Y[:,1].astype(int), Y[:,2].astype(int)
print(f'sub-{SUB}: {X.shape[0]} trials, {X.shape[1]} canais, {X.shape[2]} amostras @{info["sfreq"]:.0f} Hz | pron {np.sum(cond==0)} inner {np.sum(cond==1)} vis {np.sum(cond==2)} | sessões {np.unique(S)}')
# subconjunto 16ch ≈ nossa coroa: eletrodo Biosemi mais próximo (3D) de cada alvo 10-20
sub_idx = None
try:
    mpos = mne.channels.make_standard_montage('biosemi128').get_positions()['ch_pos']
    std = mne.channels.make_standard_montage('standard_1005').get_positions()['ch_pos']
    names = info['ch_names']; cand = [n for n in names if n in mpos]
    picks = []
    for t in NOSSA:
        best = min(cand, key=lambda n: np.linalg.norm(mpos[n] - std[t]))
        d = np.linalg.norm(mpos[best] - std[t])*1000
        if names.index(best) not in picks: picks.append(names.index(best))
    sub_idx = picks; print('16ch ≈ nossa (biosemi128 mais próximo):', [names[i] for i in sub_idx])
except Exception as e: print('sem subconjunto:', str(e)[:80])
def feats(x):
    f, P = welch(x, fs=FS, nperseg=256, axis=-1)
    bp = np.stack([np.log(P[:, :, (f>=a)&(f<b)].mean(-1) + 1e-20) for a,b in BANDS], -1)   # (n, ch, 4)
    return bp.reshape(len(x), -1)
def acc(Xtr, ytr, Xte, yte, perm=False):
    sc = StandardScaler().fit(Xtr); y = rng.permutation(ytr) if perm else ytr
    m = LogisticRegression(C=0.05, max_iter=3000).fit(sc.transform(Xtr), y)
    return (m.predict(sc.transform(Xte)) == yte).mean()
def run(F, tag, nperm=100):
    res = {}
    def loso(tr_mask_fn, te_cond, perm=False):
        a = []
        for k in np.unique(S):
            tr = tr_mask_fn(k); te = (S==k) & (cond==te_cond)
            if tr.sum() < 8 or te.sum() < 4: continue
            a.append(acc(F[tr], cls[tr], F[te], cls[te], perm))
        return float(np.mean(a)) if a else np.nan
    res['I inner→inner (LOSO)'] = loso(lambda k: (S!=k)&(cond==1), 1)
    res['P pron→pron (LOSO)']  = loso(lambda k: (S!=k)&(cond==0), 0)
    res['T PRON→INNER (transfer, LOSO)'] = loso(lambda k: (S!=k)&(cond==0), 1)
    res['M pron+inner→inner (LOSO)'] = loso(lambda k: (S!=k)&((cond==0)|(cond==1)), 1)
    nullT = [loso(lambda k: (S!=k)&(cond==0), 1, perm=True) for _ in range(nperm)]
    nullI = [loso(lambda k: (S!=k)&(cond==1), 1, perm=True) for _ in range(nperm)]
    res['nulo T (perm)'] = (float(np.mean(nullT)), float(np.percentile(nullT,95)), float((np.array(nullT) >= res['T PRON→INNER (transfer, LOSO)']).mean()))
    res['nulo I (perm)'] = (float(np.mean(nullI)), float(np.percentile(nullI,95)), float((np.array(nullI) >= res['I inner→inner (LOSO)']).mean()))
    return res
lines = [f'# RESULTADO — professor-gabarito em EEG (Nieto sub-{SUB}, 4 palavras, acaso 25%)', f'*05/09/2026 · {X.shape[0]} trials · janela {T0}-{T1} s · log-bandpower θαβγ · logreg · leave-one-session-out*', '']
for F, tag in [(feats(X), '128 canais')] + ([(feats(X[:, sub_idx]), f'16 canais ≈ nossa coroa')] if sub_idx else []):
    r = run(F, tag); lines += [f'## {tag}', '| condição | acurácia | acaso |', '|---|---|---|']
    for k,v in r.items():
        if isinstance(v, tuple): lines.append(f'| {k} | média {v[0]*100:.1f}% · p95 {v[1]*100:.1f}% | **p = {v[2]:.3f}** |')
        else: lines.append(f'| {k} | **{v*100:.1f}%** | 25% |')
    lines.append('')
lines += ['## Leitura', '- **T** é a pergunta do projeto: pronunciado ensina o imaginado em EEG? Compare com o nulo T.', '- **I** = teto do imaginado dentro do modo (sessão nova). **M** = professor misto. **P** = sanidade.', '- Limite: 4 classes, 1 sujeito por rodada, features de banda (sem dinâmica temporal); LOSO exige generalizar entre DIAS.']
# --- within-session (same day): inner→inner 5-fold stratified; pron→inner = train ALL pron of day k, test ALL inner of day k ---
from sklearn.model_selection import StratifiedKFold
NPW = 50
lines += ['## Dentro da sessão (mesmo dia)', '| montagem | inner→inner 5-fold | nulo p95 · p | pron→inner (mesmo dia) |', '|---|---|---|---|']
for F, tag in [(feats(X), '128 canais')] + ([(feats(X[:, sub_idx]), '16 canais ≈ nossa coroa')] if sub_idx else []):
    def within(perm=False):
        a = []
        for k in np.unique(S):
            mi = (S==k)&(cond==1); skf = StratifiedKFold(5, shuffle=True, random_state=0)
            a += [acc(F[mi][tr], cls[mi][tr], F[mi][te], cls[mi][te], perm) for tr,te in skf.split(F[mi], cls[mi])]
        return float(np.mean(a))
    aI = within(); null = np.array([within(perm=True) for _ in range(NPW)])
    aT = float(np.mean([acc(F[(S==k)&(cond==0)], cls[(S==k)&(cond==0)], F[(S==k)&(cond==1)], cls[(S==k)&(cond==1)]) for k in np.unique(S)]))
    lines.append(f'| {tag} | **{aI*100:.1f}%** | p95 {np.percentile(null,95)*100:.1f}% · p = {(null>=aI).mean():.3f} | {aT*100:.1f}% |')
open(OUT,'w').write('\n'.join(lines)); print('\n'.join(lines))
