from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from Gaishokurepo.db import get_db
#モデル層として作成したpost.pyのPostクラスをインポート
from Gaishokurepo.models.post import Post

#auth.pyと違ってurl_prefixがない→ブログがメイン機能なのでつけないのが理に適っている
bp = Blueprint('api_blog', __name__, url_prefix='/api')

#日付選択時の投稿一覧を表示させたい
@bp.route('/daily', methods = ["GET", "POST"])
def daily_list():
    if request.method == 'POST':
        date = request.json['date']
    else:
        date = None

    daily_data = []

    if date is None:
        return jsonify({"error": "Date parameter is required."}), 400
    else:
        posts = Post.DateList(date)
        for post in posts:
            data = {
                "id" : post['id'],
                "date" : post['date'],
                "name" : post['name'],
                "genre" : post['genre'],
                "rating" : post['rating']
            }
            daily_data.append(data)
        return jsonify({"daily_data":daily_data,}), 200
    

#日付選択時の投稿一覧と直近10件の投稿を表示させたい
@bp.route('/recently', methods = ["GET", "POST"])
def recently_list():
    recently_data = []
    
    posts = Post.NewList()
    for post in posts:
        data = {
            "id" : post['id'],
            "date" : post['date'],
            "name" : post['name'],
            "genre" : post['genre'],
            "rating" : post['rating']
        }
        recently_data.append(data)

    return jsonify({"recently_data":recently_data}), 200

#新しい投稿を追加する
@bp.route('/create', methods = ["GET", "POST"])
def create():
    if request.method == 'POST':
        data = request.get_json()
        if (#データが正しいか確認
            'date' not in data or
            'name' not in data or
            'genre' not in data or
            'rating' not in data):
            return jsonify({'error': 'Missing data'}), 400
        else:
            date = request.json['date']
            name = request.json['name']
            genre = request.json['genre']
            rating = request.json['rating']
            error, post = Post.create(date, name, genre, rating)

            if error is not None:
                return jsonify({"error":error}), 400
            else:
                create_data = {
                    "id" : post.id,
                    "date" : post.date,
                    "name" : post.name,
                    "genre" : post.genre,
                    "rating" : post.rating
                }# 更新成功のレスポンス
                return jsonify({
                    'message': 'Post successfully created',
                    'created_post': create_data
                }), 200
    else:
        return jsonify({
            "Not POST": "no data"
            }), 400

#投稿の削除、修正のために投稿が存在するか確認する関数
def get_post(id):
    post = Post.get(id)
    if post is None: #投稿がないとき
        return jsonify({'error': f"Post id {id} doesn't exist."}), 404
        #abort(404)はNot Foundのエラーを表示する
    else:
        return post

#投稿の削除
@bp.route('/delete', methods = ["GET", "POST"])
def delete():
    if request.method == 'POST':
        id = request.json['id']
    else:
        id = None
    get_post(id)
    Post.delete(id)
    return jsonify({"message": "Post successfully deleted"}), 200