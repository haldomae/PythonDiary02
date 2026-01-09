# Git用のコメント
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# データベース接続用の関数
def get_db_connection():
    conn = sqlite3.connect('diary.db')
    conn.row_factory = sqlite3.Row  # 辞書のようにアクセスできる
    return conn

@app.template_filter('format_date')
def format_date(date_string):
    dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%Y年%m月%d日 %H:%M')

@app.route('/')
def index():
    # 検索パラメータを取得
    keyword = request.args.get('keyword', '')
    year_month = request.args.get('year_month', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 基本のSQL - JOINでカテゴリ名も取得
    sql = '''
        SELECT diaries.*, categories.name as category_name
        FROM diaries
        LEFT JOIN categories ON diaries.category_id = categories.id
        WHERE 1=1
    '''
    params = []

    # キーワード検索
    if keyword:
        sql += ' AND (diaries.title LIKE ? OR diaries.content LIKE ?)'
        search_word = f'%{keyword}%'
        params.extend([search_word, search_word])

    # 年月絞り込み
    if year_month:
        sql += ' AND diaries.created_at LIKE ?'
        params.append(f'{year_month}%')

    # 並び替え
    sql += ' ORDER BY diaries.created_at DESC'

    cursor.execute(sql, params)
    diaries = cursor.fetchall()
    conn.close()

    # カテゴリ一覧も取得
    categories = get_categories()

    return render_template('index.html',
                         diaries=diaries,
                         categories=categories,
                         keyword=keyword,
                         year_month=year_month)


@app.route('/add', methods=['POST'])
def add_diary():
    # フォームからデータを取得
    title = request.form['title']
    content = request.form['content']
    # カテゴリーを取得
    category_id = request.form.get('category_id')
    # 現在の日時を取得
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # カテゴリーなしの場合は空文字になる
    # 空文字の場合はNoneにする
    if category_id == '':
        category_id = None

    # データベースに保存
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO diaries (title, content, category_id, created_at)
        VALUES (?, ?, ?, ?)
    ''', (title, content, category_id, created_at))
    
    conn.commit()
    conn.close()
    
    # トップページにリダイレクト
    return redirect(url_for('index'))

@app.route('/detail/<int:diary_id>')
def detail(diary_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # JOINでカテゴリ情報も取得
    cursor.execute('''
        SELECT diaries.*, categories.name as category_name
        FROM diaries
        LEFT JOIN categories ON diaries.category_id = categories.id
        WHERE diaries.id = ?
    ''', (diary_id,))
    
    diary = cursor.fetchone()
    conn.close()
    
    return render_template('detail.html', diary=diary)

@app.route('/edit/<int:diary_id>')
def edit(diary_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM diaries WHERE id = ?', (diary_id,))
    diary = cursor.fetchone()
    conn.close()

    # カテゴリー一覧も取得
    categories = get_categories()

    return render_template('edit.html', diary=diary, categories=categories)


@app.route('/update/<int:diary_id>', methods=['POST'])
def update(diary_id):
    title = request.form['title']
    content = request.form['content']
    # カテゴリーを取得
    category_id = request.form.get('category_id')

    # カテゴリーなしの場合は空白にする
    if category_id == '':
        category_id = None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE diaries
        SET title = ?, content = ?, category_id = ?
        WHERE id = ?
    ''', (title, content, category_id, diary_id))
    conn.commit()
    conn.close()

    return redirect(url_for('detail', diary_id=diary_id))



def get_categories():
    """全カテゴリを取得する関数"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    conn.close()
    return categories



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8888, debug=True)