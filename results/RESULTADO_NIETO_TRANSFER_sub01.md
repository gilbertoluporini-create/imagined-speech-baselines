# RESULTADO — professor-gabarito em EEG (Nieto sub-01, 4 palavras, acaso 25%)
*05/09/2026 · 500 trials · janela 1.0-3.5 s · log-bandpower θαβγ · logreg · leave-one-session-out*

## 128 canais
| condição | acurácia | acaso |
|---|---|---|
| I inner→inner (LOSO) | **27.5%** | 25% |
| P pron→pron (LOSO) | **31.7%** | 25% |
| T PRON→INNER (transfer, LOSO) | **29.2%** | 25% |
| M pron+inner→inner (LOSO) | **23.3%** | 25% |
| nulo T (perm) | média 24.5% · p95 28.7% | **p = 0.030** |
| nulo I (perm) | média 24.8% · p95 29.2% | **p = 0.200** |

## 14 canais ≈ nossa coroa
| condição | acurácia | acaso |
|---|---|---|
| I inner→inner (LOSO) | **25.4%** | 25% |
| P pron→pron (LOSO) | **33.3%** | 25% |
| T PRON→INNER (transfer, LOSO) | **27.5%** | 25% |
| M pron+inner→inner (LOSO) | **24.6%** | 25% |
| nulo T (perm) | média 24.7% · p95 28.4% | **p = 0.140** |
| nulo I (perm) | média 24.9% · p95 29.2% | **p = 0.440** |

## Leitura
- **T** é a pergunta do projeto: pronunciado ensina o imaginado em EEG? Compare com o nulo T.
- **I** = teto do imaginado dentro do modo (sessão nova). **M** = professor misto. **P** = sanidade.
- Limite: 4 classes, 1 sujeito por rodada, features de banda (sem dinâmica temporal); LOSO exige generalizar entre SESSÕES (as 3 sessões do ds003626 foram no MESMO dia, consecutivas; Nieto et al. 2022, Methods).
## Dentro da sessão (mesmo dia)
| montagem | inner→inner 5-fold | nulo p95 · p | pron→inner (mesmo dia) |
|---|---|---|---|
| 128 canais | **23.3%** | p95 30.0% · p = 0.720 | 26.7% |
| 14 canais ≈ nossa coroa | **23.8%** | p95 30.6% · p = 0.620 | 26.7% |