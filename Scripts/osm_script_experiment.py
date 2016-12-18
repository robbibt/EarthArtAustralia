__author__ = 'z3287630'

# Import libraries and set working directory
import osmnx as ox
import os

# Define city to download
city = "Canberra, Australia"
directory = "Australia"
os.chdir("D:/Geography/EAA/" + directory)

# Save and optionally plot output
try:
    city_graph = ox.graph_from_place(city, network_type='all_private') # ox.plot_graph(city_graph)
except:
    city_graph = ox.graph_from_address(city, network_type='all_private', distance = 25000) # ox.plot_graph(city_graph)

# Export to shapefile
city_graph = ox.project_graph(city_graph)
ox.save_graph_shapefile(city_graph, filename = "osm_" + city.replace(", ",""))


#
# # save street network as GraphML file
# ox.save_graphml(city_graph, filename='network.graphml')
#
# g = igraph.Graph.Read_GraphML("D:/Dropbox/EarthArtAustralia/data/network.graphml")
# igraph.plot(g)
#
#
#
# G2 = ox.load_graphml('network.graphml')
# fig, ax = ox.plot_graph(G2)
# import igraph
# import networkx


gdf = ox.gdf_from_place(city)


G = ox.graph_from_point(gdf["geometry"], distance_type = "bbox")

ox.plot_shape(ox.project_gdf(gdf))

G = ox.graph_from_address(city, distance=3000)
ox.plot_graph(G)



import osmnx as ox
gdf = ox.gdf_from_place('Povo, Italy')
G = ox.graph_from_point('Povo, Italy', distance=3000)




