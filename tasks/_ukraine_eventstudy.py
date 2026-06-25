"""ウクライナ小麦ショックの event-study（DEC-015 の existence-proof leg・最終 decider）。

advisor steer: pre-trend の傾きだけで殺さない。treatment(小麦)の pre 期間は flat、
問題は control(米)の oversupply 下落。よって米を主軸にせず、**小麦自身の flat
pre-trend に乗る ITS/event-study**で pre 期間 lead 係数を読む。

事前コミットしたルール（結果を見る前に固定）:
- KEEP(narrow LATE 有効): 小麦の pre 期間 lead が flat(無トレンド) かつ 2022-02 に鋭い break
- DEAD(bounds へ pivot): pre 期間 lead が trend している

データ: data/raw/cpi/cpi_items_ukraine_2019_2023.csv（品目別CPI 2020-01..2023-12）。
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

WHEAT = ['食パン', 'あんパン', 'ゆでうどん', 'スパゲッティ', '中華麺', '小麦粉',
         '調理パン', '調理パスタ', 'ビスケット', 'ケーキ', 'まんじゅう']
RICE = ['うるち米A', 'うるち米B', 'もち']
PART = ['豆腐', '鶏卵', '牛乳']
EVENT = '2022-02'  # ウクライナ侵攻


def load_long():
    piv = pd.read_csv('data/raw/cpi/cpi_items_ukraine_2019_2023.csv', index_col=0)
    piv.index = pd.PeriodIndex(piv.index, freq='M')
    long = piv.stack().rename('cpi').reset_index()
    long.columns = ['ym', 'item', 'cpi']
    long['lncpi'] = np.log(long['cpi'])
    long['moy'] = long['ym'].dt.month
    long['ym_str'] = long['ym'].astype(str)
    t0 = pd.Period(EVENT, freq='M')
    long['k'] = (long['ym'] - t0).apply(lambda x: x.n)  # event-time in months (0 = 2022-02)
    long['post'] = (long['k'] >= 0).astype(int)
    long['group'] = np.where(long['item'].isin(WHEAT), 'wheat',
                      np.where(long['item'].isin(RICE), 'rice', 'part'))
    return long


def its_wheat(long):
    """ITS on wheat items: pre-trend slope + break. month-of-year FE for seasonality."""
    d = long[long.group == 'wheat'].copy()
    d['trend'] = d['k']  # months since event (negative pre)
    d['trend_post'] = d['trend'] * d['post']
    m = smf.ols('lncpi ~ trend + post + trend_post + C(item) + C(moy)', data=d).fit(
        cov_type='cluster', cov_kwds={'groups': d['ym'].astype(str)})
    pre = m.params['trend']; pre_p = m.pvalues['trend']
    brk = m.params['post']; brk_p = m.pvalues['post']
    dpost = m.params['trend_post']; dpost_p = m.pvalues['trend_post']
    print("=== ITS（小麦・自身のpre-trendに乗る）item+月FE, time-cluster SE ===")
    print(f"  pre-trend 傾き(/月) = {pre*100:+.3f}%pt  p={pre_p:.3f}  ← KEEP条件: flat(p>0.1 or |傾き|小)")
    print(f"  2022-02 level break = {brk*100:+.2f}%  p={brk_p:.3f}")
    print(f"  post 傾き変化(/月)   = {dpost*100:+.3f}%pt p={dpost_p:.3f}")
    return pre, pre_p


def event_study(long, group_treat='wheat'):
    """Wheat-only event-study: event-time half-year bins vs 直前pre, item + 月-of-year FE.
    米は pre-trend 汚染ありのため control に使わず、小麦自身の pre 期間を counterfactual にする。"""
    d = long[long.group == group_treat].copy()
    def bink(k):
        if k < -18: return '1_pre4'
        if k < -12: return '2_pre3'
        if k < -6: return '3_pre2'
        if k < 0: return '4_pre1'   # reference（直前pre）
        if k < 6: return '5_p1'
        if k < 12: return '6_p2'
        if k < 18: return '7_p3'
        return '8_p4'
    d['kb'] = d['k'].apply(bink)
    m = smf.ols('lncpi ~ C(item) + C(moy) + C(kb, Treatment(reference="4_pre1"))', data=d).fit(
        cov_type='cluster', cov_kwds={'groups': d['ym_str']})
    print(f"\n=== 小麦のみ event-study（ref=直前pre[-6..-1mo]・item+月ofyear FE, time-cluster SE）===")
    print("  event-bin 係数（pre が0近傍＝小麦自身に pre-trend なし→KEEP）:")
    for name, val in m.params.items():
        if 'kb' in name:
            tag = name.split('T.')[-1].rstrip(']')
            print(f"    {tag:8s}: {val*100:+6.2f}%  p={m.pvalues[name]:.3f}")


if __name__ == '__main__':
    long = load_long()
    pre, pre_p = its_wheat(long)
    event_study(long, 'wheat')
    print("\n--- 参考: 部分被治療(豆腐/卵/牛乳)も大幅上昇＝cost-push が食料全般に広い(記述的finding) ---")
    print("--- 事前ルール適用: 小麦 pre-trend が flat か(↑ITS)で KEEP/DEAD を機械判定 ---")
