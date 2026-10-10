"""O ZIP não pode transportar segredos, cópias anteriores ou a si mesmo."""
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('delivery', Path(__file__).parents[1] / 'scripts/package_delivery.py')
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)

class DeliveryTests(unittest.TestCase):
    def test_clean_repeatable_archive_and_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['README.md', '.env.example', 'app/main.py', '.env.production', '.env', 'node_modules/a.js', 'deliveries/old.zip', '.git/config', '.aws/credentials', 'debug.log']:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('example', encoding='utf-8')
            output = root / 'deliveries/test.zip'
            for _ in range(2):
                delivery.build_package(root, output)
                with zipfile.ZipFile(output) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(set(archive.namelist()), {'README.md', '.env.example', 'app/main.py'})
                    archive.extractall(root / 'deliveries/extracted')
                self.assertEqual((root / 'deliveries/extracted/README.md').read_text(), 'example')

if __name__ == '__main__':
    unittest.main()
