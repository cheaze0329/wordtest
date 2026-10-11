import random
import tkinter as tk
from tkinter import messagebox, Label
import pandas as pd
import requests
import io

class VocabularyTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("英単語テストアプリ")
        self.root.geometry("1920x1080")  # ウィンドウサイズを1920x1080に設定
        
        # 変数の初期化
        self.vocabulary_list = []
        self.current_question = 0
        self.correct_answers = 0
        self.wrong_questions = []
        self.questions_per_test = 10
        self.used_words = []  # 使用済み単語を記録
        
        # スプレッドシートURL（修正版）
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Mtf3qBEXXpU9qn3O1EPXHBoEkHc1khDY8nWLkjijTl0/edit?gid=0#gid=0"
        
        # メイン画面の設定
        self.setup_main_screen()

    def setup_main_screen(self):
        """メイン画面のUI設定"""
        # メインフレーム
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, pady=50)
        
        # タイトルラベル
        self.title_label = tk.Label(main_frame, text="英単語テストアプリ", font=("Helvetica", 24, "bold"))
        self.title_label.pack(pady=30)
        
        # スプレッドシートURL表示フレーム
        url_frame = tk.Frame(main_frame)
        url_frame.pack(pady=20, fill="x")
        
        url_label = tk.Label(url_frame, text="スプレッドシートURL (CSV形式で公開):", font=("Helvetica", 12))
        url_label.pack(anchor="w", pady=5)
        
        # URLフレーム（URLテキストとコピーボタンを横に並べる）
        url_display_frame = tk.Frame(url_frame)
        url_display_frame.pack(fill="x", pady=5)
        
        # URLをテキストとして表示するだけ
        url_text = tk.Label(url_display_frame, text=self.spreadsheet_url, 
                          font=("Helvetica", 10), fg="blue", bg="#f0f0f0",
                          relief="ridge", padx=10, pady=5, anchor="w")
        url_text.pack(side=tk.LEFT, fill="x", expand=True)
        
        # コピーボタン
        copy_button = tk.Button(url_display_frame, text="URLをコピー", 
                              command=self.copy_url_to_clipboard,
                              font=("Helvetica", 10), bg="#e0e0e0", padx=10)
        copy_button.pack(side=tk.RIGHT, padx=5)
        
        # 注意事項を表示
        info_frame = tk.Frame(main_frame)
        info_frame.pack(pady=20)
        
        info_label = tk.Label(info_frame, text="【重要】スプレッドシートの設定方法:", 
                             font=("Helvetica", 12, "bold"), fg="red")
        info_label.pack()
        
        instructions = [
            "1. Google スプレッドシートで「ファイル」→「共有」→「ウェブに公開」を選択",
            "2. 「リンク」タブで「CSV」形式を選択",
            "3. 「公開」ボタンをクリック",
            "4. 列名は必ず「英語」と「日本語」にしてください"
        ]
        
        for instruction in instructions:
            inst_label = tk.Label(info_frame, text=instruction, font=("Helvetica", 10))
            inst_label.pack(anchor="w")
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=30)
        
        # データ更新ボタン
        self.refresh_button = tk.Button(button_frame, text="データを読み込む", command=self.load_data_from_sheet, 
                                       width=20, height=2, font=("Helvetica", 12))
        self.refresh_button.pack(pady=10)
        
        # スタートボタン
        self.start_button = tk.Button(button_frame, text="テスト開始", command=self.start_test, 
                                     width=20, height=2, font=("Helvetica", 14, "bold"), bg="#4CAF50", fg="white")
        self.start_button.pack(pady=20)
        
        # 終了ボタン
        self.quit_button = tk.Button(button_frame, text="終了", command=self.root.quit, 
                                    width=20, height=1, font=("Helvetica", 12))
        self.quit_button.pack(pady=10)
        
        # 状態表示ラベル
        self.status_label = tk.Label(main_frame, text="スプレッドシートからデータを読み込んでください", font=("Helvetica", 12))
        self.status_label.pack(pady=20)
        
        # 最初にデータを読み込む
        self.load_data_from_sheet()

    def copy_url_to_clipboard(self):
        """URLをクリップボードにコピーする"""
        self.root.clipboard_clear()  # クリップボードをクリア
        self.root.clipboard_append(self.spreadsheet_url)  # URLをクリップボードに追加
        
        # フィードバックを表示
        self.status_label.config(text="URLをクリップボードにコピーしました")
        
        # 一時的に表示を変更し、2秒後に元に戻す
        def reset_status():
            if hasattr(self, 'vocabulary_list') and len(self.vocabulary_list) > 0:
                self.status_label.config(text=f"{len(self.vocabulary_list)}個の単語を読み込みました。準備完了！")
            else:
                self.status_label.config(text="スプレッドシートからデータを読み込んでください")
        
        # 2秒後に状態表示を元に戻す
        self.root.after(2000, reset_status)

    def extract_sheet_id(self, url):
        """スプレッドシートURLからシートIDを抽出する"""
        try:
            # 複数のURL形式に対応
            if '/d/' in url:
                sheet_id = url.split('/d/')[1].split('/')[0]
                return sheet_id
            else:
                raise ValueError("無効なGoogle SpreadsheetsのURL形式です")
        except Exception as e:
            raise ValueError(f"URLの解析に失敗しました: {str(e)}")

    def load_data_from_sheet(self):
        """公開されたGoogle Spreadsheetからデータを読み込む"""
        try:
            # ステータス更新
            self.status_label.config(text="データを読み込み中...")
            self.root.update()
            
            # スプレッドシートIDを抽出
            sheet_id = self.extract_sheet_id(self.spreadsheet_url)
            
            # 複数の URL 形式を試行
            urls_to_try = [
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0"
            ]
            
            data_loaded = False
            last_error = None
            
            for export_url in urls_to_try:
                try:
                    print(f"Trying URL: {export_url}")  # デバッグ用
                    
                    # リクエストヘッダーを設定
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    # スプレッドシートのURLからCSVデータを取得
                    response = requests.get(export_url, headers=headers, timeout=10)
                    response.raise_for_status()  # エラーがあれば例外を発生させる
                    
                    # エンコーディングを自動検出
                    response.encoding = response.apparent_encoding or 'utf-8'
                    
                    # CSVデータをDataFrameに読み込む
                    df = pd.read_csv(io.StringIO(response.text))
                    
                    print(f"DataFrame columns: {df.columns.tolist()}")  # デバッグ用
                    print(f"DataFrame shape: {df.shape}")  # デバッグ用
                    
                    # 列名を確認して処理
                    if '英語' in df.columns and '日本語' in df.columns:
                        self.vocabulary_list = []
                        for _, row in df.iterrows():
                            english = str(row['英語']).strip()
                            japanese = str(row['日本語']).strip()
                            
                            # 空の行をスキップ
                            if english and japanese and english != 'nan' and japanese != 'nan':
                                self.vocabulary_list.append({"english": english, "japanese": japanese})
                        
                        data_loaded = True
                        break
                    else:
                        # 列名が見つからない場合、最初の2列を使用
                        if len(df.columns) >= 2:
                            self.vocabulary_list = []
                            col1, col2 = df.columns[0], df.columns[1]
                            
                            for _, row in df.iterrows():
                                english = str(row[col1]).strip()
                                japanese = str(row[col2]).strip()
                                
                                # 空の行をスキップ
                                if english and japanese and english != 'nan' and japanese != 'nan':
                                    self.vocabulary_list.append({"english": english, "japanese": japanese})
                            
                            data_loaded = True
                            messagebox.showwarning("警告", f"列名「英語」「日本語」が見つかりません。\n最初の2列（{col1}, {col2}）を使用します。")
                            break
                        else:
                            raise ValueError("スプレッドシートに十分な列がありません")
                            
                except requests.exceptions.RequestException as e:
                    last_error = f"ネットワークエラー: {str(e)}"
                    continue
                except pd.errors.EmptyDataError:
                    last_error = "スプレッドシートが空です"
                    continue
                except Exception as e:
                    last_error = f"データ処理エラー: {str(e)}"
                    continue
            
            if not data_loaded:
                raise Exception(last_error or "すべてのURL形式で読み込みに失敗しました")
            
            # データの検証
            if len(self.vocabulary_list) == 0:
                raise ValueError("有効なデータが見つかりませんでした")
            
            if len(self.vocabulary_list) < self.questions_per_test:
                messagebox.showwarning("警告", f"スプレッドシートには少なくとも{self.questions_per_test}個の単語が必要です。\n現在: {len(self.vocabulary_list)}個\nサンプルデータを追加します。")
                self.add_sample_data()
            else:
                self.status_label.config(text=f"{len(self.vocabulary_list)}個の単語を読み込みました。準備完了！")
                messagebox.showinfo("成功", f"{len(self.vocabulary_list)}個の単語を読み込みました。")
            
        except Exception as e:
            error_message = str(e)
            self.status_label.config(text="エラー: データの読み込みに失敗しました")
            messagebox.showerror("エラー", f"スプレッドシートからのデータ読み込みに失敗しました。\n\n詳細: {error_message}\n\n対処法:\n1. スプレッドシートが「ウェブに公開」されているか確認\n2. 列名が「英語」「日本語」になっているか確認\n3. インターネット接続を確認")
            self.add_sample_data()

    def add_sample_data(self):
        """サンプルデータを追加する"""
        sample_data = [
            {"english": "apple", "japanese": "りんご"},
            {"english": "book", "japanese": "本"},
            {"english": "cat", "japanese": "猫"},
            {"english": "dog", "japanese": "犬"},
            {"english": "elephant", "japanese": "象"},
            {"english": "flower", "japanese": "花"},
            {"english": "guitar", "japanese": "ギター"},
            {"english": "house", "japanese": "家"},
            {"english": "island", "japanese": "島"},
            {"english": "juice", "japanese": "ジュース"},
            {"english": "king", "japanese": "王様"},
            {"english": "lion", "japanese": "ライオン"}
        ]
        
        # 既存のデータにサンプルデータを追加
        self.vocabulary_list.extend(sample_data)
        
        # 重複を除去
        seen = set()
        unique_list = []
        for item in self.vocabulary_list:
            key = (item['english'].lower(), item['japanese'])
            if key not in seen:
                seen.add(key)
                unique_list.append(item)
        
        self.vocabulary_list = unique_list
        self.status_label.config(text=f"サンプルデータを使用します ({len(self.vocabulary_list)}個の単語)")
        messagebox.showinfo("情報", f"サンプルデータを追加しました。合計{len(self.vocabulary_list)}個の単語でテストを実行できます。")

    def start_test(self):
        """テストを開始する"""
        # 前回のテスト結果をリセット
        self.current_question = 0
        self.correct_answers = 0
        self.wrong_questions = []
        self.used_words = []  # 使用済み単語をリセット
        
        # 単語が足りるか確認
        if len(self.vocabulary_list) < self.questions_per_test:
            messagebox.showwarning("警告", f"単語が足りません。少なくとも{self.questions_per_test}個の単語が必要です。")
            return
        
        # メインスクリーンをクリア
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # テスト画面を表示
        self.show_question()

    def show_question(self):
        """問題を表示する"""
        if self.current_question < self.questions_per_test:
            # 使用していない単語からランダムに選択
            available_words = [word for word in self.vocabulary_list if word not in self.used_words]
            
            # 利用可能な単語がなくなったら全てリセット
            if not available_words:
                self.used_words = []
                available_words = self.vocabulary_list
            
            # 問題の英単語を選択
            question_word = random.choice(available_words)
            self.used_words.append(question_word)  # 使用済みとしてマーク
            
            correct_japanese = question_word["japanese"]
            english_word = question_word["english"]
            
            # 他の3つの選択肢（不正解）をランダムに選ぶ
            other_words = [w for w in self.vocabulary_list if w != question_word]
            if len(other_words) >= 3:
                other_choices = random.sample(other_words, 3)
                choices = [correct_japanese] + [word["japanese"] for word in other_choices]
                random.shuffle(choices)
            else:
                # 単語が足りない場合はダミーデータを使用
                dummy_choices = ["選択肢A", "選択肢B", "選択肢C"]
                choices = [correct_japanese] + dummy_choices
                random.shuffle(choices)
            
            # メインフレーム
            question_frame = tk.Frame(self.root)
            question_frame.pack(expand=True, pady=50)
            
            # 現在の問題番号を表示
            question_number = tk.Label(question_frame, text=f"問題 {self.current_question + 1}/{self.questions_per_test}", 
                                     font=("Helvetica", 16))
            question_number.pack(pady=20)
            
            # 問題の英単語を表示
            question_label = tk.Label(question_frame, text=english_word, font=("Helvetica", 36, "bold"))
            question_label.pack(pady=30)
            
            instruction_label = tk.Label(question_frame, text="この英単語の日本語訳として正しいものを選んでください：", 
                                       font=("Helvetica", 14))
            instruction_label.pack(pady=20)
            
            # 選択肢ボタンのフレーム
            buttons_frame = tk.Frame(question_frame)
            buttons_frame.pack(pady=30)
            
            # 選択肢ボタンを表示（2x2のグリッドレイアウト）
            for i, choice in enumerate(choices):
                row, col = divmod(i, 2)
                choice_button = tk.Button(buttons_frame, text=choice, width=30, height=3,
                                       font=("Helvetica", 14),
                                       command=lambda c=choice: self.check_answer(c, correct_japanese, english_word))
                choice_button.grid(row=row, column=col, padx=15, pady=15)
        else:
            # 全問題が終了したら結果を表示
            self.show_results()

    def check_answer(self, selected_choice, correct_answer, english_word):
        """答えをチェックする"""
        # 画面をクリア（選択肢ボタンを無効化するためにクリア）
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 即時フィードバックを表示するフレーム
        feedback_frame = tk.Frame(self.root)
        feedback_frame.pack(expand=True, fill='both', pady=100)
        
        # 英単語を再表示
        word_label = tk.Label(feedback_frame, text=english_word, font=("Helvetica", 36, "bold"))
        word_label.pack(pady=30)
        
        # 正解か不正解かのフィードバック表示
        is_correct = selected_choice == correct_answer
        
        if is_correct:
            self.correct_answers += 1
            result_text = "正解！"
            result_color = "green"
        else:
            self.wrong_questions.append({
                "english": english_word,
                "correct": correct_answer,
                "selected": selected_choice
            })
            result_text = "不正解"
            result_color = "red"
        
        # フィードバックラベル
        feedback_label = tk.Label(feedback_frame, text=result_text, font=("Helvetica", 48, "bold"), fg=result_color)
        feedback_label.pack(pady=30)
        
        # 正解の表示
        answer_label = tk.Label(feedback_frame, text=f"正解: {correct_answer}", font=("Helvetica", 24))
        answer_label.pack(pady=10)
        
        # あなたの選択
        if not is_correct:
            your_answer_label = tk.Label(feedback_frame, text=f"あなたの回答: {selected_choice}", font=("Helvetica", 24))
            your_answer_label.pack(pady=10)
        
        # 次の問題へ進むボタン
        self.current_question += 1
        next_button = tk.Button(feedback_frame, text="次へ", width=20, height=2, 
                              font=("Helvetica", 16), bg="#2196F3", fg="white",
                              command=self.next_question)
        next_button.pack(pady=30)

    def next_question(self):
        """次の問題に進む"""
        # 画面をクリア
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 次の問題を表示
        self.show_question()

    def show_results(self):
        """テスト結果を表示する"""
        # 画面をクリア
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 結果表示フレーム
        result_frame = tk.Frame(self.root)
        result_frame.pack(expand=True, pady=50)
        
        # 結果タイトル
        result_title = tk.Label(result_frame, text="テスト結果", font=("Helvetica", 32, "bold"))
        result_title.pack(pady=30)
        
        # 正答率を表示
        score_percentage = (self.correct_answers / self.questions_per_test) * 100
        score_label = tk.Label(result_frame, text=f"正答率: {score_percentage:.1f}%（{self.correct_answers}/{self.questions_per_test}）",
                             font=("Helvetica", 24))
        score_label.pack(pady=20)
        
        # 間違えた問題のリスト
        if self.wrong_questions:
            wrong_title = tk.Label(result_frame, text="間違えた問題:", font=("Helvetica", 20, "bold"))
            wrong_title.pack(pady=20)
            
            # スクロール可能なフレーム
            wrong_frame = tk.Frame(result_frame, width=800, height=400)
            wrong_frame.pack(fill="both", padx=50, pady=20)
            
            # 間違えた問題を表示
            for i, q in enumerate(self.wrong_questions):
                wrong_q = tk.Label(wrong_frame, text=f"{i+1}. {q['english']} - 正解: {q['correct']}（あなたの回答: {q['selected']}）", 
                                 font=("Helvetica", 16), anchor="w", justify="left")
                wrong_q.pack(fill="x", pady=5)
        else:
            perfect_label = tk.Label(result_frame, text="全問正解おめでとうございます！", font=("Helvetica", 24), fg="green")
            perfect_label.pack(pady=30)
        
        # メイン画面に戻るボタン
        back_button = tk.Button(result_frame, text="メイン画面に戻る", command=self.return_to_main, 
                              width=25, height=2, font=("Helvetica", 16), bg="#4CAF50", fg="white")
        back_button.pack(pady=30)

    def return_to_main(self):
        """メイン画面に戻る"""
        # 画面をクリア
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # メインスクリーンを再設定
        self.setup_main_screen()

# メインアプリケーションの実行
if __name__ == "__main__":
    root = tk.Tk()
    app = VocabularyTestApp(root)
    root.mainloop()