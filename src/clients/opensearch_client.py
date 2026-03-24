"""Minimal OpenSearch client for the local MVP."""

from base.base_client import BaseClient
from opensearchpy import OpenSearch


class OpenSearchClient(BaseClient):
    def __init__(self, host: str = "localhost", port: int = 9200) -> None:
        self.host = host
        self.port = port
        self.client: OpenSearch | None = None

    def connect(self) -> None:
        self.client = OpenSearch(
            hosts=[{"host": self.host, "port": self.port}],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

    def health_check(self) -> bool:
        if self.client is None:
            self.connect()
        return bool(self.client.ping())

    def ping(self) -> bool:
        return self.health_check()

    def close(self) -> None:
        transport = getattr(self.client, "transport", None)
        if transport is not None:
            transport.close()

