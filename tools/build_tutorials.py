"""Build the two Phase-3 tutorial notebooks (nbformat 4.5, clean, no outputs).

A: cvprofiles_irt_scoring_tutorial.ipynb — IRT-as-scoring, the SCORE-upstream
   pattern: hand-rolled 1PL (Rasch) item fit turns binary item responses into
   scalar person scores, which become cvprofiles measure columns.
B: cvprofiles_sensemakr_tutorial.ipynb — sensemakr-on-survivors: run a profile,
   take a survivor's OLS coefficient, apply a hand-rolled Cinelli-Hazlett OVB
   bound (bias formula + robustness value) with numpy only.

Both notebooks run against the installed package only (pip install cvprofiles):
everything is generated inline, no repo files, deterministic seeds, and they
finish with self-checking assertions.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "tutorials"

KERNEL = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
LANG = {"name": "python", "version": "3.11"}


def cell(kind: str, src: str, i: int) -> dict:
    lines = [ln + "\n" for ln in src.split("\n")]
    c = {
        "cell_type": kind,
        "metadata": {},
        "source": lines,
        "id": f"cell-{i}",
    }
    if kind == "code":
        c["execution_count"] = None
        c["outputs"] = []
    return c


def nb(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {"kernelspec": KERNEL, "language_info": LANG},
        "nbformat": 4,
        "nbformat_minor": 5,
    }


IRT = [
    cell("markdown", """# cvprofiles — IRT as a SCORE-upstream scoring technology

The engine is **score-agnostic**: any scalar column per unit can be a candidate measure,
however it was built. Item response theory (IRT) is one principled scoring technology that
lives *upstream* of the engine — it turns binary item responses into scalar person scores
$\\hat\\theta_i$, one number per unit, which then become cvprofiles measure columns.

This notebook shows the full loop with a **hand-rolled 1PL (Rasch) fit** — no IRT package,
just numpy + scipy, so the scoring step is auditable:
1. simulate a latent trait and binary item responses;
2. fit a 1PL model to recover person scores;
3. feed those scores (plus a naive sum-score and a noisy measure) into a cvprofiles profile;
4. see which operationalizations survive the researcher-authored network.

Scientific stance: the engine never scores — *you* decide how to fill score columns. IRT is
one defensible choice; the nomological network then disciplines it like any other measure.
""", 0),
    cell("code", """from __future__ import annotations
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.optimize as opt
import yaml

import cvprofiles
from cvprofiles.pipeline import run_profile

print("cvprofiles", cvprofiles.__version__)
""", 1),
    cell("markdown", """## 1. Simulate a latent trait and 1PL item responses

A 1PL (Rasch) model: person $i$ has latent score $\\theta_i$; item $j$ has difficulty $b_j$;
the probability of a correct/endorsed response is

$$P(x_{ij}=1 \\mid \\theta_i, b_j) = \\mathrm{logit}(\\theta_i - b_j).$$

We generate $n=300$ persons, $J=30$ items, and a latent trait that also drives an external
auxiliary (so the network has something to anchor on).
""", 2),
    cell("code", """rng = np.random.default_rng(20260806)
n, J = 300, 30

# latent trait and an external auxiliary that co-moves with it
theta = rng.normal(size=n)
v_aux = 0.8 * theta + 0.6 * rng.normal(size=n)

# item difficulties spread across the trait range
b = np.linspace(-1.5, 1.5, J)

# 1PL responses
logit = theta[:, None] - b[None, :]
p = 1.0 / (1.0 + np.exp(-logit))
X = (rng.random((n, J)) < p).astype(float)

print("response matrix:", X.shape, "mean endorsement:", round(float(X.mean()), 3))
""", 3),
    cell("markdown", """## 2. Hand-rolled 1PL fit (joint ML)

We maximize the joint log-likelihood over $\\theta_i$ and $b_j$ (recentering $\\theta$ for the
standard identifiability convention). Initialization matters: item difficulties start from
empirical endorsement rates, person scores from the sum-score logit. The fitted
$\\hat\\theta_i$ is our **IRT measure column**. A naive **sum score** (fraction endorsed) is
the classic model-free alternative, and a noisy "LLM-ish" score gives the menu a weak member.
""", 4),
    cell("code", """def fit_1pl(X, max_iter=1000, tol=1e-7):
    n, J = X.shape
    # empirical-difficulty init: b0 = -logit(endorsement); theta from sum-score logit
    end = np.clip(X.mean(axis=0), 1e-3, 1 - 1e-3)
    b0 = -np.log(end / (1 - end))
    z = np.log((X.mean(axis=1) + 1e-3) / (1 - X.mean(axis=1) + 1e-3))
    z = (z - z.mean()) / z.std() * 1.5

    def unpack(params):
        return params[:n], params[n:]

    def neg_ll(params):
        th, bj = unpack(params)
        m = th[:, None] - bj[None, :]
        lse = np.maximum(m, 0) + np.log1p(np.exp(-np.abs(m)))
        return float(np.sum(lse) - np.sum(X * m))

    x0 = np.concatenate([z, b0])
    res = opt.minimize(neg_ll, x0, method="L-BFGS-B",
                       options={"maxiter": max_iter, "gtol": tol})
    th, bj = unpack(res.x)
    th = th - th.mean()
    bj = bj + th.mean()  # keep logit(theta - b) invariant
    return th, bj, res

theta_irt, b_fit, res = fit_1pl(X)
sum_score = X.mean(axis=1)                                   # naive operationalization
noisy = 0.3 * theta + 1.0 * rng.normal(size=n)               # weak, noisy measure

print("fit converged:", res.success)
print("corr(theta_true, theta_irt):", round(float(np.corrcoef(theta, theta_irt)[0, 1]), 3))
print("corr(theta_true, sum_score):", round(float(np.corrcoef(theta, sum_score)[0, 1]), 3))
""", 5),
    cell("markdown", """## 3. Build the cvprofiles inputs

The fitted scores are just columns. The researcher-authored network says: *a valid measure of
this trait must correlate at least $\\theta=0.35$ with the external auxiliary, in the stated
positive direction.* The target is the correlation of each measure with the outcome $y$.
""", 6),
    cell("code", """work = Path(tempfile.mkdtemp(prefix="cvp_irt_"))

y = 0.5 * theta + rng.normal(size=n)  # outcome depends on the trait

scores = pd.DataFrame({
    "unit_id": [f"u{i:04d}" for i in range(n)],
    "m_irt": theta_irt,
    "m_sum": sum_score,
    "m_noisy": noisy,
    "v_aux": v_aux,
    "y": y,
})
scores.to_csv(work / "scores.csv", index=False)

roles = {
    "unit_id": "unit_id",
    "measures": ["m_irt", "m_sum", "m_noisy"],
    "aux": ["v_aux"],
    "outcome": "y",
    "diagnostic": [],
}
(work / "roles.json").write_text(json.dumps(roles))

network = {
    "schema_version": "1",
    "name": "irt_oracle",
    "delta": 0.0,
    "restrictions": [
        {"id": "r_corr_min_aux", "type": "corr_min", "theta": 0.35,
         "params": {"variable": "v_aux"}},
        {"id": "r_corr_sign_aux", "type": "corr_sign", "theta": 0.0,
         "params": {"variable": "v_aux", "sign": 1}},
    ],
}
(work / "network.yaml").write_text(yaml.safe_dump(network, sort_keys=False))

beta = {"schema_version": "1", "type": "corr_y", "outcome": "y", "params": {}}
(work / "beta.yaml").write_text(yaml.safe_dump(beta, sort_keys=False))

print("inputs written to", work)
""", 7),
    cell("code", """result = run_profile(
    scores=work / "scores.csv",
    roles=work / "roles.json",
    network=work / "network.yaml",
    beta=work / "beta.yaml",
    out_dir=work / "run",
    seed=0,
    title="IRT-as-scoring profile",
)

print("run_id :", result.run_id)
print("M*     :", result.identify.admissible)
print("[L,U]  :", result.identify.range_L, result.identify.range_U)
print("rejected:", result.identify.rejected)
""", 8),
    cell("markdown", """## 4. Read the profile

The **IRT score and the sum score both survive** the network: they co-move with the external
auxiliary strongly enough. The **noisy measure is rejected** — it fails the minimum
association bar. The headline range $[L,U]$ is the image of the target functional on the
survivors only; the noisy measure never enters it.

Notice what the network *did not* do: it did not judge IRT versus sum-score on intrinsic
grounds. It disciplined both through the same external implications. The honest comparison in
this DGP is that the two scoring technologies recover the latent trait similarly; IRT adds
item-level difficulty calibration and a latent metric, while the sum score is model-free and
trivially auditable. The menu, the network, and the thresholds are yours — the engine treats
any scalar column the same way.
""", 9),
    cell("code", """# self-checking assertions
assert set(result.identify.admissible) == {"m_irt", "m_sum"}
assert "m_noisy" in result.identify.rejected
assert result.identify.range_L is not None and result.identify.range_L <= result.identify.range_U
assert result.identify.empty is False
print("all IRT tutorial assertions passed")
""", 10),
    cell("markdown", """## What to look at next

- The run directory holds the full audit trail: `report.html`, `report.json`, slacks,
  admissible set, range — the same artifacts as any other profile.
- IRT is one upstream scorer. Dictionary scores, LLM scores, PCA factors all slot in the same
  way: scalar columns in, disciplined by the network.
- The engine remains score-agnostic and model-free. Scoring, the menu, and the nomological
  network are researcher-owned.
""", 11),
]

SENSEMAKR = [
    cell("markdown", """# cvprofiles — OVB sensitivity on a surviving measure (sensemakr-style)

cvprofiles answers: *which operationalizations are admissible, and what range of the target
functional follows?* It does **not** answer a different, downstream question: *for one fixed
measure's regression coefficient, how much unobserved confounding would overturn it?*

That is the omitted-variable-bias (OVB) sensitivity question of Cinelli and Hazlett (2020),
popularized in the `sensemakr` R package. This notebook runs a cvprofiles profile, takes a
survivor's OLS coefficient, and applies a **hand-rolled** Cinelli–Hazlett bound — bias
formula plus robustness value — using numpy only, so every step is auditable.
""", 0),
    cell("code", """from __future__ import annotations
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import cvprofiles
from cvprofiles.pipeline import run_profile

print("cvprofiles", cvprofiles.__version__)
""", 1),
    cell("markdown", """## 1. A DGP with an unobserved confounder

A candidate measure $m$ predicts outcome $y$, but an **unobserved** confounder $u$ affects
both. A naive regression of $y$ on $m$ (with observed control $w$) is therefore biased; the
bias is exactly what the CH framework quantifies.

$$y = \\tau m + \\gamma_w w + \\gamma_u u + \\varepsilon, \\qquad m = \\alpha_w w + \\alpha_u u + \\eta.$$

We also add a *slop* measure that fails the network, so the profile has a rejection story.
""", 2),
    cell("code", """rng = np.random.default_rng(20260806)
n = 500

u = rng.normal(size=n)            # unobserved confounder
w = rng.normal(size=n)            # observed control

# measure driven by observed control + confounder
m_good = 0.7 * w + 0.8 * u + rng.normal(size=n)
m_slop = 0.9 * rng.normal(size=n)  # unrelated noise -> should fail the network

tau, gw, gu = 0.6, 0.4, 0.7
y = tau * m_good + gw * w + gu * u + rng.normal(size=n)

# external auxiliary for the network: co-moves with the construct-bearing measure
v_aux = 0.6 * m_good + rng.normal(size=n)

print("corr(m_good, y):", round(float(np.corrcoef(m_good, y)[0, 1]), 3))
""", 3),
    cell("code", """def ols_coef(X, y):
    \"\"\"Numpy OLS coefficients with intercept; returns beta, residual sd.\"\"\"
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    sd = float(np.sqrt(np.mean(resid**2) * len(y) / max(len(y) - A.shape[1], 1)))
    return beta, sd

def partial_r2(y, D, X):
    \"\"\"Partial R2 of D with y given X (and intercept).\"\"\"
    Xa = np.column_stack([np.ones(len(y)), X])
    _, sd_restricted = ols_coef(Xa[:, 1:], y)
    A = np.column_stack([Xa, D])
    _, sd_full = ols_coef(A[:, 1:], y)
    rss_restricted = sd_restricted**2 * (len(y) - Xa.shape[1])
    rss_full = sd_full**2 * (len(y) - A.shape[1])
    return float((rss_restricted - rss_full) / rss_restricted)

def ch_bias(r2_y_z, r2_d_z, sd_y, sd_d):
    \"\"\"Cinelli-Hazlett |bias| from partial R2s and residual sds.\"\"\"
    return float(np.sqrt(r2_y_z * r2_d_z / (1 - r2_d_z)) * sd_y / sd_d)

def rv_q(tstat, df, q=1.0):
    \"\"\"Robustness value for a q-fraction reduction of the estimate (CH 2020).\"\"\"
    fq = q * abs(tstat) / np.sqrt(df)
    return float(0.5 * (np.sqrt(fq**4 + 4 * fq**2) - fq**2))
""", 4),
    cell("markdown", """## 2. Run the cvprofiles profile

The network requires a valid measure to correlate at least $\\theta=0.3$ with the external
auxiliary. The target is the standardized OLS coefficient of $y$ on each measure, controlling
for $w$.
""", 5),
    cell("code", """work = Path(tempfile.mkdtemp(prefix="cvp_sm_"))

scores = pd.DataFrame({
    "unit_id": [f"u{i:04d}" for i in range(n)],
    "m_good": m_good,
    "m_slop": m_slop,
    "v_aux": v_aux,
    "w": w,
    "y": y,
})
scores.to_csv(work / "scores.csv", index=False)

roles = {
    "unit_id": "unit_id",
    "measures": ["m_good", "m_slop"],
    "aux": ["v_aux", "w"],
    "outcome": "y",
    "diagnostic": [],
}
(work / "roles.json").write_text(json.dumps(roles))

network = {
    "schema_version": "1",
    "name": "ovb_oracle",
    "delta": 0.0,
    "restrictions": [
        {"id": "r_corr_min_aux", "type": "corr_min", "theta": 0.3,
         "params": {"variable": "v_aux"}},
    ],
}
(work / "network.yaml").write_text(yaml.safe_dump(network, sort_keys=False))

beta = {
    "schema_version": "1",
    "type": "ols_coef",
    "outcome": "y",
    "params": {"controls": ["w"]},
}
(work / "beta.yaml").write_text(yaml.safe_dump(beta, sort_keys=False))

result = run_profile(
    scores=work / "scores.csv",
    roles=work / "roles.json",
    network=work / "network.yaml",
    beta=work / "beta.yaml",
    out_dir=work / "run",
    seed=0,
    title="OVB sensitivity on survivors",
)

print("M*    :", result.identify.admissible)
print("beta  :", {m: round(float(v), 3) for m, v in result.identify.beta_values.items()})
print("[L,U] :", result.identify.range_L, result.identify.range_U)
""", 6),
    cell("markdown", """## 3. OVB sensitivity on the survivor

The profile admits `m_good`; its **standardized** OLS coefficient (controlling for `w`) is the
estimate we care about. We now ask the CH question: *how strong would an unobserved confounder
$u^*$ need to be — in partial-$R^2$ units — to move this estimate by $q$ of its value?*

First, reproduce the *known* confounder case: because we simulated $u$, we can compute its
true partial $R^2$s and confirm the OVB identity recovers the true coefficient. Then report
the robustness value for a hypothetical confounder. Everything below uses z-scored variables,
so the numbers line up with the profile's standardized $\\beta$.
""", 7),
    cell("code", """def z(v):
    return (v - v.mean()) / v.std()

mz, wz, uz, yz = z(m_good), z(w), z(u), z(y)

# survivor regression: y ~ m_good + w  (restricted; u omitted), standardized
m_hat, sd_y_mw = ols_coef(np.column_stack([mz, wz]), yz)
beta_res = float(m_hat[1])

# treatment regression: m_good ~ w (standardized)
m_hat_d, sd_d_w = ols_coef(wz[:, None], mz)

# true partial R2s of the omitted u
r2_y_u = partial_r2(yz, uz, np.column_stack([mz, wz]))
r2_d_u = partial_r2(mz, uz, wz)

# EXACT OVB identity: bias = gamma_hat * delta_hat (impact x imbalance).
# gamma: coefficient on u in y ~ m_good + w + u (impact on outcome).
# delta: coefficient on m_good in u ~ m_good + w (imbalance: how the
#        omitted confounder predicts the treatment, given controls).
full_y, _ = ols_coef(np.column_stack([mz, wz, uz]), yz)
gamma_hat = float(full_y[3])
aux_u, _ = ols_coef(np.column_stack([mz, wz]), uz)
delta_hat = float(aux_u[1])
bias_ovb = gamma_hat * delta_hat
adj_exact = beta_res - bias_ovb
tau_true = float(full_y[1])

# CH partial-R2 reparameterization (same bias, expressed in R2 units)
bias_ch = ch_bias(r2_y_u, r2_d_u, sd_y_mw, sd_d_w)

print("profile beta (std) :", round(float(result.identify.beta_values["m_good"]), 3))
print("restricted beta    :", round(beta_res, 3))
print("bias (gamma*delta) :", round(bias_ovb, 3))
print("CH |bias| (R2)     :", round(bias_ch, 3))
print("adjusted beta      :", round(adj_exact, 3))
print("true tau (full)    :", round(tau_true, 3))
print("exact recovery     :", round(abs(adj_exact - tau_true), 10) < 1e-8)
print("CH approx matches  :", round(abs(bias_ch - abs(bias_ovb)), 3) < 0.01)
""", 8),
    cell("code", """# Robustness value for a hypothetical confounder: q = 1 means "to zero".
# t-stat of the restricted treatment coefficient
se_beta = None
A = np.column_stack([np.ones(n), m_good, w])
beta_all, *_ = np.linalg.lstsq(A, y, rcond=None)
resid = y - A @ beta_all
sigma2 = float(resid @ resid / (n - A.shape[1]))
cov = np.linalg.inv(A.T @ A) * sigma2
se_beta = float(np.sqrt(cov[1, 1]))
tstat = beta_res / se_beta
df = n - A.shape[1]

rv1 = rv_q(tstat, df, q=1.0)
print("survivor t-stat:", round(tstat, 2), "| df:", df)
print("RV (q=1)       :", round(rv1, 3),
      "=> a confounder explaining", round(rv1 * 100, 1),
      "% of residual variance of BOTH treatment and outcome would zero the estimate")
""", 9),
    cell("markdown", """## 4. What OVB adds — and what it does not

- **It adds:** a quantitative, auditable statement about a *fixed* survivor's coefficient.
  The exact OVB identity decomposes the bias into the confounder's impact ($\\gamma$) times its
  imbalance ($\\delta$); the Cinelli–Hazlett reparameterization expresses the same bias in
  partial-$R^2$ units, and the robustness value summarizes how strong omitted confounding must
  be to overturn the estimate — exactly the `sensemakr` quantities.
- **It does not:** decide which measures are admissible. That is the nomological network's
  job, and it is done *before* this analysis. The slop measure is already excluded by the
  profile; we never run OVB sensitivity on it as if it were a live estimate.
- **Boundary:** this is sensitivity analysis for a regression coefficient, not causal
  identification of a structural effect, and not a substitute for the measurement layer.
""", 10),
    cell("code", """# self-checking assertions
assert set(result.identify.admissible) == {"m_good"}
assert "m_slop" in result.identify.rejected
assert abs(adj_exact - tau_true) < 1e-8          # exact OVB identity recovers full-model tau
assert abs(bias_ch - abs(bias_ovb)) < 0.01       # CH partial-R2 reparameterization matches
assert 0 < rv1 < 1                               # RV is a fraction
assert result.identify.range_L is not None
print("all sensemakr tutorial assertions passed")
""", 11),
    cell("markdown", """## What to look at next

- The hand-rolled functions here are the `sensemakr` core in ~30 lines: partial $R^2$, the CH
  bias formula, and the robustness value. For contour plots and benchmarking against observed
  covariates, the R/Stata package or a Python port adds convenience, not new math.
- cvprofiles disciplines *which* measure; OVB sensitivity disciplines *one fixed* estimate.
  They are complementary, not competing.
""", 12),
]


def main() -> None:
    for name, cells_list in [
        ("cvprofiles_irt_scoring_tutorial.ipynb", IRT),
        ("cvprofiles_sensemakr_tutorial.ipynb", SENSEMAKR),
    ]:
        out = OUT_DIR / name
        out.write_text(json.dumps(nb(cells_list), indent=1) + "\n")
        print(f"wrote {out} ({len(cells_list)} cells)")


if __name__ == "__main__":
    main()
