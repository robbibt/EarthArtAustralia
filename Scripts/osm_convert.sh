:: Convert to .o5m format
osmconvert delaware-latest.osm.pbf -o=osm_test.o5m

:: Filter
osmfilter osm_test.o5m --keep="highway=motorway =motorway_link =trunk =trunk_link =primary =primary_link" > osm_test_highway.osm
osmfilter osm_test.o5m --keep="highway=secondary =secondary_link =tertiary =tertiary_link" > osm_test_roads.osm
