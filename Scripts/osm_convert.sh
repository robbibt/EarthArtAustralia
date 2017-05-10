:: Convert to .o5m format
osmconvert australia-latest.osm.pbf -o=osm_test.o5m

:: Convert while taking spatial subset
osmconvert australia-latest.osm.pbf -b=110,-40,130,-12 -o=osm_test.o5m

:: Filter highways vs normal roads
osmfilter osm_test.o5m --keep="highway=motorway =motorway_link =trunk =trunk_link =primary =primary_link" > osm_test_highway.osm
osmfilter osm_test.o5m --keep="highway=secondary =secondary_link =tertiary =tertiary_link" > osm_test_roads.osm

:: Filter by individual types
osmfilter osm_test.o5m --keep="highway=motorway =motorway_link" > osm_test_motorway.osm
osmfilter osm_test.o5m --keep="highway=trunk =trunk_link" > osm_test_trunk.osm
osmfilter osm_test.o5m --keep="highway=primary =primary_link" > osm_test_primary.osm
osmfilter osm_test.o5m --keep="highway=secondary =secondary_link" > osm_test_secondary.osm

:: All roads
osmfilter osm_test.o5m --keep="highway=" > osm_test_roads.osm

:: All waterways
osmfilter osm_test.o5m --keep="( waterway= or natural=water or landuse=reservoir or natural=wetland )" > osm_test_waterways.osm
osmfilter osm_test.o5m --keep="( waterway=river or waterway=canal or waterway=stream or waterway=brook or waterway=drain or waterway=ditch or natural=water or landuse=reservoir or natural=wetland )" > osm_test_waterways.osm

:: No abandoned railways
osmfilter osm_test.o5m --keep="( railway= and railway!=abandoned )" > osm_test_rail.osm