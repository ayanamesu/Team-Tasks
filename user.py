from database import Neo4jConnection 


class UserService:
    def __init__(self, conn):
        self.conn = conn

    # UC-1: User Registration
    # This return True if ok and returns False if username taken
    def register_user(self, name, email, username, password):
        # Checks if username already exists
        query_check = """
        MATCH (u:User {username: $username})
        RETURN u
        """
        result = self.conn.execute_read(query_check, username=username)
        if result:
            # if username already exists
            return False

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

        self.conn.execute_write(
            query_create,
            name=name,
            email=email,
            username=username,
            password=password
        )
        return True

    # UC-2: User Login
    def authenticate_user(self, username, password):
        query = """
        MATCH (u:User {username: $username, password: $password})
        RETURN u
        """
        result = self.conn.execute_read(query, username=username, password=password)
        if not result:
            return None

        node = result[0]["u"]
        return dict(node)

    # UC-3: View Profile
    def get_profile(self, username):
        query = """
        MATCH (u:User {username: $username})
        OPTIONAL MATCH (u)<-[:FOLLOWS]-(followers)
        OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
        RETURN u,
               COUNT(DISTINCT followers) AS follower_count,
               COUNT(DISTINCT following) AS following_count
        """
        result = self.conn.execute_read(query, username=username)
        if not result:
            return None

        row = result[0]
        user_node = row["u"]
        profile = dict(user_node)
        profile["follower_count"] = row["follower_count"]
        profile["following_count"] = row["following_count"]
        return profile

    # UC-4: Edit Profile
    def update_profile(self, username, new_name, new_bio):
        query = """
        MATCH (u:User {username: $username})
        SET u.name = COALESCE($new_name, u.name),
            u.bio  = COALESCE($new_bio,  u.bio)
        RETURN u
        """
        # execute_write now already returns a list 
        records = self.conn.execute_write(
            query,
            username=username,
            new_name=new_name,
            new_bio=new_bio
        )

        if not records:
            return None

        node = records[0]["u"]
        return dict(node)

    def follow_user(self, current_user, target_user):

        query = """
        MATCH (current_user:User {username: $current_user})
        MATCH (target_user:User {username: $target_user})
        MERGE (current_user)-[:FOLLOWS]->(target_user)
        RETURN current_user, target_user
        """

        result = self.conn.execute_write(query, current_user=current_user, target_user=target_user)

        if not result:
            return f"Error: could not find user {target_user}"

        return f"Succesfully followed {target_user}"

    def unfollow_user(self, current_user, target_user):

        query = """
           MATCH (current_user:User {username: $current_user})
           MATCH (target_user:User {username: $target_user})
           MATCH (current_user)-[r:FOLLOWS]->(target_user)
           DELETE r
           RETURN current_user, target_user
           """

        result = self.conn.execute_write(query, current_user=current_user, target_user=target_user)

        if not result:
            return f"Error: could not find user {target_user}"

        return f"Succesfully unfollowed {target_user}"

    def check_following(self, username):
        query = """
                MATCH (u:User {username: $username})
                MATCH (u)-[:FOLLOWS]->(follower:User)
                RETURN follower.username AS username
                """
        result = self.conn.execute_read(query, username=username)

        if not result:
            return None

        following = [record["username"] for record in result]
        return following

    def check_followers(self, username):
        query = """
        MATCH (u:User {username: $username})
        MATCH (u)<-[:FOLLOWS]-(follower:User)
        RETURN follower.username AS username
        """
        result = self.conn.execute_read(query, username=username)

        if not result:
            return None

        followers = [record["username"] for record in result]
        return followers

    def check_mutuals(self, username):
        query = """
           MATCH (u:User {username: $username})
           MATCH (mutual:User)
           WHERE (mutual)-[:FOLLOWS]->(u) 
           AND (u)-[:FOLLOWS]->(mutual) 
           RETURN mutual.username AS username
           """
        result = self.conn.execute_read(query, username=username)

        if not result:
            return None

        mutuals = [record["username"] for record in result]
        return mutuals



