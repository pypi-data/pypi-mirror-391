from bridge.bridge_description import Notification
from bridge.bridge_description import PostBridgeApi
from bridge.bridge_description import GetCommunityResponse
from bridge.bridge_description import GetCommunityContextResponse
from bridge.bridge_description import GetDiscussionResponse
from bridge.bridge_description import Follow
from bridge.bridge_description import GetPayoutStatsResponse
from bridge.bridge_description import GetPostResponse
from bridge.bridge_description import GetPostHeaderResponse
from bridge.bridge_description import GetProfileResponse
from bridge.bridge_description import Profile
from bridge.bridge_description import GetRelationshipBetweenAccountsResponse
from bridge.bridge_description import Community
from bridge.bridge_description import ListMutedReasonsEnumResponse
from bridge.bridge_description import NormalizePostResponse
from bridge.bridge_description import UnreadNotificationsResponse
from typing import Optional
from beekeepy._apis.abc.api import AbstractAsyncApi


class Bridge(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def account_notifications(self, account: str, limit: int, /) -> list[Notification]:
        """Supported values for the `type` parameter:

        - `new_community`: A new community was created.
        - `set_role`: A mod or admin adds a role to an account.
        - `set_props`: Properties are set for a community.
        - `set_label`: A title, badge, or label has been set for an account.
        - `mute_post`: A post has been muted, with a reason.
        - `unmute_post`: A post has been unmuted, with a reason.
        - `pin_post`: A post has been pinned.
        - `unpin_post`: A post has been unpinned.
        - `flag_post`: A post has been flagged by a member, with a reason.
        - `error`: Provides feedback to developers for operations that cannot be interpreted.
        - `subscribe`: An account has subscribed to a community.
        - `reply`: A post has been replied to.
        - `reblog`: A post has been reblogged (shared again).
        - `follow`: An account has followed another account.
        - `mention`: An author mentions an account.
        - `vote`: A voter votes for an author.

        *Note:* The score value associated with each operation is based on the originating account rank.
        """

    @endpoint_jsonrpc
    async def does_user_follow_any_lists(self, observer: str, /) -> bool: ...

    @endpoint_jsonrpc
    async def get_account_posts(
        self,
        sort: str,
        account: str,
        start_author: Optional = None,
        start_permlink: Optional = None,
        limit: Optional = None,
        observer: Optional = None,
        /,
    ) -> list[PostBridgeApi]:
        """Parameters:

        - `sort`: A string indicating the type of posts to retrieve. Supported values:
          - `blog`: Top posts authored by the specified account (excluding community posts unless reblogged), plus reblogs ranked by creation or reblog time.
          - `feed`: Top posts from blogs of accounts followed by the specified account, ranked by creation or reblog time, not older than the last month.
          - `posts`: Posts authored by the specified account, sorted by newest first.
          - `replies`: Replies authored by the specified account, sorted by newest first.
          - `payout`: All posts authored by the specified account that have not yet been cashed out.

        - `account`: The account name (string) to retrieve related posts for; must be a valid account.

        - `start_author`: The author account name to start from when paginating; optional and used together with `start_permlink`.

        - `start_permlink`: The permlink of the post corresponding to `start_author`, used as a paging mechanism; optional.

        - `limit`: The maximum number of posts to retrieve. If omitted, defaults to 20.

        - `observer`: (Optional) For `blog`, `feed`, and `replies` sorts, this parameter is ignored. Otherwise, when provided, it must point to a valid account used to populate blacklist stats and mark posts from blacklisted authors. Currently, this parameter is ignored.
        """

    @endpoint_jsonrpc
    async def get_community(self, name: str, observer: str, /) -> GetCommunityResponse:
        """Parameters:

        - `name`: The community category name (string) to retrieve details for.

        - `observer`: A valid account name (string) used as an observer. This parameter is optional.
        """

    @endpoint_jsonrpc
    async def get_community_context(self, name: str, account: str, /) -> GetCommunityContextResponse: ...

    @endpoint_jsonrpc
    async def get_discussion(self, author: str, permlink: str, observer: str, /) -> GetDiscussionResponse: ...

    @endpoint_jsonrpc
    async def get_follow_list(self, observer: str, follow_type: str, /) -> list[Follow]:
        """Parameters:

        - `observer`: A valid account name (string) to act as an observer.

        - `follow_type`: A string indicating the type of follow-related list to retrieve. Supported values:
          - `follow_blacklist`: Accounts that are on the observer's follow blacklist.
          - `follow_muted`: Accounts that are on the observer's follow mute list.
          - `blacklisted`: Accounts that are directly blacklisted by the observer.
          - `muted`: Accounts that are directly muted by the observer.
        """

    @endpoint_jsonrpc
    async def get_payout_stats(self, limit: Optional = None, /) -> GetPayoutStatsResponse:
        """Parameters:

        - `limit`: An integer specifying the maximum number of results to retrieve. If omitted, the server defaults to 250. This parameter is optional.
        """

    @endpoint_jsonrpc
    async def get_post(self, author: str, permlink: str, observer: Optional = None, /) -> GetPostResponse:
        """Parameters:

        - `author`: A valid account name (string).

        - `permlink`: A valid permlink (string).

        - `observer`: A valid account name (string) used as an observer. This parameter is optional.
        """

    @endpoint_jsonrpc
    async def get_post_header(self, author: str, permlink: str, /) -> GetPostHeaderResponse:
        """Parameters:

        - `author`: A valid account name (string).

        - `permlink`: A valid permlink (string).
        """

    @endpoint_jsonrpc
    async def get_profile(self, account: str, observer: Optional = None, /) -> GetProfileResponse:
        """Parameters:

        - `account`: A valid account name (string).

        - `observer`: A valid account name (string) used as an observer. This parameter is optional.
        """

    @endpoint_jsonrpc
    async def get_profiles(self, accounts: Optional = None, observer: Optional = None, /) -> list[Profile]:
        """Parameters:

        - accounts: An array of valid account names (strings).

        - observer: A valid account name (string) used as an observer. This parameter is optional."""

    @endpoint_jsonrpc
    async def get_ranked_posts(self, sort: str, tag: str, observer: str, /) -> list[PostBridgeApi]:
        """Parameters:

        - `sort`: A string indicating the sorting method. Supported values:
          - `trending`
          - `hot`
          - `created`
          - `promoted`
          - `payout`
          - `payout_comments`
          - `muted`

        - `tag`: A string representing any valid tag.

        - `observer`: A string representing any valid account or an empty string.
        """

    @endpoint_jsonrpc
    async def get_relationship_between_accounts(
        self, account1: str, account2: Optional = None, observer: Optional = None, /
    ) -> GetRelationshipBetweenAccountsResponse: ...

    @endpoint_jsonrpc
    async def get_trending_topics(self, limit: Optional = None, observer: Optional = None, /) -> list[list]: ...

    @endpoint_jsonrpc
    async def list_all_subscriptions(self, account: str, /) -> list[list]:
        """Parameters:

        - `account`: A string representing a valid account name.
        """

    @endpoint_jsonrpc
    async def list_communities(
        self,
        last: Optional = None,
        limit: Optional = None,
        query: Optional = None,
        sort: Optional = "rank",
        observer: Optional = None,
        /,
    ) -> list[Community]:
        """Parameters:

        - `last`: A string representing the name of the community for paging purposes (optional).

        - `limit`: An integer to limit the number of listed communities; default is 100. This parameter is optional.

        - `query`: A string to filter communities based on title and about fields. This parameter is optional.

        - `sort`: A string to define the sorting method. Optional with default:
          - `rank`: sort by community rank
          - `new`: sort by newest communities
          - `subs`: sort by subscriptions

        - `observer`: A valid account name (string). This parameter is optional.
        """

    @endpoint_jsonrpc
    async def list_community_roles(
        self, community: str, last: Optional = None, limit: Optional = None, /
    ) -> list[list]:
        """Parameters:

        - `community`: A string representing the community category name.

        - `last`: A string representing the name of the subscriber for paging purposes (optional).

        - `limit`: An integer to limit the number of listed subscribers; default is 100. This parameter is optional.
        """

    @endpoint_jsonrpc
    async def list_muted_reasons_enum(self) -> ListMutedReasonsEnumResponse: ...

    @endpoint_jsonrpc
    async def list_pop_communities(self, limit: int, /) -> list[list]:
        """Parameters:

        - `limit`: An integer to limit the number of listed communities; default is 25. This parameter is optional.
        """

    @endpoint_jsonrpc
    async def list_subscribers(self, community: str, last: Optional = None, limit: Optional = None, /) -> list[list]:
        """Parameters:

        - `community`: A string representing the community category name.

        - `last`: A string indicating the name of the subscriber for paging purposes (optional).

        - `limit`: An integer to limit the number of listed subscribers; defaults to 100 if omitted. This parameter is optional.
        """

    @endpoint_jsonrpc
    async def normalize_post(self, author: str, permlink: str, /) -> NormalizePostResponse: ...

    @endpoint_jsonrpc
    async def post_notifications(
        self,
        author: str,
        permlink: str,
        min_score: Optional = None,
        last_id: Optional = None,
        limit: Optional = None,
        /,
    ) -> list[Notification]: ...

    @endpoint_jsonrpc
    async def unread_notifications(
        self, account: str, min_score: Optional = None, /
    ) -> UnreadNotificationsResponse: ...

    def argument_serialization(self) -> int:
        return 1
