from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
#モデル層として作成したpost.pyのPostクラスをインポート
from flaskr.models.post import Post

#auth.pyと違ってurl_prefixがない→ブログがメイン機能なのでつけないのが理に適っている
bp = Blueprint('api_blog', __name__, url_prefix='/api')

#投稿一覧を表示する
@bp.route('/')
def index():
    posts = Post.index()
    all_data = []
    for post in posts:
        data = {
            "id":post['id'],
            "author_id":post['author_id'],
            "created":post['created'],
            "title":post['title'],
            "body":post['body']
        }
        all_data.append(data)
    return jsonify(all_data)
    """
    Post.index()がfetchallで複数あるからそれぞれを処理する必要がある
    for post in posts:
        data = {
            "id":post.id,
            "author_id":post.author_id,
            "created":post.created,
            "title":post.title,
            "body":post.body
        }
    return jsonify(data)
    """
    

#新しい投稿を追加する　auth.pyのregisterに似てる
@bp.route('/create', methods = ["GET", "POST"])
@login_required #ログインしているか確認
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        author_id = g.user['id']

        error, post = Post.create(title,body,author_id)
        if error is not None:
            flash(error)
        else:
            data = {
                "id":post.id,
                "author_id":post.author_id,
                "created":post.created,
                "title":post.title,
                "body":post.body
            }
            return redirect(url_for('blog.index'))#blog.indexのページへリダイレクト
        
    return render_template('blog/create.html')

#投稿の削除、修正のためにユーザーとポスト作成者が一致するか確認する関数
def get_post(id, check_author=True):
    post = Post.get(id)

    if post is None: #そもそも投稿がないとき
        abort(404, f"Post id {id} doesn't exist.")
    #投稿者とユーザのIDが一致しない時
    # if check_author and post.author_id != g.user['id']:
        # abort(403)
    #abort(404)はNot Found abort(403)はForbiddenのエラーを表示する
    return post

#投稿を修正して上書きする
#入力されたIDをURLに組み込んでいる
@bp.route('/<int:id>/update', methods=["GET", "POST"])
def update(id):
    post = get_post(id)
    
    data = request.get_json()
    
    if (#データが正しいか確認
        'id' not in data or 
        'title' not in data or
        'body' not in data or
        id != data['id']):
        return jsonify({'error': 'Missing data'}), 400
    else:
        title = data['title']
        body = data['body']
        error, post = Post.update(id,title,body)
    
        if error is not None:
            return jsonify({'error': error}), 400
        else:
            updated_post = {
                "id":post.id,
                "author_id":post.author_id,
                "created":post.created,
                "title":post.title,
                "body":post.body
            }
            # 更新成功のレスポンス
            return jsonify({
                'message': 'Post updated successfully',
                'updated_post': updated_post
            }), 200
    
        

    # if request.method == 'POST':
    #     title = request.form['title']
    #     body = request.form['body']
    #     error, post = Post.update(id,title,body)
    
    #     if error is not None:
    #         flash(error)
    #     else:
    #         data = {
    #             "id":post.id,
    #             "author_id":post.author_id,
    #             "created":post.created,
    #             "title":post.title,
    #             "body":post.body
    #         }
    #         return jsonify(data)
    # return redirect(url_for('hello'))

#投稿の削除
@bp.route('/<int:id>/delete', methods=["POST"])
@login_required
def delete(id):
    get_post(id)
    Post.delete(id)
    return redirect(url_for('blog.index'))


#投稿一覧を表示する
@bp.route('/posts/<int:id>')
def json_index(id):
    post = Post.get(id)
    
    data = {
        "id":post.id,
        "author_id":post.author_id,
        "created":post.created,
        "title":post.title,
        "body":post.body
    }
    
    return jsonify(data)
