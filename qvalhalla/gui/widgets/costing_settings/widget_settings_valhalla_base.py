from qgis.gui import QgsDoubleSpinBox, QgsSpinBox
from qgis.PyQt.QtWidgets import QCheckBox, QComboBox, QWidget


class ValhallaSettingsBase(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

    def get_params(self, include_info: bool = False) -> dict:
        """
        Retrieves values from a settings widget's children.

        :param include_info: If set to true, each parameter's type will be derived from the widget type and
                             returned along with the parameter value. If the type is one of [float, int],
                             its min and max values will also be returned. Convenience for setting up the
                             processing algorithms.
        """

        params = dict()
        for layout in self.children():
            for child in layout.children():
                param_name = child.objectName().rstrip("_")
                label_identifier = f"{child.objectName()}_label".replace("__", "_")
                param_info = dict()
                if any((isinstance(child, box) for box in (QgsSpinBox, QgsDoubleSpinBox))):
                    param_info["value"] = child.value()
                    param_info["type"] = int if isinstance(child, QgsSpinBox) else float
                    param_info["min"] = child.minimum()
                    param_info["max"] = child.maximum()

                    tooltip = getattr(self, label_identifier).toolTip()
                    param_info["help"] = tooltip

                    params[param_name] = param_info
                elif isinstance(child, QCheckBox):
                    param_info["value"] = child.isChecked()
                    param_info["type"] = bool

                    tooltip = getattr(self, label_identifier).toolTip()
                    param_info["help"] = tooltip

                    params[param_name] = param_info
                elif isinstance(child, QComboBox):
                    param_info["value"] = child.currentText()
                    param_info["type"] = str

                    tooltip = getattr(self, label_identifier).toolTip()
                    param_info["help"] = tooltip

                    params[param_name] = param_info

        if include_info:
            return params

        return {k: v["value"] for k, v in params.items()}
