## American Express Default Prediction 
目的：binary<br>
データ：テーブル＋時系列(10程度)

### 気づき
* !! 環境またぐなら絶対constantsだけファイル分けといたほうが楽
    * jsonより普通に.pyでimportしたほうが楽じゃね？
* featherでメモリkillされるケースで、pickleだと通る場合がある
    * 特にto_feather, to_pickleのとき
        * こだわりないなら巨大なcsvは一旦pickleで持ち直したほうが試行錯誤が捗りそう
        * そのときに無害なfloat64を消しとくほうが良いと思う --
* Canceled future executionは大体メモリkilled

### 【EDA】
#### notebook(1)
* Target(0/1)の分布：CVの戦略、不均衡でStratified-KFoldを選択
* Target(0/1)ごとに説明変数の分布 
    * => legend分けてKDE(orヒストグラム、sns.distplotを使うと多分楽)
* 説明変数同士の相関 
    * => 相関係数行列、散布図はサンプルが多すぎる場合潰れてしまうのでhexbinを使う
* 説明変数とTargetの相関
    * => 普通に棒グラフとか
* 説明変数の欠損の量


#### notebook(2)
* 生データの時点でmemory-usageを確認しておく
    * float32, float16への変換
    * pickle < feather < parquetの順に「ファイルサイズが大きいが、読み込みが早い」

#### raddar_01
* そもそもデータがお金なら離散じゃない？
    * => 匿名化の段階でノイズ挿入されてる

#### raddar_02
* 小数で序数ということもある
* そういうのはintに直しといたほうがメモリとわかりやすさの観点でよさそう
    * => ヒストグラムをズームしないと気づかない気もする
    * => その観点でplotlyは便利かもしれない

#### raddar_03
* 「ランク学習」とは？

#### raddar_04
* 欠損値の対応を考える際、欠損値の発生パターンを見ると良い場合がある
    * 欠損が同時に発生してる列の組