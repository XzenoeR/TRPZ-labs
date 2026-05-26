#!/usr/bin/env python3
"""
migrate.py — Міграція БД для Notes Service
Ідемпотентний: повторний запуск не ламає існуючі дані.
"""

import argparse
import sys
import mariadb


def migrate(args):
    try:
        conn = mariadb.connect(
            host=args.db_host,
            port=args.db_port,
            user=args.db_user,
            password=args.db_pass,
            database=args.db_name,
            connect_timeout=10,
        )
    except mariadb.Error as e:
        print(f"[migrate] ERROR: Cannot connect to database: {e}", file=sys.stderr)
        sys.exit(1)

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id         INT          NOT NULL AUTO_INCREMENT,
            title      VARCHAR(255) NOT NULL,
            content    TEXT,
            created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()

    # Перевіряємо чи таблиця вже існувала
    cur.execute("SHOW TABLE STATUS LIKE 'notes'")
    row = cur.fetchone()
    if row:
        print("[migrate] Table 'notes' is ready.")
    else:
        print("[migrate] Table created.")

    conn.close()


def parse_args():
    parser = argparse.ArgumentParser(description="DB Migration for Notes Service")
    parser.add_argument("--db-host",  required=True)
    parser.add_argument("--db-port",  type=int, default=3306)
    parser.add_argument("--db-user",  required=True)
    parser.add_argument("--db-pass",  required=True)
    parser.add_argument("--db-name",  required=True)
    return parser.parse_args()


if __name__ == "__main__":
    migrate(parse_args())
