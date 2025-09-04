import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, get_db_connection, init_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    with patch('app.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        yield mock_cursor, mock_connection


def test_index_get_request(client):
    """Test GET request to index page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Enter Passcode' in response.data
    assert b'Passcode:' in response.data


def test_index_post_empty_passcode(client):
    """Test POST request with empty passcode"""
    response = client.post('/', data={'passcode': ''})
    assert response.status_code == 200
    assert b'Please enter a passcode' in response.data


@patch('app.get_db_connection')
def test_index_post_valid_passcode(mock_db_conn, client):
    """Test POST request with valid passcode"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ('Hello, world!',)

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn

    response = client.post('/', data={'passcode': 'secret123'})
    assert response.status_code == 200
    assert b'Hello, world!' in response.data


@patch('app.get_db_connection')
def test_index_post_invalid_passcode(mock_db_conn, client):
    """Test POST request with invalid passcode"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn

    response = client.post('/', data={'passcode': 'wrongcode'})
    assert response.status_code == 200
    assert b'Invalid passcode' in response.data


@patch('app.get_db_connection')
def test_index_post_database_error(mock_db_conn, client):
    """Test POST request with database error"""
    mock_db_conn.side_effect = Exception("Database connection failed")

    response = client.post('/', data={'passcode': 'secret123'})
    assert response.status_code == 200
    assert b'Invalid passcode' in response.data


@patch('app.get_db_connection')
def test_health_endpoint_healthy(mock_db_conn, client):
    """Test health endpoint when database is healthy"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn

    response = client.get('/health')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'


@patch('app.get_db_connection')
def test_health_endpoint_unhealthy(mock_db_conn, client):
    """Test health endpoint when database is unhealthy"""
    mock_db_conn.side_effect = Exception("Database connection failed")

    response = client.get('/health')
    assert response.status_code == 503

    data = json.loads(response.data)
    assert data['status'] == 'unhealthy'
    assert data['database'] == 'disconnected'


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('text/plain')
    assert b'flask_requests_total' in response.data


@patch('app.psycopg2.connect')
def test_get_db_connection_retry_logic(mock_connect):
    """Test database connection retry logic"""
    mock_connect.side_effect = [
        Exception("Connection failed"),
        Exception("Connection failed"),
        MagicMock()
    ]

    conn = get_db_connection()
    assert conn is not None
    assert mock_connect.call_count == 3


@patch('app.get_db_connection')
def test_init_db(mock_db_conn):
    """Test database initialization"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn

    init_db()

    assert mock_cursor.execute.call_count >= 3
    mock_conn.commit.assert_called_once()


class TestIntegration:
    """Integration tests that can be run against a real database"""

    @pytest.mark.integration
    def test_full_workflow(self, client):
        """Test complete workflow with real database (requires DB setup)"""
        try:
            get_db_connection()
        except Exception:
            pytest.skip("Database not available for integration test")

        response = client.post('/', data={'passcode': 'secret123'})
        assert response.status_code == 200
