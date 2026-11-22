from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from kariyer import new
from kayit import SaveError, backup_path, encode, load_game, save_game


class SaveSafety(TestCase):
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
