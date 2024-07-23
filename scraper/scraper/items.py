# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from itemloaders.processors import Identity, TakeFirst
from scrapy import Field, Item

from .utils import TextUtils


class ScraperItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass


class OikotieItem(Item):
    url = Field(input_processor=Identity(), output_processor=TakeFirst())

    # Basic information
    location = Field(input_processor=TextUtils.strip_join, output_processor=TakeFirst())
    city = Field(input_processor=Identity(), output_processor=TakeFirst())
    house_number = Field(input_processor=Identity(), output_processor=TakeFirst())
    district = Field(input_processor=Identity(), output_processor=TakeFirst())
    oikotie_id = Field(input_processor=Identity(), output_processor=TakeFirst())
    floor = Field(input_processor=Identity(), output_processor=TakeFirst())
    total_floors = Field(input_processor=Identity(), output_processor=TakeFirst())
    life_sq = Field(input_processor=Identity(), output_processor=TakeFirst())
    property_sq = Field(input_processor=Identity(), output_processor=TakeFirst())
    total_sq = Field(input_processor=Identity(), output_processor=TakeFirst())
    room_info = Field(input_processor=Identity(), output_processor=TakeFirst())
    number_of_rooms = Field(input_processor=Identity(), output_processor=TakeFirst())
    condition = Field(input_processor=Identity(), output_processor=TakeFirst())
    condition_details = Field(input_processor=Identity(), output_processor=TakeFirst())
    availability = Field(input_processor=Identity(), output_processor=TakeFirst())
    kitchen_appliances = Field(input_processor=Identity(), output_processor=TakeFirst())
    bathroom_appliances = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    window_direction = Field(input_processor=Identity(), output_processor=TakeFirst())
    has_balcony = Field(input_processor=Identity(), output_processor=TakeFirst())
    balcony_details = Field(input_processor=Identity(), output_processor=TakeFirst())
    storage_space = Field(input_processor=Identity(), output_processor=TakeFirst())
    view = Field(input_processor=Identity(), output_processor=TakeFirst())
    future_renovations = Field(input_processor=Identity(), output_processor=TakeFirst())
    completed_renovations = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    has_sauna = Field(input_processor=Identity(), output_processor=TakeFirst())
    sauna_details = Field(input_processor=Identity(), output_processor=TakeFirst())
    housing_type = Field(input_processor=Identity(), output_processor=TakeFirst())
    services = Field(input_processor=Identity(), output_processor=TakeFirst())
    additional_info = Field(input_processor=Identity(), output_processor=TakeFirst())
    property_id = Field(input_processor=Identity(), output_processor=TakeFirst())
    apartment_is = Field(input_processor=Identity(), output_processor=TakeFirst())
    telecommunication_services = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    # Price and cost information
    price_no_tax = Field(input_processor=Identity(), output_processor=TakeFirst())
    sales_price = Field(input_processor=Identity(), output_processor=TakeFirst())
    shared_loan_payment = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    price_per_sq = Field(input_processor=Identity(), output_processor=TakeFirst())
    share_of_liabilities = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    mortgages = Field(input_processor=Identity(), output_processor=TakeFirst())
    financial_charge = Field(input_processor=Identity(), output_processor=TakeFirst())
    condominium_payment = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    maintenance_charge = Field(input_processor=Identity(), output_processor=TakeFirst())
    water_charge = Field(input_processor=Identity(), output_processor=TakeFirst())
    water_charge_details = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    heating_charge = Field(input_processor=Identity(), output_processor=TakeFirst())
    heating_charge_details = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    other_costs = Field(input_processor=Identity(), output_processor=TakeFirst())
    # House and property
    is_brand_new = Field(input_processor=Identity(), output_processor=TakeFirst())
    housing_company_name = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    building_type = Field(input_processor=Identity(), output_processor=TakeFirst())
    build_year = Field(input_processor=Identity(), output_processor=TakeFirst())
    build_year_details = Field(input_processor=Identity(), output_processor=TakeFirst())
    number_of_apartments = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    building_has_elevator = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    building_has_sauna = Field(input_processor=Identity(), output_processor=TakeFirst())
    building_material = Field(input_processor=Identity(), output_processor=TakeFirst())
    roof_type = Field(input_processor=Identity(), output_processor=TakeFirst())
    energy_class = Field(input_processor=Identity(), output_processor=TakeFirst())
    has_energy_certificate = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    antenna_system = Field(input_processor=Identity(), output_processor=TakeFirst())
    property_size = Field(input_processor=Identity(), output_processor=TakeFirst())
    property_size_unit = Field(input_processor=Identity(), output_processor=TakeFirst())
    property_owner = Field(input_processor=Identity(), output_processor=TakeFirst())
    maintenance = Field(input_processor=Identity(), output_processor=TakeFirst())
    real_estate_management = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    plan_info = Field(input_processor=Identity(), output_processor=TakeFirst())
    plan = Field(input_processor=Identity(), output_processor=TakeFirst())
    traffic_communication = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    heating = Field(input_processor=Identity(), output_processor=TakeFirst())
    property_ownership = Field(input_processor=Identity(), output_processor=TakeFirst())
    # Spaces and material
    parking_space_description = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    common_spaces = Field(input_processor=Identity(), output_processor=TakeFirst())
    wallcovering = Field(input_processor=Identity(), output_processor=TakeFirst())
    # Contacts
    contact_person_name = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    contact_person_company = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    contact_person_job_title = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    contact_person_email = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
    contact_person_phone_number = Field(
        input_processor=Identity(), output_processor=TakeFirst()
    )
