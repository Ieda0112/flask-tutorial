from flask import (
    flash, redirect, url_for, session, g
)
from flaskr.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(self, id, username, password) -> None:
        #初期化メソッド
        #実体を持つときに渡される値をインスタンス変数として定義
        self.id = id
        self.username = username
        self.password = password

    @classmethod #usernameからユーザー情報を得る
    def get(cls, username):
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        ins = cls(user['id'], username, user['password'])
        return  ins

    @classmethod #ユーザの新規登録
    def regist(cls, username, password):
        #auth.py 21~45参照
        db = get_db()
        error = None

        #username, passwordどちらも入力されているか確認
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        #入力されたフォームをデータベースに挿入する
        if error is None:
            try:
                #プレースホルダの？でインジェクション攻撃に対応、パスワードはハッシュ値で保存
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password, method='pbkdf2:sha256')),
                )#macOSの関係でハッシュ関数をsha256に変更
                
                db.commit()                
            except db.IntegrityError:
                #usernameはUnique(schema.sql参照)なので被りがあるとエラー
                error = f"User {username} is already registered."
                
                return error, None
            else:
                ins = cls.get(username)
                return None, ins
        else:        
            return error, None
        
    @classmethod #ログイン
    def login(cls, username, password):
        #auth.py 57~77
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        #username, passwordどちらも一致しているか確認
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
        #user['password']と同じハッシュ関数で入力したpasswordを確認
            error = 'Incorrect password.'
        #どちらもerrorなく通れば認証完了、ログイン成功

        ins = user
        return error, ins

    @classmethod #ユーザがログインしているかどうかを確認し、ユーザ情報を取得
    def load_logged_in_user(cls,user_id):
        #auth.py 86~94
        if user_id is None:
            user = None
        else:
            user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

        ins = user
        return ins