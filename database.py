from neo4j import GraphDatabase


# Database actions
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def execute_read(self, query, **parameters):
        with self.driver.session() as session:
            # returns a list of records
            return session.execute_read(
                lambda tx: list(tx.run(query, **parameters))
            )

    def execute_write(self, query, **parameters):
        with self.driver.session() as session:
            # also returns a list of records
            return session.execute_write(
                lambda tx: list(tx.run(query, **parameters))
            )
