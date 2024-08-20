import sqlite3
import click
from flask import current_app, g
#gはリクエストごとの一意なオブジェクト
#curent_appはリクエストを処理するFlaskアプリケーション

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect( #DATABASE構成キーが指すファイルへの接続を行う
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        #名前によるアクセスを可能にする
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e = None):
    #g.dbが設定されているか調べる
    db = g.pop('db', None)
    
    #g.dbが設定されていたら閉じる
    if db is not None:
        db.close()
#これは各リクエストの後に呼び出させる

def init_db():
    db = get_db()

    # 相対パスでファイルを開く
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    # 既存データを削除し、表を新たに作る。上手くいったらInitialized the database.を表示
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)       #レスポンスした後のクリーンアップ時に呼び出す関数の設定
    app.cli.add_command(init_db_command)    #flaskコマンドで呼び出せるコマンドの追加