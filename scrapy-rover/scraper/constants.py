TITLE_TO_FIELD = {
    # =================
    # Perustiedot
    # =================
    "Sijainti": "location",
    "Kaupunki": "city",
    "Kaupunginosa": "district",
    # "Kohdenumero": "item_number",
    "Kerros": "floor",
    "Asuinpinta-ala": "living_area",
    # "Tontin pinta-ala": "property_sq",
    # "Kokonaispinta-ala": "total_sq",
    "Huoneiston kokoonpano": "apartment_layout",
    "Huoneita": "number_of_rooms",
    # "Kunto": "condition",
    # "Kunnon lisätiedot": "condition_details",
    # "Lisätietoa vapautumisesta": "availability",
    # "Keittiön varusteet": "kitchen_appliances",
    # "Kylpyhuoneen varusteet": "bathroom_appliances",
    # "Ikkunoiden suunta": "window_direction",
    "Parveke": "has_balcony",
    # "Parvekkeen lisätiedot": "balcony_details",
    # "Säilytystilat": "storage_space",
    # "Näkymät": "view",
    "Tulevat remontit": "future_renovations",
    "Tehdyt remontit": "completed_renovations",
    # "Asunnossa sauna": "has_sauna",
    # "Saunan lisätiedot": "sauna_details",
    "Asumistyyppi": "housing_type",
    # "Palvelut": "services",
    # "Lisätiedot": "additional_info",
    # "Kiinteistötunnus": "property_id",
    # "Kohde on": "apartment_is",
    # "Tietoliikennepalvelut": "telecommunication_services",
    # =================
    # Hintatiedot ja muut kustannukset
    # =================
    "Velaton hinta": "debt_free_price",
    "Myyntihinta": "sales_price",
    # "Lainaosuuden maksu": "shared_loan_payment",
    # "Neliöhinta": "price_per_sq",
    # "Velkaosuus": "share_of_liabilities",
    # "Kiinnitykset": "mortgages",
    # "Rahoitusvastike": "financial_charge",
    "Hoitovastike": "maintenance_charge",
    "Yhtiövastike yhteensä": "total_housing_charge",
    "Vesimaksu": "water_charge",
    # "Vesimaksun lisätiedot": "water_charge_details",
    # "Lämmityskustannukset": "heating_charge",
    # "Muut kustannukset": "other_costs",
    # =================
    # Talon ja tontin tiedot
    # =================
    # "Uudiskohde": "is_brand_new",
    # "Taloyhtiön nimi": "housing_company_name",
    "Rakennuksen tyyppi": "building_type",
    "Rakennusvuosi": "build_year",
    # "Rakennusvuoden lisätiedot": "build_year_details",
    # "Huoneistojen lukumäärä": "number_of_apartments",
    "Kerroksia": "total_floors",
    "Hissi": "building_has_elevator",
    "Taloyhtiössä on sauna": "building_has_sauna",
    # "Rakennusmateriaali": "building_material",
    # "Kattotyyppi": "roof_type",
    "Energialuokka": "energy_class",
    "Energiatoditus": "has_energy_certificate",
    # "Kiinteistön antennijärjestelmä": "antenna_system",
    "Tontin koko": "plot_area",
    # "Kiinteistönhoito": "maintenance",
    # "Isännöinti": "real_estate_management",
    # "Kaavatiedot": "plan_info",
    # "Kaavatilanne": "plan",
    # "Liikenneyhteydet": "traffic_communication",
    "Lämmitys": "heating",
    "Tontin omistus": "plot_ownership",
    # =================
    # Tilat ja materiaalit
    # =================
    # "Pysäköintitilan kuvaus": "parking_space_description",
    # "Yhteiset tilat": "common_spaces",
    # "Pintamateriaalit": "wallcovering",
}

PLOT_OWNERSHIP_TRANSLATIONS = {
    "oma": "own",
    "valinnainen vuokratontti": "optional_rent",
    "vuokralla": "rent",
}

HOUSING_TYPE_TRANSLATIONS = {
    "omistus": "ownership",
    "asumisoikeus": "right_of_residence",
}

BUILDING_TYPE_TRANSLATIONS = {
    "kerrostalo": "apartment_building",
    "luhtitalo": "apartment_building",
    "erillistalo": "detached_house",
    "omakotitalo": "detached_house",
    "paritalo": "semi_detached_house",
    "puutalo-osake": "wooden_house",
    "rivitalo": "terraced_house",
    "muu": "other",
}

BOOLEAN_TRANSLATIONS = {
    "kyllä": True,
    "ei": False,
}
