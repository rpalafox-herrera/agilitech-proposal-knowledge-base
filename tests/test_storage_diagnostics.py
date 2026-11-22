from types import SimpleNamespace
import pytest
from storage3.exceptions import StorageApiError
from kb.service import storage_failure,KBError

@pytest.mark.parametrize('code,status,message,expected',[
 ('NoSuchBucket',400,'Bucket not found','Bucket not found'),
 ('InvalidJWT',400,'Invalid JWT','Authentication failed'),
 ('InvalidKey',401,'Not authorized','Authentication failed'),
 ('AccessDenied',403,'Access denied','access was denied'),
 ('PayloadTooLarge',413,'Too large','file size'),
 ('InvalidMimeType',415,'MIME not allowed','file type'),
 ('NotFound',404,'Missing','not found'),
 ('ServerError',500,'Unexpected','Storage logs'),
])
def test_safe_status_categories(code,status,message,expected):
 error=StorageApiError(message+' fictional-secret-must-not-leak',code,status)
 result=str(storage_failure(error))
 assert expected in result and str(status) in result
 assert 'fictional-secret-must-not-leak' not in result


def test_connection_failure_does_not_expose_url_or_key():
 result=str(storage_failure(RuntimeError('https://secret.invalid/?key=fictional-secret')))
 assert 'connection' in result and 'fictional-secret' not in result


def test_cloud_upload_rejection_is_not_reported_as_disk_failure(kb):
 class Bucket:
  def upload(self,*a,**kw):raise StorageApiError('Bucket not found','NoSuchBucket',400)
  def remove(self,*a):raise AssertionError('Nothing was uploaded, so cleanup must not remove any object')
 kb.supabase=SimpleNamespace(storage=SimpleNamespace(from_=lambda name:Bucket()))
 with pytest.raises(KBError,match='Bucket not found'):
  kb.upload('fictional.txt',b'FICTIONAL upload diagnostic')
 assert kb.count_documents()==0


def test_upload_sends_actual_mime_type(kb):
 recorded={}
 class Bucket:
  def upload(self,key,data,options):recorded.update(options)
 kb.supabase=SimpleNamespace(storage=SimpleNamespace(from_=lambda name:Bucket()))
 kb.upload('fictional.txt',b'FICTIONAL upload metadata')
 assert recorded['content-type']=='text/plain'


def test_read_only_connection_check(kb):
 called=[]
 kb.supabase=SimpleNamespace(storage=SimpleNamespace(get_bucket=lambda name:called.append(name)))
 assert 'metadata is accessible' in kb.check_storage()
 assert called==[kb.supabase_bucket]


def test_real_storage_sdk_upload_with_offline_http_transport(kb):
 import httpx
 from storage3 import SyncStorageClient
 requests=[]
 def respond(request):
  requests.append(request)
  return httpx.Response(200,json={'Key':'proposal-files/uploads/fictional.txt','Id':'fictional-id'})
 with httpx.Client(transport=httpx.MockTransport(respond)) as http:
  storage=SyncStorageClient('https://fictional.invalid/storage/v1',{},http_client=http)
  kb.supabase=SimpleNamespace(storage=storage)
  ident=kb.upload('fictional.txt',b'FICTIONAL real SDK serialization')
  assert kb.get_document(ident) is not None
  assert len(requests)==1 and requests[0].method=='POST'
  assert requests[0].headers['content-type'].startswith('multipart/form-data')
  assert b'Content-Type: text/plain' in requests[0].content
  assert b'FICTIONAL real SDK serialization' in requests[0].content


def test_sqlite_failure_is_distinguished_from_cloud_failure(kb,monkeypatch):
 from contextlib import contextmanager
 import sqlite3
 original=kb.connect
 calls=[]
 @contextmanager
 def connection():
  calls.append(True)
  if len(calls)==2:raise sqlite3.OperationalError('simulated schema mismatch')
  with original() as db:yield db
 monkeypatch.setattr(kb,'connect',connection)
 with pytest.raises(KBError,match='SQLite'):
  kb.upload('fictional.txt',b'FICTIONAL database error')
 assert not list(kb.uploads.iterdir())
