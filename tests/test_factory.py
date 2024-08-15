from flaskr import create_app

def test_config():
    #デフォルトのflaskrのテストフラグがFalseであるか確認
    assert not create_app().testing
    #テストフラグをTrueにしたflaskrのテストフラグが正しくTrueになっているか確認
    assert create_app({'TESTING':True}).testing

def test_hello(client):
    response = client.get('/hello')
    #/helloから受けたレスポンスが'Hello, World!'となっているか確認
    assert response.data == b'Hello, World!'

#ファクトリーが正しく動作するか、/helloの動作によって確認した