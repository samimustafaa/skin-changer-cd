import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from safety import inspect_folder, create_backup, restore_backup, validate_package, SafetyError

class TestSafety(unittest.TestCase):
    def test_backup_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"game"
            (root/"res").mkdir(parents=True)
            p=root/"res"/"item.npk"
            p.write_bytes(b"NXPKoriginal")
            folder=create_backup(root,Path(tmp)/"backups",inspect_folder(root))
            p.write_bytes(b"modified")
            restore_backup(folder,root)
            self.assertEqual(p.read_bytes(),b"NXPKoriginal")

    def test_bad_archive_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.zip"
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("../escape",b"x")
                z.writestr("manifest.json","{}")
            with self.assertRaises(SafetyError):
                validate_package(path)

    def test_valid_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ok.zip"
            data=b"test model"
            m={"format":1,"name":"Test","target":"fashion-guru",
               "assets":[{"path":"assets/model.glb","sha256":hashlib.sha256(data).hexdigest()}]}
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("manifest.json",json.dumps(m))
                z.writestr("assets/model.glb",data)
            self.assertEqual(validate_package(path)["asset_count"],1)

if __name__=="__main__":
    unittest.main()
