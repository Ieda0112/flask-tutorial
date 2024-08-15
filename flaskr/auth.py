import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.models.user import User

#名前がauth、import_nameが__name__(モジュールの名前)、
#関連づけられるもの全てのURL先頭に/authがつくBlueprintを宣言
bp = Blueprint('auth', __name__, url_prefix='/auth')

#登録機能
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':    #フォームが送られてきた時の処理
        #入力されたusernameとpassword
        username = request.form['username']
        password = request.form['password']
        error, user = User.regist(username, password)

        if error is None:
            return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error, user = User.login(username,password)

        if error is None:
            #辞書型のsessionに認証されたIDが保存される、データはCookieに保存
            session.clear()
            session['user_id'] = user['id']
            return redirect('/') #(url_for('index'))がなぜか使えなかったので直接('/')
        flash(error)

    return render_template('auth/login.html')

#ログインで保存されたIDを後続のリクエストでも利用できるようになる
#要求されたURLに関わらずユーザーIDがsessionに格納されているかを確認
@bp.before_app_request
#ユーザがログインしているかどうかを確認
def load_logged_in_user():
    #ログインしていればuser_idに値が入るはず
    user_id = session.get('user_id')
    g.user = User.load_logged_in_user(user_id)

#ログアウト時はsessionからIDを消去
@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/') #(url_for('index'))がなぜか使えなかったので直接('/')

def login_required(view):
    @functools.wraps(view)
    #１つのビューを丸々包んで、userが読み込まれているか確認する
    def wrapped_view(**kwargs):
        if g.user is None:
            #userが読み込めなければログインページへ飛ばす
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

#いくつかのurl_forでauth.が付いているが(auth.loginのように)これはbpの名前がauthだから
#このことが、ブループリントでまとまっているということ