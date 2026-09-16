import unittest

from marimo._runtime.runner.cell_runner import Runner
from marimo._runtime.watch._file import FileState

from hamas_neches import app


class NotebookWatcherTests(unittest.TestCase):
    def test_each_file_update_schedules_timeline_reload(self):
        # Script execution alone cannot catch lost reactive dependencies. Use
        # marimo's scheduler, which matches a changed state to direct cell refs.
        _, values = app.run()
        graph = app._graph
        runner = Runner(roots=set(), graph=graph, glbls=dict(values),
                        debugger=None, hooks=None)
        loader = next(cid for cid, cell in graph.cells.items()
                      if 'scene_timelines' in cell.defs)
        watchers = [value for value in values.values() if isinstance(value, FileState)]
        self.assertEqual({watcher.name for watcher in watchers},
                         {'timeline.json', 'timeline_blocked.json', 'sequence.json'})
        for watcher in watchers:
            with self.subTest(file=watcher.name):
                scheduled = runner.resolve_state_updates({watcher: 'external-file-change'})
                self.assertIn(loader, scheduled)


if __name__ == '__main__':
    unittest.main()
