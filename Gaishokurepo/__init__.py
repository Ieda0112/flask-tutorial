import os
from flask import Flask
from flask_cors import CORS

def create_app(test_config = None):
    # アプリケーションの作成と設定
    app = Flask(__name__, instance_relative_config = True)
    CORS(app, origins=["*"], methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
    app.config.from_mapping(    #アプリのデフォルトの構成を設定する
        SECRET_KEY = 'dev',     #データを安全に保つための鍵、本当はランダムな値で上書きするべき
        DATABASE = os.path.join(app.instance_path, 'gaishokurepo.sqlite'),   #SQLiteデータベースを保存するパス
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
    
    #db.pyで定義した関数を今回作っているインスタンスappで使えるようにする
    from . import db
    db.init_app(app)

    #blog.pyで定義したブループリントをインポート
    from . import blog
    app.register_blueprint(blog.bp)
    #blogをメインと据えたので/と/blog.indexを同じものと見做させる
    app.add_url_rule('/', endpoint = 'index')

    #apiフォルダ内のblog.pyをインポート
    from .api import blog
    app.register_blueprint(blog.bp)

    return app