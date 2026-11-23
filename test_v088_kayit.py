import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from kariyer import advance, new
from kayit import SaveError, backup_path, decode, encode, load_game, save_game


class SaveSafety(TestCase):
    def test_generated_legacy_schema_migrations(self):
        state=new('GALATASARAY',seed=888,models=False)
        for key in ('attribute_profile','position_model','lineup_model','staff_system'):
            state.pop(key,None)
        for version in (None,1,2):
            with self.subTest(version=version):
                raw=json.loads(encode(state))
                if version is None:
                    for key in ('schema_version','database_version','schedule','career_id','rng_state'):
                        del raw[key]
                else:
                    raw['schema_version']=version
                text=json.dumps(raw)
                restored=decode(text)
                self.assertEqual(encode(restored),encode(decode(text)))
                self.assertEqual(restored['schema_version'],3)
                self.assertNotIn('match_model',restored)
                self.assertNotIn('economy_model',restored)
                self.assertTrue(advance(restored))
                self.assertEqual(restored['week'],2)

    def test_invalid_utf8_primary_cannot_supersede_healthy_backup(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'career.json'
            state=new('GALATASARAY',manager='MANAGER_A',seed=881,match_model=4)
            save_game(state,path)
            first=path.read_bytes()
            state['manager']='MANAGER_B'
            save_game(state,path)
            damaged=path.read_bytes().replace(b'MANAGER_B',b'MANAGER_\xff')
            path.write_bytes(damaged)
            with self.assertRaises(SaveError):
                load_game(path)
            state['manager']='MANAGER_C'
            save_game(state,path)
            self.assertEqual(backup_path(path).read_bytes(),first)
            self.assertEqual(encode(load_game(path)),encode(state))

    def test_failed_atomic_replace_leaves_primary_and_no_temporary_file(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'career.json'
            state=new('GALATASARAY',seed=882,match_model=4)
            save_game(state,path)
            first=path.read_bytes()
            state['manager']='B'
            from kayit import os
            replace=os.replace
            def fail_primary(source,destination):
                if Path(destination)==path:
                    raise PermissionError('Simulated locked file')
                replace(source,destination)
            with patch('kayit.os.replace',side_effect=fail_primary):
                with self.assertRaises(PermissionError):
                    save_game(state,path)
            self.assertEqual(path.read_bytes(),first)
            self.assertEqual(backup_path(path).read_bytes(),first)
            self.assertFalse(list(path.parent.glob('*.tmp')))

    def test_shipped_synthetic_legacy_saves_round_trip_and_continue(self):
        import gzip
        fixture=Path(__file__).with_name('testdata')/'schema3-synthetic.json.gz'
        with gzip.open(fixture,'rt',encoding='utf8') as stream:
            cases=json.load(stream)
        self.assertEqual({(d['source'],d['model']) for d in cases},
                         {('0.8.6',m) for m in (1,2,3)}|{('0.8.7',m) for m in (1,2,3,4)})
        for case in cases:
            with self.subTest(version=case['source'],model=case['model']), TemporaryDirectory() as tmp:
                source=Path(tmp)/'original.json'
                dest=Path(tmp)/'resaved.json'
                original=json.dumps(case['save'],ensure_ascii=False).encode('utf8')
                source.write_bytes(original)
                a=load_game(source)
                save_game(a,dest)
                b=load_game(dest)
                self.assertEqual(source.read_bytes(),original)
                self.assertEqual((a['schema_version'],a['match_model'],a['week']),(3,case['model'],2))
                self.assertEqual(encode(a),encode(b))
                self.assertTrue(advance(a))
                self.assertTrue(advance(b))
                self.assertEqual(encode(a),encode(b))


class SaveDialogSafety(TestCase):
    def test_corrupt_primary_opens_backup_without_rewriting_either_file(self):
        import tkinter as tk
        from arayuz import UI

        with TemporaryDirectory() as tmp, patch.dict('os.environ',{'LOCALAPPDATA':tmp}):
            path=Path(tmp)/'career.json'
            career=new('GALATASARAY',seed=889,match_model=4)
            save_game(career,path)
            from copy import deepcopy
            from personel import medical_market
            upgraded=deepcopy(dict(career,workload_model=1))
            medical_market(upgraded)
            expected=encode(upgraded)
            self.assertTrue(advance(career))
            save_game(career,path)
            backup=backup_path(path)
            healthy=backup.read_bytes()
            corrupt=b'\xff'
            path.write_bytes(corrupt)
            root=tk.Tk()
            try:
                ui=UI(root)
                with patch('arayuz.filedialog.askopenfilename',return_value=str(path)), \
                     patch('arayuz.messagebox.askyesno',side_effect=[False,True]) as confirm:
                    ui.load()
                    self.assertIsNone(ui.s)
                    ui.load()
                self.assertEqual(confirm.call_count,2)
                self.assertEqual(json.loads(encode(ui.s)),json.loads(expected))
                self.assertEqual(path.read_bytes(),corrupt)
                self.assertEqual(backup.read_bytes(),healthy)
            finally:
                root.destroy()

    def test_legacy_save_directory_selected_and_autosave_stays_in_current_profile(self):
        import gzip
        import tkinter as tk
        from arayuz import UI
        from kayit import user_directory

        fixture=Path(__file__).with_name('testdata')/'schema3-synthetic.json.gz'
        with gzip.open(fixture,'rt',encoding='utf8') as stream:
            raw=next(case['save'] for case in json.load(stream)
                     if case['source']=='0.8.7' and case['model']==3)
        with TemporaryDirectory() as tmp, patch.dict('os.environ',{'LOCALAPPDATA':tmp}):
            current=user_directory()
            self.assertEqual(current.name,'v0.9.6')
            old=current.parent/'v0.8.7'/'saves'
            old.mkdir(parents=True)
            original=old/'career.json'
            raw_bytes=json.dumps(raw,ensure_ascii=False).encode('utf8')
            original.write_bytes(raw_bytes)
            root=tk.Tk()
            try:
                ui=UI(root)
                with patch('arayuz.filedialog.askopenfilename',return_value=str(original)) as picker:
                    ui.load()
                self.assertEqual(picker.call_args.kwargs['initialdir'],old)
                self.assertEqual((ui.s['match_model'],ui.s['week']),(3,2))
                ui.autosave()
                autosaves=list((current/'autosaves').glob('*.json'))
                self.assertEqual(len(autosaves),1)
                self.assertEqual(encode(load_game(autosaves[0])),encode(ui.s))
                self.assertEqual(list(old.iterdir()),[original])
                self.assertEqual(original.read_bytes(),raw_bytes)
            finally:
                root.destroy()
