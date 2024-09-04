# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from typing import Any

from itemloaders.processors import Identity, MapCompose, TakeFirst
from parsel import Selector
from scrapy import Field, Item
from scrapy.http import Response
from scrapy.loader import ItemLoader

from .utils import ProcessorUtils


class OikotieItem(Item):
    id = Field(input_processor=MapCompose(int))
    url = Field()

    # Image urls
    image_urls = Field(output_processor=Identity())

    # Basic information
    location = Field(input_processor=ProcessorUtils.strip_join)
    city = Field()
    house_number = Field()
    district = Field()
    item_number = Field()
    floor = Field()
    total_floors = Field(input_processor=MapCompose(int))
    life_sq = Field(input_processor=MapCompose(ProcessorUtils.extract_area))
    property_sq = Field()
    total_sq = Field()
    room_info = Field()
    number_of_rooms = Field(input_processor=MapCompose(int))
    condition = Field()
    condition_details = Field()
    availability = Field()
    kitchen_appliances = Field()
    bathroom_appliances = Field()
    window_direction = Field()
    has_balcony = Field(input_processor=MapCompose(ProcessorUtils.cast_to_bool))
    balcony_details = Field()
    storage_space = Field()
    view = Field()
    future_renovations = Field()
    completed_renovations = Field()
    has_sauna = Field()
    sauna_details = Field()
    housing_type = Field()
    services = Field()
    additional_info = Field()
    property_id = Field()
    apartment_is = Field()
    telecommunication_services = Field()
    # Price and cost information
    price_no_tax = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    sales_price = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    shared_loan_payment = Field()
    price_per_sq = Field()
    share_of_liabilities = Field()
    mortgages = Field()
    financial_charge = Field()
    condominium_payment = Field(
        input_processor=MapCompose(ProcessorUtils.extract_price)
    )
    maintenance_charge = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    water_charge = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    water_charge_details = Field()
    heating_charge = Field()
    heating_charge_details = Field()
    other_costs = Field()
    # House and property
    is_brand_new = Field()
    housing_company_name = Field()
    building_type = Field()
    build_year = Field(input_processor=MapCompose(int))
    build_year_details = Field()
    number_of_apartments = Field()
    building_has_elevator = Field(
        input_processor=MapCompose(ProcessorUtils.cast_to_bool)
    )
    building_has_sauna = Field(input_processor=MapCompose(ProcessorUtils.cast_to_bool))
    building_material = Field()
    roof_type = Field()
    energy_class = Field()
    has_energy_certificate = Field()
    antenna_system = Field()
    property_size = Field(input_processor=MapCompose(ProcessorUtils.extract_area))
    property_size_unit = Field()
    property_owner = Field()
    maintenance = Field()
    real_estate_management = Field()
    plan_info = Field()
    plan = Field()
    traffic_communication = Field()
    heating = Field()
    property_ownership = Field()
    # Spaces and material
    parking_space_description = Field()
    common_spaces = Field()
    wallcovering = Field()
    # Contacts
    contact_person_name = Field()
    contact_person_company = Field()
    contact_person_job_title = Field()
    contact_person_email = Field()
    contact_person_phone_number = Field()


class OikotieItemLoader(ItemLoader):
    default_input_processor = Identity()
    default_output_processor = TakeFirst()

    def __init__(
        self,
        item: Any = None,
        selector: Selector | None = None,
        parent: ItemLoader | None = None,
        response: Response | None = None,
        **context: Any,
    ):
        super().__init__(item, selector, response, parent, **context)
