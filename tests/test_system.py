"""
Unit and Integration Tests for Student and College Management System
Run with: python -m pytest tests/test_system.py
"""

import os
import pytest
from werkzeug.security import check_password_hash
from app import app, calculate_grade

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

def test_grading_logic():
    """Verify institutional 3NF grading scale boundaries."""
    assert calculate_grade(100.0) == 'A+'
    assert calculate_grade(90.0) == 'A+'
    assert calculate_grade(89.9) == 'A'
    assert calculate_grade(80.0) == 'A'
    assert calculate_grade(79.9) == 'B'
    assert calculate_grade(70.0) == 'B'
    assert calculate_grade(69.9) == 'C'
    assert calculate_grade(60.0) == 'C'
    assert calculate_grade(59.9) == 'D'
    assert calculate_grade(50.0) == 'D'
    assert calculate_grade(49.9) == 'F'
    assert calculate_grade(0.0) == 'F'

def test_password_hash_verification():
    """Verify stored seed hash matches default admin password."""
    # Seed hash generated for 'admin123'
    seed_hash = "scrypt:32768:8:1$CZkZSTJBgS9d55fQ$93916ae95e835fe4c858ca266eea469f8c71be2bc63c77fc59a0fb11b22971495dc779ac8be8219ce0d0568bec7a9a94101a82eb73096a9b9b22aee0c0ed1db0"
    assert check_password_hash(seed_hash, "admin123") is True
    assert check_password_hash(seed_hash, "wrongpassword") is False

def test_login_page_renders(client):
    """Verify login page is rendered with status code 200."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"College Admin Portal" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data

def test_protected_routes_redirect_to_login(client):
    """Verify unauthenticated access to dashboard redirects to login."""
    routes_to_test = [
        '/',
        '/dashboard',
        '/students',
        '/faculty',
        '/departments',
        '/courses',
        '/enrollments',
        '/attendance',
        '/exam_results'
    ]
    for route in routes_to_test:
        response = client.get(route, follow_redirects=False)
        # Should redirect to /login (302)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

def test_sql_files_exist_and_non_empty():
    """Verify all database SQL scripts exist and have content."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    schema_path = os.path.join(base_dir, 'database', 'schema.sql')
    seed_path = os.path.join(base_dir, 'database', 'seed.sql')
    demo_path = os.path.join(base_dir, 'database', 'demo_queries.sql')

    assert os.path.isfile(schema_path)
    assert os.path.isfile(seed_path)
    assert os.path.isfile(demo_path)

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_content = f.read()
        assert "CREATE TABLE IF NOT EXISTS users" in schema_content
        assert "CREATE TABLE IF NOT EXISTS departments" in schema_content
        assert "CREATE TABLE IF NOT EXISTS students" in schema_content
        assert "CREATE TABLE IF NOT EXISTS faculty" in schema_content
        assert "CREATE TABLE IF NOT EXISTS courses" in schema_content
        assert "CREATE TABLE IF NOT EXISTS enrollments" in schema_content
        assert "CREATE TABLE IF NOT EXISTS attendance" in schema_content
        assert "CREATE TABLE IF NOT EXISTS exam_results" in schema_content

    with open(seed_path, 'r', encoding='utf-8') as f:
        seed_content = f.read()
        assert "INSERT INTO users" in seed_content
        assert "INSERT INTO departments" in seed_content
        assert "INSERT INTO students" in seed_content
