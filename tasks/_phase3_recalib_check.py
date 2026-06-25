"""Phase 3 minimal-honest-fix の検証（DEC-014）。

3つを確認する:
1. G-3 は既に解消済 — io cache を δ=0.55 で force 再生成し、現 cache と完全一致
   (diff=0) かつ koyck≠empirical を確認。
2. β-invariance — io 出力の delta を k 倍しても政策 gap_reduction_pct は不変
   (gap_pp は k 倍)。政策削減率は β に依存しない。
3. overshoot と新数値 — coherent δ=0.55・β=0.431 の baseline cost-push 平均が
   実績CPI総合(~2.5%)を ~2倍 overshoot すること、新しい削減率(エネ44.7%等)を表示。

結論(DEC-014): Phase 3 は定性・例示に降格。特定%・pp 絶対値は結論にしない。
真に頑健なのは符号レベル(Q1>Q5・energy 最大寄与・補助は方向として gap 縮小)。
"""
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
SIM = PROC / "simulation-params"
IO = SIM / "io_price_model_output.csv"


def check_g3():
    old = pd.read_csv(IO).sort_values(["year", "cpi_code"]).reset_index(drop=True)
    from src.analysis.import_content import compute_sector_import_content
    compute_sector_import_content()  # ensure sector IC exists (B-4 corrected)
    from src.analysis.io_price_model import run_io_price_model_all_years
    new = run_io_price_model_all_years(koyck=True, delta=0.55, force=True)
    new = new.sort_values(["year", "cpi_code"]).reset_index(drop=True)
    for c in ["delta_cpi_empirical_pp", "delta_cpi_koyck_pp"]:
        d = (old[c].values - new[c].values)
        print(f"  G-3: {c} cache-vs-fresh(δ=0.55) max|diff|={abs(d).max():.6f}")
    gd = (new["delta_cpi_koyck_pp"] - new["delta_cpi_empirical_pp"]).abs()
    print(f"  G-3: koyck≠empirical max|diff|={gd.max():.3f} (>0 = δ properly applied; G-3 already fixed)")


def check_beta_invariance():
    from src.analysis.policy_simulation import run_all_scenarios, make_policy_comparison_table
    bak = SIM / "_io_bak.csv"
    shutil.copy(IO, bak)

    def reductions(k):
        df = pd.read_csv(bak)
        for c in ["delta_cpi_koyck_pp", "delta_cpi_empirical_pp", "delta_cpi_leontief_pp"]:
            if c in df.columns:
                df[c] = df[c] * k
        df.to_csv(IO, index=False)
        res = run_all_scenarios(years=[2022], force=True)
        t = make_policy_comparison_table(res, year=2022)
        return t[["scenario", "q1_q5_gap_pp", "gap_reduction_pct"]].set_index("scenario")

    try:
        t1, t2 = reductions(1.0), reductions(2.3)
        print("  β-invariance: gap_pp ratio (k2.3/k1.0):",
              dict((t2.q1_q5_gap_pp / t1.q1_q5_gap_pp).round(2)))
        print("  β-invariance: gap_reduction_pct diff (k2.3-k1.0):",
              dict((t2.gap_reduction_pct - t1.gap_reduction_pct).round(4)),
              "(~0 => ratio is β-invariant)")
    finally:
        shutil.move(bak, IO)


def show_overshoot_and_numbers():
    from src.analysis.policy_simulation import run_all_scenarios, make_policy_comparison_table
    res = run_all_scenarios(years=[2021, 2022, 2023, 2024], force=True)
    base = res[res.scenario == "baseline"]
    g = base[base.quintile == 1].set_index("year")["q1_q5_gap_pp"]
    print("  baseline cost-push Q1-Q5 gap (pp, δ=0.55, β=0.431, model-dependent):")
    print("   ", dict(g.round(3)))
    q = base[base.year == 2022][["quintile_label", "effective_inflation_pp"]]
    avg = base[(base.year == 2022) & (base.quintile == 0)]["effective_inflation_pp"].values[0]
    print(f"  2022 baseline cost-push avg = {avg:.2f}pp vs actual total CPI ~2.5% => OVERSHOOT (C-4)")
    t = make_policy_comparison_table(res, year=2022)
    print("  2022 policy gap_reduction_pct (β-invariant but IC/Leontief-dependent, NOT headline):")
    print("   ", dict(t.set_index("scenario").gap_reduction_pct.round(1)))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    print("=== 1. G-3 (already resolved) ===")
    check_g3()
    print("=== 2. β-invariance of policy reduction ratio ===")
    check_beta_invariance()
    print("=== 3. overshoot + new (demoted, illustrative) numbers ===")
    show_overshoot_and_numbers()
    print("\nVerdict (DEC-014): Phase 3 demoted to qualitative/illustrative.")
    print("  Robust (sign-level only): Q1>Q5, energy largest contributor, subsidies reduce gap directionally.")
