DROP TABLE IF EXISTS post;

/*postテーブルの定義を宣言*/
CREATE TABLE post(
    id INTEGER PRIMARY KEY AUTOINCREMENT,   /*投稿のID*/
    date DATE NOT NULL, /*外食に行った日*/
    name TEXT NOT NULL, --レストランの名前
    genre TEXT NOT NULL, --ご飯のジャンル
    rating INTEGER NOT NULL --評価
);