from database import Neo4jConnection

class UserService:
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
    def get_profile(self, username):
        query = """
        MATCH (u:User {username: $username})
        MATCH (u)<-[:FOLLOWS]-(followers)
        MATCH (u)-[:FOLLOWS]->(following)
        RETURN u,
                COUNT(DISTINCT followers) AS follower_count,
                COUNT(DISTINCT following) AS following_count
        """
        result = self.conn.execute_read(query, username=username)
        if not result:
            return {"error": "User not found."}
        
        node = result[0]
        user_node = node["u"]
        profile = dict(user_node)
        profile["follower_count"] = node["follower_count"]
        profile["following_count"] = node["following_count"]
        return profile
    
    # Editing user profile
    def edit_profile(self, username, new_name, new_bio):
        query = """
        MATCH (u:User {username: $username})
        SET u.name = COALESCE($new_name, u.name),
            u.bio  = COALESCE($new_bio,  u.bio)
        RETURN u
        """
        result = self.conn.execute_query(
            query, 
            username=username, 
            new_name=new_name, 
            new_bio=new_bio
        )
        if not result:
            return {"error": "User not found."}
        
        node = result[0]["u"]
        return dict(node)