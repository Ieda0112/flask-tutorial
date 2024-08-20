import pytest
from flask import g,session
from Gaishokurepo.db import get_db

#登録機能のテスト
def test_register(client, app):
    #/auth/registerへGETリクエストが成功した(statusが200)かを確認
    assert client.get('/auth/register').status_code == 200
    #/auth/registerへusernameをa、passwordをaとしてPOSTリクエスト送信
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    #登録後に/auth/loginにリダイレクトされているか確認
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        #名前がaのものを取得して、それが存在するか確認
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

#ユーザー登録のバリデーション(入力が規定に即しているか)を確認
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'), #両方空欄ならUsername is required
    ('a', '', b'Password is required.'), #パスワードだけ空欄ならPassword is required.
    ('test', 'test', b'already registered'), #すでに登録されている名前ならalready registeredと出ることを期待
))
def test_register_validate_input(client, username, password, message):
    #/auth/registerに上で上げた３組のデータをPOSTリクエストで送信
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    #リクエストのレスポンス(エラーメッセージ)と上で期待したメッセージが一致するか確認
    assert message in response.data

#ログイン機能のテスト
def test_login(client, auth):
    #GETリクエストが成功か確認
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    #ログイン後/に飛ぶか確認
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

#ログイン機能のテスト
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session