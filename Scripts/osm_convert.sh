:: Convert to .o5m format
osmconvert north-america-latest.osm.pbf -o=osm_test.o5m

:: Filter highways vs normal roads
osmfilter osm_test.o5m --keep="highway=motorway =motorway_link =trunk =trunk_link =primary =primary_link" > osm_test_highway.osm
osmfilter osm_test.o5m --keep="highway=secondary =secondary_link =tertiary =tertiary_link" > osm_test_roads.osm

:: Filter by individual types
osmfilter osm_test.o5m --keep="highway=motorway =motorway_link" > osm_test_motorway.osm
osmfilter osm_test.o5m --keep="highway=trunk =trunk_link" > osm_test_trunk.osm
osmfilter osm_test.o5m --keep="highway=primary =primary_link" > osm_test_primary.osm
osmfilter osm_test.o5m --keep="highway=secondary =secondary_link" > osm_test_secondary.osm
