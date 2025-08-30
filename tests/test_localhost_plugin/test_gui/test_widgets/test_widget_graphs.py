from shutil import rmtree

from qgis.PyQt.QtTest import QSignalSpy
from qvalhalla.core.settings import ValhallaSettings
from qvalhalla.gui.dlg_plugin_settings import PluginSettingsDialog
from qvalhalla.gui.widgets.widget_graphs import GraphWidget

from .... import TEST_DIR, LocalhostPluginTestCase


class TestWidget(LocalhostPluginTestCase):
    def test_pbf_build(self):
        pbf_path = TEST_DIR.joinpath("data", "andorra-latest.osm.pbf")
        self.assertTrue(pbf_path.exists())

        old_graph_dir = ValhallaSettings().get_graph_dir()
        new_graph_dir = pbf_path.parent.joinpath("graph_dir")
        ValhallaSettings().set_graph_dir(new_graph_dir)

        settings_dlg = PluginSettingsDialog()  # technically already has a graph widget..
        graphs_dlg = GraphWidget(settings_dlg)

        root = graphs_dlg.ui_list_graphs.rootIndex()
        self.assertEqual(graphs_dlg.ui_list_graphs.model().rowCount(root), 0)

        graphs_dlg.from_pbf_dlg.ui_pbf_file.setFilePath(str(pbf_path.resolve()))
        graphs_dlg.from_pbf_dlg.ui_text_name.setText("andorra")

        build_action = graphs_dlg.ui_btn_graph_add_tar.menu().actions()[2]
        build_action.trigger()

        graphs_dlg.from_pbf_dlg.accept()

        # should finish within 5 secs
        spy_fin = QSignalSpy(graphs_dlg.valhalla_build_admins.finished)
        self.assertTrue(spy_fin.wait(5000))
        exit_code, _ = spy_fin[-1]
        self.assertEqual(exit_code, 0)

        # should finish within 10 secs
        spy_fin = QSignalSpy(graphs_dlg.valhalla_build_tiles.finished)
        self.assertTrue(spy_fin.wait(10000))
        exit_code, _ = spy_fin[-1]
        self.assertEqual(exit_code, 0)

        # the list updated
        root = graphs_dlg.ui_list_graphs.rootIndex()
        self.assertEqual(graphs_dlg.ui_list_graphs.model().rowCount(root), 1)

        # cleanup
        rmtree(new_graph_dir)
        ValhallaSettings().set_graph_dir(old_graph_dir)
