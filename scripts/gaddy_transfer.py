#!/usr/bin/env python3
"""PROFESSOR-GABARITO no dataset Gaddy (sEMG, 8ch, 1 kHz) — 05/09/2026.
Pergunta: um decodificador treinado em fala FALADA lê fala SILENCIOSA da mesma pessoa?
Desenho leve (CPU, minutos): features estilo Gaddy por quadro → pooling por enunciado (80 dims)
→ Ridge p/ um espaço de texto (TF-IDF char n-gram + SVD 128) → RETRIEVAL da frase certa
entre as candidatas do teste (top-1, top-10, MRR). Nulo: permutação dos textos no treino.
Condições: (A) silent→silent LOSO · (B) voiced→silent mesmas frases · (C) voiced→silent
FRASES INÉDITAS (5-fold) · (D) voiced→voiced inéditas · (E) silent→silent inéditas ·
(F) voiced+silent→silent inéditas. Saída: RESULTADO_GADDY_TRANSFER.md."""
import json, glob, os, sys, time, numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
RAW = os.environ.get('GADDY_RAW', 'data/gaddy_emg/emg_data')   # raw from Zenodo 4064409 (emg_data.tar.gz); optional if cache present
OUT = 'results/RESULTADO_GADDY_TRANSFER.md'; CACHE = 'cache/gaddy_features_cache.npz'; os.makedirs('results', exist_ok=True)
rng = np.random.default_rng(0)
FS, WIN, HOP = 1000, 27, 10
def feats(emg):
    """features por quadro (27 ms, hop 10): mean/rms do low-pass, rms/zcr/mean|.| do high-pass, por canal → pooling mean+std"""
    x = emg - emg.mean(0)
    k = 9; low = np.stack([np.convolve(x[:,c], np.ones(k)/k, mode='same') for c in range(x.shape[1])],1); high = x - low
    n = (len(x)-WIN)//HOP + 1
    if n < 3: return None
    idx = np.arange(WIN)[None,:] + HOP*np.arange(n)[:,None]
    L, H = low[idx], high[idx]                        # (n, WIN, 8)
    f = np.concatenate([L.mean(1), np.sqrt((L**2).mean(1)), np.sqrt((H**2).mean(1)),
                        (np.diff(np.sign(H),axis=1)!=0).mean(1), np.abs(H).mean(1)], axis=1)   # (n, 40)
    return np.concatenate([f.mean(0), f.std(0), [np.log(len(x)/FS)]])   # 81 dims
def load(split):
    d = {}
    for info in glob.glob(f'{RAW}/{split}/*/*_info.json'):
        j = json.load(open(info))
        if not j['text']: continue
        key = (j['book'], j['sentence_index'])
        emg = np.load(info.replace('_info.json','_emg.npy'))
        fv = feats(emg)
        if fv is None: continue
        d[key] = (fv, j['text'], info.split('/')[-2])
    return d
t0 = time.time()
if os.path.isdir(RAW):
    V, S = load('voiced_parallel_data'), load('silent_parallel_data')
    keys = sorted(set(V) & set(S)); print(f'pares voiced/silent: {len(keys)}  ({time.time()-t0:.0f}s)')
    XV = np.array([V[k][0] for k in keys]); XS = np.array([S[k][0] for k in keys])
    texts = [V[k][1] for k in keys]; sessS = np.array([S[k][2] for k in keys])
else:                                                     # pooled features only (81-d per utterance), no raw signal
    z = np.load(CACHE, allow_pickle=True); XV, XS, sessS = z['XV'], z['XS'], z['sessS']; texts = list(z['texts']); keys = list(z['keys'])
    print(f'pares voiced/silent (cache, sem bruto): {len(keys)}')
MODO = next((a for a in sys.argv[1:] if a.startswith('--')), '')
if MODO == '--sem-duracao': XV, XS = XV[:,:-1], XS[:,:-1]; OUT = OUT.replace('.md','_SEM_DURACAO.md')
if MODO == '--so-duracao':  XV, XS = XV[:,-1:], XS[:,-1:]; OUT = OUT.replace('.md','_SO_DURACAO.md')
print('MODO:', MODO or 'completo', '| dims:', XV.shape[1])
# espaço de texto
tf = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4), min_df=2).fit(texts)
T = TruncatedSVD(128, random_state=0).fit_transform(tf.transform(texts)); T /= np.linalg.norm(T,axis=1,keepdims=True)+1e-9
def retrieval(Xtr, Ttr, Xte, te_idx, alpha=30.0, perm=False):
    sc = StandardScaler().fit(Xtr); Ttr_ = Ttr[rng.permutation(len(Ttr))] if perm else Ttr
    m = Ridge(alpha=alpha).fit(sc.transform(Xtr), Ttr_)
    P = m.predict(sc.transform(Xte)); P /= np.linalg.norm(P,axis=1,keepdims=True)+1e-9
    C = T[te_idx]                                     # candidatos = frases do teste
    sim = P @ C.T; ranks = (sim > sim[np.arange(len(te_idx)), np.arange(len(te_idx))][:,None]).sum(1) + 1
    return dict(top1=(ranks==1).mean(), top10=(ranks<=10).mean(), mrr=(1/ranks).mean(), n=len(te_idx), ranks=ranks)
def agg(rs): return {k: float(np.mean([r[k] for r in rs])) for k in ('top1','top10','mrr')} | {'n': int(np.mean([r['n'] for r in rs]))}
res = {}; NPERM = 100
kf = KFold(5, shuffle=True, random_state=0); folds = list(kf.split(keys))
# (A) silent→silent LOSO
rs = [retrieval(XS[sessS!=s], T[sessS!=s], XS[sessS==s], np.where(sessS==s)[0]) for s in np.unique(sessS)]; res['A voiced? não: silent→silent LOSO (sessão nova)'] = agg(rs)
# (B) voiced→silent mesmas frases
allidx = np.arange(len(keys)); res['B voiced→silent, MESMAS frases (pool 1589)'] = retrieval(XV, T, XS, allidx)
res['B nulo (perm)'] = agg([retrieval(XV, T, XS, allidx, perm=True) for _ in range(20)])
# (C) voiced→silent frases inéditas
rs = [retrieval(XV[tr], T[tr], XS[te], te) for tr,te in folds]; res['C voiced→silent, frases INÉDITAS (5-fold)'] = agg(rs)
null_c = [agg([retrieval(XV[tr], T[tr], XS[te], te, perm=True) for tr,te in folds])['top10'] for _ in range(NPERM)]
res['C nulo (perm ×%d)' % NPERM] = {'top10_mean': float(np.mean(null_c)), 'top10_p95': float(np.percentile(null_c,95)),
                                   'p_valor_top10': float((np.array(null_c) >= res['C voiced→silent, frases INÉDITAS (5-fold)']['top10']).mean())}
# (D) voiced→voiced inéditas · (E) silent→silent inéditas · (F) misto→silent inéditas
res['D voiced→voiced, inéditas'] = agg([retrieval(XV[tr], T[tr], XV[te], te) for tr,te in folds])
rsE = [retrieval(XS[tr], T[tr], XS[te], te) for tr,te in folds]; res['E silent→silent, inéditas'] = agg(rsE)
# teste PAREADO falado-professor (C) vs mudo-professor (E) nos MESMOS itens de teste (mesmos folds, mesma ordem)
rc = np.concatenate([r['ranks'] for r in rs]); re_ = np.concatenate([r['ranks'] for r in rsE])
hc, he, mc, me = (rc<=10).astype(float), (re_<=10).astype(float), 1/rc, 1/re_
bidx = rng.integers(0, len(rc), (5000, len(rc))); d10 = (hc[bidx]-he[bidx]).mean(1); dmrr = (mc[bidx]-me[bidx]).mean(1)
pareado = dict(n=len(rc), d10=100*(hc-he).mean(), ci10=100*np.percentile(d10,[2.5,97.5]), p10=(d10<=0).mean(),
               dmrr=(mc-me).mean(), cimrr=np.percentile(dmrr,[2.5,97.5]), pmrr=(dmrr<=0).mean(), medC=np.median(rc), medE=np.median(re_))
res['F voiced+silent→silent, inéditas'] = agg([retrieval(np.vstack([XV[tr],XS[tr]]), np.vstack([T[tr],T[tr]]), XS[te], te) for tr,te in folds])
# relatório
lines = ['# RESULTADO — professor-gabarito no Gaddy (sEMG 8ch)', f'*05/09/2026 · {len(keys)} pares voiced/silent · features Gaddy-pooled 81d · Ridge→TF-IDF/SVD128 · retrieval entre frases do teste · {time.time()-t0:.0f}s*', '',
         '| condição | n (pool) | top-1 | top-10 | MRR | acaso top-1 | acaso top-10 |', '|---|---|---|---|---|---|---|']
for k,v in res.items():
    if 'top1' in v: lines.append(f"| {k} | {v['n']} | {v['top1']*100:.1f}% | {v['top10']*100:.1f}% | {v['mrr']:.3f} | {100/v['n']:.2f}% | {min(100,1000/v['n']):.1f}% |")
    else: lines.append(f"| {k} | — | — | top10 nulo médio {v['top10_mean']*100:.1f}% (p95 {v['top10_p95']*100:.1f}%) | — | — | **p = {v['p_valor_top10']:.3f}** |")
lines += ['', '## Teste pareado: falado-professor (C) vs mudo-professor (E), mesmos itens de teste',
          f"- n = {pareado['n']} · top-10: {100*hc.mean():.1f}% vs {100*he.mean():.1f}% → **{pareado['d10']:+.1f} pp, IC95 [{pareado['ci10'][0]:+.1f}, {pareado['ci10'][1]:+.1f}], P(dif ≤ 0) = {pareado['p10']:.3f}** (bootstrap pareado ×5000)",
          f"- MRR: dif {pareado['dmrr']:+.4f}, IC95 [{pareado['cimrr'][0]:+.4f}, {pareado['cimrr'][1]:+.4f}], P = {pareado['pmrr']:.3f} · mediana do rank {pareado['medC']:.0f} vs {pareado['medE']:.0f} (acaso ≈ {np.mean([len(te) for _,te in folds])/2:.0f})"]
lines += ['', '## Leitura', '- **C** é a pergunta do projeto: treinar só em FALADO e ler SILENCIOSO em frases nunca vistas. Se C ≫ nulo, o professor falado transfere no sEMG.',
          '- **E vs C** = duelo de professores para alvo silencioso (mudo-professor vs falado-professor). **F** = professor misto.',
          '- **D** = teto do método (dentro do modo). **A** = robustez a sessão nova (reposicionamento).',
          '- Limite honesto: features com pooling temporal (bag-of-features) — mede informação de conteúdo, não transcrição; é um teste de TRANSFER, não SOTA.']
open(OUT,'w').write('\n'.join(lines)); print('\n'.join(lines))
