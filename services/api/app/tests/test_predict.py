from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_endpoint():
    response = client.post("/predict", json={"message": "You won a free prize!"})
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "confidence" in data
