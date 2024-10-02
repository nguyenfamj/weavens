from chromadb import PersistentClient
from chromadb.utils import embedding_functions

from .graph.utils import get_openai_api_key
from .logging import Logger

logger = Logger(__name__).logger


class ChromaWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaWrapper, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance

    def initialize(self):
        if self._client is None:
            self._client = PersistentClient(
                path="./vectorstore",
            )
            self.initialize_app_collection()

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError(
                "ChromaClient has not been initialized. Call initialize() first."
            )
        return self._client

    def initialize_app_collection(self):
        embedder = embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-3-small",
            api_key=get_openai_api_key(),
        )

        # Create vector search collection for the app
        try:
            self.document_collection = self.client.get_or_create_collection(
                name="document",
                embedding_function=embedder,
            )
            logger.info("Document collection initialized")
        except Exception as e:
            logger.error(f"Error initializing document collection: {e}")
