#!/usr/bin/env python
import sys
from getopt import getopt
from PIL import Image
import os


class Rectangle:

    def __init__(self, x, y, width, height, image=None):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.image = image
        self.fills = []
        self.splits = []

    def __str__(self):
        return "<Rectangle({}, {}, {}, {})>".format(
            self.x, self.y, self.width, self.height)

    def fill_and_split_vertical(self, rect):
        """
        fill a corner of this rectangle with another rectangle
        returns a couple of rectangles created splitting the
        free area vertically
        """

        if rect.x + rect.width > self.width:
            raise ValueError("Out of boundaries of the rectangle")
        if rect.y + rect.height > self.height:
            raise ValueError("Out of boundaries of the rectangle")

        if rect.x == 0:
            rect_r = Rectangle(
                rect.width, 0,
                self.width - rect.width, self.height)
            if rect.y == 0:  # place (top left)
                rect_l = Rectangle(
                    0, rect.height,
                    rect.width, self.height - rect.height)
            else:  # place (bottom left)
                rect_l = Rectangle(
                    0, 0,
                    rect.width, self.height - rect.height)
        else:
            rect_l = Rectangle(
                0, 0,
                self.width - rect.width, self.height)
            if rect.y == 0:  # place (top right)
                rect_r = Rectangle(
                    rect.x, rect.height,
                    rect.width, self.height - rect.height)
            else:  # place (bottom right)
                rect_r = Rectangle(
                    rect.x, 0,
                    rect.width, self.height - rect.height)

        self.fills.append(rect)
        self.splits.append(rect_l)
        self.splits.append(rect_r)
        return rect_l, rect_r

    def fill_and_split_horizontal(self, rect):
        """
        fill a corner of this rectangle with another rectangle
        returns a couple of rectangles created splitting the
        free area horizontally
        """

        if rect.x + rect.width > self.width:
            raise ValueError("Out of boundaries of the rectangle")
        if rect.y + rect.height > self.height:
            raise ValueError("Out of boundaries of the rectangle")

        if rect.y == 0:
            rect_b = Rectangle(
                0, rect.height,
                self.width, self.height - rect.height)
            if rect.x == 0:  # place (top left)
                rect_t = Rectangle(
                    rect.width, 0,
                    self.width - rect.width, rect.height)
            else:  # place (bottom left)
                rect_t = Rectangle(
                    0, 0,
                    self.width - rect.width, rect.height)
        else:
            rect_t = Rectangle(
                0, 0,
                self.width, self.height - rect.height)
            if rect.x == 0:  # place (top right)
                rect_b = Rectangle(
                    rect.width, rect.y,
                    self.width - rect.width, rect.height)
            else:  # place (bottom right)
                rect_b = Rectangle(
                    0, rect.y,
                    self.width - rect.width, rect.height)

        self.fills.append(rect)
        self.splits.append(rect_t)
        self.splits.append(rect_b)
        return rect_t, rect_b


def guillotine_baf_las(box, rects=[]):
    """ guillotine algorithm for packing rectangles
        choosing rectangles by best area fit (BAF)
        splitting containers by longer axis (LAS)
    """

    sorted_rects = sorted(rects, lambda a, b: a.x * a.y > b.x * b.y)

    best_fits = [r for r in sorted_rects
                 if r.width <= box.width
                 and r.height <= box.height]

    try:
        best = best_fits.pop()
    except IndexError:
        return

    rects.remove(best)

    if best.width > best.height:
        first, second = box.fill_and_split_horizontal(best)
    else:
        first, second = box.fill_and_split_vertical(best)

    if first.width * first.height > second.width * second.height:
        guillotine_baf_las(first, rects)
        guillotine_baf_las(second, rects)
    else:
        guillotine_baf_las(second, rects)
        guillotine_baf_las(first, rects)


def depth_composite(root, box, x, y, depth=0):
    for f in box.fills:
        root.image.paste(f.image, (x + box.x + f.x, y + box.y + f.y))
    for s in box.splits:
        depth_composite(root, s, x + box.x, y + box.y, depth + 1)


if __name__ == '__main__':
    opts, args = getopt(
        sys.argv[1:],
        "w:h:",
        [
            "width=",
            "height=",
        ])

    if not len(args):
        sys.exit(0)

    width = 800
    height = 100

    for opt, arg in opts:
        if opt in ('--width', '-w'):
            width = int(arg)
        elif opt in ('--height', '-h'):
            height = int(arg)
        elif opt in ('--lines', '-l'):
            lines = int(arg)
        elif opt in ('--columns', '-c'):
            columns = int(arg)

    container = Rectangle(
        0, 0,
        width,
        height,
        Image.new("RGB", (width, height), "white"))
    images = []
    for item in os.listdir(args[0]):
        img = Image.open(args[0] + os.path.sep + item)
        images.append(
            Rectangle(
                0, 0,
                img.size[0],
                img.size[1],
                img))

    guillotine_baf_las(container, images)

    depth_composite(container, container, 0, 0)
    result = open("result.png", "w")
    container.image.save(result)
