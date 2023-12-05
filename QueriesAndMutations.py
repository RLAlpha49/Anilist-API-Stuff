class Queries:
    @staticmethod
    def Check_Authentication():
        Query = """
        query {
            Viewer {
                id
                name
            }
        }
        """
        return Query
    
    @staticmethod
    def create_page_query(query_name):
        return f"""
        query ($userId: Int!, $page: Int, $perPage: Int) {{
            Page (page: $page, perPage: $perPage) {{
                pageInfo {{
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }}
                {query_name}(userId: $userId) {{
                    id
                }}
            }}
        }}
        """

    @staticmethod
    def create_variables(user_id, page):
        return {
            "userId": user_id,
            "page": page,
            "perPage": 50
        }

    @staticmethod
    def Follower_Query(user_id, page):
        return Queries.create_page_query('followers'), Queries.create_variables(user_id, page)

    @staticmethod
    def Following_Query(user_id, page):
        return Queries.create_page_query('following'), Queries.create_variables(user_id, page)
    
    @staticmethod
    def Global_Activity_Feed_Query(page):
        Query = """
        query ($page: Int, $perPage: Int) {
            Page (page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                activities(sort: ID_DESC) {
                    ... on TextActivity {
                        id
                        user {
                            id
                        }
                    }
                    ... on ListActivity {
                        id
                        user {
                            id
                        }
                    }
                    ... on MessageActivity {
                        id
                    }
                }
            }
        }
        """
        Variables = {
            "page": page,
            "perPage": 50
        }
        return Query, Variables
    
    @staticmethod
    def Get_User_ID_Query(username):
        Query = """
        query ($name: String) {
            User(name: $name) {
                id
            }
        }
        """
        Variables = {
            "name": username
        }
        return Query, Variables

    @staticmethod
    def User_Activity_Feed_Query(userId, page, include_message_activity):
        Query = """
        query ($userId: Int, $page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                activities(userId: $userId, sort: ID_DESC) {
                    ... on TextActivity {
                        id
                        isLiked
                    }
                    ... on ListActivity {
                        id
                        isLiked
                    }
        """
        if include_message_activity:
            Query += """
                    ... on MessageActivity {
                        id
                        isLiked
                    }
            """
        Query += """
                }
            }
        }
        """
        Variables = {
            "userId": userId,
            "page": page,
            "perPage": 50
        }
        return Query, Variables

class Mutations:
    @staticmethod
    def Follow_Mutation(user_id):
        Mutation = """
        mutation ($id: Int) {
            ToggleFollow(userId: $id) {
                id
                name
                isFollowing
            }
        }
        """
        Variables = {
            "id": user_id
        }
        return Mutation, Variables
    
    @staticmethod
    def Like_Mutation(activity_id):
        Mutation = """
        mutation ($id: Int, $type: LikeableType) {
            ToggleLike(id: $id, type: $type) {
                id
            }
        }
        """
        Variables = {
            "id": activity_id,
            "type": "ACTIVITY"
        }
        return Mutation, Variables