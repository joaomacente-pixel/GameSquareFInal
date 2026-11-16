from flask import Flask, jsonify, request, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("gamelog.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            platform TEXT NOT NULL,
            year INTEGER,
            cover TEXT
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            game_id INTEGER NOT NULL,
            rating REAL NOT NULL CHECK(rating >= 0 AND rating <= 5),
            review_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(game_id) REFERENCES games(id)
        );
        """)
        if db.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 0:
            games = [
                ("The Legend of Zelda: Breath of the Wild", "Aventura", "Nintendo Switch", 2017, "/static/img/zelda.jpg"),
                ("Elden Ring", "RPG / Ação", "PC, PlayStation, Xbox", 2022, "/static/img/elden-ring.jpg"),
                ("Minecraft", "Sandbox", "Multiplataforma", 2011, "/static/img/minecraft.jpg"),
                ("Red Dead Redemption 2", "Ação / Aventura", "PC, PlayStation, Xbox", 2018, "/static/img/red-dead-redemption-2.jpg"),
                ("Hollow Knight", "Metroidvania", "PC, Console", 2017, "/static/img/hollow-knight.jpg"),
                ("Stardew Valley", "Simulação", "Multiplataforma", 2016, "/static/img/stardew-valley.jpg"),
            ]
            db.executemany("INSERT INTO games(title,genre,platform,year,cover) VALUES(?,?,?,?,?)", games)
        if db.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 0:
            db.executemany("""INSERT INTO reviews(username,game_id,rating,review_text)
                              VALUES(?,?,?,?)""", [
                ("pixelheart", 2, 5, "Um mundo absurdo de tão bonito. Cada descoberta parece uma pequena conquista."),
                ("rafa.exe", 4, 4.5, "Uma história marcante e um nível de detalhe impressionante."),
                ("luna", 5, 4.5, "Direção de arte incrível. Difícil parar de jogar depois que começa."),
                ("joaogamer", 3, 5, "LA-LA-LA-LAVA, CHI-CHI-CHI-CHICKEN"),
            ])

@app.route("/")
def home():
    return render_template("index.html")

@app.get("/api/games")
def get_games():
    with connect() as db:
        rows = db.execute("""
            SELECT g.*, ROUND(AVG(r.rating),1) AS average_rating,
                   COUNT(r.id) AS review_count
            FROM games g LEFT JOIN reviews r ON r.game_id = g.id
            GROUP BY g.id ORDER BY g.title
        """).fetchall()
    return jsonify([dict(row) for row in rows])

@app.get("/api/reviews")
def get_reviews():
    with connect() as db:
        rows = db.execute("""
            SELECT r.*, g.title AS game_title, g.cover AS game_cover, g.genre
            FROM reviews r JOIN games g ON g.id = r.game_id
            ORDER BY r.created_at DESC, r.id DESC
        """).fetchall()
    return jsonify([dict(row) for row in rows])

@app.post("/api/reviews")
def create_review():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "visitante")).strip()[:30]
    review_text = str(data.get("review_text", "")).strip()
    try:
        game_id = int(data.get("game_id"))
        rating = float(data.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "Selecione um jogo e uma nota válida."}), 400
    if not username or not review_text:
        return jsonify({"error": "Preencha seu nome e escreva uma review."}), 400
    if not 0 <= rating <= 5:
        return jsonify({"error": "A nota deve estar entre 0 e 5."}), 400
    with connect() as db:
        if not db.execute("SELECT id FROM games WHERE id=?", (game_id,)).fetchone():
            return jsonify({"error": "Jogo não encontrado."}), 404
        cur = db.execute("""INSERT INTO reviews(username,game_id,rating,review_text)
                            VALUES(?,?,?,?)""", (username, game_id, rating, review_text))
        review_id = cur.lastrowid
        row = db.execute("""SELECT r.*, g.title AS game_title, g.cover AS game_cover, g.genre
                            FROM reviews r JOIN games g ON g.id=r.game_id WHERE r.id=?""",
                         (review_id,)).fetchone()
    return jsonify(dict(row)), 201

@app.get("/api/profile")
def profile():
    username = request.args.get("username", "visitante")
    with connect() as db:
        stats = db.execute("""
            SELECT COUNT(*) AS reviews, COUNT(DISTINCT game_id) AS games,
                   ROUND(AVG(rating),1) AS average
            FROM reviews WHERE username=?
        """, (username,)).fetchone()
        rows = db.execute("""
            SELECT r.*, g.title AS game_title, g.cover AS game_cover
            FROM reviews r JOIN games g ON g.id=r.game_id
            WHERE r.username=? ORDER BY r.created_at DESC, r.id DESC
        """, (username,)).fetchall()
    return jsonify({"username": username, "stats": dict(stats),
                    "reviews": [dict(row) for row in rows]})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
