import os
import tempfile

import pytest
from Gaishokurepo import create_app
from Gaishokurepo.db import get_db, init_db

#data.sqlの内容をバイナリモードで読み込んで
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    #utf-8エンコーディングでデコード
    _data_sql = f.read().decode('utf8')

#テストのための準備と後片付けがフィクスチャ
@pytest.fixture
def app():
    #テストのための一時的なファイルを作成し、ファイル記述子とそのパスを返す
    db_fd, db_path = tempfile.mkstemp()

    #Flaskの機能でテストモードでデータベースがdb_pathの、flaskrのインスタンスappを作る
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    #テスト関数にappを渡す
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

#認証に関するテストのための準備・フィクスチャ
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        #/auth/loginにusernameとpasswordをPOSTリクエストとして送信
        return self._client.post(
            '/auth/login',
            data={'username':username, 'password':password}
        )
    
    def logout(self):
        #/auth/logoutにGETリクエストを送信
        return self._client.get('/auth/logout')
    
@pytest.fixture
def auth(client):
    return AuthActions(client)