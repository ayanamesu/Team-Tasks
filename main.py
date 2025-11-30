import csv
import random
from database import Neo4jConnection
from user import UserService  


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"   # You need to change this to your real password on neo4j. You can use the same as mine if you want but your URI might be different.


# ===============================
# This loads the users from the csv
# ===============================
def load_users_from_csv(path, conn):
    """
    This Reads the Kaggle CSV and creates User nodes.
    Assumes there is a 'screenName' column in the CSV.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            username = row["screenName"]  # using screenName as username

            query = """
            MERGE (u:User {username: $username})
            ON CREATE SET
                u.name = $username,
                u.email = "",
                u.password = "imported",
                u.bio = ""
            """
            conn.execute_write(query, username=username)
            count += 1

    print(f"Users imported from {path}: {count}")


# ===============================
# This generates synthetic FOLLOWS edges which is random users following each others
# ===============================
def generate_edges(conn, total_edges=5000):
    """
    Randomly creates FOLLOWS relationships between existing users.
    """
    # get all usernames
    result = conn.execute_read("MATCH (u:User) RETURN u.username AS username")
    usernames = [row["username"] for row in result]
    print(f"Found {len(usernames)} users in DB.")

    if len(usernames) < 2:
        print("Not enough users to generate edges.")
        return

    print(f"Generating {total_edges} synthetic FOLLOWS edges...")

    for _ in range(total_edges):
        a = random.choice(usernames)
        b = random.choice(usernames)
        if a == b:
            continue  # skip self-follow

        conn.execute_write(
            """
            MATCH (u1:User {username: $a})
            MATCH (u2:User {username: $b})
            MERGE (u1)-[:FOLLOWS]->(u2)
            """,
            a=a,
            b=b,
        )

    print("Synthetic edges created.")


def main_menu():
    print("\n===== MiniSocial =====")
    print("1. Register")
    print("2. Login")
    print("3. Exit")


def user_menu(username):
    print(f"\n===== Logged in as {username} =====")
    print("1. View Profile")
    print("2. Edit Profile")
    print("3. Logout")


def main():
    conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    user_service = UserService(conn)   # <-- correct
    logged_in = None

    # ================================================
    # THIS IMPORT KAGGLE USERS + GENERATE EDGES ONE TIME
    # ONLY UNCOMMENT these two lines once to run the import,
    # then COMMENT them again afterward.
    # ================================================
    #load_users_from_csv("data.csv", conn)
    #generate_edges(conn, total_edges=10000)
    # ================================================

    try:
        while True:
            if not logged_in:
                main_menu()
                choice = input("Choose option: ")

                if choice == "1":
                    name = input("Name: ")
                    email = input("Email: ")
                    username = input("Username: ")
                    password = input("Password: ")

                    success = user_service.register_user(name, email, username, password)
                    print("Registration successful." if success else "Username already taken.")

                elif choice == "2":
                    username = input("Username: ")
                    password = input("Password: ")

                    user = user_service.authenticate_user(username, password)
                    if user:
                        print(f"Welcome {user['name']}!")
                        logged_in = username
                    else:
                        print("Invalid login.")
                elif choice == "3":
                    break
            else:
                user_menu(logged_in)
                choice = input("Choose: ")

                if choice == "1":
                    profile = user_service.get_profile(logged_in)
                    print(profile)

                elif choice == "2":
                    new_name = input("New name (blank to keep): ")
                    if new_name == "":
                        new_name = None

                    new_bio = input("New bio (blank to keep): ")
                    if new_bio == "":
                        new_bio = None

                    updated = user_service.update_profile(logged_in, new_name, new_bio)
                    print("Updated:", updated)

                elif choice == "3":
                    logged_in = None

    finally:
        conn.close()


if __name__ == "__main__":
    main()