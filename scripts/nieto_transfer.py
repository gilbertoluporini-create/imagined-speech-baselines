#!/usr/bin/env python3
"""PROFESSOR-GABARITO em EEG (Nieto/Thinking Out Loud, espanhol, 4 palavras, 128ch @256 Hz) — 05/09/2026, revisado 07/09/2026.
Pergunta central do projeto: treinar em fala PRONUNCIADA lê fala IMAGINADA (inner) em EEG?
Leave-one-session-out (3 sessões, CONSECUTIVAS NO MESMO DIA — Nieto et al. 2022, Methods): (I) inner→inner · (P) pron→pron ·
(T) PRON→INNER (transfer) · (M) pron+inner→inner. Features: log-bandpower Welch (θ α β γ) por canal, janela = amostras 1,0–3,5 s
da época (a época começa em tmin = −0,5 s → 0,5–3,0 s pós-cue, a mesma janela de PSD_representation.py dos autores).
Montagens: 128ch e subconjunto 14ch ≈ nossa coroa (eletrodo Biosemi mais próximo, 3D; o rótulo dizia "16ch" até 06/09/2026).
Nulo: permutação dos rótulos de treino; p = (r+1)/(N+1) (Phipson & Smyth 2010) — NUNCA "p = 0.000".
REVISÃO 07/09/2026 (dentro da sessão): a versão de 05/09 usava 50 permutações (piso 1/51 ≈ 0,02, mas imprimia "p = 0.000") e
uma única semente de dobras (random_state=0), que caiu no percentil ~80 da distribuição de sementes (34,2 % vs média ~32 %).
Agora: NPW permutações (padrão 1000), média ± dp sobre NSEEDS sementes de dobras, e um esquema adicional por 5 BLOCOS
CONTÍGUOS dentro da sessão (KFold sem embaralhar), que não tem semente.
Uso: python3 nieto_transfer.py [01|02]   (env: NIETO_RAW, NPW, NSEEDS)"""
import sys, os, numpy as np, pandas as pd, mne, warnings; warnings.filterwarnings('ignore')
from scipy.signal import welch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, KFold
mne.set_log_level('ERROR'); rng = np.random.default_rng(0)
SUB = sys.argv[1] if len(sys.argv) > 1 else '01'; RAW = os.environ.get('NIETO_RAW', 'data/nieto')   # OpenNeuro ds003626 derivatives: sub-XX_ses-YY_eeg-epo.fif + _events.dat
NPW = int(os.environ.get('NPW', 1000)); NSEEDS = int(os.environ.get('NSEEDS', 20)); NPERM_LOSO = int(os.environ.get('NPERM_LOSO', 100))
OUT = f'results/RESULTADO_NIETO_TRANSFER_sub{SUB}.md'; os.makedirs('results', exist_ok=True)
FS, T0, T1 = 256, 1.0, 3.5; BANDS = [(4,8),(8,13),(13,30),(30,45)]
NOSSA = ['F7','FT7','T7','FC5','C5','C3','CP5','P7','F8','T8','C4','P8','Cz','Pz']
X_all, Y_all, S_all, info, tmin = [], [], [], None, None
for ses in ('01','02','03'):
    f = f'{RAW}/sub-{SUB}_ses-{ses}_eeg-epo.fif'
    if not os.path.exists(f): continue
    ep = mne.read_epochs(f, preload=True); info = info or ep.info; tmin = ep.tmin if tmin is None else tmin
    ev = np.asarray(pd.read_pickle(f'{RAW}/sub-{SUB}_ses-{ses}_events.dat'))
    x = ep.get_data()[:, :, int(T0*ep.info['sfreq']):int(T1*ep.info['sfreq'])]
    n = min(len(x), len(ev)); X_all.append(x[:n]); Y_all.append(ev[:n]); S_all.append(np.full(n, int(ses)))
X = np.concatenate(X_all); Y = np.concatenate(Y_all); S = np.concatenate(S_all)
cls, cond = Y[:,1].astype(int), Y[:,2].astype(int)
JAN = f'{tmin+T0:.1f}–{tmin+T1:.1f} s pós-cue (amostras {T0}–{T1} s da época, tmin = {tmin:.1f} s)'
contagem = ' · '.join(f'ses-{k:02d}: pron {np.sum((S==k)&(cond==0))} inner {np.sum((S==k)&(cond==1))} vis {np.sum((S==k)&(cond==2))}' for k in np.unique(S))
print(f'sub-{SUB}: {X.shape[0]} trials, {X.shape[1]} canais, {X.shape[2]} amostras @{info["sfreq"]:.0f} Hz | pron {np.sum(cond==0)} inner {np.sum(cond==1)} vis {np.sum(cond==2)} | janela {JAN} | {contagem}')
# subconjunto 14ch ≈ nossa coroa: eletrodo Biosemi mais próximo (3D) de cada alvo 10-20
sub_idx = None
try:
    mpos = mne.channels.make_standard_montage('biosemi128').get_positions()['ch_pos']
    std = mne.channels.make_standard_montage('standard_1005').get_positions()['ch_pos']
    names = info['ch_names']; cand = [n for n in names if n in mpos]
    picks = []
    for t in NOSSA:
        best = min(cand, key=lambda n: np.linalg.norm(mpos[n] - std[t]))
        if names.index(best) not in picks: picks.append(names.index(best))
    sub_idx = picks; print(f'{len(sub_idx)}ch ≈ nossa (biosemi128 mais próximo):', [names[i] for i in sub_idx])
except Exception as e: print('sem subconjunto:', str(e)[:80])
def feats(x):
    f, P = welch(x, fs=FS, nperseg=256, axis=-1)
    bp = np.stack([np.log(P[:, :, (f>=a)&(f<b)].mean(-1) + 1e-20) for a,b in BANDS], -1)   # (n, ch, 4)
    return bp.reshape(len(x), -1)
def acc(Xtr, ytr, Xte, yte, perm=False):
    sc = StandardScaler().fit(Xtr); y = rng.permutation(ytr) if perm else ytr
    m = LogisticRegression(C=0.05, max_iter=3000).fit(sc.transform(Xtr), y)
    return (m.predict(sc.transform(Xte)) == yte).mean()
def pval(null, obs): return float((np.sum(np.asarray(null) >= obs) + 1) / (len(null) + 1))
def run(F, tag, nperm=NPERM_LOSO):
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
    res[f'nulo T (perm ×{nperm})'] = (float(np.mean(nullT)), float(np.percentile(nullT,95)), pval(nullT, res['T PRON→INNER (transfer, LOSO)']))
    res[f'nulo I (perm ×{nperm})'] = (float(np.mean(nullI)), float(np.percentile(nullI,95)), pval(nullI, res['I inner→inner (LOSO)']))
    return res
lines = [f'# RESULTADO — professor-gabarito em EEG (Nieto sub-{SUB}, 4 palavras, acaso 25%)', f'*05/09/2026, revisado 07/09/2026 · {X.shape[0]} trials · janela {JAN} · log-bandpower θαβγ · logreg · leave-one-session-out · p = (r+1)/(N+1)*', f'*Trials por sessão: {contagem}*', '']
MONT = [(feats(X), '128 canais')] + ([(feats(X[:, sub_idx]), f'{len(sub_idx)} canais ≈ nossa coroa')] if sub_idx else [])
for F, tag in MONT:
    r = run(F, tag); lines += [f'## {tag}', '| condição | acurácia | acaso |', '|---|---|---|']
    for k,v in r.items():
        if isinstance(v, tuple): lines.append(f'| {k} | média {v[0]*100:.1f}% · p95 {v[1]*100:.1f}% | **p = {v[2]:.3f}** |')
        else: lines.append(f'| {k} | **{v*100:.1f}%** | 25% |')
    lines.append('')
lines += ['## Leitura', '- **T** é a pergunta do projeto: pronunciado ensina o imaginado em EEG? Compare com o nulo T.', '- **I** = teto do imaginado dentro do modo (sessão nova). **M** = professor misto. **P** = sanidade.', '- Limite: 4 classes, 1 sujeito por rodada, features de banda (sem dinâmica temporal); LOSO exige generalizar entre SESSÕES (as 3 sessões do ds003626 foram no MESMO dia, consecutivas; Nieto et al. 2022, Methods).']
# --- dentro da sessão (mesmo dia): inner→inner; pron→inner = treina TODO pron da sessão k, testa TODO inner da sessão k ---
lines += ['', '## Dentro da sessão (mesmo dia)', f'*inner→inner: 5-fold estratificado (média ± dp sobre {NSEEDS} sementes de dobras; a semente 0 é a publicada em 05/09) e 5 blocos CONTÍGUOS por ordem de trial (sem semente). Nulo: {NPW} permutações dos rótulos de treino, p = (r+1)/({NPW}+1). Treino por dobra ≈ 64 trials, teste 16 (20 inner por classe por sessão).*', '',
          '| montagem | inner→inner 5-fold (média ± dp, seeds) | semente 0 | nulo p95 · **p** (semente 0) | inner→inner 5 blocos contíguos | nulo p95 · **p** | pron→inner (mesma sessão) |', '|---|---|---|---|---|---|---|']
for F, tag in MONT:
    def within(seed=0, perm=False, contig=False):
        a = []
        for k in np.unique(S):
            mi = (S==k)&(cond==1)
            kf = KFold(5, shuffle=False) if contig else StratifiedKFold(5, shuffle=True, random_state=seed)
            a += [acc(F[mi][tr], cls[mi][tr], F[mi][te], cls[mi][te], perm) for tr,te in kf.split(F[mi], cls[mi])]
        return float(np.mean(a))
    seeds = np.array([within(s) for s in range(NSEEDS)]); a0 = seeds[0]
    null0 = np.array([within(0, perm=True) for _ in range(NPW)])
    ac = within(contig=True); nullc = np.array([within(0, perm=True, contig=True) for _ in range(NPW)])
    aT = float(np.mean([acc(F[(S==k)&(cond==0)], cls[(S==k)&(cond==0)], F[(S==k)&(cond==1)], cls[(S==k)&(cond==1)]) for k in np.unique(S)]))
    lines.append(f'| {tag} | **{seeds.mean()*100:.1f} ± {seeds.std()*100:.1f}%** (min {seeds.min()*100:.1f}, máx {seeds.max()*100:.1f}) | {a0*100:.1f}% | p95 {np.percentile(null0,95)*100:.1f}% · **p = {pval(null0, a0):.4f}** | **{ac*100:.1f}%** | p95 {np.percentile(nullc,95)*100:.1f}% · **p = {pval(nullc, ac):.4f}** | {aT*100:.1f}% |')
    print(f'{tag}: within seeds {seeds.mean()*100:.2f}±{seeds.std()*100:.2f} (seed0 {a0*100:.2f}, p={pval(null0,a0):.4f}) contig {ac*100:.2f} (p={pval(nullc,ac):.4f}) pron→inner {aT*100:.2f}', flush=True)
lines += ['', '- A semente 0 (publicada em 05/09 como 34,2 % no subconjunto) é UMA amostra da distribuição de dobras; a média entre sementes é a estimativa honesta. O esquema por blocos contíguos evita a semente e o embaralhamento.',
          '- "Dentro da sessão" aqui = 80 trials de inner por sessão (20 por classe), treino ≈ 64 / teste 16 por dobra. Não são "~200 trials por condição": 200 é o total de inner do sub-01 somando as 3 sessões (240 no sub-02).']
open(OUT,'w').write('\n'.join(lines)); print('\n'.join(lines))
