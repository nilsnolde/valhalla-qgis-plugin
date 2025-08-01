# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'valhalla/resources/ui/routing_settings_valhalla_pedestrian_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_settings_valhalla_pedestrian(object):
    def setupUi(self, settings_valhalla_pedestrian):
        settings_valhalla_pedestrian.setObjectName("settings_valhalla_pedestrian")
        settings_valhalla_pedestrian.resize(639, 593)
        self.verticalLayout = QtWidgets.QVBoxLayout(settings_valhalla_pedestrian)
        self.verticalLayout.setContentsMargins(0, 0, 0, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.penalties_box = gui.QgsCollapsibleGroupBox(settings_valhalla_pedestrian)
        self.penalties_box.setCollapsed(True)
        self.penalties_box.setObjectName("penalties_box")
        self.formLayout_4 = QtWidgets.QFormLayout(self.penalties_box)
        self.formLayout_4.setContentsMargins(7, 7, 0, 7)
        self.formLayout_4.setObjectName("formLayout_4")
        self.step_penalty_label = QtWidgets.QLabel(self.penalties_box)
        self.step_penalty_label.setOpenExternalLinks(True)
        self.step_penalty_label.setObjectName("step_penalty_label")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.step_penalty_label)
        self.step_penalty = gui.QgsSpinBox(self.penalties_box)
        self.step_penalty.setMaximum(43200)
        self.step_penalty.setObjectName("step_penalty")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.step_penalty)
        self.service_penalty_label = QtWidgets.QLabel(self.penalties_box)
        self.service_penalty_label.setOpenExternalLinks(True)
        self.service_penalty_label.setObjectName("service_penalty_label")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.service_penalty_label)
        self.service_penalty = gui.QgsSpinBox(self.penalties_box)
        self.service_penalty.setMaximum(43200)
        self.service_penalty.setProperty("value", 15)
        self.service_penalty.setObjectName("service_penalty")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.service_penalty)
        self.verticalLayout.addWidget(self.penalties_box)
        self.addtional_params_box = gui.QgsCollapsibleGroupBox(settings_valhalla_pedestrian)
        self.addtional_params_box.setCollapsed(True)
        self.addtional_params_box.setObjectName("addtional_params_box")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.addtional_params_box)
        self.horizontalLayout_11.setContentsMargins(7, 7, 0, 7)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.additional_params_column_1 = QtWidgets.QFormLayout()
        self.additional_params_column_1.setObjectName("additional_params_column_1")
        self.walking_speed_label = QtWidgets.QLabel(self.addtional_params_box)
        self.walking_speed_label.setOpenExternalLinks(True)
        self.walking_speed_label.setObjectName("walking_speed_label")
        self.additional_params_column_1.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.walking_speed_label)
        self.walking_speed = gui.QgsDoubleSpinBox(self.addtional_params_box)
        self.walking_speed.setMinimum(0.5)
        self.walking_speed.setMaximum(25.0)
        self.walking_speed.setSingleStep(0.1)
        self.walking_speed.setProperty("value", 5.1)
        self.walking_speed.setObjectName("walking_speed")
        self.additional_params_column_1.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.walking_speed)
        self.walkway_factor_label = QtWidgets.QLabel(self.addtional_params_box)
        self.walkway_factor_label.setOpenExternalLinks(True)
        self.walkway_factor_label.setObjectName("walkway_factor_label")
        self.additional_params_column_1.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.walkway_factor_label)
        self.walkway_factor = gui.QgsDoubleSpinBox(self.addtional_params_box)
        self.walkway_factor.setMinimum(0.1)
        self.walkway_factor.setMaximum(100000.0)
        self.walkway_factor.setSingleStep(0.1)
        self.walkway_factor.setProperty("value", 1.0)
        self.walkway_factor.setObjectName("walkway_factor")
        self.additional_params_column_1.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.walkway_factor)
        self.service_factor_label = QtWidgets.QLabel(self.addtional_params_box)
        self.service_factor_label.setOpenExternalLinks(True)
        self.service_factor_label.setObjectName("service_factor_label")
        self.additional_params_column_1.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.service_factor_label)
        self.service_factor = gui.QgsDoubleSpinBox(self.addtional_params_box)
        self.service_factor.setMinimum(0.1)
        self.service_factor.setMaximum(100000.0)
        self.service_factor.setSingleStep(0.1)
        self.service_factor.setProperty("value", 1.0)
        self.service_factor.setObjectName("service_factor")
        self.additional_params_column_1.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.service_factor)
        self.max_hiking_difficulty = gui.QgsSpinBox(self.addtional_params_box)
        self.max_hiking_difficulty.setMinimum(1)
        self.max_hiking_difficulty.setMaximum(6)
        self.max_hiking_difficulty.setObjectName("max_hiking_difficulty")
        self.additional_params_column_1.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.max_hiking_difficulty)
        self.max_hiking_difficulty_label = QtWidgets.QLabel(self.addtional_params_box)
        self.max_hiking_difficulty_label.setObjectName("max_hiking_difficulty_label")
        self.additional_params_column_1.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.max_hiking_difficulty_label)
        self.horizontalLayout_11.addLayout(self.additional_params_column_1)
        self.additional_params_column_2 = QtWidgets.QFormLayout()
        self.additional_params_column_2.setObjectName("additional_params_column_2")
        self.alley_factor_label = QtWidgets.QLabel(self.addtional_params_box)
        self.alley_factor_label.setOpenExternalLinks(True)
        self.alley_factor_label.setObjectName("alley_factor_label")
        self.additional_params_column_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.alley_factor_label)
        self.driveway_factor_label = QtWidgets.QLabel(self.addtional_params_box)
        self.driveway_factor_label.setOpenExternalLinks(True)
        self.driveway_factor_label.setObjectName("driveway_factor_label")
        self.additional_params_column_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.driveway_factor_label)
        self.sidewalk_factor_label = QtWidgets.QLabel(self.addtional_params_box)
        self.sidewalk_factor_label.setOpenExternalLinks(True)
        self.sidewalk_factor_label.setObjectName("sidewalk_factor_label")
        self.additional_params_column_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.sidewalk_factor_label)
        self.sidewalk_factor = gui.QgsDoubleSpinBox(self.addtional_params_box)
        self.sidewalk_factor.setMinimum(0.1)
        self.sidewalk_factor.setMaximum(100000.0)
        self.sidewalk_factor.setSingleStep(0.1)
        self.sidewalk_factor.setProperty("value", 1.0)
        self.sidewalk_factor.setObjectName("sidewalk_factor")
        self.additional_params_column_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.sidewalk_factor)
        self.alley_factor = gui.QgsDoubleSpinBox(self.addtional_params_box)
        self.alley_factor.setMinimum(0.1)
        self.alley_factor.setMaximum(100000.0)
        self.alley_factor.setProperty("value", 2.0)
        self.alley_factor.setObjectName("alley_factor")
        self.additional_params_column_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.alley_factor)
        self.driveway_factor = gui.QgsDoubleSpinBox(self.addtional_params_box)
        self.driveway_factor.setMinimum(0.1)
        self.driveway_factor.setMaximum(100000.0)
        self.driveway_factor.setProperty("value", 5.0)
        self.driveway_factor.setObjectName("driveway_factor")
        self.additional_params_column_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.driveway_factor)
        self.horizontalLayout_11.addLayout(self.additional_params_column_2)
        self.verticalLayout.addWidget(self.addtional_params_box)
        self.favor_types_box = gui.QgsCollapsibleGroupBox(settings_valhalla_pedestrian)
        self.favor_types_box.setCollapsed(True)
        self.favor_types_box.setObjectName("favor_types_box")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.favor_types_box)
        self.horizontalLayout_4.setContentsMargins(7, 7, 0, 7)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.use_ferry_label = QtWidgets.QLabel(self.favor_types_box)
        self.use_ferry_label.setOpenExternalLinks(True)
        self.use_ferry_label.setObjectName("use_ferry_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.use_ferry_label)
        self.use_ferry = gui.QgsDoubleSpinBox(self.favor_types_box)
        self.use_ferry.setMaximum(1.0)
        self.use_ferry.setSingleStep(0.05)
        self.use_ferry.setProperty("value", 0.5)
        self.use_ferry.setObjectName("use_ferry")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.use_ferry)
        self.use_hills_label = QtWidgets.QLabel(self.favor_types_box)
        self.use_hills_label.setOpenExternalLinks(True)
        self.use_hills_label.setObjectName("use_hills_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.use_hills_label)
        self.use_hills = gui.QgsDoubleSpinBox(self.favor_types_box)
        self.use_hills.setMaximum(1.0)
        self.use_hills.setSingleStep(0.05)
        self.use_hills.setProperty("value", 0.5)
        self.use_hills.setObjectName("use_hills")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.use_hills)
        self.horizontalLayout_4.addLayout(self.formLayout)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.use_living_streets_label = QtWidgets.QLabel(self.favor_types_box)
        self.use_living_streets_label.setOpenExternalLinks(True)
        self.use_living_streets_label.setObjectName("use_living_streets_label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.use_living_streets_label)
        self.use_tracks_label = QtWidgets.QLabel(self.favor_types_box)
        self.use_tracks_label.setOpenExternalLinks(True)
        self.use_tracks_label.setObjectName("use_tracks_label")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.use_tracks_label)
        self.use_living_streets = gui.QgsDoubleSpinBox(self.favor_types_box)
        self.use_living_streets.setMaximum(1.0)
        self.use_living_streets.setSingleStep(0.05)
        self.use_living_streets.setProperty("value", 0.6)
        self.use_living_streets.setObjectName("use_living_streets")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.use_living_streets)
        self.use_tracks = gui.QgsDoubleSpinBox(self.favor_types_box)
        self.use_tracks.setMaximum(1.0)
        self.use_tracks.setSingleStep(0.05)
        self.use_tracks.setProperty("value", 0.5)
        self.use_tracks.setObjectName("use_tracks")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.use_tracks)
        self.horizontalLayout_4.addLayout(self.formLayout_2)
        self.verticalLayout.addWidget(self.favor_types_box)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(settings_valhalla_pedestrian)
        QtCore.QMetaObject.connectSlotsByName(settings_valhalla_pedestrian)

    def retranslateUi(self, settings_valhalla_pedestrian):
        _translate = QtCore.QCoreApplication.translate
        settings_valhalla_pedestrian.setWindowTitle(_translate("settings_valhalla_pedestrian", "Form"))
        self.penalties_box.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>Penalty options are fixed costs in seconds that are only added to the path cost. Penalties can influence the route path determination but do not add to the estimated time along the path. Penalties must be in the range of 0.0 seconds to 43200.0 seconds (12 hours).</p></body></html>"))
        self.penalties_box.setTitle(_translate("settings_valhalla_pedestrian", "Penalties"))
        self.step_penalty_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>A penalty in seconds added to each transition onto a path with steps or stairs. Higher values apply larger cost penalties to avoid paths that contain flights of steps.</p></body></html>"))
        self.step_penalty_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Step</span></a></p></body></html>"))
        self.service_penalty_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>A penalty applied for transition to generic service road. </p></body></html>"))
        self.service_penalty_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Service</span></a></p></body></html>"))
        self.addtional_params_box.setTitle(_translate("settings_valhalla_pedestrian", "Additional parameters"))
        self.walking_speed_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>Walking speed in kilometers per hour. Must be between 0.5 and 25 km/hr.</p></body></html>"))
        self.walking_speed_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla\"><span style=\" text-decoration: underline; color:#000000;\">Walking speed</span></a></p></body></html>"))
        self.walkway_factor_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>A factor that penalizes the cost when traversing a closed edge. Its value can range from <span style=\" font-family:\'.SF NS Mono\';\">1.0</span> - don\'t penalize closed edges, to <span style=\" font-family:\'.SF NS Mono\';\">10.0</span> - apply high cost penalty to closed edges.</p></body></html>"))
        self.walkway_factor_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Walkway factor</span></a></p></body></html>"))
        self.service_factor_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>A factor that modifies (multiplies) the cost when generic service roads are encountered.</p></body></html>"))
        self.service_factor_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#automobile-and-bus-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Service factor</span></a></p></body></html>"))
        self.max_hiking_difficulty_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>This value indicates the maximum difficulty of hiking trails that is allowed. Values between 0 and 6 are allowed. The values correspond to <span style=\" font-style:italic;\">sac_scale</span> values within OpenStreetMap. The default value is 1 which means that well cleared trails that are mostly flat or slightly sloped are allowed.</p></body></html>"))
        self.max_hiking_difficulty_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Max hiking difficulty</span></a></p></body></html>"))
        self.alley_factor_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>A factor that modifies (multiplies) the cost when alleys are encountered. Pedestrian routes generally want to avoid alleys or narrow service roads between buildings.</p></body></html>"))
        self.alley_factor_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Alley factor</span></a></p></body></html>"))
        self.driveway_factor_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>A factor that modifies (multiplies) the cost when encountering a <a href=\"http://wiki.openstreetmap.org/wiki/Tag:service%3Ddriveway\"><span style=\" text-decoration: underline; color:#0068da;\">driveway</span></a>, which is often a private, service road. Pedestrian routes generally want to avoid driveways (private).</p></body></html>"))
        self.driveway_factor_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Driveway factor</span></a></p></body></html>"))
        self.sidewalk_factor_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>A factor that modifies the cost when encountering roads with dedicated sidewalks. Pedestrian routes generally attempt to favor using sidewalks. </p></body></html>"))
        self.sidewalk_factor_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Sidewalk factor</span></a></p></body></html>"))
        self.favor_types_box.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><table border=\"0\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;\" cellspacing=\"2\" cellpadding=\"0\"><tr><td/><td><p>Favor type values indicate the willingness to take a certain road type. This is a range of values between 0 and 1. Values near 0 attempt to avoid the road type and values near 1 will favor them a little bit. Note that sometimes certain road types are required to complete a route so values of 0 are not guaranteed to avoid them entirely.</p></td></tr></table></body></html>"))
        self.favor_types_box.setTitle(_translate("settings_valhalla_pedestrian", "Favor types"))
        self.use_ferry_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>This value indicates the willingness to take ferries.</p></body></html>"))
        self.use_ferry_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#automobile-and-bus-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Use ferry</span></a></p></body></html>"))
        self.use_hills_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>This is a range of values from 0 to 1, where 0 attempts to avoid hills and steep grades even if it means a longer (time and distance) path, while 1 indicates the pedestrian does not fear hills and steeper grades. Based on the <span style=\" font-family:\'.SF NS Mono\';\">use_hills</span> factor, penalties are applied to roads based on elevation change and grade. These penalties help the path avoid hilly roads in favor of flatter roads or less steep grades where available.</p></body></html>"))
        self.use_hills_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#pedestrian-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Use hills</span></a></p></body></html>"))
        self.use_living_streets_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>This value indicates the willingness to take living streets.</p></body></html>"))
        self.use_living_streets_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#automobile-and-bus-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Use living streets</span></a></p></body></html>"))
        self.use_tracks_label.setToolTip(_translate("settings_valhalla_pedestrian", "<html><head/><body><p>This value indicates the willingness to take track roads.</p></body></html>"))
        self.use_tracks_label.setText(_translate("settings_valhalla_pedestrian", "<html><head/><body><p><a href=\"https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference.md#automobile-and-bus-costing-options\"><span style=\" text-decoration: underline; color:#000000;\">Use tracks</span></a></p></body></html>"))
from qgis import gui
