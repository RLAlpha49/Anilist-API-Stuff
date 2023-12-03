class Queries:
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
    def Follower_Query(user_id, page):
        Query = """
        query ($userId: Int!, $page: Int, $perPage: Int) {
            Page (page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                followers(userId: $userId) {
                    id
                }
            }
        }
        """
        Variables = {
            "userId": user_id,
            "page": page,
            "perPage": 50
        }
        return Query, Variables
    
    @staticmethod
    def Following_Query(user_id, page):
        Query = """
        query ($userId: Int!, $page: Int, $perPage: Int) {
            Page (page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                following(userId: $userId) {
                    id
                }
            }
        }
        """
        Variables = {
            "userId": user_id,
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