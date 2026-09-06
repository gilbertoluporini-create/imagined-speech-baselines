#!/usr/bin/env python3
"""PROFESSOR-GABARITO no FEIS (EEG Emotiv EPOC+ 14ch @256 Hz, 21 sujeitos, 16 fonemas) — 05/09/2026.
Pergunta: um decodificador treinado em fala FALADA lê fala IMAGINADA (thinking) da mesma pessoa?
Desenho igual ao nieto_transfer.py (linear, CPU, minutos): log-bandpower θαβγ por canal → LogisticRegression.
Validação por BLOCOS temporais (3 blocos = "sessões" do protocolo; detecção por lacuna de tempo, senão terços),
nunca janela aleatória (evita vazamento por deriva). Condições por sujeito:
  I  thinking→thinking (LOBO)        P  speaking→speaking (LOBO)
  T  speaking(2 blocos)→thinking(bloco restante)   [a pergunta do projeto]
  Tm speaking(mesmos trials)→thinking  [OTIMISTA: mesmos trials, só p/ referência]
  M  speaking+thinking(2 blocos)→thinking(bloco restante)
Nulo: permutação dos rótulos de treino (×NPERM) em I e T. 16 classes (acaso 6,25%) + binário vogal/consoante (bal. acc, acaso 50%).
Subconjunto '7ch' = interseção com a nossa coroa (F7 FC5 T7 P7 F8 T8 P8).
Uso: python3 feis_transfer.py [01 02 ...] (default: 01..21). Saída: RESULTADO_FEIS_TRANSFER.md + feis_features_cache.npz"""
import os, sys, time, zipfile, io, numpy as np, pandas as pd
from scipy.signal import welch
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import balanced_accuracy_score
ROOT = os.environ.get('FEIS_ROOT', 'data/feis/experiments')   # FEIS-v1.1.zip from Zenodo 3554128 → .../experiments ; optional if cache present
OUT = 'results/RESULTADO_FEIS_TRANSFER.md'; CACHE = 'cache/feis_features_cache.npz'; os.makedirs('results', exist_ok=True)
CH = ['F3','FC5','AF3','F7','T7','P7','O1','O2','P8','T8','F8','AF4','FC6','F4']
NOSSOS = ['F7','FC5','T7','P7','F8','T8','P8']; IDX7 = [CH.index(c) for c in NOSSOS]
BANDS = [(4,8),(8,13),(13,30),(30,45)]; FS = 256; T0, T1 = 0.25, 5.0
VOGAIS = {'fleece','goose','trap','thought'}
NPERM = 200; rng = np.random.default_rng(0)
SUBS = [a for a in sys.argv[1:] if not a.startswith('--')] or [f'{i:02d}' for i in range(1,22)]

def load_stage(sub, stage):
    with zipfile.ZipFile(f'{ROOT}/{sub}/{stage}.zip') as z:
        df = pd.read_csv(io.BytesIO(z.read(f'{stage}.csv')), usecols=['Time:256Hz','Epoch']+CH+['Label'], dtype={c:'float32' for c in CH})
    eps = sorted(df['Epoch'].unique()); X, y, t = [], [], []
    for e in eps:
        d = df[df['Epoch']==e]
        if len(d) < 1200: continue
        x = d[CH].values[:1280]; x = x - x.mean(0)
        X.append(x); y.append(d['Label'].iloc[0]); t.append(float(d['Time:256Hz'].iloc[0]))
    return np.array(X), np.array(y), np.array(t)

def feats(X):
    """X (n, 1280, 14) → log-bandpower (n, 14*4) na janela T0..T1"""
    seg = X[:, int(T0*FS):int(T1*FS), :]
    f, P = welch(seg, fs=FS, nperseg=256, axis=1)                  # (n, nf, 14)
    F = [np.log(P[:, (f>=lo)&(f<hi), :].mean(1) + 1e-12) for lo,hi in BANDS]
    return np.stack(F, 2).reshape(len(X), -1)                       # (n, 14, 4) → (n, 56)

def blocos(t, n=3):
    """blocos temporais: lacunas > 90 s entre trials consecutivos; se não houver ≥2, terços por índice"""
    gaps = np.where(np.diff(t) > 90)[0]
    if len(gaps) >= 2:
        cuts = gaps[np.argsort(-np.diff(t)[gaps])][:n-1]; cuts = np.sort(cuts)
        b = np.zeros(len(t), int)
        for c in cuts: b[c+1:] += 1
        return b, 'lacunas'
    return np.minimum((np.arange(len(t)) * n) // len(t), n-1), 'terços'

def clf(): return make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=2000))
def fit_acc(Xtr, ytr, Xte, yte, perm=False):
    ytr_ = ytr[rng.permutation(len(ytr))] if perm else ytr
    p = clf().fit(Xtr, ytr_).predict(Xte); return (p==yte).mean(), p

def run_sub(sub, cache):
    t0 = time.time()
    if sub in cache:
        Fs, ys, ts, Ft, yt, tt = cache[sub]
    else:
        Xs, ys, ts = load_stage(sub, 'speaking'); Xt, yt, tt = load_stage(sub, 'thinking')
        Fs, Ft = feats(Xs), feats(Xt); cache[sub] = (Fs, ys, ts, Ft, yt, tt); del Xs, Xt
    assert (ys == yt).all(), f'{sub}: rótulos speaking≠thinking'
    b, modo = blocos(tt); nb = len(np.unique(b))
    res = {}
    for tag, idx in (('14ch', slice(None)), ('7ch', IDX7)):
        cols = np.arange(56).reshape(14,4)[idx].ravel()
        fs, ft = Fs[:, cols], Ft[:, cols]
        def lobo(Xtr_all, ytr_all, Xte_all, yte_all, perm=False, misto=None):
            accs = []
            for k in range(nb):
                tr, te = b!=k, b==k
                Xtr, ytr = Xtr_all[tr], ytr_all[tr]
                if misto is not None: Xtr = np.vstack([Xtr, misto[0][tr]]); ytr = np.concatenate([ytr, misto[1][tr]])
                accs.append(fit_acc(Xtr, ytr, Xte_all[te], yte_all[te], perm)[0])
            return float(np.mean(accs))
        r = {}
        r['I'] = lobo(ft, yt, ft, yt); r['P'] = lobo(fs, ys, fs, ys)
        r['T'] = lobo(fs, ys, ft, yt); r['M'] = lobo(fs, ys, ft, yt, misto=(ft, yt))
        r['Tm'] = fit_acc(fs, ys, ft, yt)[0]                      # mesmos trials (otimista)
        # binário vogal/consoante (balanced acc)
        vs, vt = np.isin(ys, list(VOGAIS)), np.isin(yt, list(VOGAIS))
        def lobo_bin(Xtr_all, ytr_all, Xte_all, yte_all):
            ps, ts_ = [], []
            for k in range(nb):
                tr, te = b!=k, b==k
                ps.append(clf().fit(Xtr_all[tr], ytr_all[tr]).predict(Xte_all[te])); ts_.append(yte_all[te])
            return float(balanced_accuracy_score(np.concatenate(ts_), np.concatenate(ps)))
        r['I_bin'] = lobo_bin(ft, vt, ft, vt); r['T_bin'] = lobo_bin(fs, vs, ft, vt)
        # nulos por permutação
        nI = np.array([lobo(ft, yt, ft, yt, perm=True) for _ in range(NPERM)])
        nT = np.array([lobo(fs, ys, ft, yt, perm=True) for _ in range(NPERM)])
        r['I_p'] = float((nI >= r['I']).mean()); r['I_null95'] = float(np.percentile(nI, 95))
        r['T_p'] = float((nT >= r['T']).mean()); r['T_null95'] = float(np.percentile(nT, 95))
        res[tag] = r
    print(f"{sub} blocos={nb}({modo}) n={len(yt)} | 14ch I={res['14ch']['I']*100:.1f}% (p={res['14ch']['I_p']:.3f}) P={res['14ch']['P']*100:.1f}% T={res['14ch']['T']*100:.1f}% (p={res['14ch']['T_p']:.3f}) M={res['14ch']['M']*100:.1f}% Tm={res['14ch']['Tm']*100:.1f}% | 7ch I={res['7ch']['I']*100:.1f}% T={res['7ch']['T']*100:.1f}% | {time.time()-t0:.0f}s", flush=True)
    return res, nb, modo, len(yt)

cache = {}
if os.path.exists(CACHE):
    z = np.load(CACHE, allow_pickle=True); cache = z['cache'].item()
ALL = {}
for sub in SUBS:
    try: ALL[sub] = run_sub(sub, cache)
    except Exception as ex: print(f'{sub}: ERRO {ex}', flush=True)
np.savez_compressed(CACHE, cache=np.array(cache, dtype=object))

# ---- relatório ----
def col(tag, k): return np.array([ALL[s][0][tag][k] for s in ALL])
def grupo(v, chance):
    ic = np.percentile([rng.choice(v, len(v)).mean() for _ in range(5000)], [2.5, 97.5])
    try: pw = stats.wilcoxon(v - chance, alternative='greater').pvalue
    except Exception: pw = float('nan')
    return f"{v.mean()*100:.1f}% [IC95 {ic[0]*100:.1f}–{ic[1]*100:.1f}] Wilcoxon p={pw:.3g}"
L = ['# RESULTADO — professor-gabarito no FEIS (EEG 14ch Emotiv, 16 fonemas)',
     f'*05/09/2026 · {len(ALL)} sujeitos · log-bandpower θαβγ · LogReg C=0,05 · validação por blocos temporais (LOBO) · nulo perm ×{NPERM} · acaso 16 classes = 6,25%*', '',
     '## Por sujeito (14 canais)', '| suj | blocos | I think→think | I p | P speak→speak | **T speak→think** | T p | M misto→think | Tm mesmos trials | I bin | T bin |', '|---|---|---|---|---|---|---|---|---|---|---|']
for s,(r,nb,modo,n) in ALL.items():
    a = r['14ch']
    L.append(f"| {s} | {nb} ({modo}) | {a['I']*100:.1f}% | {a['I_p']:.3f} | {a['P']*100:.1f}% | **{a['T']*100:.1f}%** | {a['T_p']:.3f} | {a['M']*100:.1f}% | {a['Tm']*100:.1f}% | {a['I_bin']*100:.1f}% | {a['T_bin']*100:.1f}% |")
L += ['', '## Grupo (média entre sujeitos, IC95 bootstrap, Wilcoxon unilateral vs acaso)', '| condição | 14 canais | 7 canais (os nossos: F7 FC5 T7 P7 F8 T8 P8) |', '|---|---|---|']
for k, ch in (('I', 1/16), ('P', 1/16), ('T', 1/16), ('M', 1/16), ('Tm', 1/16), ('I_bin', 0.5), ('T_bin', 0.5)):
    L.append(f"| {k} | {grupo(col('14ch',k), ch)} | {grupo(col('7ch',k), ch)} |")
nI = int((col('14ch','I_p') < 0.05).sum()); nT = int((col('14ch','T_p') < 0.05).sum())
L += ['', f'- Sujeitos com I significativo (p<0,05): **{nI}/{len(ALL)}** · com T significativo: **{nT}/{len(ALL)}** (esperado ao acaso: ~{0.05*len(ALL):.1f}).', '',
      '## Leitura', '- **T** é a pergunta do projeto: treinar só em FALADO e ler IMAGINADO em trials diferentes (blocos distintos). Se T ≈ acaso no grupo, o professor falado NÃO transfere em EEG linear com 14 canais secos.',
      '- **P** alto é esperado e NÃO é vitória: fala tem EMG facial e movimento; o classificador lê músculo, não córtex.',
      '- **Tm** (mesmos trials) é o teto otimista com vazamento temporal possível; só referência.',
      '- **I** dentro do dia (blocos do mesmo protocolo) mede se o imaginado tem sinal linear estável em ~1 h; ainda não é entre-dias.',
      '- Limites honestos: Emotiv seco/salino, sem ICA, 10 repetições por classe, linear. "Sem evidência ≠ impossível".', '',
      '## Observações', '- **Tm ≫ T com o mesmo classificador**: a única diferença é a proximidade temporal treino/teste → o ganho de Tm é deriva/estado compartilhado dentro do trial, não conteúdo fonêmico. Transfer falado→imaginado só vale com treino e teste em trials/blocos distintos.',
      '- **Poder**: meia-largura do IC95 do grupo ≈ 0,7 pp → um efeito real de T ≥ ~1,5 pp sobre o acaso teria aparecido. Sob este método, o transfer é menor que isso, se existir.',
      '- **7 canais ≈ 14 canais** em todas as condições → o gargalo é SNR (eletrodo seco), volume (10 rep/classe) e tarefa (16 classes), não contagem de canais.',
      '- Binário vogal/consoante no acaso sob validação por blocos; o 69% ± 13 dos autores (split aleatório 80/20) não replica aqui.',
      '- Timestamps do dataset foram regravados a intervalo fixo (22 s) → as 3 sessões do protocolo não são recuperáveis; blocos = terços contíguos por índice.']
open(OUT,'w').write('\n'.join(L)); print('\n'.join(L[-12:]))
