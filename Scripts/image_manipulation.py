__author__ = 'z3287630'

# Import modules
import os
import random
import glob
from xlutils.copy import copy
from xlrd import open_workbook
from PIL import Image, ImageEnhance, ImageCms, ImageOps, ImageFont, ImageDraw
import warnings
import httplib2
from apiclient import discovery
from oauth2client.file import Storage
from apiclient import errors
import pandas as pd
import subprocess
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

# Working directory
os.chdir("D:/Google Drive/EarthArtAustralia/")


# Get valid google Drive service
def get_service(credential_path):

    """Gets valid Google Drive service.
    Returns:
        Service, the obtained service.
    """

    store = Storage(credential_path)
    credentials = store.get()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    return service


# Insert Google Drive permission
def insert_permission(service, file_id, value="", perm_type="anyone", role="reader", link=True):
  """Insert a new permission.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to insert permission for.
    value: User or group e-mail address, domain name or None for 'default'
           type.
    perm_type: The value 'user', 'group', 'domain' or 'default'.
    role: The value 'owner', 'writer' or 'reader'.
  Returns:
    The inserted permission if successful, None otherwise.
  """
  new_permission = {
      'value': value,
      'type': perm_type,
      'role': role,
      'withLink': link
  }
  try:
    return service.permissions().insert(
        fileId=file_id, body=new_permission).execute()
  except errors.HttpError, error:
    print('An error occurred')
  return None


# Recolor greyscale image by stretching between black and white color
def colorise_image(src, black_color ="#FFFFFF", white_color ="#000000", contrast=1.0):

    src.load()
    r, g, b, alpha = src.split()
    gray = ImageOps.grayscale(src)
    gray = ImageEnhance.Contrast(gray).enhance(contrast)
    result = ImageOps.colorize(gray, black_color, white_color)
    result.putalpha(alpha)
    return result


# Insert thumbnail into frame images
def insert_frame(highres_input, size, location, frame_path, frame_ninestyles, ouput_path, nine_styles):

    image_frame = highres_input.copy()
    image_frame.thumbnail(size, Image.ANTIALIAS)

    # Improve contrast
    image_frame = ImageEnhance.Contrast(image_frame).enhance(1.15)
    image_frame = ImageEnhance.Color(image_frame).enhance(1.05)

    # Open frame and paste in image
    etsy_frame = Image.open(frame_path)
    etsy_frame_overlay = etsy_frame.copy()

    etsy_frame.paste(image_frame, location)
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(ouput_path)

    # Add "9 styles" banner
    if nine_styles:
        etsy_ninestyles = Image.open(frame_ninestyles)
        etsy_frame.paste(etsy_ninestyles, (0, 0), etsy_ninestyles)
        etsy_frame.save(ouput_path[:-4] + "_ninestyles.jpg")

        # Additional white on black frame
        etsy_frame = colorise_image(etsy_frame, black_color="#FFFFFF", white_color="#000000", contrast=1)
        etsy_frame = ImageEnhance.Brightness(etsy_frame).enhance(1.07)
        etsy_frame = ImageEnhance.Contrast(etsy_frame).enhance(1.07)
        etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
        etsy_frame.paste(etsy_ninestyles, (0, 0), etsy_ninestyles)
        etsy_frame.save(ouput_path[:-4] + "_ninestyles_bw.jpg")


# Generate tags
def etsy_tags(title, words_name, physical=False):

    name = " ".join(str.split(title)[-words_name:])
    suffixes = ["map", "art", "poster", "print", "gift", "wall art", "map print", "map art", "art print"]

    if physical:
        tag_list = "Physical " + name + " print, " + \
                   ", ".join([name + " " + s for s in suffixes])
    else:
        tag_list = "Printable " + name + ", " + \
                   ", ".join([name + " " + s for s in suffixes]) + \
                   ", Printable poster, Printable art"

    # Print and copy to clipboard
    print(tag_list)
    df = pd.DataFrame([tag_list])
    df.to_clipboard(index=False, header=False)


# Generate titles
def etsy_title(title, words_name, physical=False):

    name = " ".join(str.split(title)[-words_name:])

    if physical:
        title_string = title + " map print | Physical " + name + " map art, " + name + " print, " + name + " art, " + name + " poster"
    else:
        title_string = title + " map art | Printable " + name + " map print, " + name + " print, " + name + " art, " + name + " poster"

    if len(title_string + ", " + name + " wall art") < 141:
        title_string = title_string + ", " + name + " wall art"
        if len(title_string + ", " + name + " gift") < 141:
            title_string = title_string + ", " + name + " gift"

    # Print and copy to clipboard
    print(str(len(title_string)) + " LETTERS: " + title_string)
    df = pd.DataFrame([title_string])
    df.to_clipboard(index=False, header=False)


def physical_maps(file_string, map_name, words_name):

    # Generate tags and title
    etsy_title(title=map_name, words_name=words_name, physical=True)
    etsy_tags(title=map_name, words_name=words_name, physical=True)

    # Import image
    image_highres = Image.open(file_string)
    width, height = image_highres.size

    dir_name = os.path.dirname(file_string)
    place, map_desc, res = os.path.basename(file_string[:-4]).split("_")
    file_name = place + "_" + map_desc

    # Choice of random overlay
    x = str(random.randrange(1,6))

    # Vertical
    if height > width:

        # Main mockup
        insert_frame(highres_input=image_highres,
                     size=(1153, 1153),
                     location=(668 - (int(1153 / 1.4189) / 2), 1240 - 1153),
                     frame_path="Scripts/Elements/mockups/mockup_template_vert" + x + ".png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_mockup.jpg",
                     nine_styles=False)

        # Size frames
        insert_frame(highres_input=image_highres,
                     size=(1030, 1030),
                     location=(620 - (int(1030 / 1.4189) / 2), 1360 - 1030),
                     frame_path="Scripts/Elements/mockups/mockup_sizes_vert.png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path="Scripts/Elements/mockups/draft_overlay.png",
                     nine_styles=False)
        insert_frame(highres_input=image_highres,
                     size=(730, 730),
                     location=(1404 - (514 / 2), 1020 - 730),
                     frame_path="Scripts/Elements/mockups/draft_overlay.png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_sizes.jpg",
                     nine_styles=False)

    # Horizontal
    if width > height:

        inset_test = Image.open("Custom/test_city_highres.png")
        insert_frame(highres_input=image_highres,
                     size=(1153, 1153),
                     location=(882 - int(1153 / 2), 850 - int(1153 / 1.4189)),
                     frame_path="Scripts/Elements/mockups/mockup_template_hor" + x + ".png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_mockup.jpg",
                     nine_styles=False)

        # Size frames
        insert_frame(highres_input=image_highres,
                     size=(1030, 1030),
                     location=(587 - int(1030 / 2), 753 - int(1030 / 1.4189)),
                     frame_path="Scripts/Elements/mockups/mockup_sizes_hor.png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path="Scripts/Elements/mockups/draft_overlay.png",
                     nine_styles=False)
        insert_frame(highres_input=image_highres,
                     size=(735, 735),
                     location=(1560 - int(735 / 2), 578 - int(735 / 1.4189)),
                     frame_path="Scripts/Elements/mockups/draft_overlay.png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_sizes.jpg",
                     nine_styles=False)

    try:

        # Featured on
        image_zoom_middle = Image.open(dir_name + "/" + file_name + "/" + file_name + "_zoom_1.jpg")
        image_zoom_middle.thumbnail((755, 755), Image.ANTIALIAS)
        featuredon_overlay = Image.open("Scripts/Elements/featuredon_overlay.png")
        image_zoom_middle.paste(featuredon_overlay, (0, 0), mask=featuredon_overlay)
        image_zoom_middle.save(dir_name + "/" + file_name + "/" + file_name + "_featuredon.jpg", quality=85,
                               optimize=True)
        image_zoom_middle.close()

    except:
        print("Cannot create 'Featured on'")


# Generate PDF
def generate_pdf(map_name):

    try:
        subprocess.call(['Rscript', 'D:/Google Drive/EarthArtAustralia/Scripts/create_download_PDF.R', map_name],
                        shell=False)
    except:
        print("Error generating PDF")


# Entire function -----------------------------------------------------------------------------------------------------
def image_manipulation(file_string, map_name, words_name, inset_zoom, subsets, watermark, name, coordinates,
                       text_size, text_nudge, nine_styles, nine_styles_scale, name_text=False):

    # Generate tags and title
    print("Printable maps:")
    etsy_title(title=map_name, words_name=words_name)
    etsy_tags(title=map_name, words_name=words_name)

    # Set up file parameters ------------------------------------------------------------------------------

    # Identify file name
    dir_name = os.path.dirname(file_string)
    place, map_desc, res = os.path.basename(file_string[:-4]).split("_")
    file_name = place + "_" + map_desc

    # Set up main directory if does not exist
    if not os.path.exists(dir_name + "/" + file_name):
        os.makedirs(dir_name + "/" + file_name)

    # Set up styles directory if does not exist
    if not os.path.exists(dir_name + "/" + file_name + "/" + file_name + "_styles"):
        os.makedirs(dir_name + "/" + file_name + "/" + file_name + "_styles")

    # Read image, optionally add titles and coordinates for city maps -------------------------------------------------

    # Read image
    image_highres = Image.open(file_string)
    width, height = image_highres.size
    image_highres = image_highres.convert("RGBA")

    if name:

        # Test if custom name given
        if not name_text:
            name_text = " ".join(str.split(map_name)[-words_name:]).upper()

        # Set up layer for drawing
        draw = ImageDraw.Draw(image_highres)

        # Add in white borders
        draw.rectangle([0, (height - 1350 - text_nudge), width, height], fill="#FFFFFF")

        # Set up fonts
        city_font = ImageFont.truetype("Scripts/Fonts/ADAM_kerning.ttf", int(800 * text_size))
        coords_font = ImageFont.truetype("Scripts/Fonts/Abel-Regular.ttf", int(370 * text_size))

        # Set up city and coordinate strings for plotting (using widths to centre)
        city_width, city_height = draw.textsize(name_text, font=city_font)
        coords_split = coordinates.replace("\xc2", "").split(", ")

        if len(coords_split[0]) > len(coords_split[1]):
            coords_split[1] = coords_split[1] + "  "

        elif len(coords_split[0]) < len(coords_split[1]):
            coords_split[0] = "  " + coords_split[0]

        # Combine coordinate string and add spaces to space around title, and between letters for kerning
        coords_new = coords_split[0] + " " * (city_width / int(173 * text_size) + 5) + coords_split[1]
        coords_new = " ".join(coords_new)
        coords_width, coords_height = draw.textsize(coords_new, font=coords_font)

        # Add city name and coordinates
        draw.text(((width-city_width)/2, (height - 1060 - text_nudge)), name_text, (0, 0, 0), font=city_font)
        draw.text(((width-coords_width)/2 + 10, (height - 960 - text_nudge)), coords_new, (0, 0, 0), font=coords_font)

        # Export to file
        image_highres.save(file_string, optimize=True)

    # Generate low resolution versions --------------------------------------------------------------------------------

    image_lowres = image_highres.copy()
    image_lowres.thumbnail((2300, 2000), Image.ANTIALIAS)
    image_lowres.save(dir_name + "/" + file_name + "/" + file_name + "_lowres.jpg", quality=85, optimize=True)
    image_insta = ImageOps.expand(image_lowres, border=500, fill="#FFFFFF")
    image_insta.save(dir_name + "/" + file_name + "/" + file_name + "_insta.jpg", quality=85, optimize=True)

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
        image_lowres.save(dir_name + "/" + file_name + "/" + file_name + "_watermark.jpg", quality=85, optimize=True)

    # Frame -----------------------------------------------------------------------------------------------------------

    # Horizontal frames
    if width > height:

        insert_frame(highres_input=image_highres,
                     size=(1200, 666),
                     location=(128, 128),
                     frame_path="Scripts/Elements/frame_hor_" + str(random.randint(1, 4)) + ".png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_frame.jpg",
                     nine_styles=nine_styles)

    # Square frames
    elif width == height:

        insert_frame(highres_input=image_highres,
                     size=(781, 781),
                     location=(216, 74),
                     frame_path="Scripts/Elements/frame_sq_" + str(random.randint(1, 4)) + ".png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_hor.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_frame.jpg",
                     nine_styles=nine_styles)

    # Vertical frames
    elif width < height:

        insert_frame(highres_input=image_highres,
                     size=(643, 1175),
                     location=(277, 137),
                     frame_path="Scripts/Elements/frame_vert_" + str(random.randint(1, 4)) + ".png",
                     frame_ninestyles="Scripts/Elements/frame_9styles_vert.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_frame.jpg",
                     nine_styles=nine_styles)

    # Subsets ---------------------------------------------------------------------------------------------------------

    # Save middle inset
    image_zoom_middle = image_highres.crop((int(width * 0.500 - max(width, height) * (inset_zoom * 0.5)),
                                     int(height * 0.49 - max(width, height) * (inset_zoom * 0.5)),  # 0.388
                                     int(width * 0.500 + max(width, height) * (inset_zoom * 0.5)),
                                     int(height * 0.49 + max(width, height) * (inset_zoom * 0.5))))
    image_zoom_middle.save(dir_name + "/" + file_name + "/" + file_name + "_zoom_1.jpg", quality=85, optimize=True)

    # Save bottom inset
    image_zoom = image_highres.crop((int(width * 0.5 - width * 0.2),
                                     int(height - width * 0.3),
                                     int(width * 0.5 + width * 0.2),
                                     int(height)))
    image_zoom.thumbnail((3000, 2500), Image.ANTIALIAS)
    image_zoom.save(dir_name + "/" + file_name + "/" + file_name + "_zoom_2.jpg", quality=85, optimize=True)

    # Save random insets
    for zoom in range(3, subsets + 1):
        x = random.randint(int(width * 0.2), int(width * 0.8))
        y = random.randint(int(height * 0.2), int(height * 0.8))
        image_zoom = image_highres.crop((x - int(max(width, height) * (inset_zoom * 0.5)),
                                         y - int(max(width, height) * (inset_zoom * 0.5)),
                                         x + int(max(width, height) * (inset_zoom * 0.5)),
                                         y + int(max(width, height) * (inset_zoom * 0.5))))
        image_zoom.save(dir_name + "/" + file_name + "/" + file_name + "_zoom_" + str(zoom) + ".jpg", quality=85, optimize=True)
        image_zoom.close()

    # Physical map frames and Featured On
    print("Physical maps:")
    physical_maps(file_string=file_string,
                  map_name=map_name,
                  words_name=words_name)

    # Colors ----------------------------------------------------------------------------------------------------------

    if nine_styles:

        output_canvas = Image.open("Scripts/Elements/frame_nine_styles.png")

        if width > height:

            # Horizontal arrangement
            color_parameters = [ ["#000099", "#FFFFFF", "#000000", 1.3, 0.320, 0.010, 0.088, "blueonwhite"],
                                # ["#000000", "#FFFFFF", "#000000", 1.3, 0.320, 0.010, 0.088, "blackonwhite"],
                                ["#FFFFFF", "#006600", "",        1.3, 0.320, 0.339, 0.088, "whiteongreen"],
                                ["#006600", "#FFFFFF", "#000000", 1.4, 0.320, 0.668, 0.088, "greenonwhite"],
                                ["#FFFFFF", "#000000", "",        1.3, 0.320, 0.010, 0.392, "whiteonblack"],
                                ["#FFFFFF", "#000000", "",        1.0, 0.320, 0.339, 0.392, "lowres"],
                                ["#FFFFFF", "#000099", "",        1.3, 0.320, 0.668, 0.392, "whiteonblue"],
                                ["#0c6b71", "#FFFFFF", "#000000", 1.4, 0.320, 0.010, 0.695, "tealonwhite"],
                                ["#FFFFFF", "#990000", "",        1.3, 0.320, 0.339, 0.695, "whiteonred"],
                                ["#990000", "#FFFFFF", "#000000", 1.4, 0.320, 0.668, 0.695, "redonwhite"]]

        else:

            # Vertical arrangement
            color_parameters = [["#FFFFFF", "#000000", "",        1.3, 0.440, 0.010, 0.092, "whiteonblack"],
                                ["#0c6b71", "#FFFFFF", "#000000", 1.4, 0.440, 0.257, 0.092, "tealonwhite"],
                                ["#FFFFFF", "#006600", "",        1.3, 0.440, 0.504, 0.092, "whiteongreen"],
                                ["#000099", "#FFFFFF", "#000000", 1.3, 0.440, 0.752, 0.092, "blueonwhite"],
                                # ["#000000", "#FFFFFF", "#000000", 1.3, 0.440, 0.752, 0.092, "blackonwhite"],
                                ["#990000", "#FFFFFF", "#000000", 1.4, 0.440, 0.010, 0.542, "redonwhite"],
                                ["#FFFFFF", "#000099", "",        1.3, 0.440, 0.257, 0.542, "whiteonblue"],
                                ["#006600", "#FFFFFF", "#000000", 1.4, 0.440, 0.504, 0.542, "greenonwhite"],
                                ["#FFFFFF", "#990000", "",        1.3, 0.440, 0.752, 0.542, "whiteonred"]]

        for black_color, white_color, text_color, contrast, size, xdim, ydim, name in color_parameters:

            # Test if colored file exists either in image directory or 'Style' subdirectory
            if len(glob.glob(dir_name + "/" + file_name + "/" + file_name + "_" + name + '.*') +
                   glob.glob(dir_name + "/" + file_name + "/Styles/" + file_name + "_" + name + '.*')) == 0:

                # Rescale contrast
                contrast_scaled = (contrast - 1.0) * nine_styles_scale + 1

                # Add color to image
                print("Generating '" + name + "'")
                colorised = colorise_image(image_highres, black_color=black_color,
                                           white_color=white_color, contrast=contrast_scaled)

                # Set city title to black and white
                if len(text_color) > 0:

                    # Copy bottom of image, convert to greyscale then paste back
                    box = (0, (height - 1350 - text_nudge), width, height)
                    region = colorised.crop(box)
                    region = colorise_image(region, black_color=text_color, white_color=white_color)
                    colorised.paste(region, box)

                colorised.save(dir_name + "/" + file_name + "/" + file_name + "_styles/" + file_name + "_" + name + ".png",
                               quality=85, optimize=True)

            else:
                # If file already exists, load from either image directory or 'Style' subdirectory
                print("Loading '" + name + "' from file")
                colorised = Image.open((glob.glob(dir_name + "/" + file_name + "/" + file_name + "_" + name + '.*') +
                                        glob.glob(dir_name + "/" + file_name + "/" + file_name + "_styles/" + file_name +
                                                  "_" + name + '.*'))[0])

            # Resize color image according to parameters and paste into canvas
            colorised.thumbnail((int(output_canvas.width * size), int(output_canvas.height * size)), Image.ANTIALIAS)
            output_canvas.paste(colorised, (int(output_canvas.width * xdim), int(output_canvas.height * ydim)))

            # Close
            colorised.close()

        # Add to canvas
        output_canvas.save(dir_name + "/" + file_name + "/" + file_name + "_allstyles.png", quality=85, optimize=True)

    # Update Excel file -----------------------------------------------------------------------------------------------

    # Load excel data
    rb = open_workbook("Download links/DownloadandPrintingGuide_data.xls")
    r = rb.sheet_by_index(0).nrows

    # Main image Google Drive url
    service = get_service('C:/Users/z3287630/.credentials/drive-python-quickstart.json')
    main = service.files().list(q="name = '" + file_name + "_highres.png' ").execute()
    main_url = "https://drive.google.com/uc?export=download&id=" + main['files'][0]['id']

    # Styles folder Google Drive url
    styles = service.files().list(q="name = '" + file_name + "_styles' ").execute()
    styles_url = "https://drive.google.com/open?id=" + styles['files'][0]['id']

    # Set permissions
    new_permission = {'value': "", 'type': "anyone", 'role': "reader", 'withLink': True}
    service.permissions().create(fileId=main['files'][0]['id'], body=new_permission).execute()
    service.permissions().create(fileId=styles['files'][0]['id'], body=new_permission).execute()

    # Description
    desc = {'city': "Map created with QGIS using GIS trail and road data weighted and colored by increasing "
                          "size/importance (from small walking trails to large highways and motorways). Source data "
                          "copyright OpenStreetMap contributors available under CC BY-SA "
                          "(http://www.openstreetmap.org/copyright)",

            'roads': "Map created with QGIS using GIS trail and road data weighted and colored by increasing "
                     "size/importance (from small walking trails to large highways and motorways). Source data "
                     "copyright OpenStreetMap contributors available under CC BY-SA "
                     "(http://www.openstreetmap.org/copyright)",

            'wedding': "Map created with QGIS using GIS trail and road data weighted and colored by increasing "
                    "size/importance (from small walking trails to large highways and motorways). Source data "
                    "copyright OpenStreetMap contributors available under CC BY-SA "
                    "(http://www.openstreetmap.org/copyright)",

            'buildings': "Map created with QGIS using GIS building footprint features. Source data copyright "
                         "OpenStreetMap contributors available under CC BY-SA (http://www.openstreetmap.org/copyright)",

            'buildingsuk': "Map based on modified OS data Crown copyright and database right (2016), available: "
                           "https://www.ordnancesurvey.co.uk/business-and-government/products/os-open-map-local.html",

            'shadow': "Produced using 90m digital elevation data from the CGIAR-CSI SRTM 90m Database available "
                           "from http://srtm.csi.cgiar.org.",

            'waterwayshs': "This map incorporates data from the HydroSHEDS database which is copyright World Wildlife "
                          "Fund, Inc. (2006-2013) and has been used herein under license. WWF has not evaluated the "
                          "data as altered and incorporated within this map, and therefore gives no warranty regarding "
                          "its accuracy, completeness, currency or suitability for any particular purpose. Portions of "
                          "the HydroSHEDS database incorporate data which are the intellectual property rights of USGS "
                          "(2006-2008), NASA (2000-2005), ESRI (1992-1998), CIAT (2004-2006), UNEP-WCMC (1993), WWF "
                          "(2004), Commonwealth of Australia (2007), and Her Royal Majesty and the British Crown and "
                          "are used under license. The HydroSHEDS database and more information are available at "
                          "http://www.hydrosheds.org.",

            'waterwaysus': "Map created with QGIS using GIS data for streams and waterbodies from 1:100,000 scale "
                            "USGS National Hydrography Dataset vector datasets (U.S. Geological Survey, 2007-2014, "
                            "National Hydrography Dataset available on the World Wide Web (http://nhd.usgs.gov), "
                            "accessed 20 April 2016).",

            'waterwaysau': "Map created with open-source QGIS (http://www.qgis.org/en/site/), using a "
                                   "combination of freely available Commonwealth of Australia (Bureau of Meteorology) "
                                   "2016 Geofabric river data (http://www.bom.gov.au/water/geofabric/) and GA Geodata "
                                   "Topo 250K waterbody features (http://www.ga.gov.au/metadata-gateway/metadata/"
                                   "record/gcat_63999). Data used under a Creative Commons Attribution 4.0 "
                                   "International Licence. Full terms at https://creativecommons.org/licenses/by/4.0/."}

    # If current map not in sheet, add to excel
    if map_name not in rb.sheet_by_index(0).col_values(0):

        # Append data to last row
        wb = copy(rb)
        s = wb.get_sheet(0)
        s.write(r, 0, map_name)
        s.write(r, 3, "/" + file_string)
        s.write(r, 5, str(width) + " x " + str(height))

        # Depending on ninestyles and if waterways, customise url/map names
        if nine_styles and (map_desc[0:-2] == "waterways"):
            s.write(r, 1, map_name + " (blue on white); " + map_name + " (eight other styles)")
            s.write(r, 2, main_url + ";" + styles_url)

        elif nine_styles and map_desc[0:-2] != "waterways":
            s.write(r, 1, map_name + " (black on white); " + map_name + " (eight other styles)")
            s.write(r, 2, main_url + ";" + styles_url)

        else:
            s.write(r, 1, map_name)
            s.write(r, 2, main_url)

        # Add description from dict; add nothing if key does not exist
        try:
            s.write(r, 6, desc[map_desc])
        except:
            s.write(r, 6, "")

        # Set column widths
        s.col(0).width = 7000
        s.col(1).width = 7000
        s.col(2).width = 18000
        s.col(3).width = 9700
        s.col(4).width = 6500
        s.col(5).width = 3800

        # Save to excel document
        wb.save('Download links/DownloadandPrintingGuide_data.xls')
        print("Added data to excel!")

    else:

        print("No data added to excel")

    # Generate PDF ----------------------------------------------------------------------------------------------------
    try:

        # If description exists, create PDF
        default_desc = desc[map_desc]
        generate_pdf(map_name)

    except:

        # If no default description
        print("Generating PDF failed; no default description")

    # Close files -----------------------------------------------------------------------------------------------------

    image_highres.close()
    image_lowres.close()


# Setup ---------------------------------------------------------------------------------------------------------------

image_manipulation(file_string='USA/manhattan_buildings_highres.png',
                   map_name='Buildings of Manhattan',
                   words_name=1,
                   inset_zoom=0.13,
                   subsets=75,
                   watermark=False,

                   # Text
                   name=False,
                   coordinates='43.0125° N, 83.6875° W',
                   text_size=1,  # 1.4 for states
                   text_nudge=0,  # 800 for states
                   # name_text='',

                   # Styles
                   nine_styles=True,
                   nine_styles_scale=0.1)  # 0.1, 1.2

# Generate tags and title
map_name = "Waterways of Australia"
etsy_title(map_name, 1, True)
etsy_tags(map_name, 1)

# Re-generate PDF
generate_pdf(map_name)

# Physical maps mockups
physical_maps(file_string="Australia/melbourne_city_highres.png",
              map_name='Every Road in Melbourne',
              words_name=1)


# import requests
# url = 'https://maps.googleapis.com/maps/api/geocode/json'
# params = {'sensor': 'false', 'address': 'Birmingham, USA'}
# r = requests.get(url, params=params)
# results = r.json()['results']
# location = results[0]['geometry']['location']
# location['lat'], location['lng']

# CMYK conversion -----------------------------------------------------------------------------------------------------
#
# image_cmyk = ImageCms.profileToProfile(image_highres,
#                                         "D:/Dropbox/EarthArtAustralia/Scripts/ICC/RGB/AdobeRGB1998.icc",
#                                         "D:/Dropbox/EarthArtAustralia/Scripts/ICC/CMYK/USWebCoatedSWOP.icc",
#                                         outputMode="CMYK", renderingIntent=2)
# image_cmyk.getbands()
# image_cmyk.save(file_string[:-12] + "_cmyk.tif",  compression="tiff_deflate")
#
# # Improve contrast
# c, m, y, k = image_cmyk.split()
# c = ImageEnhance.Brightness(c).enhance(1.2)
# c = ImageEnhance.Contrast(c).enhance(0.9)
# m = ImageEnhance.Contrast(m).enhance(2)
# y = ImageEnhance.Contrast(y).enhance(1.4)
#
# image_cmyk_enhanced = Image.merge(image_cmyk.mode, (c,m,y,k))
# image_cmyk_enhanced.save(file_string[:-12] + "_cmyk.tif",  compression="tiff_deflate")
#
# image_highres = Image.open(file_string[:-12] + "_cmyk.tif")



# Featured on
inset_test = Image.open("Custom/test_buildings_highres.png")

# Single
mockup_test = Image.open("Scripts/Elements/mockups/mockup_template_vert.png")
mockup_test_overlay = mockup_test.copy()

inset_test.thumbnail((1150, 1150), Image.ANTIALIAS)
mockup_test.paste(inset_test, (668-(inset_test.width / 2), 1240 - inset_test.height), mask=inset_test)

mockup_test.paste(mockup_test_overlay, (0, 0), mask=mockup_test_overlay)
mockup_test.save("Scripts/Elements/mockups/test.png", quality=85, optimize=True)
mockup_test.close()

# Double

mockup_test = Image.open("Scripts/Elements/mockups/mockup_sizes_vert.png")
mockup_test_overlay = mockup_test.copy()

inset_test.thumbnail((1022, 1022), Image.ANTIALIAS)
mockup_test.paste(inset_test, (668-(inset_test.width / 2), 1240 - inset_test.height), mask=inset_test)
inset_test.thumbnail((1150, 1150), Image.ANTIALIAS)
mockup_test.paste(inset_test, (668-(inset_test.width / 2), 1240 - inset_test.height), mask=inset_test)

mockup_test.paste(mockup_test_overlay, (0, 0), mask=mockup_test_overlay)
mockup_test.save("Scripts/Elements/mockups/test.png", quality=85, optimize=True)
mockup_test.close()




image_zoom_middle.thumbnail((755, 755), Image.ANTIALIAS)
featuredon_overlay = Image.open("Scripts/Elements/featuredon_overlay.png")
image_zoom_middle.paste(featuredon_overlay, (0, 0), mask=featuredon_overlay)
image_zoom_middle.save(dir_name + "/" + file_name + "/" + file_name + "_featuredon.jpg", quality=85, optimize=True)
image_zoom_middle.close()




