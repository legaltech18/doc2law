import logging
import re
import sys

import pyocr
import pyocr.builders
from PIL import Image

from ocr import OCRError
from settings import OCR_LANGUAGE, OCR_MIN_WIDTH, OCR_MIN_HEIGHT

# Prepare logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class ImageToText(object):
    """

    OCR based on pyocr / tesseract
    - only works for "our images"
    - requires DPI ~ 400

    Usage:

    img2text = ImageToText()
    recognized_text = img2text.get_text('path/to/image')

    """

    tool = None

    def get_tool(self):
        if self.tool is None:

            tools = pyocr.get_available_tools()

            if len(tools) == 0:
                raise OCRError("No OCR tool found")

            # The tools are returned in the recommended order of usage
            self.tool = tools[0]
            logger.debug("Will use tool '%s'" % (self.tool.get_name()))
            # Ex: Will use tool 'libtesseract'

            langs = self.tool.get_available_languages()

            if OCR_LANGUAGE not in langs:
                raise OCRError('%s is not available with your OCR' % OCR_LANGUAGE)
        return self.tool

    def get_text(self, image_fn: str) -> str:
        """
        Does the actual OCR

        :param image_fn: Path to image file
        :return: Recognized text as string
        """
        img = Image.open(image_fn)

        logger.debug('Reading image from: %s' % image_fn)

        # Validate image
        if img.size[0] < OCR_MIN_WIDTH:
            raise OCRError('Input image is too small; width=%i, min_width=%i' % (img.size[0], OCR_MIN_WIDTH))

        if img.size[1] < OCR_MIN_HEIGHT:
            raise OCRError('Input image is too small; height=%i, min_height=%i' % (img.size[1], OCR_MIN_HEIGHT))

        # Actual OCR
        txt = self.get_tool().image_to_string(img, lang=OCR_LANGUAGE, builder=pyocr.builders.TextBuilder())

        # Search for details in text
        match = re.search(r'DETAILS OF OFFENCE/ S(.*)', txt, re.MULTILINE + re.DOTALL)

        if match:
            # Use regex match as text
            txt = match.group(1)

            # Remove sections
            txt = re.sub(r'Section ([0-9]+)', '', txt)
            txt = re.sub(r'([0-9]+)', '', txt)

            # Remove line breaks and white spaces
            txt = txt.replace('\n', '').strip()

            logger.debug('Query from OCR: %s' % txt)
        else:
            logger.warning('No query match. Using all OCR text')

        return txt
