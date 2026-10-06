import io
import os
import sys
from contextlib import asynccontextmanager
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import MLModels, app


@pytest.fixture
def client():
    ocr = MagicMock()
    ocr.readtext.return_value = ["line1", "line2"]
    tok = MagicMock()
    tok.return_value.to.return_value = {"input_ids": []}
    tok.decode.return_value = "fake summary"
    summr = MagicMock()
    summr.generate.return_value = [[]]

    @asynccontextmanager
    async def _lifespan(application):
        application.state.ml_models = MLModels(ocr=ocr,tokenizer=tok, summarizer=summr)
    yield
    if hasattr(application.state, "ml_models"):
        del application.state.ml_models
    orig_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _lifespan
    with TestClient(app) as tc:
        yield tc
    app.router.lifespan_context = orig_lifespan


def test_redirect_to_docs(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers.get("location") == "/docs"


def test_image_to_text_success(client):
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), "white").save(buf, "PNG")
    buf.seek(0)
    files = {"file": ("test.png", buf, "image/png")}
    r = client.post("/api/image-to-text", files=files)
    assert r.status_code == 200
    payload = r.json()
    assert payload["filename"] == "test.png"
    assert payload["raw_lines_count"] == 2
    assert "line1 line2" in payload["extracted_text"]


def test_image_to_text_invalid_format(client):
    files = {"file": ("doc.txt", io.BytesIO(b"not an image"), "text / plain")}
    r = client.post("/api/image-to-text", files=files)
    assert r.status_code == 400
    assert "Unsupported file format" in r.json()["detail"]


def test_summarize_success(client):
    text = " ".join(["very long text"] * 15)
    r = client.post("/api/summarize", data={"text": text})
    assert r.status_code == 200
    payload = r.json()
    assert payload["original_length"] == len(text)
    assert payload["summary"] == "fake summary"


def test_summarize_too_short(client):
    r = client.post("/api/summarize", data={"text":
                                                "short"})
    assert r.status_code == 400
    assert "too short" in r.json()["detail"].lower()
