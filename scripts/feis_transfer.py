#!/usr/bin/env python3
"""PROFESSOR-GABARITO no FEIS (EEG Emotiv EPOC+ 14 ch SALINOS @256 Hz, 21 sujeitos, 16 fonemas do INGLÊS) — 05/09/2026, revisado 07/09/2026.
Pergunta: um decodificador treinado em fala FALADA lê fala IMAGINADA (thinking) da mesma pessoa?
Desenho igual ao nieto_transfer.py (linear, CPU, minutos): log-bandpower θαβγ por canal → LogisticRegression.

VALIDAÇÃO POR SESSÕES DO PROTOCOLO (leave-one-session-out). REVISÃO 07/09/2026: as 3 sessões SÃO recuperáveis pelo
índice de epoch. Os autores concatenaram as 3 gravações somando +64/+112 ao Epoch e +1408/+2464 s ao Time
(B059691/code/merge_trial_csvs.py: "time and epochs were reset to 0 per recording"). Sessão 1 = epochs 0–63 (64 trials),
sessão 2 = 64–111 (48), sessão 3 = 112–159 (48); o sujeito 12 tem 2 sessões (112 trials). A versão de 05/09 afirmava,
ERRADO, que "os timestamps não permitem recuperar as sessões" e usava terços contíguos (53/53/54). Aqui: sessões reais.

Condições por sujeito:
  I      thinking→thinking (LOSO)                 P  speaking→speaking (LOSO)
  T      speaking(2 sessões)→thinking(sessão restante)          [a pergunta do projeto]
  M      speaking+thinking(2 sessões)→thinking(sessão restante)
  Tm     speaking(TODOS)→thinking(MESMOS trials)  [otimista; treino 160 vs ~106 de T → NÃO é comparação limpa]
  Tm_eq  speaking(2 sessões)→thinking(MESMAS 2 sessões)  [mesmos trials COM tamanho de treino igual ao de T: o par justo de T]
  C_par / C_impar  speaking(trials pares)→thinking(pares = pareados) vs thinking(ímpares = intercalados, não pareados)
  C_viz  nos ímpares: fração de predições iguais ao rótulo do trial par vizinho (assinatura de memorização de vizinho)
  I_bin_rand  binário vogal/consoante com 5-fold ALEATÓRIO estratificado (o esquema dos autores) — para testar se o split explica o 69 %
Nulo: permutação dos rótulos de treino (×NPERM) em I e T; p = (r+1)/(NPERM+1) (Phipson & Smyth 2010). 16 classes (acaso 6,25 %)
+ binário vogal/consoante (bal. acc, acaso 50 %). Subconjunto '7ch' = interseção com a nossa coroa (F7 FC5 T7 P7 F8 T8 P8).
Uso: python3 feis_transfer.py [01 02 ...] (default: 01..21). Saída: results/RESULTADO_FEIS_TRANSFER.md + cache/feis_features_cache.npz"""
import os, sys, time, zipfile, io, numpy as np, pandas as pd
from scipy.signal import welch
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
ROOT = os.environ.get('FEIS_ROOT', 'data/feis/experiments')   # FEIS-v1.1.zip from Zenodo 3554128 → .../experiments ; optional if cache present
OUT = 'results/RESULTADO_FEIS_TRANSFER.md'; CACHE = 'cache/feis_features_cache.npz'; os.makedirs('results', exist_ok=True)
CH = ['F3','FC5','AF3','F7','T7','P7','O1','O2','P8','T8','F8','AF4','FC6','F4']
NOSSOS = ['F7','FC5','T7','P7','F8','T8','P8']; IDX7 = [CH.index(c) for c in NOSSOS]
BANDS = [(4,8),(8,13),(13,30),(30,45)]; FS = 256; T0, T1 = 0.25, 5.0
VOGAIS = {'fleece','goose','trap','thought'}
NPERM = int(os.environ.get('NPERM', 200)); rng = np.random.default_rng(0)
SUBS = [a for a in sys.argv[1:] if not a.startswith('--')] or [f'{i:02d}' for i in range(1,22)]
TRIAL_S = 22.0            # período nominal do trial (5 cue + 1 prepare + 5 thinking + 5 speaking + 5 rest + 1); passo usado pelos autores ao concatenar
T_FIRST = 11.0            # Time do 1º trial em todos os sujeitos conferidos (01, 12, 21)
SESS_EDGES = (64, 112)    # epoch < 64 → sessão 1; 64–111 → sessão 2; ≥ 112 → sessão 3 (merge_trial_csvs.py L156-176)

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
    """sessões do protocolo pelo índice de epoch recuperado do Time (passo fixo 22 s a partir de 11 s);
    fallback 1: lacunas > 90 s; fallback 2: terços por índice (o que a versão de 05/09 usava sempre)"""
    ep = np.rint((t - T_FIRST) / TRIAL_S).astype(int)
    if ep.min() >= 0 and ep.max() < 160 and len(np.unique(ep)) == len(ep) and np.allclose((t - T_FIRST) / TRIAL_S, ep, atol=0.05):
        return np.digitize(ep, SESS_EDGES), 'sessões'
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
def pval(null, obs): return float((np.sum(np.asarray(null) >= obs) + 1) / (len(null) + 1))

def run_sub(sub, cache):
    t0 = time.time()
    if sub in cache:
        Fs, ys, ts, Ft, yt, tt = cache[sub]
    else:
        Xs, ys, ts = load_stage(sub, 'speaking'); Xt, yt, tt = load_stage(sub, 'thinking')
        Fs, Ft = feats(Xs), feats(Xt); cache[sub] = (Fs, ys, ts, Ft, yt, tt); del Xs, Xt
    assert (ys == yt).all(), f'{sub}: rótulos speaking≠thinking'
    b, modo = blocos(tt); nb = len(np.unique(b)); tam = [int((b==k).sum()) for k in range(nb)]
    res = {}
    for tag, idx in (('14ch', slice(None)), ('7ch', IDX7)):
        cols = np.arange(56).reshape(14,4)[idx].ravel()
        fs, ft = Fs[:, cols], Ft[:, cols]
        def lobo(Xtr_all, ytr_all, Xte_all, yte_all, perm=False, misto=None, mesmos=False):
            """LOSO. mesmos=True → testa nos MESMOS trials de treino (sessões b!=k), com o tamanho de treino de T"""
            accs = []
            for k in range(nb):
                tr, te = b!=k, (b!=k if mesmos else b==k)
                Xtr, ytr = Xtr_all[tr], ytr_all[tr]
                if misto is not None: Xtr = np.vstack([Xtr, misto[0][tr]]); ytr = np.concatenate([ytr, misto[1][tr]])
                accs.append(fit_acc(Xtr, ytr, Xte_all[te], yte_all[te], perm)[0])
            return float(np.mean(accs))
        r = {}
        r['I'] = lobo(ft, yt, ft, yt); r['P'] = lobo(fs, ys, fs, ys)
        r['T'] = lobo(fs, ys, ft, yt); r['M'] = lobo(fs, ys, ft, yt, misto=(ft, yt))
        r['Tm'] = fit_acc(fs, ys, ft, yt)[0]                      # todos os trials → mesmos trials (treino 160; otimista)
        r['Tm_eq'] = lobo(fs, ys, ft, yt, mesmos=True)            # mesmos trials, treino ≈ 106 como em T (o par justo)
        # controle intercalado: treina speaking nos trials PARES; testa thinking nos pares (pareado) e nos ímpares (não pareado, intercalado)
        ev = (np.arange(len(yt)) % 2 == 0); od = ~ev
        a_par, _ = fit_acc(fs[ev], ys[ev], ft[ev], yt[ev]); a_imp, p_imp = fit_acc(fs[ev], ys[ev], ft[od], yt[od])
        r['C_par'], r['C_impar'] = float(a_par), float(a_imp)
        viz = ys[ev][:len(p_imp)]                                   # rótulo do trial par imediatamente anterior a cada ímpar
        r['C_viz'] = float((p_imp == viz).mean())
        r['C_viz_esp'] = float(np.mean([(p_imp[rng.permutation(len(p_imp))] == viz).mean() for _ in range(200)]))
        # binário vogal/consoante (balanced acc): LOSO e split aleatório (esquema dos autores)
        vs, vt = np.isin(ys, list(VOGAIS)), np.isin(yt, list(VOGAIS))
        def lobo_bin(Xtr_all, ytr_all, Xte_all, yte_all):
            ps, ts_ = [], []
            for k in range(nb):
                tr, te = b!=k, b==k
                ps.append(clf().fit(Xtr_all[tr], ytr_all[tr]).predict(Xte_all[te])); ts_.append(yte_all[te])
            return float(balanced_accuracy_score(np.concatenate(ts_), np.concatenate(ps)))
        r['I_bin'] = lobo_bin(ft, vt, ft, vt); r['T_bin'] = lobo_bin(fs, vs, ft, vt)
        skf = StratifiedKFold(5, shuffle=True, random_state=0); ps, ts_ = [], []
        for tr, te in skf.split(ft, vt):
            ps.append(clf().fit(ft[tr], vt[tr]).predict(ft[te])); ts_.append(vt[te])
        r['I_bin_rand'] = float(balanced_accuracy_score(np.concatenate(ts_), np.concatenate(ps)))
        # nulos por permutação
        nI = np.array([lobo(ft, yt, ft, yt, perm=True) for _ in range(NPERM)])
        nT = np.array([lobo(fs, ys, ft, yt, perm=True) for _ in range(NPERM)])
        r['I_p'] = pval(nI, r['I']); r['I_null95'] = float(np.percentile(nI, 95))
        r['T_p'] = pval(nT, r['T']); r['T_null95'] = float(np.percentile(nT, 95))
        res[tag] = r
    a = res['14ch']
    print(f"{sub} {modo} {tam} n={len(yt)} | 14ch I={a['I']*100:.1f}% (p={a['I_p']:.3f}) P={a['P']*100:.1f}% T={a['T']*100:.1f}% (p={a['T_p']:.3f}) M={a['M']*100:.1f}% Tm={a['Tm']*100:.1f}% Tm_eq={a['Tm_eq']*100:.1f}% | C par/ímpar={a['C_par']*100:.1f}/{a['C_impar']*100:.1f}% viz={a['C_viz']*100:.1f}% (esp {a['C_viz_esp']*100:.1f}) | bin LOSO/rand={a['I_bin']*100:.1f}/{a['I_bin_rand']*100:.1f}% | 7ch I={res['7ch']['I']*100:.1f}% T={res['7ch']['T']*100:.1f}% | {time.time()-t0:.0f}s", flush=True)
    return res, nb, modo, len(yt), tam

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
def pareado(a, b):
    """diferença a−b entre sujeitos: média em pp, IC95 bootstrap, Wilcoxon pareado bicaudal"""
    d = a - b; ic = np.percentile([rng.choice(d, len(d)).mean() for _ in range(5000)], [2.5, 97.5])
    try: pw = stats.wilcoxon(d).pvalue
    except Exception: pw = float('nan')
    return d.mean()*100, ic[0]*100, ic[1]*100, pw
g = {k: col('14ch', k) for k in ('I','P','T','M','Tm','Tm_eq','C_par','C_impar','C_viz','C_viz_esp','I_bin','T_bin','I_bin_rand')}
dTmT = pareado(g['Tm'], g['T']); dEqT = pareado(g['Tm_eq'], g['T']); dTmEq = pareado(g['Tm'], g['Tm_eq'])
dPar = pareado(g['C_par'], g['C_impar']); dViz = pareado(g['C_viz'], g['C_viz_esp'])
ic_T = np.percentile([rng.choice(g['T'], len(g['T'])).mean() for _ in range(20000)], [2.5, 97.5])
nsess = [ALL[s][1] for s in ALL]; modos = sorted(set(ALL[s][2] for s in ALL))
L = ['# RESULTADO — professor-gabarito no FEIS (EEG 14 ch Emotiv EPOC+ salino, 16 fonemas do inglês)',
     f'*05/09/2026, revisado 07/09/2026 · {len(ALL)} sujeitos · log-bandpower θαβγ · LogReg C=0,05 · validação leave-one-SESSION-out ({"/".join(modos)}; {sum(1 for n in nsess if n==3)} sujeitos com 3 sessões, {sum(1 for n in nsess if n==2)} com 2) · nulo perm ×{NPERM}, p=(r+1)/(N+1) · acaso 16 classes = 6,25%*', '',
     '**Revisão 07/09/2026.** A versão de 05/09 dizia que as sessões do FEIS não eram recuperáveis e usava terços contíguos. Estava errado: os autores concatenaram as 3 gravações somando +64/+112 ao índice de epoch (`B059691/code/merge_trial_csvs.py`), e o índice se recupera do `Time` (passo fixo 22 s a partir de 11 s). Sessões = epochs 0–63 / 64–111 / 112–159 (64/48/48 trials; sujeito 12: 2 sessões, 112 trials). Todos os números abaixo foram recalculados com as sessões reais. Também entraram os controles Tm_eq, C_par/C_impar/C_viz e I_bin_rand, e o p passou ao estimador (r+1)/(N+1).', '',
     '## Por sujeito (14 canais)', '| suj | sessões (trials) | I think→think | I p | P speak→speak | **T speak→think** | T p | M misto→think | Tm todos→mesmos | Tm_eq 2 ses→mesmas | C par / ímpar | I bin LOSO | I bin rand | T bin |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for s,(r,nb,modo,n,tam) in ALL.items():
    a = r['14ch']
    L.append(f"| {s} | {nb} ({'/'.join(map(str,tam))}) | {a['I']*100:.1f}% | {a['I_p']:.3f} | {a['P']*100:.1f}% | **{a['T']*100:.1f}%** | {a['T_p']:.3f} | {a['M']*100:.1f}% | {a['Tm']*100:.1f}% | {a['Tm_eq']*100:.1f}% | {a['C_par']*100:.1f} / {a['C_impar']*100:.1f}% | {a['I_bin']*100:.1f}% | {a['I_bin_rand']*100:.1f}% | {a['T_bin']*100:.1f}% |")
L += ['', '## Grupo (média entre sujeitos, IC95 bootstrap, Wilcoxon unilateral vs acaso)', '| condição | 14 canais | 7 canais (os nossos: F7 FC5 T7 P7 F8 T8 P8) |', '|---|---|---|']
for k, ch in (('I', 1/16), ('P', 1/16), ('T', 1/16), ('M', 1/16), ('Tm', 1/16), ('Tm_eq', 1/16), ('C_par', 1/16), ('C_impar', 1/16), ('I_bin', 0.5), ('I_bin_rand', 0.5), ('T_bin', 0.5)):
    L.append(f"| {k} | {grupo(col('14ch',k), ch)} | {grupo(col('7ch',k), ch)} |")
nI = int((col('14ch','I_p') < 0.05).sum()); nT = int((col('14ch','T_p') < 0.05).sum())
L += ['', f'- Sujeitos com I significativo (p<0,05): **{nI}/{len(ALL)}** · com T significativo: **{nT}/{len(ALL)}** (esperado ao acaso: ~{0.05*len(ALL):.1f}).', '',
      '## Comparações pareadas entre sujeitos (14 canais; diferença em pp, IC95 bootstrap, Wilcoxon pareado bicaudal)', '| comparação | diferença | IC95 | p |', '|---|---|---|---|',
      f"| Tm − T (treino 160 vs ~106: confunde trial E tamanho) | {dTmT[0]:+.2f} pp | [{dTmT[1]:+.2f}; {dTmT[2]:+.2f}] | {dTmT[3]:.3g} |",
      f"| **Tm_eq − T** (mesmos trials vs sessão retida, MESMO tamanho de treino) | **{dEqT[0]:+.2f} pp** | [{dEqT[1]:+.2f}; {dEqT[2]:+.2f}] | {dEqT[3]:.3g} |",
      f"| Tm − Tm_eq (efeito do tamanho de treino, teste nos mesmos trials) | {dTmEq[0]:+.2f} pp | [{dTmEq[1]:+.2f}; {dTmEq[2]:+.2f}] | {dTmEq[3]:.3g} |",
      f"| C_par − C_impar (pareado vs intercalado não pareado, mesmo modelo) | {dPar[0]:+.2f} pp | [{dPar[1]:+.2f}; {dPar[2]:+.2f}] | {dPar[3]:.3g} |",
      f"| C_viz − esperado (predição nos ímpares = rótulo do par vizinho) | {dViz[0]:+.2f} pp | [{dViz[1]:+.2f}; {dViz[2]:+.2f}] | {dViz[3]:.3g} |", '',
      '## Leitura', '- **T** é a pergunta do projeto: treinar só em FALADO e ler IMAGINADO em sessões distintas. Se T ≈ acaso no grupo, o professor falado NÃO transfere em EEG linear com 14 canais salinos.',
      '- **P** alto é esperado e NÃO é vitória: fala tem EMG facial e movimento; o classificador lê músculo, não córtex.',
      '- **Tm** (todos os trials → mesmos trials) mistura dois efeitos: identidade do trial E tamanho de treino (160 vs ~106). **Tm_eq** isola o primeiro.',
      '- **I** entre sessões do mesmo protocolo mede se o imaginado tem sinal linear estável em ~1 h; as 3 sessões são consecutivas na mesma visita — não é entre dias.',
      '- Limites honestos: Emotiv EPOC+ salino (feltro + solução salina, não seco), sem ICA, 10 repetições por classe (7 no sujeito 12), linear. "Sem evidência ≠ impossível".', '',
      '## Observações',
      f"- **Mesmos trials vs sessão retida, com tamanho de treino igualado:** Tm_eq {g['Tm_eq'].mean()*100:.2f}% vs T {g['T'].mean()*100:.2f}% = {dEqT[0]:+.2f} pp (IC95 [{dEqT[1]:+.2f}; {dEqT[2]:+.2f}], p={dEqT[3]:.2g}). O tamanho de treino em si vale {dTmEq[0]:+.2f} pp (p={dTmEq[3]:.2g}). A versão de 05/09 dizia que \"a única diferença é a proximidade temporal\" — havia DUAS diferenças (identidade do trial e tamanho de treino); a frase caiu, a conclusão sobreviveu.",
      f"- **O mecanismo é identidade do trial, não proximidade temporal:** com o mesmo modelo treinado nos trials pares de speaking, thinking nos MESMOS pares dá {g['C_par'].mean()*100:.2f}% e thinking nos ímpares INTERCALADOS (vizinhos a ≤22 s) dá {g['C_impar'].mean()*100:.2f}% ({dPar[0]:+.2f} pp, p={dPar[3]:.2g}). Nos ímpares, a predição coincide com o rótulo do par vizinho em {g['C_viz'].mean()*100:.1f}% dos casos contra {g['C_viz_esp'].mean()*100:.1f}% esperado ({dViz[0]:+.2f} pp, p={dViz[3]:.2g}): o modelo memoriza estado lento trial a trial.",
      f"- **Poder:** IC95 do grupo para T = [{ic_T[0]*100:.2f}; {ic_T[1]*100:.2f}]% → o que o IC licencia é \"efeito médio de grupo ≤ {max(0,(ic_T[1]-1/16)*100):+.2f} pp sobre o acaso\". Isso NÃO é piso por sujeito: um efeito concentrado em poucos sujeitos escapa deste teste (a frase de 05/09, \"≥1,5 pp teria aparecido\", só vale para efeito homogêneo).",
      f"- **7 canais ≈ 14 canais** em todas as condições → o gargalo é SNR (eletrodo salino de consumo), volume (10 rep/classe) e tarefa (16 classes), não contagem de canais.",
      f"- **Binário vogal/consoante:** LOSO {g['I_bin'].mean()*100:.1f}% e split ALEATÓRIO estratificado {g['I_bin_rand'].mean()*100:.1f}% — os dois no acaso (50%). O 69 % ± 13 dos autores (5 sujeitos sorteados, features 22.344-d, SVM-RBF com grid search) NÃO replica com este pipeline sob nenhum dos dois splits; portanto o esquema de validação não explica a diferença — a versão de 05/09 atribuía a diferença ao split, e isso caiu.",
      '- **Sessões do FEIS recuperadas** pelo índice de epoch (ver cabeçalho). As 3 sessões de cada sujeito são consecutivas na mesma visita (~59 min no total), então I e T aqui são "entre sessões da mesma visita", não entre dias.']
open(OUT,'w').write('\n'.join(L)); print('\n'.join(L[-14:]))
