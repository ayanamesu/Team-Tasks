from neo4j import GraphDatabase

class Neo4jDatabase:

    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def execute_query(self, query, str, **params):
        with self.driver.session() as session:
            return session.execute_query(
                lambda tx: list(tx.run(query, **params))
            )
        
    def execute_read(self, query: str, **params):
        with self._driver.session() as session:
            return session.execute_read(
                lambda tx: list(tx.run(query, **params))
            )