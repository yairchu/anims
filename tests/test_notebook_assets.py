from types import SimpleNamespace
import unittest
from unittest.mock import patch

from marimo._runtime.virtual_file import VirtualFileLifecycleItem
from hamas_neches import app


class NotebookAssetTests(unittest.TestCase):
    def test_preview_uses_served_image_urls_and_stays_small(self):
        # Exercise real marimo URL generation without a listening server.
        files = {}
        registry = SimpleNamespace(has=lambda name: name in files,
                                   add=lambda file, ctx: files.update({file.filename: file}))
        context = SimpleNamespace(virtual_files_supported=True, virtual_file_registry=registry)
        with patch.object(VirtualFileLifecycleItem, 'add_to_cell_lifecycle_registry',
                          lambda item: item.create(context)):
            _, values = app.run(defs={
                'scene_choice': SimpleNamespace(value='blocked'),
                'control_mode': SimpleNamespace(value='Manual'),
                'video_format': SimpleNamespace(value='portrait'),
            })
        self.assertNotIn('data:image', values['scene_svg'])
        self.assertLess(len(values['scene_svg'].encode()), 100_000)
        for actor in ('netanyahu', 'abbas', 'smotrich'):
            self.assertTrue(values['preview_assets'][actor].startswith('./@file/'))
        self.assertGreater(sum(len(file.buffer) for file in files.values()), 1_000_000)
        # Scrubbing reads URLs; the asset loader cell does not depend on time.
        asset_cell = next(cell for cell in app._graph.cells.values() if 'preview_assets' in cell.defs)
        self.assertEqual(asset_cell.refs, {'notebook_asset_urls'})


if __name__ == '__main__':
    unittest.main()
