from follow_api.follow_api_description import FollowGetAccountReputationsResponse
from follow_api.follow_api_description import BlogCondenserApi
from follow_api.follow_api_description import BlogEntries
from follow_api.follow_api_description import FollowCondenserApi
from follow_api.follow_api_description import CondenserGetFollowCountResponse
from typing import Optional
from beekeepy._apis.abc.api import AbstractAsyncApi


class FollowApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def get_account_reputations(
        self, *, account_lower_bound: Optional = None, limit: Optional = None
    ) -> FollowGetAccountReputationsResponse:
        """Parameters:

        - `account_lower_bound`: A string representing the starting account name (lower bound) for the query.

        - `limit`: An integer up to 1000 specifying the maximum number of accounts to return.

        Examples:

        - `account_lower_bound = "hiveio"`, `limit = 1` — queries accounts starting with "hiveio", returning only one result.

        - `account_lower_bound = "a"`, `limit = 10` — queries accounts starting with "a", returning up to 10 results.
        """

    @endpoint_jsonrpc
    async def get_blog(
        self, *, account: str, start_entry_id: Optional = None, limit: Optional = None, observer: Optional = None
    ) -> list[BlogCondenserApi]:
        """Parameters:

        - `account`: A string representing the account name to query the blog for.

        - `start_entry_id`: An integer representing the starting entry ID for querying the blog.

        - `limit`: An integer up to 500 specifying the maximum number of blog entries to return.

        Examples:

        - `account = "hiveio"`, `start_entry_id = 0`, `limit = 1` — queries the blog for the account named "hiveio", returning up to one result.

        - `account = "alice"`, `start_entry_id = 0`, `limit = 50` — queries the blog for the account named "alice", returning up to 50 results.
        """

    @endpoint_jsonrpc
    async def get_blog_entries(
        self, *, account: str, start_entry_id: Optional = None, limit: Optional = None, observer: Optional = None
    ) -> list[BlogEntries]:
        """Parameters:

        - `account`: A string representing the account name to query the blog entries for.

        - `start_entry_id`: An integer representing the starting entry ID for querying the blog entries.

        - `limit`: An integer up to 500 specifying the maximum number of blog entries to return.

        Examples:

        - `account = "hiveio"`, `start_entry_id = 0`, `limit = 1` — queries the blog entries for the account named "hiveio", returning up to one result.

        - `account = "alice"`, `start_entry_id = 0`, `limit = 50` — queries the blog entries for the account named "alice", returning up to 50 results.
        """

    @endpoint_jsonrpc
    async def get_followers(
        self, *, account: str, start: Optional = None, type: Optional = None, limit: Optional = None
    ) -> list[FollowCondenserApi]:
        """Parameters:

        - `account`: A string representing the account name to query.
        - `start`: A string indicating the account to start from (optional).
        - `type`: A string specifying the type of data, e.g., 'blog' or 'ignore'.
        - `limit`: An integer up to 1000 specifying the maximum number of results.

        Examples:
        - `account = "hiveio"`, `type = "blog"`, `limit = 10` — Queries for follows of 'hiveio', up to 10 results.
        - `account = "alice"`, `type = "ignore"`, `limit = 100` — Queries for mutes of 'alice', up to 100 results."""

    @endpoint_jsonrpc
    async def get_following(
        self, *, account: str, start: Optional = None, type: Optional = None, limit: Optional = None
    ) -> list[FollowCondenserApi]:
        """Parameters:

        - `account`: A string representing the account name to query.
        - `start`: A string specifying the account to start from (optional).
        - `type`: A string indicating the relationship type, e.g., 'blog' for followers or 'ignore' for mutes.
        - `limit`: An integer up to 1000 defining the maximum number of results.

        Examples:
        - `account = "hiveio"`, `type = "blog"`, `limit = 10` — Queries for follows of 'hiveio', up to 10 results.
        - `account = "alice"`, `type = "ignore"`, `limit = 100` — Queries for mutes of 'alice', up to 100 results."""

    @endpoint_jsonrpc
    async def get_follow_count(self, *, account: str) -> CondenserGetFollowCountResponse:
        """Parameters:

        - `account`: A string representing the account name to query.

        Examples:
        - `account = "hiveio"` — Queries the account named hiveio.
        - `account = "alice"` — Queries the account named alice."""

    @endpoint_jsonrpc
    async def get_reblogged_by(self, *, author: str, permlink: str) -> list[list]:
        """Parameters:

        - `author`: A string representing the author's username.
        - `permlink`: A string representing the unique identifier of the content (permalink).

        Examples:
        - `author = "hiveio"`, `permlink = "firstpost"` — Queries reblogs for content with a slug @hiveio/firstpost.
        - `author = "alice"`, `permlink = "a-post-by-alice"` — Queries reblogs for content with a slug @alice/a-post-by-alice."""
