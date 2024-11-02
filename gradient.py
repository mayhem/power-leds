from math import fabs, fmod
import traceback

class Gradient(object):
    def __init__(self, palette, leds=1):

        # palletes are in format [ (.345, (128, 0, 128)) ]
        self._validate_palette(palette)
        self.palette = palette
        self.leds = leds
        self.led_scale = 1.0
        self.led_offset = 0.0

    def _validate_palette(self, palette):
        if len(palette) < 2:
            self.print_palette(palette)
            raise ValueError("Palette must have at least two points.")

        if palette[0][0] > 0.0:
            self.print_palette(palette)
            raise ValueError("First point in palette must be less than or equal to 0.0")

        if palette[-1][0] < 1.0:
            self.print_palette(palette)
            raise ValueError("Last point in palette must be greater than or equal to 1.0")

    def set_scale(self, scale):
        self.led_scale = scale

    def set_offset(self, offset):
        self.led_offset = offset

    def print_palette(self, palette=None):
        print("Gradient palette:")
        for pal in palette or self.palette:
            print("%.3f: %d, %d, %d" % (pal[0], pal[1][0], pal[1][1], pal[1][2]))
        print()

    def get_color(self, offset):

        if offset < 0.0 or offset > 1.0:
            raise IndexError("Invalid offset %f" % offset)

        for index in range(len(self.palette)):

            # skip the first item
            if index == 0:
                continue

            if self.palette[index][0] >= offset:
                section_begin_offset = self.palette[index - 1][0]
                section_end_offset = self.palette[index][0]

                percent = (offset - section_begin_offset) / (section_end_offset - section_begin_offset)
                new_color = []
                for color in range(3):
                    new_color.append(
                        int(self.palette[index - 1][1][color] +
                            ((self.palette[index][1][color] - self.palette[index - 1][1][color]) * percent)))

                return (max(min(new_color[0], 255), 0), max(min(new_color[1], 255), 0), max(min(new_color[2], 255), 0))

        self.print_palette()
        assert False
