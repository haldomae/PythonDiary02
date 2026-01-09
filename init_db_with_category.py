import sqlite3

# データベースに接続
conn = sqlite3.connect('diary.db')
cursor = conn.cursor()

# diariesテーブルを作成（既存のテーブルがない場合）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS diaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
''')

# カテゴリテーブルを作成
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
''')

# diariesテーブルにcategory_idカラムを追加
# （既存のテーブルがある場合のため、エラーを無視）
try:
    cursor.execute('''
        ALTER TABLE diaries 
        ADD COLUMN category_id INTEGER
    ''')
    print("diariesテーブルにcategory_idカラムを追加しました")
except sqlite3.OperationalError:
    print("category_idカラムは既に存在します")

# 初期カテゴリデータを投入
initial_categories = [
    ('仕事',),
    ('プライベート',),
    ('旅行',),
    ('学習',),
    ('その他',)
]

# 既存のカテゴリがあるかチェック
cursor.execute('SELECT COUNT(*) FROM categories')
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany('''
        INSERT INTO categories (name) VALUES (?)
    ''', initial_categories)
    print("初期カテゴリを追加しました")
else:
    print("カテゴリは既に存在します")

# 変更を保存
conn.commit()
conn.close()

print("データベースの拡張が完了しました！")