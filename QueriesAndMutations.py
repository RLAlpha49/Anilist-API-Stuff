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
                        messengerId
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
    def Following_Activity_Feed_Query(page):
        Query = """
        query ($page: Int, $perPage: Int, $isFollowing: Boolean) {
            Page (page: $page, perPage: $perPage) {
                activities(sort: ID_DESC, isFollowing: $isFollowing) {
                    ... on TextActivity {
                        id
                        isLiked
                        user {
                            id
                        }
                    }
                    ... on ListActivity {
                        id
                        isLiked
                        user {
                            id
                        }
                    }
                }
            }
        }
        """
        Variables = {
            "page": page,
            "perPage": 50,
            "isFollowing": True
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
    def User_Activity_Feed_Query(userId, page, perPage, include_message_activity, start_time=None, end_time=None):
        Query = """
        query ($userId: Int, $page: Int, $perPage: Int, $createdAtGreater: Int, $createdAtLesser: Int) {
            Page(page: $page, perPage: $perPage) {
                activities(userId: $userId, sort: ID_DESC, createdAt_greater: $createdAtGreater, createdAt_lesser: $createdAtLesser) {
                    ... on TextActivity {
                        id
                        isLiked
                        likes {
                            id
                        }
                        user {
                            id
                        }
                    }
                    ... on ListActivity {
                        id
                        isLiked
                        likes {
                            id
                        }
                        user {
                            id
                        }
                    }
        """
        if include_message_activity:
            Query += """
                    ... on MessageActivity {
                        id
                        isLiked
                        likes {
                            id
                        }
                        recipientId
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
            "perPage": perPage,
            "createdAtGreater": start_time,
            "createdAtLesser": end_time
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