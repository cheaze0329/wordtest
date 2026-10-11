# 英単語テストアプリ

Google スプレッドシートに登録した英単語を使って、4択形式の英単語テストができる Tkinter 製のデスクトップアプリです。

## 主な機能

- Google スプレッドシートから単語データ（英語・日本語）を読み込み
- 1回10問、英単語に対する日本語訳を4択から選択
- 回答ごとに正解／不正解を即時表示
- テスト終了後に正答率と間違えた問題の一覧を表示
- 読み込みに失敗した場合や単語が10個未満の場合はサンプルデータで補完

## 必要環境

- Python 3.x（Tkinter 同梱のもの）
- pandas
- requests

```
pip install pandas requests
```

`python check.py` でライブラリが入っているか確認できます。

## 使い方

```
python your_package/python_vocabulary_test_app.py
```

1. 起動すると自動でスプレッドシートからデータを読み込みます
2. 「テスト開始」で10問のテストが始まります
3. 結果画面から「メイン画面に戻る」で再挑戦できます

## スプレッドシートの準備

1. Google スプレッドシートで「ファイル」→「共有」→「ウェブに公開」を選択
2. 「リンク」タブで「CSV」形式を選択して「公開」
3. 1行目の列名を「英語」「日本語」にする（見つからない場合は先頭2列を使用）

読み込むスプレッドシートの URL は `python_vocabulary_test_app.py` 内の `self.spreadsheet_url` で変更できます。

## exe のビルド

PyInstaller 用の spec ファイルを同梱しています。

```
cd your_package
pyinstaller python_vocabulary_test_app.spec
```

`your_package/dist/` に exe が生成されます。
