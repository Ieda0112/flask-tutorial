from flaskr.db import get_db
from werkzeug.exceptions import abort

class Post:
    def __init__(self, id, author_id, created, title, body) -> None:
        #初期化メソッド
        #実体を持つときに渡される値をインスタンス変数として定義
        self.id = id
        self.author_id = author_id
        self.created = created
        self.title = title
        self.body = body


    @classmethod #全ての投稿の情報を取得して返す
    def index(cls):
        #blog.py 17~26
        #executeの引数としてSQLクエリを入れている
        db = get_db()
        posts = db.execute(
            #投稿のID、タイトル、本文、作成日時(created)、投稿者のID、投稿者の名前を取得
            'SELECT p.id, title, body, created, author_id, username'
            #postテーブルpとuserテーブルuから、pの投稿者IDとuのIDを一致させる
            ' FROM post p JOIN user u ON p.author_id = u.id'
            #作成日時(created)で降順に並び替え、最新が一番上に来る
            ' ORDER BY created DESC'
        ).fetchall()#クエリの結果を全て取得
        #取得した全てをレンダーする

        return posts


    @classmethod #idから投稿の情報を取得して返す
    def get(cls, id):
        #blog.py 58~68参照
        db = get_db()
        post = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        #p.idが?(今回は変数id)と一致するものを取得
        ' WHERE p.id = ?',
        (id,)
        ).fetchone()#クエリ結果の最初の１行を取得

        if post is None: #そもそも投稿がないとき
            return None
        else:
            #投稿の各要素を取得
            author_id = post['author_id']
            created = post['created']
            title = post['title']
            body = post['body']
        
        ins = cls(id, author_id, created, title, body)
        return ins
    
    @classmethod #投稿の新規作成　エラーと作成した投稿の情報を返す
    def create(cls, title, body, author_id):
        #blog.py 35~52
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            return error, None
        else:
            db = get_db()
            db.execute(
                #postテーブルに新たなtitle,body,author_idを挿入する
                'INSERT INTO post (title, body, author_id)'
                #プレースホルダ、インジェクション対策
                ' VALUES (?, ?, ?)',
                #上で定義したtitle,bodyと今ログインしているユーザのIDを入れる
                (title, body, author_id)
            )
            db.commit()#変更を確定させて保存
            #postをcreatedで降順に並び替え、一番上の投稿(最新)の情報を取得
            post = db.execute(
            'SELECT p.id, author_id, created, title, body'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
            ).fetchone()

            ins = cls(post['id'],author_id,post['created'],title,body)
            return None, ins

    
    @classmethod #投稿の編集、エラーについて返す
    def update(cls,id,title,body):
        #blog.py 86~101
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            ins = cls.get(id)
            return error, ins
        else:
            db = get_db()
            db.execute(
                #postテーブルのtitle,bodyを新しい値を設定(SET)して、更新(UPDATE)する
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',#どこを更新するかをidで指定
                (title, body, id)
            )
            db.commit()
            #修正後のポスト情報を返すようなSQL(上のgetと同じ処理)
            ins = cls.get(id)
            return None, ins

    @classmethod #投稿の削除
    def delete(cls, id):
        #blog.py 111~114
        #postテーブルから削除する、どこを削除するかはidで指定
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?',(id,))
        db.commit()