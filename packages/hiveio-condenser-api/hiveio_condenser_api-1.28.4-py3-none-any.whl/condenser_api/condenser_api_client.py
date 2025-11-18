from condenser_api.condenser_api_description import CondenserBroadcastTransactionResponse
from condenser_api.condenser_api_description import CondenserBroadcastTransactionSynchronousResponse
from condenser_api.condenser_api_description import ProposalsCondenserApi
from condenser_api.condenser_api_description import RcAccountCondenserApi
from condenser_api.condenser_api_description import RecurrentTransferCondenserApi
from condenser_api.condenser_api_description import AccountReputation
from condenser_api.condenser_api_description import AccountExtendedCondenserApi
from condenser_api.condenser_api_description import ActiveVotesDefault
from condenser_api.condenser_api_description import CondenserGetBlockResponse
from condenser_api.condenser_api_description import CondenserGetBlockHeaderResponse
from condenser_api.condenser_api_description import BlogCondenserApi
from condenser_api.condenser_api_description import BlogEntries
from condenser_api.condenser_api_description import CondenserGetChainPropertiesResponse
from condenser_api.condenser_api_description import CollateralizedConversionRequestsCondenserApi
from condenser_api.condenser_api_description import PostCondenserApi
from condenser_api.condenser_api_description import CondenserGetConfigResponse
from condenser_api.condenser_api_description import CondenserGetContentResponse
from condenser_api.condenser_api_description import PostDefault
from condenser_api.condenser_api_description import ConversionRequest
from condenser_api.condenser_api_description import CondenserGetCurrentMedianHistoryPriceResponse
from condenser_api.condenser_api_description import CondenserGetDynamicGlobalPropertiesResponse
from condenser_api.condenser_api_description import VestingDelegationExpirationsCondenserApi
from condenser_api.condenser_api_description import CondenserGetFeedHistoryResponse
from condenser_api.condenser_api_description import CondenserGetFollowCountResponse
from condenser_api.condenser_api_description import FollowCondenserApi
from condenser_api.condenser_api_description import MarketHistory
from condenser_api.condenser_api_description import CondenserGetNextScheduledHardforkResponse
from condenser_api.condenser_api_description import LimitOrderCondenserApi
from condenser_api.condenser_api_description import OperationCondenserApi
from condenser_api.condenser_api_description import CondenserGetOrderBookResponse
from condenser_api.condenser_api_description import OwnerAuthHistory
from condenser_api.condenser_api_description import CondenserGetPotentialSignaturesResponse
from condenser_api.condenser_api_description import TradeCondenserApi
from condenser_api.condenser_api_description import CondenserGetRewardFundResponse
from condenser_api.condenser_api_description import SavingsWithdrawalCondenserApi
from condenser_api.condenser_api_description import CondenserGetTickerResponse
from condenser_api.condenser_api_description import CondenserGetTransactionResponse
from condenser_api.condenser_api_description import TrendingTag
from condenser_api.condenser_api_description import GetVersionResponse
from condenser_api.condenser_api_description import VestingDelegationCondenserApi
from condenser_api.condenser_api_description import CondenserGetVolumeResponse
from condenser_api.condenser_api_description import WithdrawVestingRoutes
from condenser_api.condenser_api_description import CondenserGetWitnessScheduleResponse
from condenser_api.condenser_api_description import WitnessCondenserApi
from condenser_api.condenser_api_description import ProposalVoteCondenserApi
from condenser_api.condenser_api_description import RcAccountDelegation
from condenser_api.condenser_api_description import AccountCondenserApi
from condenser_api.condenser_api_description import CondenserBroadcastTransactionItem
from condenser_api.condenser_api_description import CondenserBroadcastTransactionSynchronou
from typing import Union[str, int
from typing import Optional
from typing import Union[str, int
from typing import Union[int, str
from typing import Union[int, bool
from condenser_api.condenser_api_description import CondenserGetPotentialSignature
from typing.Union[condenser_api.condenser_api_description import CondenserGetRequiredSignatures1, list[str
from typing import Union[str, int
from condenser_api.condenser_api_description import CondenserGetTransactionHexItem
from typing import Union[str, int, NoneType
from typing import Union[str, int, NoneType
from typing import Union[str, int, list, NoneType
from typing import Union[str, int, list, NoneType
from typing import Union[str, int
from typing import Union[list, int
from typing import Union[list[str
from typing import Union[str, int
from typing import Union[str, int
from condenser_api.condenser_api_description import CondenserVerifyAuthorityItem
from beekeepy._apis.abc.api import AbstractAsyncApi

class CondenserApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def broadcast_transaction(self, array_param: list[CondenserBroadcastTransactionItem], /) -> CondenserBroadcastTransactionResponse:
        ...

    @endpoint_jsonrpc
    async def broadcast_transaction_synchronous(self, array_param: list[CondenserBroadcastTransactionSynchronou], /) -> CondenserBroadcastTransactionSynchronousResponse:
        ...

    @endpoint_jsonrpc
    async def find_proposals(self, array_param: list[list[int]], /) -> list[ProposalsCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def find_rc_accounts(self, array_param: list[list[str]], /) -> list[RcAccountCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def find_recurrent_transfers(self, array_param: list[str], /) -> list[RecurrentTransferCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_account_count(self, array_param: list[str], /) -> int:
        ...

    @endpoint_jsonrpc
    async def get_account_history(self, array_param: list[Union[str, int]], /) -> list[list]:
        """Parameters:

- `account`: A string representing the account name to query.

- `start`: An integer indicating the starting point for the query. Use `-1` for reverse history or any positive number for a specific starting point.

- `limit`: An integer up to 1000 specifying the maximum number of results to return.

- `operation_filter_low`: An integer (optional) used to filter the first 64 operations based on a bitwise mask.

- `operation_filter_high`: An integer (optional) used to filter higher-numbered operations with a 128-bit bitmask composed of {operation_filter_high, operation_filter_low}.

If either `operation_filter_low` or `operation_filter_high` are set, the response will include only these operations matching the bitwise filter.

Examples:

- `account = "hiveio"`, `start = 1000`, `limit = 1000`: Queries the latest items in history for the account "hiveio", with up to 1,000 results.

- `account = "alice"`, `start = -1`, `limit = 1000`: Queries the oldest items in history for the account "alice", with up to 1,000 results.

- `account = "bob"`, `start = -1`, `limit = 1000`, `operation_filter_low = 1`: Queries only vote operations for "bob" from the oldest item, up to 1,000 results.

- `account = "charlie"`, `start = -1`, `limit = 1000`, `operation_filter_low = 262144`: Queries only custom JSON operations for "charlie" from the oldest item, up to 1,000 results.

- `account = "emma"`, `start = -1`, `limit = 1000`, `operation_filter_low = 0`, `operation_filter_high = 1`: Queries only proposal payments for "emma" from the oldest item, up to 1,000 results.
"""

    @endpoint_jsonrpc
    async def get_account_reputations(self, account_lower_bound: Optional=None, limit: Optional=None, /) -> list[AccountReputation]:
        """Parameters:

- `account_lower_bound`: A string representing the starting account name (lower bound) for the query.

- `limit`: An integer up to 1000 specifying the maximum number of accounts to return.

Examples:

- `account_lower_bound = "hiveio"`, `limit = 1` — queries accounts starting with "hiveio", returning only one result.

- `account_lower_bound = "a"`, `limit = 10` — queries accounts starting with "a", returning up to 10 results.
"""

    @endpoint_jsonrpc
    async def get_accounts(self, array_param: list[list[str]], /) -> list[AccountExtendedCondenserApi]:
        """Parameters:

- `account`: An array of strings representing account names to query.

- `delayed_votes_active`: A boolean indicating whether to include only accounts with active delayed votes.

Examples:

- `account = ["hiveio"]`, `delayed_votes_active = true` — queries for account named "hiveio".

- `account = ["hiveio", "alice"]`, `delayed_votes_active = false` — queries for accounts "hiveio" and "alice" with delayed votes hidden."""

    @endpoint_jsonrpc
    async def get_active_votes(self, account: str, permlink: str, observer: Optional=None, /) -> list[ActiveVotesDefault]:
        """Parameters:

- `author`: A string representing the author of the content.

- `permlink`: A string representing the permlink of the content.

Examples:

- `author = "hiveio"`, `permlink = "firstpost"` — queries votes for content with the slug @hiveio/firstpost.

- `author = "alice"`, `permlink = "a-post-by-alice"` — queries votes for content with the slug @alice/a-post-by-alice."""

    @endpoint_jsonrpc
    async def get_active_witnesses(self, array_param: list[str], /) -> list[list]:
        ...

    @endpoint_jsonrpc
    async def get_block(self, array_param: list[int], /) -> CondenserGetBlockResponse:
        """Parameters:

- `block_num`: An integer representing the block number to query.

Examples:

- `block_num = 1` — queries the very first block.

- `block_num = 8675309` — queries block number 8,675,309.

- `block_num = 62396745` — queries block number 62,396,745.
"""

    @endpoint_jsonrpc
    async def get_block_header(self, array_param: list[int], /) -> CondenserGetBlockHeaderResponse:
        """Parameters:

- `block_num`: An integer representing the block number to query.

Examples:

- `block_num = 1` — queries the block header for the very first block.

- `block_num = 8675309` — queries the block header for block number 8,675,309.

- `block_num = 62396745` — queries the block header for block number 62,396,745.
"""

    @endpoint_jsonrpc
    async def get_blog(self, account: str, start_entry_id: Optional=None, limit: Optional=None, observer: Optional=None, /) -> list[BlogCondenserApi]:
        """Parameters:

- `account`: A string representing the account name to query the blog for.

- `start_entry_id`: An integer representing the starting entry ID for querying the blog.

- `limit`: An integer up to 500 specifying the maximum number of blog entries to return.

Examples:

- `account = "hiveio"`, `start_entry_id = 0`, `limit = 1` — queries the blog for the account named "hiveio", returning up to one result.

- `account = "alice"`, `start_entry_id = 0`, `limit = 50` — queries the blog for the account named "alice", returning up to 50 results.
"""

    @endpoint_jsonrpc
    async def get_blog_entries(self, account: str, start_entry_id: Optional=None, limit: Optional=None, observer: Optional=None, /) -> list[BlogEntries]:
        """Parameters:

- `account`: A string representing the account name to query the blog entries for.

- `start_entry_id`: An integer representing the starting entry ID for querying the blog entries.

- `limit`: An integer up to 500 specifying the maximum number of blog entries to return.

Examples:

- `account = "hiveio"`, `start_entry_id = 0`, `limit = 1` — queries the blog entries for the account named "hiveio", returning up to one result.

- `account = "alice"`, `start_entry_id = 0`, `limit = 50` — queries the blog entries for the account named "alice", returning up to 50 results.
"""

    @endpoint_jsonrpc
    async def get_chain_properties(self, array_param: list[str], /) -> CondenserGetChainPropertiesResponse:
        ...

    @endpoint_jsonrpc
    async def get_collateralized_conversion_requests(self, array_param: list[str], /) -> list[CollateralizedConversionRequestsCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_comment_discussions_by_payout(self, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, tag: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_config(self, array_param: list[str], /) -> CondenserGetConfigResponse:
        ...

    @endpoint_jsonrpc
    async def get_content(self, account: str, permlink: str, observer: Optional=None, /) -> CondenserGetContentResponse:
        """Parameters:

- `author`: A string representing the author of the content.

- `permlink`: A string representing the permlink of the content.

Examples:

- `author = "hiveio"`, `permlink = "firstpost"` — queries content with the slug @hiveio/firstpost.

- `author = "alice"`, `permlink = "a-post-by-alice"` — queries content with the slug @alice/a-post-by-alice.
"""

    @endpoint_jsonrpc
    async def get_content_replies(self, account: str, permlink: str, observer: Optional=None, /) -> list[PostDefault]:
        """Parameters:

- `author`: A string representing the author of the content.

- `permlink`: A string representing the permlink of the content.

Examples:

- `author = "hiveio"`, `permlink = "firstpost"` — queries content with the slug @hiveio/firstpost.

- `author = "alice"`, `permlink = "a-post-by-alice"` — queries content with the slug @alice/a-post-by-alice.
"""

    @endpoint_jsonrpc
    async def get_conversion_requests(self, array_param: list[str], /) -> list[ConversionRequest]:
        """Parameters:

- `account`: A string representing the account name to query a conversion request for.

Example:

- `account = "hiveio"` — queries a conversion request for the account name "hiveio".
"""

    @endpoint_jsonrpc
    async def get_current_median_history_price(self, array_param: list[str], /) -> CondenserGetCurrentMedianHistoryPriceResponse:
        ...

    @endpoint_jsonrpc
    async def get_discussions_by_author_before_date(self, account: str, start_permlink: Optional=None, before_date: Optional=None, limit: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_discussions_by_blog(self, tag: str, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_discussions_by_comments(self, start_author: str, start_permlink: Optional=None, limit: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_discussions_by_created(self, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, tag: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_discussions_by_feed(self, tag: str, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_discussions_by_hot(self, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, tag: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_discussions_by_trending(self, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, tag: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_dynamic_global_properties(self, array_param: list[str], /) -> CondenserGetDynamicGlobalPropertiesResponse:
        ...

    @endpoint_jsonrpc
    async def get_escrow(self, array_param: list[Union[str, int]], /):
        ...

    @endpoint_jsonrpc
    async def get_expiring_vesting_delegations(self, array_param: list[str], /) -> list[VestingDelegationExpirationsCondenserApi]:
        """Parameters:

- `account`: A string representing the account name to query for expiring vesting.
- `after`: A timestamp to filter expiring vesting entries after a specified date.

Examples:
- `account = "hiveio"`, `after = "2018-01-01T00:00:00"` — Queries for expiring vesting after January 1st, 2018.
- `account = "alice"`, `after = "2017-12-01T00:00:00"` — Queries for expiring vesting after December 1st, 2017."""

    @endpoint_jsonrpc
    async def get_feed_history(self, array_param: list[str], /) -> CondenserGetFeedHistoryResponse:
        ...

    @endpoint_jsonrpc
    async def get_follow_count(self, account: str, /) -> CondenserGetFollowCountResponse:
        """Parameters:

- `account`: A string representing the account name to query.

Examples:
- `account = "hiveio"` — Queries the account named hiveio.
- `account = "alice"` — Queries the account named alice."""

    @endpoint_jsonrpc
    async def get_followers(self, account: str, start: Optional=None, follow_type: Optional=None, limit: Optional=None, /) -> list[FollowCondenserApi]:
        """Parameters:

- `account`: A string representing the account name to query.
- `start`: A string indicating the account to start from (optional).
- `type`: A string specifying the type of data, e.g., 'blog' or 'ignore'.
- `limit`: An integer up to 1000 specifying the maximum number of results.

Examples:
- `account = "hiveio"`, `type = "blog"`, `limit = 10` — Queries for follows of 'hiveio', up to 10 results.
- `account = "alice"`, `type = "ignore"`, `limit = 100` — Queries for mutes of 'alice', up to 100 results."""

    @endpoint_jsonrpc
    async def get_following(self, account: str, start: Optional=None, follow_type: Optional=None, limit: Optional=None, /) -> list[FollowCondenserApi]:
        """Parameters:

- `account`: A string representing the account name to query.
- `start`: A string specifying the account to start from (optional).
- `type`: A string indicating the relationship type, e.g., 'blog' for followers or 'ignore' for mutes.
- `limit`: An integer up to 1000 defining the maximum number of results.

Examples:
- `account = "hiveio"`, `type = "blog"`, `limit = 10` — Queries for follows of 'hiveio', up to 10 results.
- `account = "alice"`, `type = "ignore"`, `limit = 100` — Queries for mutes of 'alice', up to 100 results."""

    @endpoint_jsonrpc
    async def get_hardfork_version(self, array_param: list[str], /) -> str:
        ...

    @endpoint_jsonrpc
    async def get_key_references(self, array_param: list[list[str]], /) -> list[list]:
        ...

    @endpoint_jsonrpc
    async def get_market_history(self, array_param: list[Union[int, str]], /) -> list[MarketHistory]:
        """Parameters:

- `bucket_seconds`: An integer representing the segment size in seconds for market history data.
- `start`: A timestamp indicating the start of the query period.
- `end`: A timestamp indicating the end of the query period.

Examples:
- `bucket_seconds = 15`, `start = "2018-01-01T00:00:00"`, `end = "2018-01-02T00:00:00"` — Queries market history segmented by 15 seconds.
- `bucket_seconds = 60`, `start = "2018-01-01T00:00:00"`, `end = "2018-01-02T00:00:00"` — Queries market history segmented by one minute.
- `bucket_seconds = 300`, `start = "2018-01-01T00:00:00"`, `end = "2018-01-02T00:00:00"` — Queries market history segmented by five minutes.
- `bucket_seconds = 3600`, `start = "2018-01-01T00:00:00"`, `end = "2018-01-02T00:00:00"` — Queries market history segmented by one hour.
- `bucket_seconds = 86400`, `start = "2018-01-01T00:00:00"`, `end = "2018-01-02T00:00:00"` — Queries market history segmented by one day."""

    @endpoint_jsonrpc
    async def get_market_history_buckets(self, array_param: list[str], /) -> list[list]:
        ...

    @endpoint_jsonrpc
    async def get_next_scheduled_hardfork(self, array_param: list[str], /) -> CondenserGetNextScheduledHardforkResponse:
        ...

    @endpoint_jsonrpc
    async def get_open_orders(self, array_param: list[str], /) -> list[LimitOrderCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_ops_in_block(self, array_param: list[Union[int, bool]], /) -> list[OperationCondenserApi]:
        """Parameters:

- `block_num`: An integer representing the block number to query.
- `only_virtual`: A boolean indicating whether to query only virtual operations.

Examples:
- `block_num = 1`, `only_virtual = false` — Queries the operations in block #1.
- `block_num = 5443322`, `only_virtual = true` — Queries only the virtual operations in block #5,443,322."""

    @endpoint_jsonrpc
    async def get_order_book(self, array_param: list[int], /) -> CondenserGetOrderBookResponse:
        """Parameters:

- `limit`: An integer up to 500 specifying the maximum number of items to query in the order book.

Examples:
- `limit = 10` — Queries up to 10 items in the order book.
- `limit = 500` — Queries up to 500 items in the order book."""

    @endpoint_jsonrpc
    async def get_owner_history(self, array_param: list[str], /) -> list[OwnerAuthHistory]:
        """Parameters:

- `account`: A string representing the account name to query.

Example:
- `account = "hiveio"` — Queries the owner history for account named "hiveio"."""

    @endpoint_jsonrpc
    async def get_post_discussions_by_payout(self, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, tag: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_potential_signatures(self, array_param: list[CondenserGetPotentialSignature], /) -> CondenserGetPotentialSignaturesResponse:
        ...

    @endpoint_jsonrpc
    async def get_reblogged_by(self, author: str, permlink: str, /) -> list[list]:
        """Parameters:

- `author`: A string representing the author's username.
- `permlink`: A string representing the unique identifier of the content (permalink).

Examples:
- `author = "hiveio"`, `permlink = "firstpost"` — Queries reblogs for content with a slug @hiveio/firstpost.
- `author = "alice"`, `permlink = "a-post-by-alice"` — Queries reblogs for content with a slug @alice/a-post-by-alice."""

    @endpoint_jsonrpc
    async def get_recent_trades(self, array_param: list[int], /) -> list[TradeCondenserApi]:
        """Parameters:

- `limit`: An integer up to 1000 specifying the maximum number of latest trades to retrieve.

Examples:
- `limit = 10` — Queries up to 10 latest trades.
- `limit = 500` — Queries up to 500 latest trades."""

    @endpoint_jsonrpc
    async def get_recovery_request(self, array_param: list[str], /):
        """Parameters:

- `account`: A string representing the account name to query.

Example:
- `account = "hiveio"` — Queries the recovery requests for account named "hiveio"."""

    @endpoint_jsonrpc
    async def get_replies_by_last_update(self, start_author: str, start_permlink: Optional=None, limit: Optional=None, truncate_body: Optional=None, observer: Optional=None, /) -> list[PostCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_required_signatures(self, array_param: list[CondenserGetRequiredSignatures1, list[str]]], /) -> list[list]:
        """Parameters:

- `trx`: An object representing a transaction.
- `available_keys`: An array of strings listing the available keys related to the transaction."""

    @endpoint_jsonrpc
    async def get_reward_fund(self, array_param: list[str], /) -> CondenserGetRewardFundResponse:
        ...

    @endpoint_jsonrpc
    async def get_savings_withdraw_from(self, array_param: list[str], /) -> list[SavingsWithdrawalCondenserApi]:
        """Parameters:

- `account`: A string representing the account name to query.

Example:
- `account = "hiveio"` — Queries the savings withdrawal for account named "hiveio"."""

    @endpoint_jsonrpc
    async def get_savings_withdraw_to(self, array_param: list[str], /) -> list[SavingsWithdrawalCondenserApi]:
        """Parameters:

- `account`: A string representing the account name to query.

Example:
- `account = "hiveio"` — Queries the savings withdrawal for account named "hiveio"."""

    @endpoint_jsonrpc
    async def get_ticker(self, array_param: list[str], /) -> CondenserGetTickerResponse:
        ...

    @endpoint_jsonrpc
    async def get_trade_history(self, array_param: list[Union[str, int]], /) -> list[TradeCondenserApi]:
        """Parameters:

- `start`: A timestamp indicating the beginning of the query period.
- `end`: A timestamp indicating the end of the query period.
- `limit`: An integer up to 1000 specifying the maximum number of trades to retrieve.

Example:
- `start = "2018-01-01T00:00:00"`, `end = "2018-01-02T00:00:00"`, `limit = 10` — Queries up to 10 trades between January 1st, 2018 and January 2nd, 2018."""

    @endpoint_jsonrpc
    async def get_transaction(self, array_param: list[str], /) -> CondenserGetTransactionResponse:
        """Parameters:

- `trx_id`: A string representing the transaction ID to query.

Example:
- `trx_id = "6fde0190a97835ea6d9e651293e90c89911f933c"` — Queries for this exact transaction ID."""

    @endpoint_jsonrpc
    async def get_transaction_hex(self, array_param: list[CondenserGetTransactionHexItem], /) -> str:
        ...

    @endpoint_jsonrpc
    async def get_trending_tags(self, start_tag: Optional=None, limit: Optional=None, /) -> list[TrendingTag]:
        ...

    @endpoint_jsonrpc
    async def get_version(self, array_param: list[str], /) -> GetVersionResponse:
        ...

    @endpoint_jsonrpc
    async def get_vesting_delegations(self, array_param: list[Union[str, int, NoneType]], /) -> list[VestingDelegationCondenserApi]:
        """Parameters:

- `delegator_account`: A string representing the account that delegated vesting.
- `start_account`: A string indicating the account to start from (optional).
- `limit`: An integer up to 1000 specifying the maximum number of vesting delegations to retrieve.

Example:
- `delegator_account = "hiveio"`, `limit = 10` — Queries up to 10 vesting delegations by "hiveio"."""

    @endpoint_jsonrpc
    async def get_volume(self, array_param: list[str], /) -> CondenserGetVolumeResponse:
        ...

    @endpoint_jsonrpc
    async def get_withdraw_routes(self, array_param: list[str], /) -> list[WithdrawVestingRoutes]:
        """Parameters:

- `account`: A string representing the account name.
- `type`: A string indicating the type of withdraw routes to query, e.g., 'outgoing', 'incoming', or 'all'.

Examples:
- `account = "hiveio"`, `type = "outgoing"` — Queries outgoing withdraw routes by "hiveio".
- `account = "hiveio"`, `type = "incoming"` — Queries incoming withdraw routes by "hiveio".
- `account = "hiveio"`, `type = "all"` — Queries all withdraw routes by "hiveio"."""

    @endpoint_jsonrpc
    async def get_witness_by_account(self, array_param: list[str], /):
        """Parameters:

- `account`: A string representing the account name to query.

Example:
- `account = "hiveio"` — Queries the witness account of "hiveio" (or null if none exists)."""

    @endpoint_jsonrpc
    async def get_witness_count(self, array_param: list[str], /) -> int:
        ...

    @endpoint_jsonrpc
    async def get_witness_schedule(self, array_param: list[str], /) -> CondenserGetWitnessScheduleResponse:
        ...

    @endpoint_jsonrpc
    async def get_witnesses(self, array_param: list[list[int]], /) -> list[WitnessCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def get_witnesses_by_vote(self, array_param: list[Union[str, int, NoneType]], /) -> list[WitnessCondenserApi]:
        """Parameters:

- `start_name`: A string indicating the starting name for the query (optional).
- `limit`: An integer up to 1000 specifying the maximum number of witness votes to retrieve.

Examples:
- `start_name = null`, `limit = 21` — Queries top 21 witness votes.
- `start_name = "a"`, `limit = 1` — Queries top 1 witness votes starting with "a"."""

    @endpoint_jsonrpc
    async def is_known_transaction(self, array_param: list[str], /) -> bool:
        ...

    @endpoint_jsonrpc
    async def list_proposal_votes(self, array_param: list[Union[str, int, list, NoneType]], /) -> list[ProposalVoteCondenserApi]:
        """Parameters:

- `start`: An array that depends on the order parameter, e.g., ["voter_name"] for 'by_voter_proposal' or [proposal_id] for 'by_proposal_voter'.
- `limit`: An integer up to 1000 specifying the maximum number of results to retrieve.
- `order`: A string specifying the ordering criterion, which can be 'by_voter_proposal' or 'by_proposal_voter'.
- `order_direction`: A string indicating the direction of the order, which can be 'ascending' or 'descending'.
- `status`: A string representing the proposal status, which can be 'all', 'inactive', 'active', 'expired', or 'votable'.

Examples:
- `start = ["alice"]`, `limit = 10`, `order = "by_voter_proposal"`, `order_direction = "ascending"`, `status = "active"` — Lists 10 proposals with active status, ordered by voter, ascending.
- `start = [10]`, `limit = 1000`, `order = "by_proposal_voter"`, `order_direction = "ascending"`, `status = "votable"` — Lists 1000 votes on proposal 10, ordered by proposal.id, ascending."""

    @endpoint_jsonrpc
    async def list_proposals(self, array_param: list[Union[str, int, list, NoneType]], /) -> list[ProposalsCondenserApi]:
        """Parameters:

- `start`: An array that is determined by the order parameter, e.g., ["creator_name"] for 'by_creator', ["start_date"] for 'by_start_date', ["end_date"] for 'by_end_date', or [total_votes] for 'by_total_votes'.
- `limit`: An integer up to 1000 specifying the maximum number of results to retrieve.
- `order`: A string specifying the ordering criterion, which can be 'by_creator', 'by_start_date', 'by_end_date', or 'by_total_votes'.
- `order_direction`: A string indicating the direction of the order, which can be 'ascending' or 'descending'.
- `status`: A string representing the proposal status, which can be 'all', 'inactive', 'active', 'expired', or 'votable'."""

    @endpoint_jsonrpc
    async def list_rc_accounts(self, array_param: list[Union[str, int]], /) -> list[RcAccountCondenserApi]:
        ...

    @endpoint_jsonrpc
    async def list_rc_direct_delegations(self, array_param: list[Union[list, int]], /) -> list[RcAccountDelegation]:
        ...

    @endpoint_jsonrpc
    async def lookup_account_names(self, array_param: list[Union[list[str], bool]], /) -> list[AccountCondenserApi]:
        """Parameters:

- `accounts`: An array of strings representing account names.
- `delayed_votes_active`: A boolean indicating whether to filter for active delayed votes.

This parameter set allows querying for multiple accounts with an optional filter on the status of delayed votes."""

    @endpoint_jsonrpc
    async def lookup_accounts(self, array_param: list[Union[str, int]], /) -> list[list]:
        """Parameters:

- `lower_bound_name`: A string indicating the starting account name for the query.
- `limit`: An integer up to 1000 specifying the maximum number of accounts to retrieve.

Example:
- `lower_bound_name = "a"`, `limit = 10` — Queries up to 10 accounts that start with "a"."""

    @endpoint_jsonrpc
    async def lookup_witness_accounts(self, array_param: list[Union[str, int]], /) -> list[list]:
        """Parameters:

- `lower_bound_name`: A string indicating the starting account name for the query.
- `limit`: An integer up to 1000 specifying the maximum number of accounts to retrieve.

Example:
- `lower_bound_name = "a"`, `limit = 10` — Queries up to 10 accounts that start with "a"."""

    @endpoint_jsonrpc
    async def verify_authority(self, array_param: list[CondenserVerifyAuthorityItem], /) -> bool:
        ...

    def argument_serialization(self) -> int:
        return 1