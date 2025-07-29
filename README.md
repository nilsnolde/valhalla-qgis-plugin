[![Test - QGIS releases](https://github.com/nilsnolde/valhalla-qgis-plugin/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/nilsnolde/valhalla-qgis-plugin/actions/workflows/ci-tests.yml) [![Test - QGIS master](https://github.com/nilsnolde/valhalla-qgis-plugin/actions/workflows/ci-tests-latest.yml/badge.svg)](https://github.com/nilsnolde/valhalla-qgis-plugin/actions/workflows/ci-tests-latest.yml) [![Coverage Status](https://coveralls.io/repos/github/nilsnolde/valhalla-qgis-plugin/badge.svg?branch=master)](https://coveralls.io/github/nilsnolde/valhalla-qgis-plugin?branch=master)

QGIS Plugin for the [Valhalla routing engine](https://github.com/valhalla/valhalla).

It features:
- UI & processing algorithms to routing, isochrones, matrix & expansion endpoints for `pedestrian`, `bicycle`, `car`, `truck` & `motorcycle`
- support for most[^1] of Valhalla costing options in both UI & processing algorithms for **all endpoints**, e.g.
  - time-dependent routing
  - exclude polygons to avoid user-defined areas
  - and various other [costing options](https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference/#costing-options)
- support for multiple Valhalla servers, the [public server](https://github.com/valhalla/valhalla?tab=readme-ov-file#demo-server) and `localhost` are preconfigured
- get extended graph information from the Valhalla server:
  - load the graph extent from a given instance (usually `localhost`) as a polygon layer
  - check for admins & timezone DBs
  - print Valhalla server version
  - print date of last graph update

> [!NOTE]
> Starting with `v3.0.0` this plugin had a complete re-write from scratch. Previously it was loosely based on one of my ex-plugins [ORS Tools](https://plugins.qgis.org/plugins/ORStools/), but that design has a quite a few shortcomings in terms of UX and aesthetics. The biggest problem is that the dialogs are huge and one can't properly access both the map canvas **and** the plugin at the same time. Starting with `v3.0.0` it's a docked plugin, i.e. a proper panel.

[^1]: Some costing options make little sense, e.g. transit, some other we didn't get around to yet. Valhalla is also under constant development, we might miss a few recently added ones.

## How To

![explanatory UI pic](./docs/img/RoutingUI_explained.png)

1. Select the endpoint/action to "Execute". Note that some endpoints expect multiple waypoints.
2. Manage the servers which are shown in the "Provider" drop-down
3. Add/remove/clear waypoints in the table:
  - to add waypoints, click the "add" button and then in the map canvas. To end the adding session, either double-click in the map canvas or click the "add" button again.
  - to remove single/multiple waypoints, click rows in the waypoints table before clicking the "remove" button.
  - the "clear" button will remove _all_ waypoints from the table
4. Multiple alternatives to add waypoints to the table:
  - "From Point Layer": parses waypoints from the features of a user-specified point layer
  - "From Valhalla JSON": parses waypoints from a Valhalla `locations` request array (TODO: [#27](https://github.com/nilsnolde/valhalla-qgis-plugin/issues/27))
  - "From OSRM URL": parses waypoints from a OSRM GET request URL, also sets `bearing` etc in the "Extra" column
5. Shows/hides the "Valhalla waypoints" annotation layer
6. Moves the _selected_ waypoint rows up & down, also updates the "Valhalla waypoints" annotation layer
7. Set a radius for each waypoint which will snap more roads
8. Set extra Valhalla waypoint properties in URL query parameter form (i.e.`k1=v1&k2=v2`), e.g. `waiting=1800&date_time=2025-07-25T09:00`
9. Additional costing options to influence the path finding for _any_ endpoint
10. View the full most recent request, mostly useful when reporting issues, or debugging.
11. Check the remote graph for admin & timezone DBs (they should exist) and loads the graph extent of the currently set Valhalla server as a polygon layer (if available).
12. Some information about the plugin and (if available) the currently set Valhalla server.

## Test

To run the tests, one needs a locally running Valhalla server with an Andorra graph, e.g.

```
docker run --rm -dt --name valhalla-router -p 8002:8002 -v $PWD/tests/data:/custom_files -e tileset_name=andorra-tiles ghcr.io/valhalla/valhalla-scripted:latest
```

### Local

`python -m unittest discover`

### Docker

In CI we run the tests with the QGIS docker image, have a look [there](.github/workflows/ci-tests.yml).

## History

Without going into too much detail, this plugin had once a **much** wider scope. Back when I was still running [GIS-OPS](https://github.com/gis-ops), I was a bit obsessed with providing an alternative to ESRI's network analyst, one of the last areas where QGIS is very very far behind ESRI. That's a crazy huge task, especially including all those optimization algorithms. However, we actually did come a pretty long way:

- support for both Valhalla & OSRM
- optimization support [`spopt`](https://github.com/pysal/spopt) and [`pyvroom`](https://pypi.org/project/pyvroom/) in the plugin UI
- support for **all local** calculations via
  - [`pyvalhalla`](https://pypi.org/project/pyvalhalla/)
  - [`py-osrm`](https://github.com/nilsnolde/py-osrm)

We were also planning to open a web shop where you could buy Valhalla & OSRM graphs right from QGIS and load them locally in a heartbeat. The idea was grand and a lot of OSS was being released as the result of it, e.g. the python bindings to Valhalla & OSRM and Windows support for `pyvroom`. Sadly the work to get there was grand as well and we never ended up releasing the full plugin.

The current Valhalla plugin still has all the source code though, mostly just commented out. In case anyone ever feels the urge to rival ESRI Network Analyst, please contact me on nilsnolde+github@proton.me.

## Python Bindings

Originally we wanted to make this plugin work with https://pypi.org/project/pyvalhalla and other Python bindings, so no one would have to install Valhalla locally (QGIS users are not always comfy with that sort of thing).

However, that's not possible with PyPI distributions, because the wheels vendor the dependencies and Valhalla & QGIS share a lot of dependencies. That makes QGIS crash as it's basically UB what happens when two versions of the same library are loaded into the same process.

There are 2 ways to make this work:
1. either not use the bindings directly, but rather the packaged Valhalla C++ executables. Obvious downside is performance: if used like that, for every single request Valhalla will have to load the relevant graph tiles, because there is of course no persisted cache. On the upside: it's possible today, even including building the graph.
2. publish Valhalla (with `-DENABLE_PYTHON_BINDINGS=ON`) on all package management platforms that QGIS uses for distribution. That's of course the harder solution: apt/dnf/pacman for Linux, God knows what we'd need to do or who to bribe for OSX & Win. I saw some `vcpkg` mentions in the QGIS repo and know Matthias was advocating for it (at least OSX builds), but have no idea about the current state or platform-scope. If `vcpkg` would be the future of > 90% of QGIS distributions, it could make this option fairly easy.
