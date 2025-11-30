from db import Neo4jConnection

class User:
    def __init__(self, conn):
        self.conn = conn

    
    def create_user(self, name, email, username, password):

        #if username exists 

        query_check = """
        MATCH (u:User {username: $username})
        RETURN u
        """
        result = self.conn.execute_read(query_check, username=username)
        if result:
            return {"error": "Username already exists."}
        
        # Create new user
        query_create = """
        CREATE (u:User {
            name: $name, 
            email: $email, 
            username: $username, 
            password: $password,
            bio: ""
        })
        """
        self.conn.execute_query(
            query_create, 
            name=name, 
            email=email, 
            username=username, 
            password=password
        )
        return True
    
    #User login
    def login_user(self, username, password):
        query = """
        MATCH (u:User {username: $username, password: $password})
        RETURN u
        """
        result = self.conn.execute_read(query, username=username, password=password)
        if not result:
            return {"error": "Invalid username or password."}
        
        node = result[0]["u"]
        return dict(node)
    
    # Viewing user profile