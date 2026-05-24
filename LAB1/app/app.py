import os
import argparse
import mariadb
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
db_config = {}

def get_db_connection():
    return mariadb.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

@app.route('/health/alive', methods=['GET'])
def health_alive():
    return "OK", 200

@app.route('/health/ready', methods=['GET'])
def health_ready():
    try:
        conn = get_db_connection()
        conn.close()
        return "OK", 200
    except Exception as e:
        return f"Database error: {str(e)}", 500

@app.route('/', methods=['GET'])
def index():
    html = '''
    <html>
        <head>
            <meta charset="UTF-8">
            <title>Notes Service API</title>
        </head>
        <body>
            <h1>Ендпоінти бізнес-логіки</h1>
            <table border="1">
                <tr><th>Метод</th><th>Ендпоінт</th></tr>
                <tr><td>GET, POST</td><td>/notes</td></tr>
                <tr><td>GET</td><td>/notes/&lt;id&gt;</td></tr>
            </table>
        </body>
    </html>
    '''
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/notes', methods=['GET', 'POST'])
def handle_notes():
    accept_header = request.headers.get('Accept', '')

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        title = data.get('title')
        content = data.get('content')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        
        if 'text/html' in accept_header:
            return "<html><head><meta charset='UTF-8'></head><body><h1>Нотатку успішно створено</h1></body></html>", 201, {'Content-Type': 'text/html; charset=utf-8'}
        return jsonify({"status": "success", "message": "Note created"}), 201

    elif request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM notes")
        notes = cursor.fetchall()
        conn.close()
        
        if 'text/html' in accept_header:
            html = "<html><head><meta charset='UTF-8'></head><body><table border='1'><tr><th>ID</th><th>Title</th></tr>"
            for note in notes:
                html += f"<tr><td>{note[0]}</td><td>{note[1]}</td></tr>"
            html += "</table></body></html>"
            return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        else:
            result = [{"id": note[0], "title": note[1]} for note in notes]
            return jsonify(result), 200

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    accept_header = request.headers.get('Accept', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at, content FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    
    if not note:
        if 'text/html' in accept_header:
            return "<html><head><meta charset='UTF-8'></head><body><h1>Нотатку не знайдено</h1></body></html>", 404, {'Content-Type': 'text/html; charset=utf-8'}
        return jsonify({"error": "Note not found"}), 404

    if 'text/html' in accept_header:
        html = f'''
        <html><head><meta charset='UTF-8'></head><body><table border='1'>
            <tr><th>ID</th><td>{note[0]}</td></tr>
            <tr><th>Title</th><td>{note[1]}</td></tr>
            <tr><th>Created At</th><td>{note[2]}</td></tr>
            <tr><th>Content</th><td>{note[3]}</td></tr>
        </table></body></html>
        '''
        return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    else:
        created_at = note[2].isoformat() if isinstance(note[2], datetime) else str(note[2])
        result = {
            "id": note[0],
            "title": note[1],
            "created_at": created_at,
            "content": note[3]
        }
        return jsonify(result), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Notes Service Web Application")
    parser.add_argument('--db-host', required=True, help="MariaDB Host")
    parser.add_argument('--db-port', type=int, default=3306, help="MariaDB Port")
    parser.add_argument('--db-user', required=True, help="MariaDB User")
    parser.add_argument('--db-pass', required=True, help="MariaDB Password")
    parser.add_argument('--db-name', required=True, help="MariaDB Database Name")
    parser.add_argument('--app-port', type=int, default=5000, help="Application Port")
    
    args = parser.parse_args()
    
    db_config['host'] = args.db_host
    db_config['port'] = args.db_port
    db_config['user'] = args.db_user
    db_config['password'] = args.db_pass
    db_config['database'] = args.db_name
    
    # Запускаємо сервер на всіх інтерфейсах (0.0.0.0)
    app.run(host='0.0.0.0', port=args.app_port)