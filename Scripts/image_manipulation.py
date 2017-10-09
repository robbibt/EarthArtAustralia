# coding=utf-8
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
import itertools
import subprocess
import textwrap
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


# Produces output colorised images using colorise_image
def custom_color(highres_input, black_color, white_color, text_color, contrast, title_nudge, name,
                 styles_path):
    # If highres_input is an image, else if a path:
    if type(highres_input) is not Image.Image:
        highres_input = Image.open(highres_input)

    # Define image size
    width, height = highres_input.size

    # Rescale contrast
    contrast_scaled = (contrast - 1.0) * nine_styles_scale + 1

    # Add color to image
    print("    Generating '" + name + "'")
    colorised = colorise_image(highres_input, black_color=black_color,
                               white_color=white_color, contrast=contrast_scaled)

    # Set city title to black and white
    if len(text_color) > 0:
        # Copy bottom of image, convert to greyscale then paste back
        box = (0, (height - 1350 - title_nudge), width, height)
        region = colorised.crop(box)
        region = colorise_image(region, black_color=text_color, white_color=white_color)
        colorised.paste(region, box)

    colorised.save(styles_path + styles_path.split("/")[1] + "_" + name + ".png", quality=85, optimize=True)

    return colorised


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
    etsy_frame.save(ouput_path)

    return etsy_frame


# uses insert_frame to create cover images
def etsy_frame(highres_input, ouput_path, map_name, nine_styles=True):

    # If highres_input is an image, else if a path:
    if type(highres_input) is not Image.Image:
        highres_input = Image.open(highres_input)

    # Define image size
    width, height = highres_input.size

    # Horizontal frames
    if width > height:

        # If nine styles, use nine styles frame
        if nine_styles:
            frame_path="Scripts/Elements/frame_hor.png"
        else:
            frame_path="Scripts/Elements/frame_hor_nostyles.png"


        cover_image = insert_frame(highres_input=highres_input,
                     size=(1051, 1051),
                     location=(693, 93),
                     frame_path=frame_path,
                     ouput_path=ouput_path)

        # Set up layer for drawing
        draw = ImageDraw.Draw(cover_image)
        lines = textwrap.wrap(map_name, width=13)

        # Set up fonts
        font = ImageFont.truetype("Scripts/Fonts/ADAM_kerning.ttf", 130)

        # Add name to cover plot
        line1_width, line1_height = draw.textsize(lines[0], font=font)
        line2_width, line2_height = draw.textsize(lines[1], font=font)
        draw.text(((680 + (1075 - line1_width) / 2), 985), lines[0], (0, 0, 0), font=font)
        draw.text(((680 + (1075 - line2_width) / 2), 985 + line1_height * 1.3), lines[1], (0, 0, 0), font=font)

        # Old style frame
        insert_frame(highres_input=highres_input,
                     size=(1200, 666),
                     location=(128, 128),
                     frame_path="Scripts/Elements/frame_hor_" + str(random.randint(1, 3)) + ".png",
                     ouput_path=ouput_path[:-9] + "frame.jpg")

    # Vertical frames
    else:

        # If nine styles, use nine styles frame
        if nine_styles:
            frame_path="Scripts/Elements/frame_vert.png"
        else:
            frame_path="Scripts/Elements/frame_vert_nostyles.png"

        cover_image = insert_frame(highres_input=highres_input,
                     size=(1150, 1150),
                     location=(923, 92),
                     frame_path=frame_path,
                     ouput_path=ouput_path)

        # Set up layer for drawing
        draw = ImageDraw.Draw(cover_image)
        lines = textwrap.wrap(map_name, width=11)

        # Set up fonts
        font = ImageFont.truetype("Scripts/Fonts/ADAM-CG PRO.ttf", 95)

        # If two lines, add name to image
        if len(lines) < 3:

            # Add name to cover image
            line1_width, line1_height = draw.textsize(lines[0], font=font)
            line2_width, line2_height = draw.textsize(lines[1], font=font)
            draw.text(((221 + (620 - line1_width) / 2), 75), lines[0], (0, 0, 0), font=font)
            draw.text(((221 + (620 - line2_width) / 2), 75 + line1_height * 1.35), lines[1], (0, 0, 0), font=font)

            # Add overlay to improve spacing if two lines
            overlay = Image.open("Scripts/Elements/frame_vert_overlay.png")
            cover_image.paste(overlay, (0, 0), overlay)


        else:

            # Set up fonts
            font_small = ImageFont.truetype("Scripts/Fonts/ADAM-CG PRO.ttf", 76)
            lines_small = textwrap.wrap(map_name, width=13)
            lines_large = textwrap.wrap(" ".join(lines_small[1:]), width=11)

            # Add name to cover image
            line1_width, line1_height = draw.textsize(lines_small[0], font=font_small)
            line2_width, line2_height = draw.textsize(lines_large[0], font=font)
            draw.text(((221 + (620 - line1_width) / 2), 65), lines_small[0], (0, 0, 0), font=font_small)
            draw.text(((221 + (620 - line2_width) / 2), 65 + line1_height * 1.28), lines_large[0], (0, 0, 0), font=font)

            try:
                line3_width, line3_height = draw.textsize(lines_large[1], font=font)
                draw.text(((221 + (620 - line3_width) / 2), 65 + line1_height * 2.75), lines_large[1], (0, 0, 0), font=font)

            except:

                # Add overlay to improve spacing if two lines
                overlay = Image.open("Scripts/Elements/frame_vert_overlay.png")
                cover_image.paste(overlay, (0, 0), overlay)

        # Old style frame
        insert_frame(highres_input=highres_input,
                     size=(643, 1175),
                     location=(277, 137),
                     frame_path="Scripts/Elements/frame_vert_" + str(random.randint(1, 3)) + ".png",
                     ouput_path=ouput_path[:-9] + "frame.jpg")

    # Save to file
    cover_image.save(ouput_path, optimize=True)


# Generate tags
def etsy_tags(title, words_name, physical=False):

    name = " ".join(str.split(title)[-words_name:])
    suffixes = ["map", "art", "poster", "print", "gift", "wall art", "map print", "map art", "art print"]

    if physical:
        tag_list = "Physical print, " + name + ", " + \
                   ", ".join([name + " " + s for s in suffixes])
    else:
        tag_list = "Printable " + name + ", " + name + ", " + \
                   ", ".join([name + " " + s for s in suffixes]) + \
                   ", Map of " + name

    # Print and copy to clipboard
    print("    " + tag_list)
    df = pd.DataFrame([tag_list])
    df.to_clipboard(index=False, header=False)


# Generate titles
def etsy_title(title, words_name, physical=False):

    name = " ".join(str.split(title)[-words_name:])

    if physical:
        title_string = title + " print | Physical " + name + " map print, " + name + " poster, " + name + " art, " + name + " map art"
    else:
        title_string = name + " map print, Printable " + name + " map art, " + name + " print, " + name + " art, " + name + " poster"

    if len(title_string + ", " + name + " wall art") < 141:
        title_string = title_string + ", " + name + " wall art"
        if len(title_string + ", " + name + " gift") < 141:
            title_string = title_string + ", " + name + " gift"
            if len(title_string + ", Map of " + name) < 141:
                title_string = title_string + ", Map of " + name

    # Print and copy to clipboard
    print("    " + title_string)
    df = pd.DataFrame([title_string])
    df.to_clipboard(index=False, header=False)


# Physical maps
def physical_maps(file_string, map_name, words_name, templates):

    if map_name is not "":

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
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_mockup.jpg")

        # Size frames
        insert_frame(highres_input=image_highres,
                     size=(1040, 1040),
                     location=(440 - (int(1040 / 1.4189) / 2), 1200 - 1040),
                     frame_path="Scripts/Elements/mockups/mockup_sizes_vert_v2.png",
                     ouput_path="Scripts/Elements/mockups/draft_overlay.png")
        insert_frame(highres_input=image_highres,
                     size=(737, 737),
                     location=(1155 - (int(737 / 1.4189) / 2), 858 - 737),
                     frame_path="Scripts/Elements/mockups/draft_overlay.png",
                     ouput_path="Scripts/Elements/mockups/draft_overlay.png")
        insert_frame(highres_input=image_highres,
                     size=(525, 525),
                     location=(1705 - (int(525 / 1.4189) / 2), 676 - 525),
                     frame_path="Scripts/Elements/mockups/draft_overlay.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_sizes.jpg")

    # Horizontal
    if width > height:

        inset_test = Image.open("Custom/test_city_highres.png")
        insert_frame(highres_input=image_highres,
                     size=(1153, 1153),
                     location=(882 - int(1153 / 2), 850 - int(1153 / 1.4189)),
                     frame_path="Scripts/Elements/mockups/mockup_template_hor" + x + ".png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_mockup.jpg")

        # Size frames
        insert_frame(highres_input=image_highres,
                     size=(1038, 1038),
                     location=(587 - int(1038 / 2), 757 - int(1038 / 1.4189)),
                     frame_path="Scripts/Elements/mockups/mockup_sizes_hor_v2.png",
                     ouput_path="Scripts/Elements/mockups/draft_overlay.png")
        insert_frame(highres_input=image_highres,
                     size=(743, 743),
                     location=(1560 - int(743 / 2), 580 - int(743 / 1.4189)),
                     frame_path="Scripts/Elements/mockups/draft_overlay.png",
                     ouput_path="Scripts/Elements/mockups/draft_overlay.png")
        insert_frame(highres_input=image_highres,
                     size=(533, 533),
                     location=(333 - int(533 / 2), 1204 - int(533 / 1.4189)),
                     frame_path="Scripts/Elements/mockups/draft_overlay.png",
                     ouput_path=dir_name + "/" + file_name + "/" + file_name + "_sizes.jpg")

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

    # Generate template files with Printful safe printing area overlay
    if templates:

        print("Generating templates")

        # Rotate template files if horizontal
        if width > height:
            rotate_amount = 90
        else:
            rotate_amount = 0

        # For 24 x 36
        template_image = image_highres.copy()
        template_small = Image.open("D:/Google Drive/EarthArtAustralia/Printful/Posters/24x36/24x36.png")
        template_small = template_small.rotate(rotate_amount, expand=True)
        template_image.thumbnail((max(template_small.size), max(template_small.size)))
        template_small_overlay = template_small.copy()
        template_small.paste(template_image, ((template_small.width - template_image.width)/2,
                                              template_small.height - template_image.height), mask=template_image)
        template_small.paste(template_small_overlay, (0, 0), mask=template_small_overlay)
        template_small.thumbnail((1200, 1200))
        template_small.save(dir_name + "/" + file_name + "/" + file_name + "_template24x36.jpg", quality=20, optimize=True)

        # For 18 x 24
        template_small = Image.open("D:/Google Drive/EarthArtAustralia/Printful/Posters/18x24/18x24.png")
        template_small = template_small.rotate(rotate_amount, expand=True)
        template_image.thumbnail((min(template_small.size)*1.4189, min(template_small.size)*1.4189))
        template_small_overlay = template_small.copy()
        template_small.paste(template_image, ((template_small.width - template_image.width)/2,
                                              template_small.height - template_image.height), mask=template_image)
        template_small.paste(template_small_overlay, (0, 0), mask=template_small_overlay)
        template_small.thumbnail((1200, 1200))
        template_small.save(dir_name + "/" + file_name + "/" + file_name + "_template18x24.jpg", quality=20, optimize=True)

        # For 12 x 18
        template_small = Image.open("D:/Google Drive/EarthArtAustralia/Printful/Posters/12x18/12x18.png")
        template_small = template_small.rotate(rotate_amount, expand=True)
        template_image.thumbnail((max(template_small.size), max(template_small.size)))
        template_small_overlay = template_small.copy()
        template_small.paste(template_image, ((template_small.width - template_image.width)/2,
                                              template_small.height - template_image.height), mask=template_image)
        template_small.paste(template_small_overlay, (0, 0), mask=template_small_overlay)
        template_small.thumbnail((1200, 1200))
        template_small.save(dir_name + "/" + file_name + "/" + file_name + "_template12x18.jpg", quality=20, optimize=True)
        template_small.close()

    # Close image
    image_highres.close()


# Add map titles
def map_title(image_highres, file_string, title_name, title_nudge, title_size, title_font, coordinates=False,
              white_manual=False):

    # Define image size
    width, height = image_highres.size

    # Set up layer for drawing
    draw = ImageDraw.Draw(image_highres)

    # Add in white borders
    if white_manual is False:
        draw.rectangle([0, (height - 1350 - title_nudge), width, height], fill="#FFFFFF")
    else:
        print("Using manual white overlay")
        draw.rectangle([0, (height - white_manual), width, height], fill="#FFFFFF")

    # Set up fonts
    title_font = ImageFont.truetype(title_font, int(800 * title_size))
    coords_font = ImageFont.truetype("Scripts/Fonts/Abel-Regular.ttf", int(370 * title_size))

    # Set up city and coordinate strings for plotting (using widths to centre)
    title_width, title_height = draw.textsize(title_name, font=title_font)
    draw.text(((width - title_width) / 2, (height - 1060 - title_nudge)), title_name, (0, 0, 0), font=title_font)

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
def wedding_map(file_string, couple_name, couple_size, couple_nudge, couple_font, date_name, date_size, date_nudge, date_font, white_manual=False):

    image_highres = Image.open(file_string)

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


# Generate PDF
def generate_pdf(map_name):

    try:
        subprocess.call(['Rscript', 'D:/Google Drive/EarthArtAustralia/Scripts/create_download_PDF.R', map_name],
                        shell=False)
    except:
        print("Error generating PDF")



# Entire function -----------------------------------------------------------------------------------------------------
def image_manipulation(file_string, map_name, words_name, inset_zoom, watermark, name, title_size, title_nudge,
                       nine_styles, nine_styles_scale, pdf, blue=False, coordinates=False, name_text=False):

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

        image_highres = map_title(image_highres,
                                  file_string=file_string,
                                  title_name=name_text,
                                  title_nudge=title_nudge,
                                  title_size=title_size,
                                  title_font="Scripts/Fonts/ADAM_kerning.ttf",
                                  coordinates=coordinates,
                                  white_manual=False)

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
    etsy_frame(highres_input=image_highres, ouput_path=dir_name + "/" + file_name + "/" + file_name + "_cover.jpg",
               map_name=map_name, nine_styles=nine_styles)


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

    x_dims = range(int(width * 0.14), int(width * 0.86), 2000)
    y_dims = range(int(height * 0.14), int(height * 0.86), 2000)

    for zoom, (x, y) in enumerate(itertools.product(x_dims, y_dims)):
        image_zoom = image_highres.crop((x - int(max(width, height) * (inset_zoom * 0.5)),
                                         y - int(max(width, height) * (inset_zoom * 0.5)),
                                         x + int(max(width, height) * (inset_zoom * 0.5)),
                                         y + int(max(width, height) * (inset_zoom * 0.5))))
        image_zoom.save(dir_name + "/" + file_name + "/" + file_name + "_zoom_" + str(zoom + 3) + ".jpg", quality=85, optimize=True)
        image_zoom.close()

    # Physical map frames and Featured On
    print("Physical maps:")
    physical_maps(file_string=file_string,
                  map_name=map_name,
                  words_name=words_name,
                  templates=False)

    # Colors ----------------------------------------------------------------------------------------------------------

    if nine_styles:

        print("Nine styles:")
        output_canvas = Image.open("Scripts/Elements/frame_nine_styles.png")

        # Change blue on white to black on white for blue maps
        if blue:
            bw_blue_hor = ["#000000", "#FFFFFF", "#000000", 1.3, 0.320, 0.010, 0.088, "blackonwhite"]
            bw_blue_vert = ["#000000", "#FFFFFF", "#000000", 1.3, 0.440, 0.752, 0.092, "blackonwhite"]
        else:
            bw_blue_hor = ["#000099", "#FFFFFF", "#000000", 1.3, 0.320, 0.010, 0.088, "blueonwhite"]
            bw_blue_vert = ["#000099", "#FFFFFF", "#000000", 1.3, 0.440, 0.752, 0.092, "blueonwhite"]

        if width > height:

            # Horizontal arrangement
            color_parameters = [bw_blue_hor,
                               ["#FFFFFF", "#006600", "",        1.3, 0.320, 0.339, 0.088, "whiteongreen"],
                               ["#006600", "#FFFFFF", "#000000", 1.4, 0.320, 0.668, 0.088, "greenonwhite"],
                               ["#FFFFFF", "#000000", "",        1.3, 0.320, 0.010, 0.392, "whiteonblack"],
                               ["#FFFFFF", "#000000", "",        1.0, 0.320, 0.339, 0.392, "lowres"],
                               ["#FFFFFF", "#000099", "",        1.3, 0.320, 0.668, 0.392, "whiteonblue"],
                               ["#ff8a00", "#FFFFFF", "#000000", 1.3, 0.320, 0.010, 0.695, "orangeonwhite"],
                               ["#FFFFFF", "#990000", "",        1.3, 0.320, 0.339, 0.695, "whiteonred"],
                               ["#990000", "#FFFFFF", "#000000", 1.4, 0.320, 0.668, 0.695, "redonwhite"]]

        else:

            # Vertical arrangement
            color_parameters = [["#FFFFFF", "#000000", "",        1.3, 0.440, 0.010, 0.092, "whiteonblack"],
                                ["#ff8a00", "#FFFFFF", "#000000", 1.3, 0.440, 0.257, 0.092, "orangeonwhite"],
                                ["#FFFFFF", "#006600", "",        1.3, 0.440, 0.504, 0.092, "whiteongreen"],
                                 bw_blue_vert,
                                ["#990000", "#FFFFFF", "#000000", 1.4, 0.440, 0.010, 0.542, "redonwhite"],
                                ["#FFFFFF", "#000099", "",        1.3, 0.440, 0.257, 0.542, "whiteonblue"],
                                ["#006600", "#FFFFFF", "#000000", 1.4, 0.440, 0.504, 0.542, "greenonwhite"],
                                ["#FFFFFF", "#990000", "",        1.3, 0.440, 0.752, 0.542, "whiteonred"]]

            # # Vertical arrangement for custom Palestine
            # color_parameters = [["#FFFFFF", "#000000", "",       1.3, 0.440, 0.010, 0.092, "whiteonblack"],
            #                     ["#000000", "#777e4d", "",        1.4, 0.440, 0.257, 0.092, "blackonarmygreen"],
            #                     ["#FFFFFF", "#4b5320", "",        1.3, 0.440, 0.504, 0.092, "whiteonarmygreen"],
            #                      bw_blue_vert,
            #                     ["#4b5320", "#FFFFFF", "#000000", 1.4, 0.440, 0.504, 0.542, "armygreenonwhite"],
            #                     ["#0c6b71", "#FFFFFF", "#000000", 1.4, 0.440, 0.257, 0.092, "tealonwhite"],
            #                     ["#FFFFFF", "#006600", "",        1.3, 0.440, 0.504, 0.092, "whiteongreen"],
            #                     ["#990000", "#FFFFFF", "#000000", 1.4, 0.440, 0.010, 0.542, "redonwhite"],
            #                     ["#FFFFFF", "#000099", "",        1.3, 0.440, 0.257, 0.542, "whiteonblue"],
            #                     ["#006600", "#FFFFFF", "#000000", 1.4, 0.440, 0.504, 0.542, "greenonwhite"],
            #                     ["#FFFFFF", "#990000", "",        1.3, 0.440, 0.752, 0.542, "whiteonred"]]

        for black_color, white_color, text_color, contrast, size, xdim, ydim, name in color_parameters:

            # Recolor images and save to style directory
            colorised = custom_color(highres_input=image_highres,
                                     black_color=black_color,
                                     white_color=white_color,
                                     text_color=text_color,
                                     contrast=contrast,
                                     title_nudge=title_nudge,
                                     name=name,
                                     styles_path=dir_name + "/" + file_name + "/" + file_name + "_styles/")

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

            'waterways': "Map created with QGIS using Openstreetmap water line and polygon features. Source data "
                    "copyright OpenStreetMap contributors available under CC BY-SA "
                    "(http://www.openstreetmap.org/copyright)",

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

            'waterwayseu': "Map created with QGIS using spatial vector GIS data from 1:250000 scale European "
                           "Environment Agency Catchments and Rivers Network System datasets. Rivers are weighted "
                           "from first order streams (i.e. tiny tributaries or headwaters at the very beginning of a "
                           "river system) to major rivers into which thousands of smaller streams flow (e.g. the "
                           "Danube and Volga Rivers). Source dataset: European Environment Agency (EEA). 2012. EEA "
                           "Catchments and Rivers Network System (ECRINS) v1.1. Available from "
                           "http://www.eea.europa.eu/data-and-maps/data/european-catchments-and-riversnetwork",

            'waterwaysca': "Map created with QGIS using GIS data for streams and waterbodies from Government of "
                           "Canada, Natural Resources Canada, Earth Sciences Sector. 2016. Lakes and rivers in "
                           "Canada CanVec Hydro Features. Ottawa, ON: Department of Natural Resources Canada. "
                           "Data freely available (http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/93b9a6e6-1264"
                           "-47f6-ad55-c60f842c550d.html) and licensed under the Open Government Licence - Canada: "
                           "http://open.canada.ca/en/open-government-licence-canada",

            'waterwaysie': "Map created with QGIS using GIS data for streams and waterbodies from INSPIRE Directive "
                           "Environmental Protection Agency and Northern Ireland Environment Agency data. Data is "
                           "for public use under Creative Commons CC-By 4.0",

            'waterwaysnz': "Map created with QGIS using GIS data for rivers and streams from the New Zealand Topo50, "
                           "Topo250 and Topo500 map series. The Topo50, Topo250 and Topo500 map series provides "
                           "topographic mapping for the New Zealand mainland and Chatham Islands, from 1:50,000 to "
                           "1:500,000 scale. Further information: www.linz.govt.nz/topography/topo-maps/topo250. "
                           "Datasets available under a Creative Commons Attribution 3.0 New Zealand license. Full "
                           "terms at https://creativecommons.org/licenses/by/3.0/nz/.",

            'waterwaysnl': "Map created with QGIS using GIS data for rivers, streams, lakes and canals from the"
                           "TOP50NL 1:50000 scale mapping product. Freely available online under the CC-BY-4.0 "
                           "license (https://www.pdok.nl/nl/producten/pdok-downloads/basisregistratie-topografie/topnl/"
                           "topnl-actueel/top50nl) ",

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
    if pdf:

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

image_manipulation(file_string='USA/ohio_waterwaysus_highres.png',
                   map_name='Waterways of Ohio',
                   words_name=1,
                   inset_zoom=0.12,
                   watermark=False,

                   # Title
                   name=False,
                   title_size=1.4,  # 1.4 for states
                   title_nudge=800,  # 800 for states
                   # coordinates="31.9038° N, 35.2034° E",
                   # name_text='YOUR CITY',

                   # Styles
                   nine_styles=True,
                   nine_styles_scale=1.2,  # 0.1, 1.2
                   blue=True,

                   # Generate PDF?
                   pdf=True)

# Generate tags and title
map_name = "Shadowlands California"
file_string="Asia/ramallah_city_highres.png"
etsy_title(map_name, 1, False)
# etsy_tags(map_name, 1, False)

# Uses insert_frame to create cover images
etsy_frame(highres_input=file_string,
           ouput_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1] + "_cover.jpg",
           map_name=map_name,
           nine_styles=False)

# Re-generate PDF
generate_pdf(map_name)




# Produce custom color versions
custom_color(highres_input=file_string,
             black_color="#9fa2a2",
             white_color="#FFFFFF",
             text_color="#000000",
             contrast=1.3,
             title_nudge=0,
             name="greyonwhite",
             styles_path=file_string[:-12] + "/" + file_string[:-12].split("/")[1] + "_styles/")



# Physical maps mockups
for file_string in glob.glob("Canada/*_highres.png"):

    print(file_string)

    try:

        physical_maps(file_string=file_string,
                      map_name="",
                      words_name=1,
                      templates=False)
    except:
        print("   Failed")




# Wedding maps
wedding_map(file_string="Custom/AlexandraJoshua/alexandrajoshua_wedding_highres.png",
            couple_name="ALEXANDRA + JOSHUA",
            couple_size=1.2,
            couple_nudge=1000,
            couple_font="Scripts/Fonts/ADAM_kerning.ttf",
            date_name="10.06.2017",
            date_size=0.6,
            date_nudge=40,
            date_font="Scripts/Fonts/Autumn in November.ttf",
            white_manual=2500)

wedding_map(file_string="Custom/test_buildings_highres3.png",
            couple_name=" Adam & Eve",
            couple_size=1.9,
            couple_nudge=1450,
            couple_font="Scripts/Fonts/trendsetter-Regular.ttf",
            date_name="15 July 2017",
            date_size=0.55,
            date_nudge=-150,
            date_font="Scripts/Fonts/ADAM_kerning.ttf",
            white_manual=2500)

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
