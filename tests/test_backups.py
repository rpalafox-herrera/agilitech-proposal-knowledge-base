from io import BytesIO
from zipfile import ZipFile
import pytest
from kb.backups import create_backup,restore_backup
from kb.service import KnowledgeBase,KBError


def test_backup_restore_search_metadata_and_originals(kb,tmp_path):
    ident=kb.upload('fictional.txt',b'FICTIONAL persistent water recovery',{'industry':'Water','proposal_year':2020})
    original=kb.read_original(ident)
    archive=tmp_path/'backup.zip';archive.write_bytes(create_backup(kb))
    assert restore_backup(archive,tmp_path/'restored')==1
    restored=KnowledgeBase(tmp_path/'restored')
    assert restored.read_original(ident)==original
    assert restored.search('"water recovery"',{'industry':'Water','proposal_year':2020})[0]['id']==ident
    assert restored.get_document(ident)['title']=='fictional'
    # Reopen yet again, independently of the source database connection.
    assert KnowledgeBase(tmp_path/'restored').count_documents()==1


def test_restore_refuses_overwrite(kb,tmp_path):
    kb.upload('a.txt',b'fictional')
    archive=tmp_path/'backup.zip';archive.write_bytes(create_backup(kb))
    with pytest.raises(KBError,match='empty'):restore_backup(archive,kb.data_dir)
    assert kb.count_documents()==1


def test_backup_refuses_missing_or_changed_original(kb):
    ident=kb.upload('a.txt',b'fictional')
    kb._file(kb.get_document(ident)['file_location']).write_bytes(b'changed')
    with pytest.raises(KBError,match='checksum'):create_backup(kb)


def test_restore_rejects_traversal_and_damaged_archive(tmp_path):
    archive=tmp_path/'bad.zip'
    with ZipFile(archive,'w') as z:z.writestr('../outside.txt','bad')
    with pytest.raises(KBError,match='unsafe'):restore_backup(archive,tmp_path/'new')
    assert not (tmp_path/'outside.txt').exists()
    archive.write_bytes(b'broken')
    with pytest.raises(KBError):restore_backup(archive,tmp_path/'new')
