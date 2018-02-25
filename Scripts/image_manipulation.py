# coding=utf-8
__author__ = 'Robbi Bishop-Taylor'

# Import modules
import os
import warnings
from PIL import Image, ImageOps
import earthartaustralia_tools as earthart
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

# Working directory
os.chdir("C:/Users/Robbi/Google Drive/EarthArtAustralia/")

# Map descriptions
data_source_desc = {'custom': "Custom map - contact Robbi for more detail",

                    'city': "Map based on GIS road data weighted by increasing size/importance. Source data copyright "
                            "OpenStreetMap contributors available under CC BY-SA (http://www.openstreetmap.org/copyright)",

                    'roads': "Map based on GIS road data weighted by increasing size/importance. Source data copyright "
                             "OpenStreetMap contributors available under CC BY-SA (http://www.openstreetmap.org/copyright)",

                    'wedding': "Map based on GIS road data weighted by increasing size/importance. Source data copyright "
                               "OpenStreetMap contributors available under CC BY-SA (http://www.openstreetmap.org/copyright)",

                    'vertical': "Map based on GIS road data weighted by increasing size/importance. Source data copyright "
                                "OpenStreetMap contributors available under CC BY-SA (http://www.openstreetmap.org/copyright)",

                    'buildings': "Map created with QGIS using GIS building footprint features. Source data copyright "
                                 "OpenStreetMap contributors available under CC BY-SA (http://www.openstreetmap.org/copyright)",

                    'buildingsuk': "Map based on modified OS data Crown copyright and database right (2016), available: "
                                   "https://www.ordnancesurvey.co.uk/business-and-government/products/os-open-map-local.html",

                    'shadow': "Produced using 90m digital elevation data from the CGIAR-CSI SRTM 90m Database available "
                              "from http://srtm.csi.cgiar.org.",

                    'waterways': "Map created with QGIS using Openstreetmap water line and polygon features. Source data "
                                 "copyright OpenStreetMap contributors available under CC BY-SA "
                                 "(http://www.openstreetmap.org/copyright)",

                    'waterwayshs': "This map incorporates data from the HydroSHEDS database which is copyright World Wildlife "
                                   "Fund, Inc. (2006-2013). The HydroSHEDS database and more information are available at "
                                   "http://www.hydrosheds.org.",

                    'waterwaysus': "Map based on GIS stream and waterbody data from USGS National Hydrography Dataset vector "
                                   "datasets (USGS, 2007-2014, National Hydrography Dataset available at http://nhd.usgs.gov)",

                    'waterwayseu': "GIS data from European Environment Agency (EEA). 2012. EEA Catchments and Rivers Network "
                                   "System (ECRINS) v1.1. Freely available from http://www.eea.europa.eu/data-and-maps/data/"
                                   "european-catchments-and-riversnetwork",

                    'waterwaysca': "GIS data from freely available Government of Canada, NRC, ESS. 2016. CanVec Hydro "
                                   "Features. Ottawa, ON: DNRC (http://open.canada.ca/data/en/dataset/9d96e8c9-22fe-4ad2-b5e8-"
                                   "94a6991b744b), Open Government Licence - Canada: http://open.canada.ca/en/open-government-"
                                   "licence-canada",

                    'waterwaysie': "Map created with QGIS using GIS data for streams and waterbodies from INSPIRE Directive "
                                   "Environmental Protection Agency and Northern Ireland Environment Agency data. Data is "
                                   "for public use under Creative Commons CC-By 4.0",

                    'waterwaysnz': "GIS data from New Zealand Topo50, Topo250 and Topo500 map series (see www.linz.govt.nz/"
                                   "topography/topo-maps/), freely available under a Creative Commons Attribution 3.0 New "
                                   "Zealand license: https://creativecommons.org/licenses/by/3.0/nz/",

                    'waterwaysnl': "GIS data from the TOP50NL 1:50000 scale mapping product, freely available online under the "
                                   "CC-BY-4.0 license (https://www.pdok.nl/nl/producten/pdok-downloads/basisregistratie-"
                                   "topografie/topnl/topnl-actueel/top50nl)",

                    'waterwaysau': "GIS data from freely available Commonwealth of Australia (BOM) 2016 "
                                   "Geofabric river data (http://www.bom.gov.au/water/geofabric/) and GA Geodata Topo 250K "
                                   "(http://www.ga.gov.au/metadata-gateway/metadata/record/gcat_63999), CC BY 4.0 Licence: "
                                   "https://creativecommons.org/licenses/by/4.0/",

                    'waterwaysfi': "Map created with QGIS using Finnish Environment Institute (SYKE) GIS data at "
                                   "1:10 000 scale (Jarvien ja jokien syvyysaineisto and Ranta10 - rantaviiva "
                                   "1:10,000 ja uomaverkosto), freely available at "
                                   "http://www.syke.fi/fi-FI/Avoin_tieto/Paikkatietoaineistot",

                    'forests': "Data from Hansen et al. 2013. High Resolution Global Maps of 21st Century Forest Cover Change. "
                               "Science 342, p850 (http://earthenginepartners.appspot.com/science-2013-global-forest) and "
                               "90m DEM data from the CGIAR-CSI SRTM 90m Database (http://srtm.csi.cgiar.org)"}


# Entire function -----------------------------------------------------------------------------------------------------
def image_manipulation(file_string, map_name, words_name, inset_zoom, watermark, metric, name, title_size, title_nudge,
                       nine_styles, nine_styles_scale, pdf, desc=data_source_desc, blue=False, coordinates=False,
                       name_text=False):

    # Generate tags and title
    print("Printable maps:")
    earthart.etsy_title(title=map_name, words_name=words_name)
    earthart.etsy_tags(title=map_name, words_name=words_name, copy_clipboard=False)

    # Set up file parameters ------------------------------------------------------------------------------

    # Identify file name
    dir_name = os.path.dirname(file_string)
    place, map_desc, res = os.path.basename(file_string[:-4]).split("_")
    file_name = place + "_" + map_desc

    # Test if custom name given
    if not name_text:
        name_text = " ".join(str.split(map_name)[-words_name:]).upper()

    # Set up main directory if does not exist
    if not os.path.exists(dir_name + "/" + file_name):
        os.makedirs(dir_name + "/" + file_name)

    # Set up styles directory if does not exist
    if not os.path.exists(dir_name + "/" + file_name + "/" + file_name + "_styles"):
        os.makedirs(dir_name + "/" + file_name + "/" + file_name + "_styles")

    # Read image, optionally add titles and coordinates for city maps -------------------------------------------------

    # Read image
    image_highres = Image.open(file_string)
    image_highres = image_highres.convert("RGBA")

    if name:

        print("Adding title")
        image_highres = earthart.map_title(image_highres,
                                           file_string=file_string,
                                           title_name=name_text,
                                           title_nudge=title_nudge,
                                           title_size=title_size,
                                           title_font="Scripts/Fonts/ADAM-CG PRO Kerning.ttf",
                                           coordinates=coordinates,
                                           white_manual=False)

    # Generate low resolution versions --------------------------------------------------------------------------------

    image_lowres = image_highres.copy()
    image_lowres.thumbnail((2300, 2000), Image.ANTIALIAS)
    image_lowres.convert("RGB").save(dir_name + "/" + file_name + "/" + file_name + "_lowres.jpg", quality=85, optimize=True)
    image_insta = ImageOps.expand(image_lowres, border=500, fill="#FFFFFF")
    image_insta.convert("RGB").save(dir_name + "/" + file_name + "/" + file_name + "_insta.jpg", quality=85, optimize=True)

    # Optionally create low-res version with watermark for small areas
    if watermark:

        watermark_overlay = Image.open("Scripts/Elements/watermark.png")
        image_lowres.paste(watermark_overlay, (100, 100),
                           mask=watermark_overlay.split()[1])
        image_lowres.paste(watermark_overlay, (int(image_lowres.width*0.2), int(image_lowres.height*0.2)),
                           mask=watermark_overlay.split()[1])
        image_lowres.paste(watermark_overlay, (int(image_lowres.width*0.4), int(image_lowres.height*0.4)),
                           mask=watermark_overlay.split()[1])
        image_lowres.paste(watermark_overlay, (image_lowres.width - 800, image_lowres.height - 800),
                           mask=watermark_overlay.split()[1])
        image_lowres.convert("RGB").save(dir_name + "/" + file_name + "/" + file_name + "_watermark.jpg", quality=85, optimize=True)

    # Frame -----------------------------------------------------------------------------------------------------------
    earthart.etsy_frame(highres_input=image_highres,
                        ouput_path=dir_name + "/" + file_name + "/" + file_name,
                        map_name=map_name,
                        nine_styles=nine_styles,
                        metric=metric)

    # Subsets ---------------------------------------------------------------------------------------------------------
    earthart.image_subsets(highres_input=image_highres,
                           ouput_path=dir_name + "/" + file_name + "/" + file_name,
                           inset_zoom=inset_zoom)

    # Featured on overlay
    earthart.featured_on(file_string,
                         output_path=dir_name + "/" + file_name + "/" + file_name,
                         desc=data_source_desc)

    # Physical map frames and Featured On -----------------------------------------------------------------------------
    print("Physical maps:")
    earthart.physical_maps(highres_input=image_highres,
                           output_path=dir_name + "/" + file_name + "/" + file_name,
                           map_name=map_name,
                           words_name=words_name,
                           templates=False,
                           copy_clipboard=False)

    # Colors ----------------------------------------------------------------------------------------------------------
    earthart.color_styles(highres_input=image_highres,
                          blue=blue,
                          nine_styles = nine_styles,
                          nine_styles_scale=nine_styles_scale,
                          title_nudge=title_nudge,
                          styles_path=dir_name + "/" + file_name + "/" + file_name + "_styles/")

    # Generate PDF ----------------------------------------------------------------------------------------------------
    if pdf:

        try:

            # If description exists, create PDF
            default_desc = desc[map_desc]
            earthart.generate_pdf(map_name,
                                  file_string,
                                  nine_styles=nine_styles,
                                  desc=desc)

        except:

            # If no default description
            print("Generating PDF failed; no default description")

    # Close files -----------------------------------------------------------------------------------------------------

    image_highres.close()
    image_lowres.close()


# Setup ---------------------------------------------------------------------------------------------------------------

image_manipulation(map_name="Roads of Australia",
                   file_string="Australia/australia_roads_highres.png",
                   words_name=2,
                   inset_zoom=0.1,
                   watermark=True,
                   metric=False,

                   # Title
                   name=True,
                   title_size=1,  # 1.4 for states
                   title_nudge=0,  # 800 for states
                   coordinates="44.9537° N, 93.0900° W",
                   name_text='Saint Paul',

                   # Styles
                   nine_styles=True,
                   nine_styles_scale=0.1,  # cities = 0.1, waterways = 0.5
                   blue=False,

                   # Generate PDF?
                   pdf=True)


# Generate tags and title
map_name = "Every Road in Bucharest"
file_string="Canada/canada_shadow_highres.png"
nine_styles, metric, words_name = True, True, 1
earthart.etsy_title(map_name, words_name=words_name, physical=False)
# earthart.etsy_tags(map_name, words_name, physical=False)

# Uses insert_frame to create cover images
earthart.etsy_frame(highres_input=file_string,
                    ouput_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1],
                    map_name=map_name,
                    nine_styles=nine_styles,
                    metric=metric)

# Featured on overlay
earthart.featured_on(file_string=file_string,
                     output_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1],
                     desc=data_source_desc)

# Physical maps mockups
earthart.physical_maps(highres_input=file_string,
                       output_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1],
                       map_name="",
                       words_name=words_name,
                       offset=False,
                       templates=False,
                       copy_clipboard=False)

# Rerun nine colors frame
earthart.color_styles(highres_input=file_string,
                      blue=False,
                      nine_styles = nine_styles,
                      nine_styles_scale=0.1,
                      title_nudge=0,  # wedding: 2500-1360
                      styles_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1] + "_styles/")

# Re-generate PDF
earthart.generate_pdf(map_name=map_name,
                      file_string=file_string,
                      nine_styles=nine_styles,
                      desc=data_source_desc)




# Re-run subsets
earthart.image_subsets(highres_input=file_string,
                       ouput_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1],
                       inset_zoom=0.12,
                       x_offset=0.25,
                       y_offset=0.5)







# Produce custom color versions
earthart.custom_color(highres_input=file_string,
             black_color="#FFFFFF",
             white_color="#474c48",
             text_color="",
             contrast=(1.3 - 1.0) * 0.1 + 1,
             title_nudge=0,  # wedding: 2500-1360
             name="whiteongreygreen",
             # styles_path="USA/dallas_city/Styles/")
             styles_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1] + "_styles/")

# Produce custom color versions
earthart.custom_color(highres_input=file_string,
             black_color="#FFFFFF",
             white_color="#085d72",
             text_color="",
             contrast=(1.3 - 1.0) * 0.1 + 1,
             title_nudge=0,  # wedding: 2500-1360
             name="whiteonteal",
             # styles_path="USA/dallas_city/Styles/")
             styles_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1] + "_styles/")


earthart.custom_color(highres_input=file_string,
             black_color="#FFFFFF",
             white_color="#c10b07",
             text_color="",
             contrast=(1.3 - 1.0) * 0.1 + 1,
             title_nudge=0,  # wedding: 2500-1360
             name="whiteonred2",
             # styles_path="USA/dallas_city/Styles/")
             styles_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1] + "_styles/")




# Wedding maps - style 1
wedding_map(file_string=file_string,
            couple_name="David & Joanne",
            couple_size=1.25,
            couple_nudge=1030,
            couple_font="Scripts/Fonts/ADAM-CG PRO Kerning.ttf",
            date_name=" ".join("20.01.18"),
            date_size=0.55,
            date_nudge=47,
            date_font="Scripts/Fonts/Autumn in November.ttf",
            white_manual=2500)

# Wedding maps - style 4
wedding_map(file_string=file_string,
            couple_name="Nick & Sarah",
            couple_size=1.6,
            couple_nudge=1450,
            couple_font="Scripts/Fonts/Nickainley-Normal.otf",
            date_name=" ".join("3.4.2018"),
            date_size=0.55,
            date_nudge=50,
            date_font="Scripts/Fonts/GOTHIC.ttf",
            white_manual=2500)


wedding_map(file_string="Custom/DelhiKochiAuckland/kochi_custom_highres.png",
            couple_name="COCHIN",
            couple_size=2.3,
            couple_nudge=1690,
            couple_font="Scripts/Fonts/ADAM-CG PRO Kerning.ttf",
            date_name="I  N  D  I  A",   #" ".join("28.7041° N  77.1025° E".replace("\xc2", "")),
            date_size=0.63,
            date_nudge=120,
            date_font="Scripts/Fonts/Abel-Regular.ttf",
            white_manual=300