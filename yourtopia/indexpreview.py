# encoding: utf-8

from PIL import Image
from PIL import ImageDraw
import math
import os


def create_preview_image(values, width=270, height=100):
    """
    Creates an index preview image based on
    the values passed and returns a PIL image object.
    """
    sfactor = 4  # for antialiasing
    padding_top = 21  # distance from top edge to line
    padding_bottom = 4  # distance  from bottom edge to line
    padding_x = 5  # distance to the side edges
    radius_min = 0  # minimal circle radius
    swidth = width * sfactor
    sheight = height * sfactor
    circle_linewidth = 1
    stem_linewidth = 1
    stem_color = '#444444'
    sheight_range = (sheight - (padding_top * sfactor) -
        (padding_bottom * sfactor))
    num_values = len(values)
    slot_width = (swidth - (2 * (padding_x * sfactor))) / num_values
    img = Image.new("RGB", (swidth, sheight), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    y_bottom = sheight - (padding_bottom * sfactor)
    slotcount = 0
    for value in values:
        x = (slot_width / 2) + (slotcount * slot_width) + (padding_x * sfactor)
        y_top = padding_top * sfactor + ((1 - value) * sheight_range)
        r = radius(value, radius_min) * sfactor
        draw.line((x, y_top, x, y_bottom), fill=stem_color, width=(stem_linewidth * sfactor))
        # rear larger ellipse (black)
        draw.ellipse((x - r - (circle_linewidth * sfactor), y_top - r - (circle_linewidth * sfactor),
            x + r + (circle_linewidth * sfactor), y_top + r + (circle_linewidth * sfactor)),
            fill=(0, 0, 0), outline=(0, 0, 0))
        #front ellipse (white)
        draw.ellipse((x - r, y_top - r, x + r, y_top + r),
            fill=(255, 255, 255), outline=(255, 255, 255))
        slotcount += 1
    return img


def radius(v, minr):
    factor = 350.0
    return float(minr) + math.sqrt(factor * v)


def get_folder_path(id, root='.'):
    """
    Returns the appropriate relative folder path
    for images with the given id
    """
    idstring = "%03d" % id
    # three levels of sub folders taken from the last three digits
    return os.sep.join([root, idstring[-1], idstring[-2], idstring[-3], str(id)])


def save_image_versions(img, id, root_path):
    """
    Saves the image in all required sizes
    in the appropriate path. Creates subfolders
    as necessary
    """
    folder = get_folder_path(id, root_path)
    if not os.access(folder, os.F_OK):
        os.makedirs(folder)
    # preview image for browse page
    browse_img = img.resize((270, 100), Image.ANTIALIAS)
    browse_img = browse_img.convert("L")
    browse_img.save(folder + os.sep + 'pv.png', 'PNG')
    # opengraph / facebook image
    og_img = img.resize((130, 48), Image.ANTIALIAS)
    og_img = og_img.convert("L")
    og_img.save(folder + os.sep + 'og.png', 'PNG')


if __name__ == '__main__':
    THUMBS_PATH = 'test/thumbs'
    values = [0.2, 0.8, 0.1, 0.75, 0.23, 0.99, 0.0, 1.0]
    img = create_preview_image(values)
    save_image_versions(img, 123, THUMBS_PATH)
