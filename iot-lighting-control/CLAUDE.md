# IoT照明制御プロジェクト

## プロジェクト概要
Raspberry Pi 3と赤外線LEDを使用して照明を制御するプロジェクト

## 環境
- **ターゲット**: Raspberry Pi 3 (aarch64)
- **OS**: Debian 13 (trixie)
- **Python**: 3.13.5
- **SSH接続**: `ssh raspi`

## ハードウェア部品
| 部品 | 型番 | 用途 |
|------|------|------|
| 赤外線LED 940nm | OSI5FU5111C-40 | 赤外線送信 |
| 赤外線受信モジュール | OSRB38C9AA | リモコン信号学習 |
| NPNトランジスタ | 2SC1815-Y | LEDドライバ |

## ディレクトリ構成
```
iot-lighting-control/
├── src/       # Pythonソースコード
├── config/    # 赤外線信号データ、設定ファイル
├── docs/      # 回路図、ドキュメント
└── scripts/   # セットアップ・ユーティリティスクリプト
```

## 開発ルール
- ラズパイ上で動作するコードは `src/` に配置
- 赤外線信号のデータは `config/` にJSON形式で保存
- ラズパイへのデプロイは `rsync` または `scp` を使用

## SSH経由のコマンド実行
```bash
# ラズパイでコマンドを実行
ssh raspi "コマンド"

# ファイルをラズパイに転送
scp -r src/ raspi:~/iot-lighting-control/
```

## 使用予定ライブラリ
- pigpio: GPIO制御、赤外線送受信
- RPi.GPIO: GPIO基本制御（代替）
