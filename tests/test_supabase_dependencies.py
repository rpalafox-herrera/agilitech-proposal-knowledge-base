"""Use the real SDK without contacting any service or using real credentials."""
from importlib.metadata import version
import builtins
import socket

import pytest

from kb.service import KnowledgeBase, KBError


def test_real_supabase_sdk_initializes_offline(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError('Client construction must not access a real network service.')
    monkeypatch.setattr(socket.socket, 'connect', no_network)
    monkeypatch.setattr(socket.socket, 'connect_ex', no_network)
    monkeypatch.setenv('SUPABASE_URL', 'https://fictional-example.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'fictional-placeholder-not-a-real-key')
    kb = KnowledgeBase(tmp_path)
    assert kb.original_storage == 'Supabase'
    assert kb.supabase.storage.from_('proposal-files') is not None
    assert kb.supabase.postgrest is not None
    assert kb.supabase.functions is not None
    assert kb.count_documents() == 0


def test_installed_supabase_release_family_is_aligned():
    for package in ['supabase', 'supabase-auth', 'postgrest', 'storage3', 'realtime', 'supabase-functions']:
        assert version(package) == '2.20.0', f'{package} must match the pinned SDK release family'


def test_missing_sdk_reports_dependency_error_without_exposing_key(tmp_path, monkeypatch):
    original_import = builtins.__import__
    def broken_import(name, *args, **kwargs):
        if name == 'supabase':
            raise ModuleNotFoundError("No module named 'supabase_auth.http_clients'")
        return original_import(name, *args, **kwargs)
    monkeypatch.setenv('SUPABASE_URL', 'https://fictional-example.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'fictional-key-must-not-appear-in-error')
    monkeypatch.setattr(builtins, '__import__', broken_import)
    with pytest.raises(KBError, match='dependencies') as error:
        KnowledgeBase(tmp_path)
    assert 'fictional-key-must-not-appear-in-error' not in str(error.value)
