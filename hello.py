from flask import Flask
app = Flask(__name__)

@app.route('/') # ルートとして'/'がアプリに入力された時の処理を定義する
def hello():
    
    return 'Hello, World!'
