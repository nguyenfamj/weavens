class PropertyQueryParams:
    def __init__(
        self,
        city: str | None = None,
        property_ownership: str | None = None,
        district: str | None = None,
        location: str | None = None,
        housing_type: str | None = None,
        building_type: str | None = None,
    ):
        self.city = city
        self.property_ownership = property_ownership
        self.district = district
        self.location = location
        self.housing_type = housing_type
        self.building_type = building_type
