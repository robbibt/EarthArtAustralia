__author__ = 'z3287630'

# Import modules
from PIL import Image, ImageEnhance, ImageCms, ImageOps
import random, os
import warnings; warnings.simplefilter('ignore', Image.DecompressionBombWarning)


# Setup and import ----------------------------------------------------------------------------------------------------

file_string = 'D:/Dropbox/EarthArtAustralia/Test/colorado_roads_highres.png'
all_styles = True
inset_zoom = 0.2
all_styles_zoom = 1

# Set up directory if does not exist
if not os.path.exists(file_string[:-12]):
    os.makedirs(file_string[:-12])

# Read image
image_highres = Image.open(file_string)
width, height = image_highres.size


# Optional: desaturate and invert -----------------------------------------------------------------------------------------------

if all_styles:

    # Remove color and increase contrast
    image_black = ImageEnhance.Color(image_highres).enhance(0)
    image_black = ImageEnhance.Contrast(image_black).enhance(1.5)
    image_black.save(file_string[:-12] + "_black_highres.png")

    # Convert to RGB if RGBA to allow invert
    if image_black.mode == 'RGBA':

        r,g,b,a = image_black.split()
        rgb_image = Image.merge('RGB', (r,g,b))
        inverted_image = ImageOps.invert(rgb_image)
        r2,g2,b2 = inverted_image.split()
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
    all_styles_frame.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_frame_all.jpg")


# Low res -------------------------------------------------------------------------------------------------------------

image_lowres = image_highres.copy()
maxsize = (3000, 2500)
image_lowres.thumbnail(maxsize, Image.ANTIALIAS)
image_lowres.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_lowres.jpg")


# Frame ---------------------------------------------------------------------------------------------------------------

# Horizontal frames
if (width > height):

    image_frame = image_highres.copy()
    maxsize = (1200, 666)
    image_frame.thumbnail(maxsize, Image.ANTIALIAS)

    # Improve contrast
    contrast = ImageEnhance.Contrast(image_frame)
    image_frame = contrast.enhance(1.2)
    color = ImageEnhance.Color(image_frame)
    image_frame = color.enhance(1.2)

    # Open frame and paste in image
    etsy_frame = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_hor_" + str(random.randint(1,5)) + ".png")
    etsy_frame_overlay = etsy_frame.convert("RGBA")

    etsy_frame.paste(image_frame, (128, 128))
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_frame.jpg")

    # Add "new" banner
    etsy_new = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_new.png")
    etsy_frame.paste(etsy_new, (0, 0), etsy_new)
    etsy_frame.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_frame_new.jpg")

# Square frames
elif (width == height):

    image_frame = image_highres.copy()
    maxsize = (777, 777)
    image_frame.thumbnail(maxsize, Image.ANTIALIAS)

    # Improve contrast
    contrast = ImageEnhance.Contrast(image_frame)
    image_frame = contrast.enhance(1.2)
    color = ImageEnhance.Color(image_frame)
    image_frame = color.enhance(1.2)

    # Open frame and paste in image
    etsy_frame = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_sq_" + str(random.randint(1,5)) + ".png")
    etsy_frame_overlay = etsy_frame.copy()

    etsy_frame.paste(image_frame, (215, 75), image_frame)
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_frame.jpg")

    # Add "new" banner
    etsy_new = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_new.png")
    etsy_frame.paste(etsy_new, (0, 0), etsy_new)
    etsy_frame.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_frame_new.jpg")

# Vertical frames
elif (width < height):

    image_frame = image_highres.copy()
    maxsize = (666, 1200)
    image_frame.thumbnail(maxsize, Image.ANTIALIAS)

    # Improve contrast
    contrast = ImageEnhance.Contrast(image_frame)
    image_frame = contrast.enhance(1.2)
    color = ImageEnhance.Color(image_frame)
    image_frame = color.enhance(1.2)

    # Open frame and paste in image
    etsy_frame = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_vert_" + str(random.randint(1,5)) + ".png")
    etsy_frame_overlay = etsy_frame.copy()

    etsy_frame.paste(image_frame, (275, 150), image_frame)
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_frame.jpg")


# Subsets -------------------------------------------------------------------------------------------------------------

# Save middle inset
image_zoom = image_highres.crop((int(width * 0.5 - width * 0.05),
                                 int(height * 0.485 - height * 0.05),
                                 int(width * 0.5 + width * 0.05),
                                 int(height * 0.485 + height * 0.05)))
image_zoom.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_zoom_1.jpg")

# Save random insets
for zoom in range(2, 11):
    x = random.randint(int(width * 0.2), int(width * 0.8))
    y = random.randint(int(height * 0.2), int(height * 0.8))
    image_zoom = image_highres.crop((x - int(width * (inset_zoom * 0.5)),
                                     y - int(height * (inset_zoom * 0.5)),
                                     x + int(width * (inset_zoom * 0.5)),
                                     y + int(height * (inset_zoom * 0.5))))
    image_zoom.save(file_string[:-12] + "/" + os.path.basename(file_string[:-12]) + "_zoom_" + str(zoom) + ".jpg")


# Close files ---------------------------------------------------------------------------------------------------------

image_highres.close()
image_black.close()
image_white.close()
image_plasma.close()


# # CMYK conversion ---------------------------------------------------------------------------------------------------
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
# c = ImageEnhance.Contrast(c).enhance(0.9)
# m = ImageEnhance.Contrast(m).enhance(4)
# y = ImageEnhance.Contrast(y).enhance(3)
#
# image_cmyk_enhanced = Image.merge(image_cmyk.mode, (c,m,y,k))
# image_cmyk_enhanced.save(file_string[:-12] + "_cmyk_test.tif",  compression="tiff_deflate")






