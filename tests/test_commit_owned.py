"""A shared-worktree commit never sweeps another program's pending ledger row."""
import json
import subprocess
import pytest
from scripts.commit_owned import commit_owned


def git(root,*args):
    return subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True).stdout


def repo(tmp_path):
    git(tmp_path,'init','-q')
    git(tmp_path,'config','user.name','Synthetic Test')
    git(tmp_path,'config','user.email','test@example.invalid')
    (tmp_path/'ledger.json').write_text(json.dumps({'programs':[{'program_id':'a','value':0},{'program_id':'b','value':0}]}))
    (tmp_path/'owned.txt').write_text('before')
    git(tmp_path,'add','.')
    git(tmp_path,'commit','-qm','initial')
    return tmp_path


def test_only_owned_ledger_row_and_file_are_committed(tmp_path):
    root=repo(tmp_path)
    (root/'ledger.json').write_text(json.dumps({'programs':[{'program_id':'a','value':1},{'program_id':'b','value':2}]}))
    (root/'owned.txt').write_text('after')
    commit_owned(root,'owned batch',['owned.txt'],['ledger.json:a'])
    committed=json.loads(git(root,'show','HEAD:ledger.json'))
    assert [r['value'] for r in committed['programs']]==[1,0]
    assert [r['value'] for r in json.loads((root/'ledger.json').read_text())['programs']]==[1,2]
    assert git(root,'show','HEAD:owned.txt')=='after'


def test_existing_staging_is_preserved_and_commit_refused(tmp_path):
    root=repo(tmp_path)
    (root/'owned.txt').write_text('someone else staged this')
    git(root,'add','owned.txt')
    head=git(root,'rev-parse','HEAD')
    with pytest.raises(ValueError,match='already contains staged work'):
        commit_owned(root,'must not commit',[],['ledger.json:a'])
    assert git(root,'rev-parse','HEAD')==head
    assert git(root,'show',':owned.txt')=='someone else staged this'
