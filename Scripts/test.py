# Test if custom name given
if not name_text:
    name_text = " ".join(str.split(map_name)[-words_name:]).upper()


image_highres = Image.open("Custom/test_buildings_highres.png")

image_highres = map_title(image_highres,
                          file_string="Custom/test_buildings_highres.png",
                          title_name="SYDNEY",
                          title_nudge=1070,
                          title_size=1.4,
                          title_font="Scripts/Fonts/ADAM_kerning.ttf",
                          coordinates="36.8485° S, 174.763° E",
                          white=True)

image_highres = map_title(image_highres,
                          file_string="Custom/test_buildings_highres.png",
                          title_name="21 July 2017",
                          title_nudge=75,
                          title_size=0.62,
                          title_font="Scripts/Fonts/Autumn in November.ttf",
                          # coordinates=", ",
                          white=False)

image_highres.close()

def map_title(image_highres, file_string, title_name, title_nudge, title_size, title_font, coordinates=False, white=True):

    # Define image size
    width, height = image_highres.size

    # Set up layer for drawing
    draw = ImageDraw.Draw(image_highres)

    # Add in white borders
    if white:
        draw.rectangle([0, (height - 1350 - title_nudge), width, height], fill="#FFFFFF")

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
        draw.text(((width - coords_width) / 2 + 10, (height - 965 - title_nudge)), coords_new, (0, 0, 0), font=coords_font)

    # Export to file
    image_highres.save(file_string, optimize=True)

    # Return image
    return image_highres