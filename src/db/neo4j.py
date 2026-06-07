from neo4j import GraphDatabase


class Neo4jService:
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.auth = (user, password)
        self._driver = None

    def connect(self):
        self._driver = GraphDatabase.driver(self.uri, auth=self.auth)

    def disconnect(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    @property
    def driver(self):
        if not self._driver:
            raise RuntimeError("Neo4j no conectado")
        return self._driver

    def read(self, query, **params):
        with self.driver.session() as session:
            return session.run(query, **params).data()

    def write(self, query, **params):
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(query, **params).data()
            )

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()
