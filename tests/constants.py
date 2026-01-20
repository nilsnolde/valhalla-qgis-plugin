# coords are in andorra, our bindings test dataset

WAYPOINTS_4326 = [
    [1.539283, 42.612798],
    [1.543225, 42.523528],
    [1.709114, 42.542892],
]

WAYPOINTS_4326_MAP_MATCH = [
    [1.59164691, 42.54688538],
    [1.59146759, 42.54629091],
    [1.59128828, 42.54589459],
    [1.59151242, 42.54421021],
]

WAYPOINTS_3857 = [[171352.2, 5253220.2], [171791.0, 5239726.9], [190257.7, 5242652.2]]

# TODO: this is still in netherlands, but doesn't seem to test anything anyways
POLYGON_4326 = [
    [
        [5.118921, 52.091565],
        [5.126385, 52.0908],
        [5.125864, 52.092871],
        [5.118479, 52.092428],
        [5.118921, 52.091565],
    ]
]

GRAPHS = (("valhalla", "andorra-tiles.tar"),)
