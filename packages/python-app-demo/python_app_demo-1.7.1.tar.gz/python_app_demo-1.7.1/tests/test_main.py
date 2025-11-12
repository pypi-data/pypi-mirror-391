from app.main import greet


def test_greet_default():
    assert greet("世界") == "你好，世界！"

