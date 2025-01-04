from opensearchpy import OpenSearch, AWSV4SignerAuth, RequestsHttpConnection
import boto3

from src.core.config import settings
from src.core.logging import Logger

logger = Logger(__name__).logger

credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(
    credentials=credentials,
    region=settings.AWS_REGION_NAME,
    service="es",
)

opensearch_client = OpenSearch(
    hosts=[{"host": settings.OPENSEARCH_DOMAIN, "port": 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)


# TODO: migrate this to a proper data migration script
def initialize_search_properties_index():
    logger.info("Initializing search properties index")
    index_name = "properties"

    if not opensearch_client.indices.exists(index=index_name):
        mappings = {
            "properties": {
                "id": {"type": "integer"},
                "oikotie_id": {"type": "integer"},
                "url": {"type": "keyword"},
                # "image_urls": {"type": "keyword"}, // Should not be searchable
                "location": {"type": "text"},
                "city": {"type": "keyword"},
                "district": {"type": "keyword"},
                "building_type": {"type": "keyword"},
                "housing_type": {"type": "keyword"},
                "build_year": {"type": "integer"},
                "floor": {"type": "integer"},
                "total_floors": {"type": "integer"},
                "living_area": {"type": "float"},
                "plot_area": {"type": "float"},
                "plot_ownership": {"type": "keyword"},
                "apartment_layout": {"type": "text"},
                "number_of_rooms": {"type": "integer"},
                "number_of_bedrooms": {"type": "integer"},
                "has_balcony": {"type": "boolean"},
                "building_has_elevator": {"type": "boolean"},
                "building_has_sauna": {"type": "boolean"},
                # "has_energy_certificate": {"type": "keyword"}, // Complex case
                # "energy_class": {"type": "keyword"},
                # "heating": {"type": "keyword"},
                # "future_renovations": {"type": "text"}, // Needs language processing
                # "completed_renovations": {"type": "text"}, // Needs language processing
                "debt_free_price": {"type": "float"},
                "sales_price": {"type": "float"},
                "maintenance_charge": {"type": "float"},
                "total_housing_charge": {"type": "float"},
                "water_charge": {"type": "float"},
            }
        }

        settings = {"index": {"number_of_shards": 1, "number_of_replicas": 1}}

        # Create the index with mappings and settings
        opensearch_client.indices.create(
            index=index_name, body={"settings": settings, "mappings": mappings}
        )

        logger.info(
            f"Index {index_name} created successfully with mappings: {mappings}"
        )
    else:
        logger.info(f"Index {index_name} already exists, skipping creation")
