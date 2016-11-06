__author__ = 'z3287630'

# Import modules
from PIL import Image, ImageEnhance
import random

# File string
file_string = 'D:/Dropbox/EarthArtAustralia/Canada/City/calgary_white_highres.png'


# Low res ------------------------------------------------------------------------------------

# Read image
image_highres = Image.open(file_string)
width, height = image_highres.size

image_lowres = image_highres.copy()
maxsize = (2500, 3000)
image_lowres.thumbnail(maxsize, Image.ANTIALIAS)
image_lowres.save(file_string[:-12] + "_lowres.jpg")



# Frame --------------------------------------------------------------------------------------

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
    etsy_frame_overlay = etsy_frame.copy()

    etsy_frame.paste(image_frame, (158, 128), image_frame)
    etsy_frame.paste(etsy_frame_overlay, (0, 0), etsy_frame_overlay)
    etsy_frame.save(file_string[:-12] + "_frame.jpg")

    # Add "new" banner
    etsy_new = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_new.png")
    etsy_frame.paste(etsy_new, (0, 0), etsy_new)
    etsy_frame.save(file_string[:-12] + "_frame_new.jpg")

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
    etsy_frame.save(file_string[:-12] + "_frame.jpg")

    # Add "new" banner
    etsy_new = Image.open("D:/Dropbox/EarthArtAustralia/Scripts/Elements/frame_new.png")
    etsy_frame.paste(etsy_new, (0, 0), etsy_new)
    etsy_frame.save(file_string[:-12] + "_frame_new.jpg")

# Vertical frames
elif (width < height):

    image_frame = image_highres.copy()
    maxsize = (650, 1200)
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
    etsy_frame.save(file_string[:-12] + "_frame.jpg")


# Subsets ------------------------------------------------------------------------------------

# Save middle inset
image_zoom = image_highres.crop((int(width * 0.5 - width * 0.05),
                                 int(height * 0.485 - height * 0.05),
                                 int(width * 0.5 + width * 0.05),
                                 int(height * 0.485 + height * 0.05)))
image_zoom.save(file_string[:-12] + "_zoom_1.jpg")

# Save random insets
for zoom in range(2, 11):
    x = random.randint(int(width * 0.2), int(width * 0.8))
    y = random.randint(int(height * 0.2), int(height * 0.8))
    image_zoom = image_highres.crop((x - int(width * 0.05),
                                     y - int(height * 0.05),
                                     x + int(width * 0.05),
                                     y + int(height * 0.05)))
    image_zoom.save(file_string[:-12] + "_zoom_" + str(zoom) + ".jpg")
