# coding=utf-8
__author__ = 'z3287630'

# Import modules
import glob
import itertools
import os
import random
import subprocess
import textwrap
import httplib2

import pandas as pd
from PIL import Image, ImageEnhance, ImageOps, ImageFont, ImageDraw
from apiclient import discovery, errors
from geopy import geocoders
from oauth2client.file import Storage
from xlrd import open_workbook
from xlutils.copy import copy


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

    new_permission = {'value': value,
                      'type': perm_type,
                      'role': role,
                      'withLink': link}
    try:
        return service.permissions().insert(fileId = file_id, body = new_permission).execute()

    except errors.HttpError, error:

        print('An error occurred')

    return None


# Recolor greyscale image by stretching between black and white color
def colorise_image(src, black_color ="#FFFFFF", white_color ="#000000", contrast=1.0):

    src.load()
    src = src.convert("RGBA")
    r, g, b, alpha = src.split()
    gray = ImageOps.grayscale(src)
    gray = ImageEnhance.Contrast(gray).enhance(contrast)
    result = ImageOps.colorize(gray, black_color, white_color)
    result.putalpha(alpha)
    return result


# Produces output colorised images using colorise_image
def custom_color(highres_input, black_color, white_color, text_color, contrast, title_nudge, name, styles_path):

    # If highres_input is an image, else if a path:
    if isinstance(highres_input, basestring):
        highres_input = Image.open(highres_input)

    # Define image size
    width, height = highres_input.size

    # Rescale contrast
    contrast_scaled = contrast

    # Add color to image
    print("    Generating '" + name + "'")
    colorised = colorise_image(src=highres_input, black_color=black_color,
                               white_color=white_color, contrast=contrast_scaled)

    # Set city title to black and white
    if len(text_color) > 0:

        # Copy bottom of image, convert to grey-scale then paste back
        box = (0, (height - 1350 - title_nudge), width, height)
        region = highres_input.crop(box)
        colorised.paste(region, box)

    colorised.convert("RGB").save(styles_path + styles_path.split("/")[1] + "_" + name + ".jpg")

    return colorised


# Generate all nine color styles and add to 3x3 or 2x4 frame
def color_styles(highres_input, blue, nine_styles, nine_styles_scale, title_nudge, styles_path):

    print("Nine styles:")

    # If highres_input is an image, else if a path:
    if isinstance(highres_input, basestring):
        highres_input = Image.open(highres_input)

    # Define image size
    width, height = highres_input.size

    # Change blue on white to black on white for blue maps
    if blue:
        bw_blue_hor = ["#000000", "#FFFFFF", "#000000", 1.3, 0.290, 0.030, 0.352, "blackonwhite"]
        bw_blue_vert = ["#000000", "#FFFFFF", "#000000", 1.3, 0.400, 0.269, 0.057, "blackonwhite"]
        output_canvas_vert = "Scripts/Elements/frame_ninestyles_vertblue.png"
        output_canvas_hor = "Scripts/Elements/frame_ninestyles_horblue.png"

        # Write temp placeholder image so sync happens quickly
        Image.new('RGB', (1, 1)).save(styles_path + styles_path.split("/")[1] + "_blueonwhite.jpg", quality=1)

    else:
        bw_blue_hor = ["#000099", "#FFFFFF", "#000000", 1.3, 0.290, 0.030, 0.352, "blueonwhite"]
        bw_blue_vert = ["#000099", "#FFFFFF", "#000000", 1.3, 0.400, 0.269, 0.057, "blueonwhite"]
        output_canvas_vert = "Scripts/Elements/frame_ninestyles_vertbw.png"
        output_canvas_hor = "Scripts/Elements/frame_ninestyles_horbw.png"

        # Write temp placeholder image so sync happens quickly
        Image.new('RGB', (1, 1)).save(styles_path + styles_path.split("/")[1] + "_blackonwhite.jpg", quality=1)

    if width > height:

        # Read in canvas
        output_canvas = Image.open(output_canvas_hor)

        # Horizontal arrangement
        color_parameters = [["#FFFFFF", "#006600", "",        1.3, 0.290, 0.030, 0.044, "whiteongreen"],
                            ["#FFFFFF", "#000000", "",        1.3, 0.290, 0.355, 0.044, "whiteonblack"],
                            ["#FFFFFF", "#000099", "",        1.3, 0.290, 0.680, 0.044, "whiteonblue"],
                            bw_blue_hor,
                            ["#006600", "#FFFFFF", "#000000", 1.4, 0.290, 0.680, 0.352, "greenonwhite"],
                            ["#FFFFFF", "#085d72", "",        1.3, 0.290, 0.030, 0.660, "whiteonteal"],
                            ["#FFFFFF", "#474c48", "",        1.3, 0.290, 0.355, 0.660, "whiteongrey"],
                            ["#FFFFFF", "#990000", "",        1.3, 0.290, 0.680, 0.660, "whiteonred"]]

        # Resize low_res according to parameters and paste into middle of horizontal canvas
        image_lowres = highres_input.copy()
        image_lowres.thumbnail((int(output_canvas.width * 0.29), int(output_canvas.height * 0.29)), Image.ANTIALIAS)
        output_canvas.paste(image_lowres, (int(output_canvas.width * 0.355), int(output_canvas.height * 0.352)))

    else:

        # Read in canvas
        output_canvas = Image.open(output_canvas_vert)

        # Vertical arrangement
        color_parameters = [["#FFFFFF", "#006600", "",        1.3, 0.400, 0.030, 0.057, "whiteongreen"],
                            bw_blue_vert,
                            ["#FFFFFF", "#085d72", "",        1.3, 0.400, 0.509, 0.057, "whiteonteal"],
                            ["#FFFFFF", "#990000", "",        1.3, 0.400, 0.748, 0.057, "whiteonred"],
                            ["#FFFFFF", "#000099", "",        1.3, 0.400, 0.030, 0.517, "whiteonblue"],
                            ["#FFFFFF", "#474c48", "",        1.3, 0.400, 0.269, 0.517, "whiteongrey"],
                            ["#006600", "#FFFFFF", "#000000", 1.4, 0.400, 0.509, 0.517, "greenonwhite"],
                            ["#FFFFFF", "#000000", "",        1.3, 0.400, 0.748, 0.517, "whiteonblack"]]

    if nine_styles:

        for black_color, white_color, text_color, contrast, size, xdim, ydim, name in color_parameters:

            # If either .jpg or .png version of color style exists, load from file
            try:

                # Import from file
                colorised_path = glob.glob(styles_path + styles_path.split("/")[-2][:-7] + "_" + name + ".jpg")[0]
                colorised = Image.open(colorised_path)

            except:

                # Recolor images and save to style directory
                colorised = custom_color(highres_input=highres_input,
                                         black_color=black_color,
                                         white_color=white_color,
                                         text_color=text_color,
                                         contrast=(contrast - 1.0) * nine_styles_scale + 1,
                                         title_nudge=title_nudge,
                                         name=name,
                                         styles_path=styles_path)

            # Resize color image according to parameters and paste into canvas
            colorised.thumbnail((int(output_canvas.width * size), int(output_canvas.height * size)), Image.ANTIALIAS)
            output_canvas.paste(colorised, (int(output_canvas.width * xdim), int(output_canvas.height * ydim)))

            # Close
            colorised.close()

    # Finally, save original image as new JPG, overwriting 1x1 pixel placeholder image
    if blue:
        highres_input.convert("RGB").save(styles_path + styles_path.split("/")[1] + "_blueonwhite.jpg")
    else:
        highres_input.convert("RGB").save(styles_path + styles_path.split("/")[1] + "_blackonwhite.jpg")

    # Save canvas
    output_canvas.convert("RGB").save(styles_path.replace("_styles/", "_allstyles.jpg"), quality=85, optimize=True)


# Insert thumbnail into frame images
def insert_frame(highres_input, size, location, frame_path, ouput_path):

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
    etsy_frame.convert("RGB").save(ouput_path, compress_level=1)

    return etsy_frame


# uses insert_frame to create cover images
def etsy_frame(highres_input, ouput_path, map_name, nine_styles=True, metric=False):

    # If highres_input is an image, else if a path:
    if type(highres_input) is not Image.Image:
        highres_input = Image.open(highres_input)

    # Define image size
    width, height = highres_input.size
    vertical = width < height

    # Params: vert   9st,  met,  csize,  cx, cy, fsize1, fsize2, fx, fy, name,
    pars = [[False, True,  False, 1051, 254, 93, 1200, 666, 128, 128, "cover_hor.png"],
            [False, True,   True, 1051, 254, 93, 1200, 666, 128, 128, "cover_hor_metric.png"],
            [False, False, False, 1051, 254, 93, 1200, 666, 128, 128, "cover_hor_nostyles.png"],
            [False, False,  True, 1051, 254, 93, 1200, 666, 128, 128, "cover_hor_nostyles_metric.png"],
            [True,  True,  False, 1150, 267, 92, 643, 1175, 277, 137, "cover_vert.png"],
            [True,  True,   True, 1150, 267, 92, 643, 1175, 277, 137, "cover_vert_metric.png"],
            [True,  False, False, 1150, 267, 92, 643, 1175, 277, 137, "cover_vert_nostyles.png"],
            [True,  False,  True, 1150, 267, 92, 643, 1175, 277, 137, "cover_vert_nostyles_metric.png"]]

    par = [par for par in pars if par[0] == vertical and par[1] == nine_styles and par[2] == metric][0]
    csize, cx, cy, fsize1, fsize2, fx, fy, name = par[3:]

    # New covers
    cover_image = insert_frame(highres_input=highres_input,
                               size=(csize, csize),
                               location=(cx, cy),
                               frame_path="Scripts/Elements/Printable/" + name,
                               ouput_path=ouput_path + "_cover.jpg")

    # Old style frames
    frame_or = {True: "vert", False: "hor"}
    insert_frame(highres_input=highres_input,
                 size=(fsize1, fsize2),
                 location=(fx, fy),
                 frame_path="Scripts/Elements/frame_" + frame_or[vertical] + "_" + str(random.randint(1, 3)) + ".png",
                 ouput_path=ouput_path + "_frame.jpg")

    # Horizontal frames
    if width > height:

        # Set up layer for drawing
        draw = ImageDraw.Draw(cover_image)
        lines = textwrap.wrap(map_name, width=14)

        # Set up fonts
        font = ImageFont.truetype("Scripts/Fonts/ADAM-CG PRO.ttf", 125)

        # Add name to cover plot
        line1_width, line1_height = draw.textsize(lines[0], font=font)
        line2_width, line2_height = draw.textsize(lines[1], font=font)
        draw.text(((249 + (1075 - line1_width) / 2), 985), lines[0], (0, 0, 0), font=font)
        draw.text(((249 + (1075 - line2_width) / 2), 985 + line1_height * 1.3), lines[1], (0, 0, 0), font=font)

    # Vertical frames
    else:

        # Set up layer for drawing
        draw = ImageDraw.Draw(cover_image)
        lines = textwrap.wrap(map_name, width=13)

        y_loc = 0
        line_height = 0
        for line in lines:

            # Add last line y location to total so that each line is plotted below last
            y_loc += line_height

            # Use while loop to maximise font size
            size = 0
            while (draw.textsize(line, font=ImageFont.truetype("Scripts/Fonts/ADAM-CG PRO.ttf", size))[0] < 600) and \
                    (draw.textsize(line, font=ImageFont.truetype("Scripts/Fonts/ADAM-CG PRO.ttf", size))[1] < 95):

                # Measure height and width of text using current font size
                font = ImageFont.truetype("Scripts/Fonts/ADAM-CG PRO.ttf", size)
                line_width, line_height = draw.textsize(line, font=font)
                size = size + 1

            # Plot font at resulting size, centred in frame using last-calculated width and cumulative height (y_loc)
            spacing_factor = (0.8 / len(lines)) * 3 + 0.28
            offset_factor = 65 + (len(lines) > 2) * -27

            draw.text(((1165 + (620 - line_width) / 2), offset_factor + y_loc * spacing_factor), line, (0, 0, 0),
                      font=font)

        # Add overlay to improve spacing if name takes less than 160 characters
        if (y_loc + line_height) < 160:

            frame_met = {True: "_metric", False: ""}
            overlay = Image.open("Scripts/Elements/Printable/cover_vert_overlay" + frame_met[metric] + ".png")
            cover_image.paste(overlay, (0, 0), overlay)

    # Save to file
    cover_image.convert("RGB").save(ouput_path + "_cover.jpg", optimize=True)


# Update listings
def update_listings(name_text):

    # Set up and run geocoder
    gn = geocoders.GoogleV3()

    try:
        geocode_results, (lat, lng) = gn.geocode(name_text)
        country = geocode_results.split(", ")[-1].encode("UTF-8")

    except:
        print("Geocoding failed")
        country = ""

    # Replace city names in template file and write to new file
    f1 = open('Scripts/listing_templates.txt', 'r')
    f2 = open('listings.txt', 'w')
    for line in f1:

        # If country is the same as name or if geocode failed
        if country == name_text or country == "":
            f2.write(line.replace('[NAME]', name_text).replace('[COUNTRY]', ""))
        else:
            f2.write(line.replace('[NAME]', name_text).replace('[COUNTRY]', ", " + country))

    f1.close()
    f2.close()

    return(country)


# Generate tags
def etsy_tags(title, words_name, physical=False, copy_clipboard=True):

    name = " ".join(str.split(title)[-words_name:])

    # Find country using geocode
    geo = update_listings(name)

    # If geocode produces result, append text
    if len(geo) > 0:
        geo = ", " + geo + " map"

    if physical:
        words = ["XX map poster", "XX print", "XX map print", "XX city map", "XX poster", "XX wall art",
                 "XX art print", "Map of XX", "XX gift", "XX map art", "XX art", "XX map"]
    else:
        words = ["XX map print", "XX print", "XX city map", "XX art print", "XX poster", "XX wall art",
                 "Map of XX", "XX map poster", "XX gift", "XX printable", "XX map art", "XX art", "XX map"]

    words_new = [w.replace('XX', name) for w in words]
    title_string = ", ".join(words_new) + geo

    # Print and copy to clipboard
    print("    " + title_string)
    df = pd.DataFrame([title_string])

    # Optionally copy to clipboard
    if copy_clipboard:
        df.to_clipboard(index=False, header=False)


# Generate titles
def etsy_title(title, words_name, physical=False, copy_clipboard=True):

    name = " ".join(str.split(title)[-words_name:])

    # Find country using geocode
    geo = update_listings(name)

    # If geocode produces result, append text
    if len(geo) > 0:
        geo = ", " + geo + " map"

    if physical:
        words = [title + " map poster", "XX print", "XX map print", "XX city map", "XX poster", "XX wall art",
                 "XX art print", "Map of XX", "XX gift", "XX map art", "XX art"]
    else:
        words = ["XX map print", "XX print", "XX city map", "XX poster", "XX wall art", "Map of XX", "XX art print",
                 "XX map poster", "XX gift", "XX printable", "XX map art", "XX art"]

    words_new = [w.replace('XX', name) for w in words]
    title_string = ", ".join(words_new[0:3]) + geo
    remainder = words_new[3:]

    # Incrementally add on words until length exceeds maximum
    while len(title_string) + len(remainder[0]) < 139:
        title_string = title_string + ", " + remainder.pop(0)

    # Print and copy to clipboard
    print("    " + title_string)
    df = pd.DataFrame([title_string])

    # Optionally copy to clipboard
    if copy_clipboard:
        df.to_clipboard(index=False, header=False)


# Physical maps
def physical_maps(highres_input, output_path, map_name, words_name, offset=False, templates=False, copy_clipboard=True):

    # If highres_input is an image, else if a path:
    if type(highres_input) is not Image.Image:
        highres_input = Image.open(highres_input)

    # Define image size
    width, height = highres_input.size

    if map_name is not "":

        # Generate tags and title
        etsy_title(title=map_name, words_name=words_name, physical=True, copy_clipboard=copy_clipboard)
        etsy_tags(title=map_name, words_name=words_name, physical=True, copy_clipboard=copy_clipboard)

    # Choice of random overlay
    x = str(random.randrange(1,6))

    # Resize image at start to optimise timing
    size_image = highres_input.copy()
    size_image.thumbnail((1153, 1153), Image.ANTIALIAS)

    # Vertical
    if height > width:

        # Main mockup
        insert_frame(highres_input=size_image,
                     size=(1153, 1153),
                     location=(668 - (int(1153 / 1.4189) / 2), 1240 - 1153),
                     frame_path="Scripts/Elements/mockups/mockup_template_vert" + x + ".png",
                     ouput_path=output_path + "_mockup.jpg")

        # Wall mockup
        insert_frame(highres_input=size_image,
                     size=(702, 702),
                     location=(1027 - (int(702 / 1.4189) / 2), 960 - 702),
                     frame_path="Scripts/Elements/mockups/mockup_wall_vert.png",
                     ouput_path=output_path + "_mockupwall.jpg")

        # Size frames
        size_frame = Image.open("Scripts/Elements/mockups/mockup_sizes_vert.png")
        size_frame_overlay = size_frame.copy()

        # Copy highres_input, and sequentially add to plot
        size_1, size_2, size_3 = [1041, 748, 525]
        xoff_1, xoff_2, xoff_3 = [440, 1155, 1705]
        yoff_1, yoff_2, yoff_3 = [1196, 859, 679]
        size_image.thumbnail((size_1, size_1), Image.ANTIALIAS)
        size_frame.paste(size_image, (xoff_1 - (int(size_1 / 1.4189) / 2), yoff_1 - size_1))
        size_image.thumbnail((size_2, size_2), Image.ANTIALIAS)
        size_frame.paste(size_image, (xoff_2 - (int(size_2 / 1.4189) / 2), yoff_2 - size_2 + 12 * offset))
        size_image.thumbnail((size_3, size_3), Image.ANTIALIAS)
        size_frame.paste(size_image, (xoff_3 - (int(size_3 / 1.4189) / 2), 679 - size_3))

        # Put overlay over the top and save
        size_frame.paste(size_frame_overlay, (0, 0), size_frame_overlay)
        size_frame.convert("RGB").save(output_path + "_sizes.jpg")

    # Horizontal
    else:

        insert_frame(highres_input=size_image,
                     size=(1153, 1153),
                     location=(882 - int(1153 / 2), 850 - int(1153 / 1.4189) + 17 * offset),
                     frame_path="Scripts/Elements/mockups/mockup_template_hor" + x + ".png",
                     ouput_path=output_path + "_mockup.jpg")

        # Wall mockup
        insert_frame(highres_input=size_image,
                     size=(702, 702),
                     location=(1006 - int(702 / 2), 810 - int(702 / 1.4189) + 12 * offset),
                     frame_path="Scripts/Elements/mockups/mockup_wall_hor.png",
                     ouput_path=output_path + "_mockupwall.jpg")

        # Size frames
        size_frame = Image.open("Scripts/Elements/mockups/mockup_sizes_hor.png")
        size_frame_overlay = size_frame.copy()

        # Sequentially add to plot
        size_image.thumbnail((1039, 1039), Image.ANTIALIAS)
        size_frame.paste(size_image, (588 - int(1039 / 2), 758 - int(1039 / 1.4189) + 14 * offset))
        size_image.thumbnail((749, 749), Image.ANTIALIAS)
        size_frame.paste(size_image, (1562 - int(749 / 2), 580 - int(749 / 1.4189)))
        size_image.thumbnail((533, 533), Image.ANTIALIAS)
        size_frame.paste(size_image, (333 - int(533 / 2), 1204 - int(533 / 1.4189) + 14 * offset))

        # Put overlay over the top and save
        size_frame.paste(size_frame_overlay, (0, 0), size_frame_overlay)
        size_frame.convert("RGB").save(output_path + "_sizes.jpg")

    # Close images
    size_image.close()
    size_frame.close()
    size_frame_overlay.close()

    # Generate template files with Printful safe printing area overlay
    if templates:

        print("Generating templates")

        # Rotate template files if horizontal
        if width > height:
            rotate_amount = 90
        else:
            rotate_amount = 0

        # For 24 x 36
        template_image = highres_input.copy()
        template_small = Image.open("D:/Google Drive/EarthArtAustralia/Printful/Posters/24x36/24x36.png")
        template_small = template_small.rotate(rotate_amount, expand=True)
        template_image.thumbnail((max(template_small.size), max(template_small.size)))
        template_small_overlay = template_small.copy()
        template_small.paste(template_image, ((template_small.width - template_image.width)/2,
                                              template_small.height - template_image.height), mask=template_image)
        template_small.paste(template_small_overlay, (0, 0), mask=template_small_overlay)
        template_small.thumbnail((1200, 1200))
        template_small.save(output_path + "_template24x36.jpg", quality=20, optimize=True)

        # For 18 x 24
        template_small = Image.open("D:/Google Drive/EarthArtAustralia/Printful/Posters/18x24/18x24.png")
        template_small = template_small.rotate(rotate_amount, expand=True)
        template_image.thumbnail((min(template_small.size)*1.4189, min(template_small.size)*1.4189))
        template_small_overlay = template_small.copy()
        template_small.paste(template_image, ((template_small.width - template_image.width)/2,
                                              template_small.height - template_image.height), mask=template_image)
        template_small.paste(template_small_overlay, (0, 0), mask=template_small_overlay)
        template_small.thumbnail((1200, 1200))
        template_small.save(output_path + "_template18x24.jpg", quality=20, optimize=True)

        # For 12 x 18
        template_small = Image.open("D:/Google Drive/EarthArtAustralia/Printful/Posters/12x18/12x18.png")
        template_small = template_small.rotate(rotate_amount, expand=True)
        template_image.thumbnail((max(template_small.size), max(template_small.size)))
        template_small_overlay = template_small.copy()
        template_small.paste(template_image, ((template_small.width - template_image.width)/2,
                                              template_small.height - template_image.height), mask=template_image)
        template_small.paste(template_small_overlay, (0, 0), mask=template_small_overlay)
        template_small.thumbnail((1200, 1200))
        template_small.save(output_path + "_template12x18.jpg", quality=20, optimize=True)

        # Close files
        template_small.close()
        template_image.close()


# Add map titles
def map_title(image_highres, file_string, title_name, title_nudge, title_size, title_font, coordinates=False,
              white_manual=False):

    # Define image size
    width, height = image_highres.size

    # Set up layer for drawing
    draw = ImageDraw.Draw(image_highres)

    # Add in white borders
    if white_manual is False:
        draw.rectangle([0, (height - 1360 - title_nudge), width, height], fill="#FFFFFF")
    else:
        print("Using manual white overlay")
        draw.rectangle([0, (height - white_manual), width, height], fill="#FFFFFF")

    # Set up fonts
    title_font = ImageFont.truetype(title_font, int(800 * title_size))
    coords_font = ImageFont.truetype("Scripts/Fonts/Abel-Regular.ttf", int(370 * title_size))

    # Set up city and coordinate strings for plotting (using widths to centre)
    title_width, title_height = draw.textsize(title_name, font=title_font)
    draw.text(((width - title_width) / 2, (height - 1065 - title_nudge)), title_name, (0, 0, 0), font=title_font)

    # If coords
    if coordinates:

        coords_split = coordinates.replace("\xc2", "").split(", ")

        if len(coords_split[0]) > len(coords_split[1]):
            coords_split[1] = coords_split[1] + "  "

        elif len(coords_split[0]) < len(coords_split[1]):
            coords_split[0] = "  " + coords_split[0]

        # Combine coordinate string and add spaces to space around title, and between letters for kerning
        coords_new = coords_split[0] + " " * (title_width / int(173 * title_size) + 5) + coords_split[1]
        coords_new = " ".join(coords_new)
        coords_width, coords_height = draw.textsize(coords_new, font=coords_font)
        draw.text(((width - coords_width) / 2 + 10, (height - 965 - title_nudge)), coords_new, (0, 0, 0),
                  font=coords_font)

    # Export to file
    image_highres.save(file_string, optimize=True)

    # Return image
    return image_highres


# Wedding
def wedding_map(file_string, couple_name, couple_size, couple_nudge, couple_font, date_name, date_size, date_nudge,
                date_font, white_manual=False):

    image_highres = Image.open(file_string)
    image_highres = image_highres.convert("RGBA")

    print("Adding names")
    image_highres = map_title(image_highres,
                              file_string=file_string,
                              title_name=couple_name,
                              title_size=couple_size,
                              title_nudge=couple_nudge,
                              title_font=couple_font,
                              white_manual=white_manual)

    print("Adding dates")
    image_highres = map_title(image_highres,
                              file_string=file_string,
                              title_name=date_name,
                              title_size=date_size,
                              title_nudge=date_nudge,
                              title_font=date_font,
                              white_manual=0)

    image_highres.close()


# Subset image into zooms
def image_subsets(highres_input, ouput_path, inset_zoom, x_offset=0, y_offset=0):

    # If highres_input is an image, else if a path:
    if type(highres_input) is not Image.Image:
        highres_input = Image.open(highres_input)

    # Define image size
    width, height = highres_input.size
    highres_input = highres_input.convert("RGBA")

    # Save middle inset
    image_zoom_middle = highres_input.crop((int(width * 0.500 - max(width, height) * (inset_zoom * 0.5)),
                                            int(height * 0.49 - max(width, height) * (inset_zoom * 0.5)),  # 0.388
                                            int(width * 0.500 + max(width, height) * (inset_zoom * 0.5)),
                                            int(height * 0.49 + max(width, height) * (inset_zoom * 0.5))))
    image_zoom_middle.convert("RGB").save(ouput_path + "_zoom_1.jpg", quality=85, optimize=True)

    # Save bottom inset
    image_zoom = highres_input.crop((int(width * 0.5 - width * 0.2),
                                     int(height - width * 0.3),
                                     int(width * 0.5 + width * 0.2),
                                     int(height)))
    image_zoom.thumbnail((3000, 2500), Image.ANTIALIAS)
    image_zoom.convert("RGB").save(ouput_path + "_zoom_2.jpg", quality=85, optimize=True)

    # Define start points of zooms including offsets
    x = int(x_offset * inset_zoom * max(width, height))
    y = int(y_offset * inset_zoom * max(width, height))
    x_dims = range(int(width * 0.14) + x, int(width * 0.86) + x, int(max(width, height) * (inset_zoom * 1.02)))
    y_dims = range(int(height * 0.14) + y, int(height * 0.86) + y, int(max(width, height) * (inset_zoom * 1.02)))

    for zoom, (x, y) in enumerate(itertools.product(x_dims, y_dims)):
        image_zoom = highres_input.crop((x - int(max(width, height) * (inset_zoom * 0.5)),
                                         y - int(max(width, height) * (inset_zoom * 0.5)),
                                         x + int(max(width, height) * (inset_zoom * 0.5)),
                                         y + int(max(width, height) * (inset_zoom * 0.5))))
        image_zoom.convert("RGB").save(ouput_path + "_zoom_" + str(zoom + 3) + ".jpg", quality=85, optimize=True)
        image_zoom.close()


# Generate PDF
def generate_pdf(map_name, file_string, desc, nine_styles=True):

    # Identify file name
    place, map_desc, res = os.path.basename(file_string[:-4]).split("_")
    file_name = place + "_" + map_desc

    # Set up Google Drive service
    service = get_service('Scripts/drive-python-quickstart.json')

    # Identify which JPG to import as main image depending on whether input is waterways (blue) or other (black)
    if map_desc[:9] == "waterways":
        bw_blue = "blueonwhite"
    else:
        bw_blue = "blackonwhite"

    try:

        # Main image Google Drive url
        main = service.files().list(q="name = '" + file_name + "_" + bw_blue + ".jpg' and trashed = false ").execute()
        main_url = "https://drive.google.com/uc?export=download&id=" + main['files'][0]['id']

        # Styles folder Google Drive url
        styles = service.files().list(q="name = '" + file_name + "_styles' and trashed = false ").execute()
        styles_url = "https://drive.google.com/open?id=" + styles['files'][0]['id']

        # Set permissions
        new_permission = {'value': "", 'type': "anyone", 'role': "reader", 'withLink': True}
        service.permissions().create(fileId=main['files'][0]['id'], body=new_permission).execute()
        service.permissions().create(fileId=styles['files'][0]['id'], body=new_permission).execute()

        # Update Excel file -------------------------------------------------------------------------------------------

        # Load excel data
        rb = open_workbook("Download links/DownloadandPrintingGuide_data.xls")
        r = rb.sheet_by_index(0).nrows

        # If current map not in sheet, add to excel
        if map_name not in rb.sheet_by_index(0).col_values(0):

            # Image details
            width, height = Image.open(file_string).size

            # Append data to last row
            wb = copy(rb)
            s = wb.get_sheet(0)
            s.write(r, 0, map_name)
            s.write(r, 3, "/" + file_string)
            s.write(r, 5, str(width) + " x " + str(height))

            # Depending on ninestyles and if waterways, customise url/map names
            if nine_styles and (map_desc[:9] == "waterways"):
                s.write(r, 1, map_name + " (blue on white); " + map_name + " (eight other styles)")
                s.write(r, 2, main_url + ";" + styles_url)

            elif nine_styles and map_desc[:9] != "waterways":
                s.write(r, 1, map_name + " (black on white); " + map_name + " (all colour styles)")
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

        # Get path to R script
        createdownload_path = os.getcwd() + '/Scripts/create_download_PDF.R'

        try:
            # Run on desktop
            subprocess.call(['Rscript', createdownload_path, map_name, os.getcwd()], shell=False)

        except WindowsError, e:

            # If file can't be found, try different Rpath
            if e.errno == 2:
                # Run on laptop
                print("Running on laptop")
                rpath = 'C:/Program Files/R/R-3.3.2/bin/Rscript'
                subprocess.call([rpath, createdownload_path, map_name, os.getcwd()], shell=True)

            else:
                # If other error, re-raise exception
                raise

        except:
            # If all fails
            print("Error generating PDF")

    except IndexError, e:
        print("File not synced to Google Drive")


# Featured on overlay
def featured_on(file_string, output_path, desc):

    # Identify map_desc
    _, map_desc, _ = os.path.basename(file_string[:-4]).split("_")

    # Featured on
    try:

        # Featured on
        image_zoom_middle = Image.open(output_path + "_zoom_1.jpg")
        image_zoom_middle.thumbnail((755, 755), Image.ANTIALIAS)
        featuredon_overlay = Image.open("Scripts/Elements/featuredon_overlay.png")
        image_zoom_middle.paste(featuredon_overlay, (0, 0), mask=featuredon_overlay)

        # Add text
        desc_text = desc[map_desc]
        desc_lines = textwrap.wrap(desc_text, width=100)
        draw = ImageDraw.Draw(image_zoom_middle)
        data_source_font = ImageFont.truetype("Scripts/Fonts/Abel-Regular.ttf", 18)

        # Iterate through lines in reverse order, adding to bottom of plot
        for i, line in enumerate(reversed(desc_lines)):

            line_width, _ = draw.textsize(line, font=data_source_font)
            draw.text((377 - (line_width / 2), (725 - i * 19)), line, (0, 0, 0), font=data_source_font)

        # Save
        image_zoom_middle.convert("RGB").save(output_path + "_featuredon.jpg", quality=85, optimize=True)

        # Close files
        image_zoom_middle.close()
        featuredon_overlay.close()

    # If file does not exist
    except IOError as e:

        print(e)

    # Other errors
    except:

        print("Cannot create 'Featured on'")
