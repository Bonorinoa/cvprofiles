# 11 — Glossary

| Term | Definition |
|---|---|
| **Construct $C$** | Latent concept the researcher wants to measure (e.g. policy uncertainty). |
| **Measure $m_j$** | One operationalization; a score column mapping units → $\mathbb{R}$. |
| **Menu $M$** | Finite set of candidate measures. |
| **Nomological network $R$** | Researcher-stated restrictions that valid measures of $C$ should satisfy. |
| **$\theta$** | Threshold vector anchoring restriction strength. |
| **Slack $s_r(m)$** | Sample analogue of restriction $r$ at measure $m$; $\ge 0$ = satisfied. |
| **Admissible set $M^*$** | Measures that clear all restrictions. |
| **Target $\beta(\cdot)$** | Downstream functional of a measure (e.g. OLS coefficient on outcome). |
| **Construct-identified set $B^*$** | $\{\beta(m): m \in M^*\}$. |
| **Range $[L,U]$** | Reported bounds on $B^*$ (with inference layer). |
| **SCORE / RESTRICT / IDENTIFY / REPORT** | Four engine states; see architecture doc. |
| **Unit** | Row of the score matrix (firm-year, article, person, …). |
| **Bootstrap over units** | Resample rows; menu $M$ stays fixed. |
| **False admission** | Invalid measure enters $M^*$ (synthetic oracle metric). |
| **Coverage** | True $\beta^*$ lies in reported $[L,U]$ (synthetic oracle metric). |
| **Empty-set rate** | Fraction of runs with $M^*=\emptyset$. |
| **Point-ID rate** | Fraction of runs with $|M^*|=1$ (or $|B^*|$ degenerate under tolerance). |
| **Run freeze** | Hashed `(scores, network, beta, seed, version)` bundle for reproducibility. |
| **Score-agnostic** | Engine does not care how columns were produced. |
| **Model-free (engine)** | No trained model or LLM call inside states 0–3. |
| **Composite measure** | Scalar formed upstream by aggregating items/scores; recipe is researcher-owned (see `14_Researcher_Input_Guide`). |
| **Criterion posture (P1)** | One measure is the standard; others judged by recovery of / agreement with it. |
| **Peer posture (P2)** | Menu members face a common external network; no sacred measure. |
| **Eval anchor** | Designated valid measure in synthetic gates (e.g. `m_dict` for H1a/H1b); not an empirical truth claim. |
