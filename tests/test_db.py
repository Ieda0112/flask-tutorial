import sqlite3

import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    #sqlite3.ProgrammingErrorのエラーが発生することを期待する
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1') #この操作がエラー(sqlite3.ProgrammingError)を起こす

    #起こったエラーのメッセージにcloseが含まれるか確認
    assert 'closed' in str(e.value)

    #get_dbがただしく呼び出され、閉じられているかを確認した

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    #テストのためのinit_dbの代替関数
    def fake_init_db():
        Recorder.called = True

    #テストのためにflaskr.db.init_dbをfake_init_dbに置き換える
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    #init-dbコマンドを実行
    result = runner.invoke(args=['init-db'])
    #実行結果にInitializedが含まれるか確認
    assert 'Initialized' in result.output
    #fake_init_dbが呼び出されたか確認
    assert Recorder.called

#init_dbを呼び出す流れが正しくできているかを確認した