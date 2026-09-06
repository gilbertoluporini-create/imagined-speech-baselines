# RESULTADO — professor-gabarito no Gaddy (sEMG 8ch)
*05/09/2026 · 1588 pares voiced/silent · features Gaddy-pooled 81d · Ridge→TF-IDF/SVD128 · retrieval entre frases do teste · 2s*

| condição | n (pool) | top-1 | top-10 | MRR | acaso top-1 | acaso top-10 |
|---|---|---|---|---|---|---|
| A voiced? não: silent→silent LOSO (sessão nova) | 226 | 0.5% | 4.7% | 0.027 | 0.44% | 4.4% |
| B voiced→silent, MESMAS frases (pool 1589) | 1588 | 0.1% | 0.6% | 0.005 | 0.06% | 0.6% |
| B nulo (perm) | 1588 | 0.1% | 0.6% | 0.005 | 0.06% | 0.6% |
| C voiced→silent, frases INÉDITAS (5-fold) | 317 | 0.3% | 3.1% | 0.020 | 0.32% | 3.2% |
| C nulo (perm ×100) | — | — | top10 nulo médio 3.1% (p95 3.2%) | — | — | **p = 0.660** |
| D voiced→voiced, inéditas | 317 | 0.3% | 3.2% | 0.020 | 0.32% | 3.2% |
| E silent→silent, inéditas | 317 | 0.3% | 3.2% | 0.020 | 0.32% | 3.2% |
| F voiced+silent→silent, inéditas | 317 | 0.3% | 3.2% | 0.020 | 0.32% | 3.2% |

## Teste pareado: falado-professor (C) vs mudo-professor (E), mesmos itens de teste
- n = 1588 · top-10: 3.1% vs 3.2% → **-0.1 pp, IC95 [-0.2, +0.0], P(dif ≤ 0) = 1.000** (bootstrap pareado ×5000)
- MRR: dif +0.0001, IC95 [-0.0001, +0.0004], P = 0.179 · mediana do rank 155 vs 157 (acaso ≈ 159)

## Leitura
- **C** é a pergunta do projeto: treinar só em FALADO e ler SILENCIOSO em frases nunca vistas. Se C ≫ nulo, o professor falado transfere no sEMG.
- **E vs C** = duelo de professores para alvo silencioso (mudo-professor vs falado-professor). **F** = professor misto.
- **D** = teto do método (dentro do modo). **A** = robustez a sessão nova (reposicionamento).
- Limite honesto: features com pooling temporal (bag-of-features) — mede informação de conteúdo, não transcrição; é um teste de TRANSFER, não SOTA.