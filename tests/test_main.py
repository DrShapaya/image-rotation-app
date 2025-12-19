from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Поворот изображения" in response.text

def test_process_without_file():
    response = client.post("/process", data={
        "session_id": "fake",
        "captcha_input": "123",
        "angle": "45"
    })
    assert response.status_code == 400
