interface Property {
  id: number;
  oikotie_id?: number;
  url?: string;
  image_urls?: string[];

  // Address information
  location?: string;
  city?: string;
  district?: string;

  // Property information
  building_type?: string;
  housing_type?: string;
  build_year?: number;
  floor?: number;
  total_floors?: number;
  living_area?: number;
  plot_area?: number;
  plot_ownership?: string;
  apartment_layout?: string;
  number_of_rooms?: number;
  number_of_bedrooms?: number;
  has_balcony?: boolean;
  building_has_elevator?: boolean;
  building_has_sauna?: boolean;
  has_energy_certificate?: string;
  energy_class?: string;
  heating?: string;

  // Renovation information
  future_renovations?: string;
  completed_renovations?: string;

  // Sales information
  debt_free_price?: number;
  sales_price?: number;
  maintenance_charge?: number;
  total_housing_charge?: number;
  water_charge?: number;

  // Metadata
  opensearch_version?: number;
}
