import argparse
import mariadb


def init_db(host, port, user, password, database):
    conn = mariadb.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ''')
    conn.commit()
    conn.close()
    print("Database migration completed successfully.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Notes Service Database Migration")
    parser.add_argument('--db-host', required=True)
    parser.add_argument('--db-port', type=int, default=3306)
    parser.add_argument('--db-user', required=True)
    parser.add_argument('--db-pass', required=True)
    parser.add_argument('--db-name', required=True)
    args = parser.parse_args()
    init_db(args.db_host, args.db_port, args.db_user, args.db_pass, args.db_name)
