from typing import Any, Tuple
from PIL import Image, ImageFont, ImageDraw


class Meme:
    """Meme class."""
    def set_font_size(self, word: str) -> None:
        """Set the minimum font size needed to fit the word on the image.

        :param str word: The word of which to check.
        :note: Max font size is 120.
        """
        font_size = 1
        font = ImageFont.truetype(self.font_path, font_size)
        while True:
            font_length = font.getlength(word)
            img_fraction = 0.90 * self.image.size[0]
            if font_length < img_fraction:
                font_size += 1
                font = ImageFont.truetype(self.font_path, font_size)
                continue
            if font_size == 120:
                break
            break
        if font_size <= self.font_size:
            self.font_size = font_size

    def parse_wrapped_text(self, text: str) -> Tuple[str, Any]:
        """Parse all the text in the given string.

        :param str text: The text of which to parse.
        :returns: A Tuple of wrapped lines and Font for the image.
        """
        wrapped_lines = []
        buf = []
        buf_width = 0
        font_size = 120
        font = ImageFont.truetype(self.font_path, font_size)
        space_width = self.img.textlength(text=" ", font=font)
        text_lines = text.split("\n")
        for line in text_lines:
            for word in line.split(" "):
                self.set_font_size(word)
                word_width = int(self.img.textlength(text=word, font=font))
                total_text_width = word_width
                if buf:
                    total_text_width += buf_width + space_width
                if (
                    total_text_width <= self.max_length
                    and word_width + buf_width <= self.max_length
                ):
                    # word fits in line
                    buf_width = total_text_width
                    buf.append(word)
                else:
                    # word doesn't fit in line
                    wrapped_lines.append(" ".join(buf))
                    buf = [word]
                    buf_width = word_width

            if buf:
                wrapped_lines.append(" ".join(buf))
                buf = []
                buf_width = 0
        return "\n".join(wrapped_lines), ImageFont.truetype(self.font_path, self.font_size)

    def make_image(self, text: str) -> None:
        """Generate a meme based on cmd input.

        :param str text: The text of which to put on the meme.
        """
        text = self.cmd + " " + " ".join(text)
        wrapped_text, font = self.parse_wrapped_text(text)
        text_width = self.img.textlength(wrapped_text.replace("\n", ""))
        text_start = (350 - text_width) / 2
        ret = self.img.multiline_textbbox((text_start, 10), text, font, align="center")
        self.img.multiline_text((ret[1], 11 / 2), wrapped_text, font=font)
        try:
            self.image.save(f"images/{self.cmd}_edited.jpg")
            self.image.close()
        except (OSError, ValueError) as err:
            print(str(err))

    def __init__(self, cmd):
        self.image = Image.open(f"images/{cmd}.jpg")
        self.font_path = "junk/truetypes/impact.ttf"
        self.img = ImageDraw.Draw(self.image)
        self.font_size = 120
        self.max_length = int((self.image.size[0] - self.font_size) + (self.image.size[0] - self.font_size)*0.1)
        self.cmd = cmd
