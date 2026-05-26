#!/usr/bin/env python3
"""
Notes Service — Лабораторна робота №4
Variant 24: Flask + MariaDB, port 5000, config via CLI args
"""

import argparse
import sys
import mariadb
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
db_config = {}


# ─── DB connection ──────────────────────────────────────────────────────────

def get_db():
    """Створює нове з'єднання з БД для кожного запиту."""
    return mariadb.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        connect_timeout=5,
    )


# ─── Health endpoints ────────────────────────────────────────────────────────

@app.route("/health/alive")
def health_alive():
    """Перевірка живості сервісу. Завжди повертає 200."""
    return Response("OK", status=200, mimetype="text/plain")


@app.route("/health/ready")
def health_ready():
    """
    Перевірка готовності — перевіряє зв'язок з БД на VM2.
    Повертає 200 якщо БД доступна, 503 якщо ні.
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return Response("READY", status=200, mimetype="text/plain")
    except mariadb.Error as e:
        return Response(
            f"NOT READY: database connection failed: {e}",
            status=503,
            mimetype="text/plain",
        )


# ─── Root ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    html = """<!DOCTYPE html>
<html lang="uk">
<head><meta charset="UTF-8"><title>Notes Service</title></head>
<body>
<h1>Notes Service API</h1>
<table border="1" cellpadding="6">
  <tr><th>Метод</th><th>Ендпоінт</th><th>Опис</th></tr>
  <tr><td>GET</td><td>/notes</td><td>Список усіх нотаток</td></tr>
  <tr><td>POST</td><td>/notes</td><td>Створити нотатку (title, content)</td></tr>
  <tr><td>GET</td><td>/notes/&lt;id&gt;</td><td>Отримати нотатку за ID</td></tr>
</table>
</body>
</html>"""
    return Response(html, mimetype="text/html")


# ─── Notes endpoints ─────────────────────────────────────────────────────────

def _wants_json():
    accept = request.headers.get("Accept", "text/html")
    return "application/json" in accept


@app.route("/notes", methods=["GET"])
def list_notes():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM notes ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500

    if _wants_json():
        return jsonify([{"id": r[0], "title": r[1]} for r in rows])

    rows_html = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>" for r in rows
    )
    html = f"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><title>Notes</title></head>
<body>
<h1>Нотатки</h1>
<table border="1" cellpadding="6">
  <tr><th>ID</th><th>Title</th></tr>
  {rows_html}
</table>
</body></html>"""
    return Response(html, mimetype="text/html")


@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)", (title, content)
        )
        conn.commit()
        conn.close()
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success", "message": "Note created"}), 201


@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, content, created_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cur.fetchone()
        conn.close()
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500

    if row is None:
        return jsonify({"error": "Note not found"}), 404

    note = {
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "created_at": str(row[3]),
    }

    if _wants_json():
        return jsonify(note)

    html = f"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><title>{note['title']}</title></head>
<body>
<h1>{note['title']}</h1>
<p><strong>ID:</strong> {note['id']}</p>
<p><strong>Дата:</strong> {note['created_at']}</p>
<pre>{note['content']}</pre>
</body></html>"""
    return Response(html, mimetype="text/html")


# ─── Entry point ─────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Notes Service")
    parser.add_argument("--db-host",  required=True, help="MariaDB host (IP VM2)")
    parser.add_argument("--db-port",  type=int, default=3306)
    parser.add_argument("--db-user",  required=True)
    parser.add_argument("--db-pass",  required=True)
    parser.add_argument("--db-name",  required=True)
    parser.add_argument("--app-port", type=int, default=5000)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    db_config.update({
        "host":     args.db_host,
        "port":     args.db_port,
        "user":     args.db_user,
        "password": args.db_pass,
        "database": args.db_name,
    })
    app.run(host="127.0.0.1", port=args.app_port, debug=False)
