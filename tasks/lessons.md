# Lessons

プロジェクト固有の再発防止パターンを記録する。意図した test-first の失敗は記録対象外とする。

## 分析結果CSVの複合キー

- Error: IC variant だけで結果行を選ぶと、複数の回帰仕様が一致して係数を一意に読めなかった。
- Cause: 出力表の一意キーが `ic_variant × specification` なのに、読み手が前者だけをキーとみなした。
- Fix: 分析結果の読み込みでは生成側の複合キーをすべて指定し、競合するvariant・specを含むfixtureで一意性をテストする。
