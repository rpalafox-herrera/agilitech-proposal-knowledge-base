from pathlib import Path
from streamlit.testing.v1 import AppTest
from kb.service import KnowledgeBase

APP=Path(__file__).resolve().parents[1]/'app.py'


def test_start_navigation_metadata_delete_and_backup(tmp_path,monkeypatch):
    monkeypatch.setenv('AGILITECH_DATA_DIR',str(tmp_path/'ui'))
    kb=KnowledgeBase()
    ident=kb.upload('fictional.txt',b'FICTIONAL water recovery',{'industry':'Water/Wastewater'})
    at=AppTest.from_file(str(APP),default_timeout=30).run()
    assert not at.exception
    at.button(key='nav_search').click().run()
    at.text_input(key='search_query').set_value('"water recovery"').run()
    assert not at.exception
    assert any('fictional'==s.value for s in at.subheader)
    at.button(key='nav_upload').click().run()
    assert not at.exception
    at.button(key='nav_library').click().run()
    assert not at.exception
    at.text_input(key=f'edit_{ident}_title').set_value('FICTIONAL Updated')
    next(b for b in at.button if b.label=='Save metadata').click().run()
    assert not at.exception
    assert kb.get_document(ident)['title']=='FICTIONAL Updated'
    at.button(key='prepare_backup').click().run()
    assert not at.exception
    assert at.session_state['backup_bytes'][:2]==b'PK'
    at.checkbox(key=f'confirm_delete_{ident}').check().run()
    at.button(key=f'delete_{ident}').click().run()
    assert not at.exception
    assert kb.count_documents()==0
    at.button(key='nav_project_idea').click().run()
    assert not at.exception


def test_project_matching_without_local_ai_controls_or_model_calls(tmp_path, monkeypatch):
    from kb.assistant import Assistant
    monkeypatch.setenv('AGILITECH_DATA_DIR', str(tmp_path / 'matching'))
    kb = KnowledgeBase()
    kb.upload('fictional-water.txt', b'FICTIONAL water recovery process controls automation',
              {'industry': 'Water/Wastewater'})
    def no_model(*args, **kwargs):
        raise AssertionError('Project matching should not query a local AI model')
    monkeypatch.setattr(Assistant, 'status', no_model)
    monkeypatch.setattr(Assistant, 'answer', no_model)
    monkeypatch.setattr(Assistant, 'summarize_project_direction', no_model)
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    at.button(key='nav_project_idea').click().run()
    assert not at.exception
    assert not any('local AI' in c.label for c in at.checkbox)
    assert not any('Local AI' in c.value for c in at.caption)
    at.text_area(key='project_idea_input_all').set_value('We need water recovery and process controls references')
    next(b for b in at.button if b.label == 'Analyze project direction').click().run()
    assert not at.exception
    assert any('Recommended reference files (1 of 1)' in h.value for h in at.subheader)
    assert not any('local AI' in c.label for c in at.checkbox)
