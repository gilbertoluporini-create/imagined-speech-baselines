# RESULTADO — professor-gabarito em EEG (Nieto sub-02, 4 palavras, acaso 25%)
*05/09/2026 · 600 trials · janela 1.0-3.5 s · log-bandpower θαβγ · logreg · leave-one-session-out*

## 128 canais
| condição | acurácia | acaso |
|---|---|---|
| I inner→inner (LOSO) | **26.7%** | 25% |
| P pron→pron (LOSO) | **30.8%** | 25% |
| T PRON→INNER (transfer, LOSO) | **25.4%** | 25% |
| M pron+inner→inner (LOSO) | **23.7%** | 25% |
| nulo T (perm) | média 25.3% · p95 29.2% | **p = 0.500** |
| nulo I (perm) | média 25.1% · p95 29.2% | **p = 0.270** |

## 16 canais ≈ nossa coroa
| condição | acurácia | acaso |
|---|---|---|
| I inner→inner (LOSO) | **23.3%** | 25% |
| P pron→pron (LOSO) | **27.5%** | 25% |
| T PRON→INNER (transfer, LOSO) | **23.8%** | 25% |
| M pron+inner→inner (LOSO) | **25.0%** | 25% |
| nulo T (perm) | média 25.0% · p95 27.9% | **p = 0.760** |
| nulo I (perm) | média 25.1% · p95 29.2% | **p = 0.770** |

## Leitura
- **T** é a pergunta do projeto: pronunciado ensina o imaginado em EEG? Compare com o nulo T.
- **I** = teto do imaginado dentro do modo (sessão nova). **M** = professor misto. **P** = sanidade.
- Limite: 4 classes, 1 sujeito por rodada, features de banda (sem dinâmica temporal); LOSO exige generalizar entre DIAS.
## Dentro da sessão (mesmo dia)
| montagem | inner→inner 5-fold | nulo p95 · p | pron→inner (mesmo dia) |
|---|---|---|---|
| 128 canais | **30.8%** | p95 28.3% · p = 0.040 | 23.3% |
| 16 canais ≈ nossa coroa | **34.2%** | p95 28.7% · p = 0.000 | 24.2% |