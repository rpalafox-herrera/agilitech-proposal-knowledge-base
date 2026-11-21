from io import BytesIO
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import sys
import pytest
from docx import Document
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from kb.service import KnowledgeBase, KBError, DuplicateDocument
from kb.extraction import extract


def pdf_bytes():
    buffer=BytesIO();pdf=canvas.Canvas(buffer)
    pdf.drawString(50,750,'FICTIONAL sample water recovery.');pdf.showPage()
    pdf.drawString(50,750,'industrial electrical construction');pdf.showPage();pdf.save()
    return buffer.getvalue()


def docx_bytes():
    buffer=BytesIO();doc=Document();doc.add_paragraph('FICTIONAL solar installation planning')
    table=doc.add_table(rows=1,cols=2);table.cell(0,0).text='Automation';table.cell(0,1).text='controls review'
    doc.save(buffer);return buffer.getvalue()


@pytest.mark.parametrize('name,data,query,location',[
    ('sample.pdf',pdf_bytes(),'"water recovery"','Page 1'),
    ('sample.docx',docx_bytes(),'"solar installation"','Paragraph 1'),
    ('sample.txt',b'FICTIONAL water recovery','"water recovery"','Lines 1-1')])
def test_upload_extract_search_download_and_reopen(kb,name,data,query,location):
    ident=kb.upload(name,data)
    assert kb.read_original(ident)==data
    assert kb.search(query)[0]['id']==ident
    assert kb.search(query)[0]['sources'][0]['location']==location
    assert KnowledgeBase(kb.data_dir).read_original(ident)==data
    assert KnowledgeBase(kb.data_dir).search(query)[0]['id']==ident


def test_cross_page_search_and_docx_tables(kb):
    ident=kb.upload('sample.pdf',pdf_bytes())
    assert kb.search('water electrical')[0]['id']==ident
    assert not kb.search('"water electrical"')
    output=extract('sample.docx',docx_bytes())
    assert any(s['location']=='Table 1, row 1' and 'Automation' in s['text'] for s in output.segments)


def test_duplicate_hash_and_same_filename(kb):
    kb.upload('one.txt',b'FICTIONAL identical text')
    with pytest.raises(DuplicateDocument):kb.upload('renamed.txt',b'FICTIONAL identical text')
    kb.upload('one.txt',b'FICTIONAL different text')
    assert kb.count_documents()==2
    assert len(list(kb.uploads.iterdir()))==2


@pytest.mark.parametrize('filters,count',[
    ({'industry':'Water'},1),({'proposal_year':2020},1),({'engineering_discipline':'Electrical'},1),
    ({'project_type':'Study'},1),({'industry':'Other'},0),({'proposal_year':'Unknown'},1),
    ({'industry':'Water','proposal_year':2020,'engineering_discipline':'Electrical','project_type':'Study'},1)])
def test_filters(kb,filters,count):
    kb.upload('a.txt',b'fictional water recovery',{'industry':'Water','proposal_year':2020,'engineering_discipline':'Electrical','project_type':'Study'})
    kb.upload('b.txt',b'fictional solar installation')
    assert kb.count_documents(filters)==count
    assert len(kb.search('fictional',filters))==count
    assert kb.count_search('fictional',filters)==count


def test_metadata_index_update_unknown_and_original(kb):
    ident=kb.upload('one.txt',b'FICTIONAL equipment review')
    assert kb.get_document(ident)['industry']=='Unknown'
    assert kb.get_document(ident)['proposal_year'] is None
    kb.update_metadata(ident,{'title':'Uniqueupdatedtitle','industry':'Water','description':'newdescription'})
    assert kb.search('Uniqueupdatedtitle')[0]['id']==ident
    assert kb.search('newdescription')[0]['id']==ident
    assert kb.filter_options()['industry']==['Water']
    assert kb.read_original(ident)==b'FICTIONAL equipment review'


def test_ranking_and_unique_results(kb):
    a=kb.upload('focused.txt',b'water recovery water recovery water recovery')
    b=kb.upload('broad.txt',('water recovery '+'different topic '*100).encode())
    results=kb.search('water recovery')
    assert [r['id'] for r in results]==[a,b]
    assert results[0]['score'] <= results[1]['score']


def test_confirmation_and_deletion_cleans_original_segments_and_indexes(kb):
    ident=kb.upload('one.txt',b'uniquedeletiontoken')
    path=kb._file(kb.get_document(ident)['file_location'])
    with pytest.raises(KBError,match='Confirm'):kb.delete_document(ident)
    assert kb.count_documents()==1 and path.exists()
    kb.delete_document(ident,confirmed=True)
    assert not path.exists() and kb.count_documents()==0
    assert not kb.search('uniquedeletiontoken') and not kb.get_segments(ident)
    with kb.connect() as db:
        assert not db.execute("SELECT rowid FROM segments_fts WHERE segments_fts MATCH 'uniquedeletiontoken'").fetchall()
        db.execute("INSERT INTO documents_fts(documents_fts,rank) VALUES('integrity-check',1)")
        db.execute("INSERT INTO segments_fts(segments_fts,rank) VALUES('integrity-check',1)")


def test_delete_file_error_rolls_back(kb,monkeypatch):
    ident=kb.upload('one.txt',b'fictional rollbacktoken')
    def fail(*a,**k):raise PermissionError('simulated lock')
    monkeypatch.setattr(Path,'rename',fail)
    with pytest.raises(KBError,match='retained'):kb.delete_document(ident,confirmed=True)
    assert kb.search('rollbacktoken') and kb.read_original(ident)


@pytest.mark.parametrize('name,data',[
    ('x.exe',b'hello'),('x.doc',b'hello'),('x.pdf',b'bad pdf'),('x.docx',b'bad docx'),
    ('x.txt',b''),('x.txt',b' \n'),('x.txt',b'a\x00b'),('x.txt',b'\x81'),('x.txt',b'x'*(20*1024*1024+1))])
def test_bad_upload_never_saves(kb,name,data):
    with pytest.raises(KBError):kb.upload(name,data)
    assert kb.count_documents()==0 and not list(kb.uploads.iterdir())


def test_pdf_scans_encryption_and_limits(kb):
    writer=PdfWriter();writer.add_blank_page(100,100);data=BytesIO();writer.write(data)
    with pytest.raises(KBError,match='OCR'):kb.upload('scan.pdf',data.getvalue())
    writer.encrypt('secret');data=BytesIO();writer.write(data)
    with pytest.raises(KBError,match='Encrypted'):kb.upload('password.pdf',data.getvalue())


@pytest.mark.parametrize('year',['1800','nope','2020.5','2101'])
def test_invalid_year(kb,year):
    with pytest.raises(KBError):kb.upload('one.txt',b'fictional',{'proposal_year':year})
    assert not list(kb.uploads.iterdir())


def test_safe_names_search_input_and_pagination(kb):
    ident=kb.upload('../../one.txt',b'FICTIONAL water recovery')
    assert kb.get_document(ident)['original_filename']=='one.txt'
    with pytest.raises(KBError):kb._file('../../outside.txt')
    for q in ['NEAR(water recovery)',"water'; DROP TABLE documents; --",'water OR recovery','***']:
        kb.search(q)
    with pytest.raises(KBError):kb.search('x'*501)
    with pytest.raises(KBError):kb.list_documents({'invalid':'x'})
    assert kb.count_documents()==1
    kb.upload('two.txt',b'FICTIONAL water solar')
    assert len(kb.list_documents(limit=1))==1
    assert kb.list_documents(limit=1)[0]['id']!=kb.list_documents(limit=1,offset=1)[0]['id']


@pytest.mark.parametrize('backend',['supabase','firebase'])
def test_optional_remote_originals_round_trip(tmp_path,monkeypatch,backend):
    files={}
    class Bucket:
        def upload(self,key,data,*a):files[key]=data
        def download(self,key):return files[key]
        def remove(self,keys):
            for key in keys:files.pop(key)
        def blob(self,key):
            return SimpleNamespace(upload_from_string=lambda data,**k:files.update({key:data}),
                download_as_bytes=lambda:files[key],delete=lambda:files.pop(key))
    bucket=Bucket()
    if backend=='supabase':
        monkeypatch.setenv('SUPABASE_URL','https://fictional.invalid');monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY','dummy')
        monkeypatch.setitem(sys.modules,'supabase',SimpleNamespace(create_client=lambda *a:SimpleNamespace(storage=SimpleNamespace(from_=lambda name:bucket))))
    else:
        monkeypatch.setenv('FIREBASE_SERVICE_ACCOUNT_JSON','{"project_id":"fictional"}')
        monkeypatch.setitem(sys.modules,'firebase_admin',SimpleNamespace(_apps={'mock':True},storage=SimpleNamespace(bucket=lambda:bucket),credentials=SimpleNamespace()))
    kb=KnowledgeBase(tmp_path/'cloud')
    ident=kb.upload('sample.txt',b'fictional remoteoriginal')
    assert kb.original_storage.lower()==backend
    assert kb.read_original(ident)==b'fictional remoteoriginal'
    assert not list(kb.uploads.iterdir())
    assert kb.search('remoteoriginal')
    kb.delete_document(ident,confirmed=True)
    assert not files and kb.count_documents()==0


def test_partial_supabase_config_fails_instead_of_silent_local_fallback(tmp_path,monkeypatch):
    monkeypatch.setenv('SUPABASE_URL','https://fictional.invalid')
    with pytest.raises(KBError,match='both'):KnowledgeBase(tmp_path)


def test_assistant_retrieval_idea_matching_and_storage_guidance(kb):
    from kb.assistant import Assistant
    from kb.project_ideas import ProjectIdeaMatcher
    ident=kb.upload('fictional.txt',b'FICTIONAL water recovery process controls and pump automation',{'industry':'Water/Wastewater'})
    result=ProjectIdeaMatcher(kb).analyze('We need water recovery and process controls',industry='Water/Wastewater')
    assert result['recommendations'][0]['id']==ident
    answer=Assistant(kb).answer('Explain the water recovery process',use_model=False,allow_navigation=False)
    assert answer['sources'] and answer['sources'][0]['document_id']==ident
    privacy=Assistant(kb).answer('Explain storage and backups',use_model=False)
    assert 'SQLite' in privacy['answer'] and 'temporary' in privacy['answer']
