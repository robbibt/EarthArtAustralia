__author__ = 'z3287630'

# Import modules
import os
import random
from xlutils.copy import copy
from xlrd import open_workbook
from PIL import Image, ImageEnhance, ImageCms, ImageOps
import warnings
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

# Working directory
os.chdir("D:/Dropbox/EarthArtAustralia/")


# Setup and import ----------------------------------------------------------------------------------------------------

file_string = 'Australia/australia_shadow_highres.png'
map_name = 'Shadow lands Australia'
all_styles = False
inset_zoom = 0.3
all_styles_zoom = 1.1
subsets = 25

# Set up directory if does not exist
if not os.path.exists(file_string[:-12]):
    os.makedirs(file_string[:-12])

# Identify file name
file_name = os.path.basename(file_string[:-12])

# Read image
image_highres = Image.open(file_string)
width, height = image_highres.size


# Low res -------------------------------------------------------------------------------------------------------------

image_lowres = image_highres.copy()
maxsize = (3000, 2500)
image_lowres.thumbnail(maxsize, Image.ANTIALIAS)
image_lowres.save(file_string[:-12] + "/" + file_name + "_lowres.jpg")


# Optional: desaturate and invert -------------------------------------------------------------------------------------

# Only run if all frames requested and either black or all style frame doesn't exist
desat_exists = os.path.isfile(file_string[:-12] + "_black_highres.png")
styles_frame_exists = os.path.isfile(file_string[:-12] + "/" + file_name + "_frame_all.jpg")

if all_styles and (not desat_exists or not styles_frame_exists):

    # Remove color and increase contrast
    image_black = ImageEnhance.Color(image_highres).enhance(0)
    image_black = ImageEnhance.Contrast(image_black).enhance(1.5)
    image_black.save(file_string[:-12] + "_black_highres.png")

    # Convert to RGB if RGBA to allow invert
    if image_black.mode == 'RGBA':

        r, g, b, a = image_black.split()
        rgb_image = Image.merge('RGB', (r,g,b))
        inverted_image = ImageOps.invert(rgb_image)
        r2, g2, b2 = inverted_image.split()
        image_white = Image.merge('RGBA', (r2, g2, b2, a))
        image_white.save(file_string[:-12] + "_white_highres.png")

    # If already RGB
    else:
        image_white = ImageOps.invert(image_black)
        image_white.save(file_string[:-12] + "_white_highres.png")

    # Resize into thumbnails
    maxsize = (1200 * all_styles_zoom, 720 * all_styles_zoom)
    image_plasma = image_highres.copy()
    image_plasma.thumbnail(maxsize, Image.ANTIALIAS)
    image_black.thumbnail(maxsize, Image.ANTIALIAS)
    image_white.thumbnail(maxsize, Image.ANTIALIAS)

    # Set to alpha in-place
    image_white = image_white.convert("RGBA")
    pixdata = image_white.load()

    for y in xrange(image_white.size[1]):
        for x in xrange(image_white.size[0]):
            if pixdata[x, y] == (255, 255, 255, 255):
                pixdata[x, y] = (255, 255, 255, 0)

    # Paste into all style frame
    height_adj = int((720 - 720 * all_styles_zoom) * 0.7)
    all_styles_frame = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_all_styles.png")
    all_styles_frame.paste(image_white, (30, 100 + height_adj), image_white)
    all_styles_frame.paste(image_plasma, (980, 255 + height_adj), image_white)
    all_styles_frame.paste(image_black, (710, 820 + height_adj), image_white)
    all_styles_frame.save(file_string[:-12] + "/" + file_name + "_frame_all.jpg")

    # Close files
    image_black.close()
    image_white.close()
    image_plasma.close()


# Frame ---------------------------------------------------------------------------------------------------------------

# Horizontal frames
frame_exists = os.path.isfile(file_string[:-12] + "/" + file_name + "_frame.jpg")

if width > height and not frame_exists:

    image_frame = image_highres.copy()
    maxsize = (1200, 666)
    image_frame.thumbnail(maxsize, Image.ANTIALIAS)

    # Improve contrast
    image_frame = ImageEnhance.Contrast(image_frame).enhance(1.2)
    image_frame = ImageEnhance.Color(image_frame).enhance(1.05)

    # Open frame and paste in image
    etsy_frame = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_hor_" + str(random.randint(1,5)) + ".png")
    etsy_frame_overlay = etsy_frame.convert("RGBA")

    etsy_frame.paste(image_frame, (128, 128))
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(file_string[:-12] + "/" + file_name + "_frame.jpg")

    # Add "new" banner
    etsy_new = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_new.png")
    etsy_frame.paste(etsy_new, (0, 0), etsy_new)
    etsy_frame.save(file_string[:-12] + "/" + file_name + "_frame_new.jpg")

# Square frames
elif width == height and not frame_exists:

    image_frame = image_highres.copy()
    maxsize = (777, 777)
    image_frame.thumbnail(maxsize, Image.ANTIALIAS)

    # Improve contrast
    image_frame = ImageEnhance.Contrast(image_frame).enhance(1.2)
    image_frame = ImageEnhance.Color(image_frame).enhance(1.05)

    # Open frame and paste in image
    etsy_frame = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_sq_" + str(random.randint(1,5)) + ".png")
    etsy_frame_overlay = etsy_frame.copy()

    etsy_frame.paste(image_frame, (215, 75))
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(file_string[:-12] + "/" + file_name + "_frame.jpg")

    # Add "new" banner
    etsy_new = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_new.png")
    etsy_frame.paste(etsy_new, (0, 0), etsy_new)
    etsy_frame.save(file_string[:-12] + "/" + file_name + "_frame_new.jpg")

# Vertical frames
elif width < height and not frame_exists:

    image_frame = image_highres.copy()
    maxsize = (666, 1200)
    image_frame.thumbnail(maxsize, Image.ANTIALIAS)

    # Improve contrast
    image_frame = ImageEnhance.Contrast(image_frame).enhance(1.2)
    image_frame = ImageEnhance.Color(image_frame).enhance(1.05)

    # Open frame and paste in image
    etsy_frame = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_vert_" + str(random.randint(1,5)) + ".png")
    etsy_frame_overlay = etsy_frame.copy()

    etsy_frame.paste(image_frame, (265, 135))
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(file_string[:-12] + "/" + file_name + "_frame.jpg")


# Subsets -------------------------------------------------------------------------------------------------------------

# Save middle inset
image_zoom = image_highres.crop((int(width * 0.5 - width * (inset_zoom * 0.5)),
                                 int(height * 0.485 - height * (inset_zoom * 0.5)),
                                 int(width * 0.5 + width * (inset_zoom * 0.5)),
                                 int(height * 0.485 + height * (inset_zoom * 0.5))))
image_zoom.save(file_string[:-12] + "/" + file_name + "_zoom_1.jpg")

# Save random insets
for zoom in range(2, subsets + 1):
    x = random.randint(int(width * 0.2), int(width * 0.75))
    y = random.randint(int(height * 0.2), int(height * 0.75))
    image_zoom = image_highres.crop((x - int(width * (inset_zoom * 0.5)),
                                     y - int(height * (inset_zoom * 0.5)),
                                     x + int(width * (inset_zoom * 0.5)),
                                     y + int(height * (inset_zoom * 0.5))))
    image_zoom.save(file_string[:-12] + "/" + file_name + "_zoom_" + str(zoom) + ".jpg")
    image_zoom.close()


# Update Excel file ---------------------------------------------------------------------------------------------------

# Load excel data
rb = open_workbook("Download links/DownloadandPrintingGuide_data.xls")
r = rb.sheet_by_index(0).nrows

# Calculate image file size
file_size = os.path.getsize(file_string) / 1024.0 / 1024.0

# If current map not in sheet and above 20mb, add to excel
if map_name not in rb.sheet_by_index(0).col_values(0) and file_size > 20:

    # Append data to last row
    wb = copy(rb)
    s = wb.get_sheet(0)
    s.write(r, 0, map_name)
    s.write(r, 1, map_name)
    s.write(r, 3, "/" + file_string)
    s.write(r, 5, str(width) + " x " + str(height))

    # Set column widths
    s.col(0).width = 7000
    s.col(1).width = 7000
    s.col(2).width = 18000
    s.col(3).width = 9700
    s.col(4).width = 6500
    s.col(5).width = 3800

    # Save to excel document
    wb.save('Download links/DownloadandPrintingGuide_data.xls')

else:

    print("No data added to excel")


# Close files ---------------------------------------------------------------------------------------------------------

image_highres.close()
image_lowres.close()


# CMYK conversion ---------------------------------------------------------------------------------------------------
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
