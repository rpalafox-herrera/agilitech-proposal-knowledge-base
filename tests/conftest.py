import pytest
from kb.service import KnowledgeBase

@pytest.fixture(autouse=True)
def local_only(monkeypatch):
    for key in ['SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','FIREBASE_SERVICE_ACCOUNT_JSON','FIREBASE_STORAGE_BUCKET']:
        monkeypatch.delenv(key, raising=False)

@pytest.fixture
def kb(tmp_path):
    return KnowledgeBase(tmp_path / 'library')
