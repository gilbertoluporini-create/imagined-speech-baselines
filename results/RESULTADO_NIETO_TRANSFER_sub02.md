# RESULTADO — professor-gabarito em EEG (Nieto sub-02, 4 palavras, acaso 25%)
*05/09/2026, revisado 07/09/2026 · 600 trials · janela 0.5–3.0 s pós-cue (amostras 1.0–3.5 s da época, tmin = -0.5 s) · log-bandpower θαβγ · logreg · leave-one-session-out · p = (r+1)/(N+1)*
*Trials por sessão: ses-01: pron 40 inner 80 vis 80 · ses-02: pron 40 inner 80 vis 80 · ses-03: pron 40 inner 80 vis 80*

## 128 canais
| condição | acurácia | acaso |
|---|---|---|
| I inner→inner (LOSO) | **26.7%** | 25% |
| P pron→pron (LOSO) | **30.8%** | 25% |
| T PRON→INNER (transfer, LOSO) | **25.4%** | 25% |
| M pron+inner→inner (LOSO) | **23.7%** | 25% |
| nulo T (perm ×100) | média 25.3% · p95 29.2% | **p = 0.505** |
| nulo I (perm ×100) | média 25.1% · p95 29.2% | **p = 0.277** |

## 14 canais ≈ nossa coroa
| condição | acurácia | acaso |
|---|---|---|
| I inner→inner (LOSO) | **23.3%** | 25% |
| P pron→pron (LOSO) | **27.5%** | 25% |
| T PRON→INNER (transfer, LOSO) | **23.8%** | 25% |
| M pron+inner→inner (LOSO) | **25.0%** | 25% |
| nulo T (perm ×100) | média 25.0% · p95 27.9% | **p = 0.762** |
| nulo I (perm ×100) | média 25.1% · p95 29.2% | **p = 0.772** |

## Leitura
- **T** é a pergunta do projeto: pronunciado ensina o imaginado em EEG? Compare com o nulo T.
- **I** = teto do imaginado dentro do modo (sessão nova). **M** = professor misto. **P** = sanidade.
- Limite: 4 classes, 1 sujeito por rodada, features de banda (sem dinâmica temporal); LOSO exige generalizar entre SESSÕES (as 3 sessões do ds003626 foram no MESMO dia, consecutivas; Nieto et al. 2022, Methods).

## Dentro da sessão (mesmo dia)
*inner→inner: 5-fold estratificado (média ± dp sobre 20 sementes de dobras; a semente 0 é a publicada em 05/09) e 5 blocos CONTÍGUOS por ordem de trial (sem semente). Nulo: 1000 permutações dos rótulos de treino, p = (r+1)/(1000+1). Treino por dobra ≈ 64 trials, teste 16 (20 inner por classe por sessão).*

| montagem | inner→inner 5-fold (média ± dp, seeds) | semente 0 | nulo p95 · **p** (semente 0) | inner→inner 5 blocos contíguos | nulo p95 · **p** | pron→inner (mesma sessão) |
|---|---|---|---|---|---|---|
| 128 canais | **32.3 ± 1.9%** (min 28.7, máx 35.4) | 30.8% | p95 29.6% · **p = 0.0240** | **32.9%** | p95 28.3% · **p = 0.0030** | 23.3% |
| 14 canais ≈ nossa coroa | **32.4 ± 2.2%** (min 27.9, máx 38.8) | 34.2% | p95 30.0% · **p = 0.0010** | **31.2%** | p95 27.9% · **p = 0.0060** | 24.2% |

- A semente 0 (publicada em 05/09 como 34,2 % no subconjunto) é UMA amostra da distribuição de dobras; a média entre sementes é a estimativa honesta. O esquema por blocos contíguos evita a semente e o embaralhamento.
- "Dentro da sessão" aqui = 80 trials de inner por sessão (20 por classe), treino ≈ 64 / teste 16 por dobra. Não são "~200 trials por condição": 200 é o total de inner do sub-01 somando as 3 sessões (240 no sub-02).