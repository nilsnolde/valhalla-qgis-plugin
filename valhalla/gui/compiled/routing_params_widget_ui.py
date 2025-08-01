# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'valhalla/resources/ui/routing_params_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RoutingParams(object):
    def setupUi(self, RoutingParams):
        RoutingParams.setObjectName("RoutingParams")
        RoutingParams.resize(693, 606)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RoutingParams.sizePolicy().hasHeightForWidth())
        RoutingParams.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(RoutingParams)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ui_reset_settings = QtWidgets.QToolButton(RoutingParams)
        icon = QtGui.QIcon.fromTheme(":images/themes/default/mActionRedo.svg")
        self.ui_reset_settings.setIcon(icon)
        self.ui_reset_settings.setObjectName("ui_reset_settings")
        self.horizontalLayout_2.addWidget(self.ui_reset_settings)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 10)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.ui_extra_box = gui.QgsCollapsibleGroupBox(RoutingParams)
        self.ui_extra_box.setCheckable(True)
        self.ui_extra_box.setChecked(False)
        self.ui_extra_box.setCollapsed(True)
        self.ui_extra_box.setSaveCheckedState(True)
        self.ui_extra_box.setObjectName("ui_extra_box")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.ui_extra_box)
        self.verticalLayout_3.setContentsMargins(7, 7, 0, 7)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ui_extra_json = QtWidgets.QTextEdit(self.ui_extra_box)
        self.ui_extra_json.setObjectName("ui_extra_json")
        self.verticalLayout_3.addWidget(self.ui_extra_json)
        self.verticalLayout.addWidget(self.ui_extra_box)
        self.ui_time_box = gui.QgsCollapsibleGroupBox(RoutingParams)
        self.ui_time_box.setCheckable(True)
        self.ui_time_box.setChecked(False)
        self.ui_time_box.setCollapsed(True)
        self.ui_time_box.setObjectName("ui_time_box")
        self.formLayout = QtWidgets.QFormLayout(self.ui_time_box)
        self.formLayout.setContentsMargins(7, 7, 0, 7)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.ui_time_box)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.ui_date_time_value = gui.QgsDateTimeEdit(self.ui_time_box)
        self.ui_date_time_value.setAllowNull(False)
        self.ui_date_time_value.setObjectName("ui_date_time_value")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.ui_date_time_value)
        self.label_2 = QtWidgets.QLabel(self.ui_time_box)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ui_time_current = QtWidgets.QRadioButton(self.ui_time_box)
        self.ui_time_current.setChecked(True)
        self.ui_time_current.setObjectName("ui_time_current")
        self.horizontalLayout_4.addWidget(self.ui_time_current)
        self.ui_time_depart = QtWidgets.QRadioButton(self.ui_time_box)
        self.ui_time_depart.setObjectName("ui_time_depart")
        self.horizontalLayout_4.addWidget(self.ui_time_depart)
        self.ui_time_arrive = QtWidgets.QRadioButton(self.ui_time_box)
        self.ui_time_arrive.setObjectName("ui_time_arrive")
        self.horizontalLayout_4.addWidget(self.ui_time_arrive)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.ui_time_box)
        self.exclude_geometries_box = gui.QgsCollapsibleGroupBox(RoutingParams)
        self.exclude_geometries_box.setCollapsed(True)
        self.exclude_geometries_box.setObjectName("exclude_geometries_box")
        self.formLayout_5 = QtWidgets.QFormLayout(self.exclude_geometries_box)
        self.formLayout_5.setContentsMargins(7, 7, 0, 7)
        self.formLayout_5.setObjectName("formLayout_5")
        self.exclude_locations_label = QtWidgets.QLabel(self.exclude_geometries_box)
        self.exclude_locations_label.setOpenExternalLinks(True)
        self.exclude_locations_label.setObjectName("exclude_locations_label")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.exclude_locations_label)
        self.exclude_locations = gui.QgsMapLayerComboBox(self.exclude_geometries_box)
        self.exclude_locations.setAllowEmptyLayer(True)
        self.exclude_locations.setObjectName("exclude_locations")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.exclude_locations)
        self.exclude_polygons_label = QtWidgets.QLabel(self.exclude_geometries_box)
        self.exclude_polygons_label.setOpenExternalLinks(True)
        self.exclude_polygons_label.setObjectName("exclude_polygons_label")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.exclude_polygons_label)
        self.exclude_polygons = gui.QgsMapLayerComboBox(self.exclude_geometries_box)
        self.exclude_polygons.setAllowEmptyLayer(True)
        self.exclude_polygons.setObjectName("exclude_polygons")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.exclude_polygons)
        self.verticalLayout.addWidget(self.exclude_geometries_box)
        self.ui_metric_box = gui.QgsCollapsibleGroupBox(RoutingParams)
        self.ui_metric_box.setCollapsed(True)
        self.ui_metric_box.setObjectName("ui_metric_box")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui_metric_box)
        self.horizontalLayout_5.setContentsMargins(7, 7, 0, 7)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui_metric_fastest = QtWidgets.QRadioButton(self.ui_metric_box)
        self.ui_metric_fastest.setChecked(True)
        self.ui_metric_fastest.setObjectName("ui_metric_fastest")
        self.horizontalLayout_5.addWidget(self.ui_metric_fastest)
        self.ui_metric_shortest = QtWidgets.QRadioButton(self.ui_metric_box)
        self.ui_metric_shortest.setObjectName("ui_metric_shortest")
        self.horizontalLayout_5.addWidget(self.ui_metric_shortest)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.verticalLayout.addWidget(self.ui_metric_box)
        self.ui_settings_stacked = QtWidgets.QStackedWidget(RoutingParams)
        self.ui_settings_stacked.setObjectName("ui_settings_stacked")
        self.verticalLayout.addWidget(self.ui_settings_stacked)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)

        self.retranslateUi(RoutingParams)
        QtCore.QMetaObject.connectSlotsByName(RoutingParams)

    def retranslateUi(self, RoutingParams):
        _translate = QtCore.QCoreApplication.translate
        RoutingParams.setWindowTitle(_translate("RoutingParams", "Form"))
        self.ui_reset_settings.setToolTip(_translate("RoutingParams", "<html><head/><body><p>Resets the costing settings of the</p><p>currently selected profile as well as</p><p>for the global costing settings</p></body></html>"))
        self.ui_reset_settings.setText(_translate("RoutingParams", "..."))
        self.ui_extra_box.setToolTip(_translate("RoutingParams", "Supply extra JSON parameters"))
        self.ui_extra_box.setTitle(_translate("RoutingParams", "Extra JSON "))
        self.ui_extra_json.setPlaceholderText(_translate("RoutingParams", "E.g. {\"options\": {\"ignore_restrictions\": true}}"))
        self.ui_time_box.setTitle(_translate("RoutingParams", "Time settings"))
        self.label.setText(_translate("RoutingParams", "Date & Time"))
        self.label_2.setText(_translate("RoutingParams", "Type"))
        self.ui_time_current.setText(_translate("RoutingParams", "Current"))
        self.ui_time_depart.setText(_translate("RoutingParams", "Depart"))
        self.ui_time_arrive.setText(_translate("RoutingParams", "Arrive"))
        self.exclude_geometries_box.setTitle(_translate("RoutingParams", "Exclude geometries"))
        self.exclude_locations_label.setToolTip(_translate("RoutingParams", "<html><head/><body><p>A set of locations to exclude or avoid within a route. The avoid_locations are mapped to the closest road or roads and these roads are excluded from the route path computation.</p></body></html>"))
        self.exclude_locations_label.setText(_translate("RoutingParams", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#other-request-options\"><span style=\" text-decoration: underline; color:#000000;\">Exclude locations</span></a></p></body></html>"))
        self.exclude_polygons_label.setToolTip(_translate("RoutingParams", "<html><head/><body><p>One or multiple exterior rings of polygons. Roads intersecting these rings will be avoided during path finding. If you only need to avoid a few specific roads, it\'s <span style=\" font-weight:600;\">much</span> more efficient to use <span style=\" font-family:\'.SF NS Mono\';\">exclude_locations</span>.</p></body></html>"))
        self.exclude_polygons_label.setText(_translate("RoutingParams", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#other-request-options\"><span style=\" text-decoration: underline; color:#000000;\">Exclude polygons</span></a></p></body></html>"))
        self.ui_metric_box.setToolTip(_translate("RoutingParams", "<html><head/><body><p>If shortest is selected, Valhalla will solely use distance as cost and disregard all other costs, penalties and factors.</p></body></html>"))
        self.ui_metric_box.setTitle(_translate("RoutingParams", "Routing metric"))
        self.ui_metric_fastest.setText(_translate("RoutingParams", "fastest"))
        self.ui_metric_shortest.setText(_translate("RoutingParams", "shortest"))
from qgis import gui
