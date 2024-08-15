import os
from flask import Flask

def create_app(test_config = None):
    # アプリケーションの作成と設定
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(    #アプリのデフォルトの構成を設定する
        SECRET_KEY = 'dev',     #データを安全に保つための鍵、本当はランダムな値で上書きするべき
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),   #SQLiteデータベースを保存するパス
    )

    if test_config is None:
        #instance configがあれば読み込む
        app.config.from_pyfile('config.py',silent= True)
    else:
        #渡された場合テスト設定を読み込む
        app.config.from_mapping(test_config)
    
    #インスタンスフォルダの存在を確認する
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    #db.pyで定義した関数を今回作っているインスタンスappで使えるようにする
    from . import db
    db.init_app(app)

    #auth.pyで定義したブループリントをインポート
    from . import auth
    app.register_blueprint(auth.bp)

    #blog.pyで定義したブループリントをインポート
    from . import blog
    app.register_blueprint(blog.bp)
    #blogをメインと据えたので/と/blog.indexを同じものと見做させる
    app.add_url_rule('/', endpoint = 'index')

    return app