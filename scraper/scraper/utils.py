import re
from decimal import Decimal
import dateparser
from bs4 import BeautifulSoup
from .constants import (
    BOOLEAN_TRANSLATIONS,
    BUILDING_TYPE_TRANSLATIONS,
    HOUSING_TYPE_TRANSLATIONS,
    PROPERTY_OWNERSHIP_TRANSLATIONS,
)


class ProcessorUtils:
    @staticmethod
    def strip_join(text_list: list[str], join_element: str = " ") -> str:
        return join_element.join(
            text.strip() for text in text_list if text and text != " "
        )

    @staticmethod
    def parse_date(date_string: str):
        return int(dateparser.parse(date_string).timestamp())

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
    def extract_price(text: str) -> Decimal:
        text = re.sub(r"\xa0", " ", text)
        price_match = re.search(r"(\d+(?:\s*\d+)?,?\d*\.?\d*) €", text)
        if price_match:
            price_str = price_match.group(1).replace(" ", "").replace(",", ".")
            return Decimal(price_str)
        else:
            return None

    @staticmethod
    def extract_floor_number(text: str) -> int | None:
        try:
            return int(text.split("/")[0])
        except ValueError:
            return None

    @staticmethod
    def translate_property_ownership(text: str) -> str:
        return PROPERTY_OWNERSHIP_TRANSLATIONS.get(text.lower(), text)

    @staticmethod
    def translate_housing_type(text: str) -> str:
        return HOUSING_TYPE_TRANSLATIONS.get(text.lower(), text)

    @staticmethod
    def translate_building_type(text: str) -> str:
        return BUILDING_TYPE_TRANSLATIONS.get(text.lower(), text)

    @staticmethod
    def clean_html_space(html: str) -> str:
        cleaned_html = html.strip()

        return cleaned_html

    @staticmethod
    def remove_html_attributes(html: str) -> str:
        soup = BeautifulSoup(html, features="html.parser")

        for tag in soup.find_all(True):
            if tag.name == "a" and tag.has_attr("href"):
                href = tag["href"]
                tag.attrs = {"href": href}
            else:
                tag.attrs = {}

        return str(soup)

    @staticmethod
    def remove_empty_tags(html: str) -> str:
        soup = BeautifulSoup(html, features="html.parser")
        for tag in soup.find_all(True):  # True finds all tags
            if not tag.get_text(strip=True) and tag.name not in ["html", "body"]:
                tag.decompose()

        return str(soup)

    @staticmethod
    def get_text_from_html(html: str) -> str:
        soup = BeautifulSoup(html, features="html.parser")
        return soup.get_text(strip=True)
