from unittest import TestCase

import os

from ocr import OCRError
from ocr.image_to_text import ImageToText
from settings import BASE_DIR

RESOURCES_DIR = os.path.join(BASE_DIR, 'tests/resources/ocr')


class OCRTest(TestCase):
    img2txt = None

    def setUp(self):
        self.img2txt = ImageToText()

    def test_image_to_test(self):

        self.assertEqual('Taking a false oath before a court.',
                         self.img2txt.get_text(os.path.join(RESOURCES_DIR, 'perjury.jpg')),
                         'Invalid OCR text returned')

        self.assertEqual('Causing negligent death of a person.',
                         self.img2txt.get_text(os.path.join(RESOURCES_DIR, 'manslaughter.jpg')),
                         'Invalid OCR text returned')

        self.assertEqual('Asserting and disseminating a fact about a person which has defamed or negatively affected '
                         'public opinion about the person.',
                         self.img2txt.get_text(os.path.join(RESOURCES_DIR, 'defamation.jpg')),
                         'Invalid OCR text returned')

    def test_image_to_test_with_error(self):
        try:
            self.img2txt.get_text(os.path.join(RESOURCES_DIR, 'defamation.small.jpg'))

            raise ValueError('No exception raised...')
        except OCRError:
            pass
