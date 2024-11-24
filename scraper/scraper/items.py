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
    oikotie_id = Field(input_processor=MapCompose(int))
    url = Field()

    # Image urls
    image_urls = Field(output_processor=Identity())

    # Basic information
    location = Field(input_processor=ProcessorUtils.strip_join)
    city = Field()
    house_number = Field()
    district = Field()
    item_number = Field()
    floor = Field(input_processor=MapCompose(ProcessorUtils.extract_floor_number))
    total_floors = Field(input_processor=MapCompose(int))
    living_area = Field(input_processor=MapCompose(ProcessorUtils.extract_area))
    property_sq = Field()
    total_sq = Field()
    apartment_layout = Field()
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
    housing_type = Field(
        input_processor=MapCompose(ProcessorUtils.translate_housing_type)
    )
    services = Field()
    additional_info = Field()
    property_id = Field()
    apartment_is = Field()
    telecommunication_services = Field()
    # Price and cost information
    debt_free_price = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    sales_price = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    shared_loan_payment = Field()
    price_per_sq = Field()
    share_of_liabilities = Field()
    mortgages = Field()
    financial_charge = Field()
    maintenance_charge = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    total_housing_charge = Field(
        input_processor=MapCompose(ProcessorUtils.extract_price)
    )
    water_charge = Field(input_processor=MapCompose(ProcessorUtils.extract_price))
    water_charge_details = Field()
    heating_charge = Field()
    heating_charge_details = Field()
    other_costs = Field()
    # House and property
    is_brand_new = Field()
    housing_company_name = Field()
    building_type = Field(
        input_processor=MapCompose(ProcessorUtils.translate_building_type)
    )
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
    plot_area = Field(input_processor=MapCompose(ProcessorUtils.extract_area))
    property_size_unit = Field()
    property_owner = Field()
    maintenance = Field()
    real_estate_management = Field()
    plan_info = Field()
    plan = Field()
    traffic_communication = Field()
    heating = Field()
    plot_ownership = Field(
        input_processor=MapCompose(ProcessorUtils.translate_plot_ownership)
    )
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

    # Additional fields
    number_of_bedrooms = Field()


class BlogItem(Item):
    site = Field()
    url = Field()
    title = Field()
    content_text = Field(
        input_processor=MapCompose(
            ProcessorUtils.get_text_from_html,
        ),
    )
    content_html = Field(
        input_processor=MapCompose(
            ProcessorUtils.remove_html_attributes,
            ProcessorUtils.clean_html_space,
            ProcessorUtils.remove_empty_tags,
        ),
    )
    author = Field()
    main_image_url = Field()
    created_at = Field(input_processor=MapCompose(ProcessorUtils.parse_date))
    updated_at = Field(input_processor=MapCompose(ProcessorUtils.parse_date))
    content_type = Field()


class ScrapeContentItem(Item):
    url = Field()
    type = Field()
    mime_type = Field()
    source_page = Field()
    status = Field()


class ScrapeMetadata(Item):
    initial_url = Field()
    scraped_at = Field()
    status = Field()
    error_message = Field()


class OutputTakeFirstItemLoader(ItemLoader):
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
