import re
from decimal import Decimal

from .constants import BOOLEAN_TRANSLATIONS


class ProcessorUtils:
    @staticmethod
    def strip_join(text_list: list[str], join_element: str = " ") -> str:
        return join_element.join(
            text.strip() for text in text_list if text and text != " "
        )

    @staticmethod
    def extract_area(text: str) -> Decimal:
        area_match = re.search(r"(\d+(?:\s*\d+)?,?\d*\.?\d*) m²", text)
        if area_match:
            area_str = area_match.group(1).replace(" ", "").replace(",", ".")
            return Decimal(area_str)
        else:
            return None

    @staticmethod
    def cast_to_bool(text: str) -> bool:
        if text.lower() in BOOLEAN_TRANSLATIONS.keys():
            return BOOLEAN_TRANSLATIONS[text.lower()]

    @staticmethod
    def cast_to_bool(text: str) -> bool:
        if text.lower() in BOOLEAN_TRANSLATIONS.keys():
            return BOOLEAN_TRANSLATIONS[text.lower()]

    @staticmethod
    def extract_price(text: str) -> Decimal:
        text = re.sub(r"\xa0", " ", text)
        price_match = re.search(r"(\d+(?:\s*\d+)?,?\d*\.?\d*) €", text)
        if price_match:
            price_str = price_match.group(1).replace(" ", "").replace(",", ".")
            return Decimal(price_str)
        else:
            return None
