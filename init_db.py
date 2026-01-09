# Git用のコメント
import sqlite3

# データベースファイルに接続（存在しなければ作成される）
conn = sqlite3.connect('diary.db')
cursor = conn.cursor()

# テーブルを作成
cursor.execute('''
    CREATE TABLE IF NOT EXISTS diaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
''')

# 変更を保存
conn.commit()

# 接続を閉じる
conn.close()

print("データベースの初期化が完了しました！")