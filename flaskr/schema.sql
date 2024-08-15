DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

/*userテーブルの定義を宣言*/
CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,   /*IDは整数のインクリメント*/
    username TEXT UNIQUE NOT NULL,  /*usernameはテキストで一意に定まり、Nullはダメ*/
    password TEXT NOT NULL  /*passwordもテキストで、Nullはダメ*/
);

/*postテーブルの定義を宣言*/
CREATE TABLE post(
    id INTEGER PRIMARY KEY AUTOINCREMENT,   /*ポストのIDは整数のインクリメント*/
    author_id INTEGER NOT NULL, /*ポスト投稿者のID*/
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);