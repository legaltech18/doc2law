"""

Extract punishments (imprisonment, fine etc) from law text.

Example input text:

    imprisonment not exceeding five years or a fine

    be liable to imprisonment not exceeding one year or a fine and, if the offence was committed publicly or through the dissemination of written materials (section 11(3)), to imprisonment not exceeding two years or a fine.

    Whosoever through negligence causes the death of a person shall be liable to imprisonment not exceeding five years or a fine.

    shall be imprisonment from six months to five years.

    shall be liable to imprisonment of not less than one year

Solution regex: împrisonment(.*?)year(s)

"""
import re


def extract_punishments(law_text) -> list:
    """Extract punishments with a regex (very simple)"""

    matches = re.finditer(r'imprisonment(.*?)year((s)?)(( or a fine)?)', law_text)
    punishments = [m.group() for m in matches]

    return punishments
