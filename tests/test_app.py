import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_doctors_page(client):
    response = client.get("/doctors")
    assert response.status_code == 200


def test_book_page(client):
    response = client.get("/book")
    assert response.status_code == 200


def test_appointments_page(client):
    response = client.get("/appointments")
    assert response.status_code == 200

def test_doctors_page_contains_doctors(client):
    response = client.get("/doctors")
    assert b"Cardiologist" in response.data
    assert b"General Physician" in response.data
