from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def token() -> str:
    response = client.post('/api/v1/auth/login', json={'email': 'founder@arxivcopilot.ai', 'password': 'research'})
    assert response.status_code == 200
    return response.json()['access_token']


def test_login_dashboard_and_chat_flow():
    access_token = token()
    headers = {'Authorization': f'Bearer {access_token}'}
    dashboard = client.get('/api/v1/dashboard', headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()['reading_stats']['read'] == 128
    chat = client.post('/api/v1/papers/attention/chat', json={'message': 'What method is used?'}, headers=headers)
    assert chat.status_code == 200
    assert 'Attention Is All You Need' in chat.json()['answer']


def test_feed_and_graph_are_public():
    assert client.get('/api/v1/feed').status_code == 200
    graph = client.get('/api/v1/graph')
    assert graph.status_code == 200
    assert graph.json()['edges']
