from unittest import TestCase

import os

from punishment import extract_punishments
from settings import BASE_DIR

RESOURCES_DIR = os.path.join(BASE_DIR, 'tests/resources/punishment')


class PunishmentTest(TestCase):

    def test_defamation(self):
        self.assertEqual(
            [
                'imprisonment not exceeding one year or a fine',
                'imprisonment not exceeding two years or a fine'
            ],
            extract_punishments(open(os.path.join(RESOURCES_DIR, 'defamation.txt')).read())
        )

    def test_perjury(self):
        self.assertEqual(
            [
                'imprisonment of not less than one year',
                'imprisonment from six months to five years'
            ],
            extract_punishments(open(os.path.join(RESOURCES_DIR, 'perjury.txt')).read())
        )

    def test_manslaughter(self):
        self.assertEqual(
            [
                'imprisonment not exceeding five years or a fine'
            ],
            extract_punishments(open(os.path.join(RESOURCES_DIR, 'manslaughter.txt')).read())
        )

