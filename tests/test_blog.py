import pytest
from flaskr.db import get_db

#ホーム画面のテスト
def test_index(client, auth):
    response = client.get('/')
    #レスポンスデータにLogINとRegisterが含まれているか確認
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    #ログイン後のレスポンスデータに以下の５つが含まれているか確認
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',#投稿、修正、削除を一気にテストする
))
#ログインしてない状態で投稿などしようとするとログインページに飛ぶか確認
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

#他人が修正、削除できないことのテスト
def test_author_required(app, client, auth):
    #投稿者IDを別のものに変える(1の投稿の投稿者IDを2に変える)
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    #IDが異なる投稿の修正、削除が禁止されていること(403)を確認
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    #ホーム画面のGETリクエストの結果に編集リンクがないことを確認
    assert b'href="/1/update"' not in client.get('/').data

#存在しない投稿への修正、削除機能のテスト
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',#存在しない投稿の修正、削除のURL
))
def test_exists_required(client, auth, path):
    auth.login()
    #投稿が存在しないこと(404)を確認
    assert client.post(path).status_code == 404

#投稿機能のテスト
def test_create(client, auth, app):
    auth.login()
    #/createにアクセスできたか確認
    assert client.get('/create').status_code == 200
    #タイトルcreated、本文なしで投稿
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        #投稿総数が２(data.sqlの1つ、上で投稿した1つ)であるか確認
        assert count == 2

#修正機能のテスト
def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    #投稿(ID=1)をタイトルupdated、本文なしで修正
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        #投稿(ID=1)のタイトルを確認
        assert post['title'] == 'updated'

#投稿、修正のバリデーションが正しいか確認
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    #タイトル、本文なしの投稿をPOSTリクエスト
    response = client.post(path, data={'title': '', 'body': ''})
    #タイトルなしで出るエラーが正しく出ているか確認
    assert b'Title is required.' in response.data

#削除機能のテスト
def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    #削除成功後ホームに戻るか確認
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        #削除後に投稿がないことを確認
        assert post is None