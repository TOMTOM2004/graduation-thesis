"""A-4 Step2-3: group-specific shift-share（実験ブランチ・非保持）。

Step2: IC_{c,g} = Σ_i B(c,i) · (μ_g^T L^d)_i   （μ_g = μ をグループg セクターに制限）
Step3: ΔCPI_{c,t} = Σ_g β_g (IC_{c,g}×(P_{g,t}−100)) + γ_t + δ_c + ε
       joint 5群 + 群別単変量で「どの群が識別を駆動するか」を見る。
出力: IC_{c,g} と group-specific panel を CSV（step4 の AKM SE 用）。
"""
import numpy as np
import pandas as pd
from src.utils.io_utils import load_io_table, compute_input_coefficients
from src.analysis.import_content import SECTOR_GROUP_MAP, GROUPS
from src.analysis.bridge_matrix_mid import build_bridge_matrix_mid, CPI_MID_CATEGORY_MAP
from src.analysis.cost_push_panel import build_panel_dataset

# --- Step2: IC_{c,g} ---
io = load_io_table(); A = compute_input_coefficients(io)
x = io["output"]; imp = io["imports"].abs()
mu = (imp/(x+imp).replace(0,np.inf)).fillna(0.0)
n = A.shape[0]
L_d = np.linalg.inv(np.eye(n) - (np.eye(n)-np.diag(mu.values))@A.values)
codes = io["sector_codes"]

# 群別 sector import content: ic_g[j] = (μ_g^T L^d)_j  （Series indexed by codes）
sector_ic_g = {}
for g in GROUPS:
    mu_g = pd.Series([mu[c] if SECTOR_GROUP_MAP.get(c)==g else 0.0 for c in codes], index=codes)
    sector_ic_g[g] = pd.Series(np.clip(mu_g.values @ L_d, 0, 1), index=codes)

bridge = build_bridge_matrix_mid()
rows=[]
for cat_name, cat in CPI_MID_CATEGORY_MAP.items():
    w = bridge.loc[cat_name]  # Series indexed by sectors
    rec = {"cpi_mid_name":cat_name, "group":cat["group"], "is_competitive_import":cat.get("is_competitive_import",False)}
    for g in GROUPS:
        rec[f"ic_{g}"] = float((w * sector_ic_g[g]).sum())  # index-aligned（既存 compute_mid と同方式）
    rec["ic_total"] = sum(rec[f"ic_{g}"] for g in GROUPS)
    rows.append(rec)
icg = pd.DataFrame(rows)
print("=== Step2: IC_{c,g} 検証 ===")
print(f"Σ_g IC_cg の範囲: {icg['ic_total'].min():.3f}〜{icg['ic_total'].max():.3f}（≤1 かつ食料/光熱は当該群heavyか）")
for c in ["穀類","外食","電気代","ガス代","他の光熱","被服(和服)"]:
    r = icg[icg.cpi_mid_name==c]
    if len(r):
        r=r.iloc[0]
        dom = max(GROUPS, key=lambda g: r[f"ic_{g}"])
        print(f"  {c:8s}: " + " ".join(f"{g[:3]}={r[f'ic_{g}']:.2f}" for g in GROUPS) + f"  → 支配={dom}")

# --- Step3: group-specific panel + 回帰 ---
panel = build_panel_dataset()  # delta_cpi, year, cpi_mid_name, is_competitive_import
ap = pd.read_csv("data/processed/trade-loss/annual_price_index.csv")
pg = ap.pivot(index="year", columns="group", values="price_index")
m = panel.merge(icg.drop(columns=["group","is_competitive_import"]), on="cpi_mid_name", how="left")
for g in GROUPS:
    m[f"ss_{g}"] = m[f"ic_{g}"] * (m["year"].map(pg[g]) - 100.0)

# メイン仕様: 競争的輸入財除外・2021-2024
sub = m[(~m["is_competitive_import"]) & (m["year"].between(2021,2024))].dropna(subset=[f"ss_{g}" for g in GROUPS]+["delta_cpi"])
sub.to_csv("data/processed/price-indices/panel_groupspec.csv", index=False)
icg.to_csv("data/processed/import-content/mid_category_ic_by_group.csv", index=False)

from linearmodels import PanelOLS
ps = sub.set_index(["cpi_mid_name","year"])

# ゼロ分散の群（消費カテゴリに当該群の IC 変動が無い）を除外
valid_g = [g for g in GROUPS if ps[f"ss_{g}"].std() > 1e-9]
dropped = [g for g in GROUPS if g not in valid_g]
print(f"\n（識別変動のある群: {valid_g} / 除外〔変動なし〕: {dropped}）")

print("=== Step3a: joint 群別回帰（two-way FE, cluster-entity SE）===")
res = PanelOLS(ps["delta_cpi"], ps[[f"ss_{g}" for g in valid_g]], entity_effects=True, time_effects=True, drop_absorbed=True, check_rank=False).fit(cov_type="clustered", cluster_entity=True)
for g in valid_g:
    v=f"ss_{g}"
    if v in res.params.index:
        print(f"  β_{g:9s}={res.params[v]:+.3f}  SE={res.std_errors[v]:.3f}  p={res.pvalues[v]:.3f}")
    else:
        print(f"  β_{g:9s}= (absorbed/dropped)")
print(f"  R²_within={res.rsquared_within:.3f}  N={res.nobs}")

print("\n=== Step3b: 群別単変量（どの群が単独で識別を持つか）===")
for g in valid_g:
    try:
        r1 = PanelOLS(ps["delta_cpi"], ps[[f"ss_{g}"]], entity_effects=True, time_effects=True, drop_absorbed=True, check_rank=False).fit(cov_type="clustered", cluster_entity=True)
        v=f"ss_{g}"
        print(f"  {g:9s}: β={r1.params[v]:+.3f} SE={r1.std_errors[v]:.3f} p={r1.pvalues[v]:.3f} R²w={r1.rsquared_within:.3f}")
    except Exception as e:
        print(f"  {g:9s}: 推定不可 ({type(e).__name__})")
