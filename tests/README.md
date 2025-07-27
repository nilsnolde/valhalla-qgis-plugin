# Running the tests

A lot of our tests are doing HTTP requests to OSRM/Valhalla and the public servers available have some pretty restrictive rate limits. Consequently, we run local instances of both engines for tests.

To start the docker containers locally, just do:

```shell
# create the graphs if they don't exist already
docker run --rm -it --name valhalla-tests -v $PWD/tests/data:/custom_files  -e tileset_name=andorra-tiles -e serve_tiles=False gisops/valhalla:latest
docker run --rm -it -v $PWD/tests/data:/data --name osrm-tests osrm/osrm-backend:latest /bin/bash -c "osrm-extract -p /opt/car.lua /data/andorra-latest.osm.pbf && osrm-partition /data/andorra-latest.osrm && osrm-customize /data/andorra-latest.osrm"

# then run the routing engines
docker run -dt --name valhalla-tests -p 8002:8002 -v $PWD/tests/data:/custom_files -e tileset_name=andorra-tiles -e use_tiles_ignore_pbf=True gisops/valhalla:latest
docker run -dt --name osrm-tests -p 5000:5000 -v $PWD/tests/data:/data osrm/osrm-backend:latest osrm-routed --algorithm=MLD /data/andorra-latest.osrm
```

To run with coverage, `pip install coverage` and run:

```
coverage run -m unittest discover && coverage report  # or "coverage html" for annotated html report 
```
