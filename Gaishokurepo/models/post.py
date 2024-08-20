from Gaishokurepo.db import get_db
from werkzeug.exceptions import abort

class Post:
    def __init__(self, id, date, name, genre, rating) -> None:
        #初期化メソッド
        #実体を持つときに渡される値をインスタンス変数として定義
        self.id = id
        self.date = date
        self.name = name
        self.genre = genre
        self.rating = rating

    @classmethod #選択した日付のリストを返したい
    def DateList(cls,date):
        db = get_db()
        posts = db.execute(
            'SELECT p.id, date, name, genre, rating'
            ' FROM post p '
            ' WHERE p.date = ?'
            ' ORDER BY rating DESC',
            (date,)
        ).fetchall()
        return posts
    
    @classmethod #直近10件のリストを返したい
    def NewList(cls):
        db = get_db()
        posts = db.execute(
            'SELECT p.id, date, name, genre, rating'
            ' FROM post p '
            ' ORDER BY date DESC'
            ' LIMIT 10'
        ).fetchall()
        return posts
    
    @classmethod #idから投稿の情報を取得して返す
    def get(cls, id):
        db = get_db()
        post = db.execute(
        'SELECT p.id, date, name, genre, rating'
        ' FROM post p'
        ' WHERE p.id = ?',
        (id,)
        ).fetchone()

        if post is None: #投稿がないとき
            return None
        else:
            #投稿の各要素を取得
            date = post['date']
            name = post['name']
            genre = post['genre']
            rating = post['rating']
        
        ins = cls(id,date, name, genre, rating)
        return ins
    
    @classmethod #投稿の新規作成　エラーと作成した投稿の情報を返す
    def create(cls, date, name, genre, rating):
        error = None

        if not date:
            error = 'Date is required.'
        elif  not name:
            error = 'Name is required.'

        if error is not None:
            return error, None
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (date, name, genre, rating)'
                ' VALUES (?, ?, ?, ?)',
                (date, name, genre, rating)
            )
            db.commit()#変更を確定させて保存
            #postをcreatedで降順に並び替え、一番上の投稿(最新)の情報を取得
            post = db.execute(
            'SELECT p.id, date, name, genre, rating'
            ' FROM post p'
            ' ORDER BY p.id DESC '
            ).fetchone()

            ins = cls(post['id'],date, name, genre, rating)
            return None, ins

    @classmethod #投稿の削除
    def delete(cls, id):
        #postテーブルから削除する、どこを削除するかはidで指定
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?',(id,))
        db.commit()