import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from app import app


app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app'))
sys.path.insert(0, app_path)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_alive(client):
    response = client.get('/health/alive')
    assert response.status_code == 200
    assert response.data == b"OK"


@patch('app.get_db_connection')
def test_health_ready_success(mock_get_db, client):
    mock_get_db.return_value.close.return_value = None
    response = client.get('/health/ready')
    assert response.status_code == 200
    assert b"OK" in response.data


@patch('app.get_db_connection')
def test_health_ready_failure(mock_get_db, client):
    mock_get_db.side_effect = Exception("Connection Refused")
    response = client.get('/health/ready')
    assert response.status_code == 500
    assert b"Database error" in response.data


@patch('app.get_db_connection')
def test_create_note_json(mock_get_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    response = client.post('/notes', json={
        "title": "Test Title",
        "content": "Test Content"
    })
    assert response.status_code == 201
    assert response.get_json() == {"status": "success", "message": "Note created"}
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        ("Test Title", "Test Content")
    )


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Notes Service API" in response.data


@patch('app.get_db_connection')
def test_get_notes_json(mock_get_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, "First Note"), (2, "Second Note")]
    response = client.get('/notes')
    assert response.status_code == 200
    expected_data = [{"id": 1, "title": "First Note"}, {"id": 2, "title": "Second Note"}]
    assert response.get_json() == expected_data
