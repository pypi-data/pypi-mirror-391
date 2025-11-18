from database_api.database_api_description import FindAccountRecoveryRequestsResponse
from database_api.database_api_description import FindAccountsResponse
from database_api.database_api_description import FindChangeRecoveryAccountRequestsResponse
from database_api.database_api_description import FindCollateralizedConversionRequestsResponse
from database_api.database_api_description import FindCommentsResponse
from database_api.database_api_description import FindDeclineVotingRightsRequestsResponse
from database_api.database_api_description import FindEscrowsResponse
from database_api.database_api_description import FindHbdConversionRequestsResponse
from database_api.database_api_description import FindLimitOrdersResponse
from database_api.database_api_description import FindOwnerHistoriesResponse
from database_api.database_api_description import FindProposalsResponse
from database_api.database_api_description import FindRecurrentTransfersResponse
from database_api.database_api_description import FindSavingsWithdrawalsResponse
from database_api.database_api_description import FindVestingDelegationExpirationsResponse
from database_api.database_api_description import FindVestingDelegationsResponse
from database_api.database_api_description import FindVotesResponse
from database_api.database_api_description import FindWithdrawVestingRoutesResponse
from database_api.database_api_description import FindWitnessesResponse
from database_api.database_api_description import GetActiveWitnessesResponse
from database_api.database_api_description import GetCommentPendingPayoutsResponse
from database_api.database_api_description import GetConfigResponse
from database_api.database_api_description import GetCurrentPriceFeedResponse
from database_api.database_api_description import GetDynamicGlobalPropertiesResponse
from database_api.database_api_description import GetFeedHistoryResponse
from database_api.database_api_description import GetHardforkPropertiesResponse
from database_api.database_api_description import GetOrderBookResponse
from database_api.database_api_description import GetPotentialSignaturesResponse
from database_api.database_api_description import GetRewardFundsResponse
from database_api.database_api_description import GetTransactionHexResponse
from database_api.database_api_description import GetVersionResponse
from database_api.database_api_description import GetWitnessScheduleResponse
from database_api.database_api_description import IsKnownTransactionResponse
from database_api.database_api_description import ListAccountRecoveryRequestsResponse
from database_api.database_api_description import ListAccountsResponse
from database_api.database_api_description import ListChangeRecoveryAccountRequestsResponse
from database_api.database_api_description import ListCollateralizedConversionRequestsResponse
from database_api.database_api_description import ListDeclineVotingRightsRequestsResponse
from database_api.database_api_description import ListEscrowsResponse
from database_api.database_api_description import ListHbdConversionRequestsResponse
from database_api.database_api_description import ListLimitOrdersResponse
from database_api.database_api_description import ListOwnerHistoriesResponse
from database_api.database_api_description import ListProposalVotesResponse
from database_api.database_api_description import ListProposalsResponse
from database_api.database_api_description import ListSavingsWithdrawalsResponse
from database_api.database_api_description import ListVestingDelegationExpirationsResponse
from database_api.database_api_description import ListVestingDelegationsResponse
from database_api.database_api_description import ListVotesResponse
from database_api.database_api_description import ListWithdrawVestingRoutesResponse
from database_api.database_api_description import ListWitnessVotesResponse
from database_api.database_api_description import ListWitnessesResponse
from database_api.database_api_description import VerifyAccountAuthorityResponse
from database_api.database_api_description import VerifyAuthorityResponse
from database_api.database_api_description import VerifySignaturesResponse
from typing import Optional
from database_api.database_api_description import Base
from database_api.database_api_description import Quote
from database_api.database_api_description import Trx1
from database_api.database_api_description import Trx2
from database_api.database_api_description import Trx3
from typing import Union
from database_api.database_api_description import Trx4
from beekeepy._apis.abc.api import AbstractAsyncApi


class DatabaseApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def find_account_recovery_requests(self, *, accounts: list) -> FindAccountRecoveryRequestsResponse:
        """Parameters:

        - `accounts`: A string representing the account name to query. Example:
          - `"hiveio"` — queries the recovery requests for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_accounts(self, *, accounts: list, delayed_votes_active: Optional = None) -> FindAccountsResponse:
        """Parameters:

        - `accounts`: An array of strings representing account names to query. Example:
          - `["hiveio"]` — queries for the account named "hiveio".
          - `["hiveio", "alice"]` — queries for accounts "hiveio" and "alice".

        - `delayed_votes_active`: A boolean indicating whether to include only accounts with active delayed votes. Defaults to false if not specified.
        """

    @endpoint_jsonrpc
    async def find_change_recovery_account_requests(
        self, *, accounts: list
    ) -> FindChangeRecoveryAccountRequestsResponse:
        """Parameters:

        - `accounts`: An array of strings representing account names to query. Example:
          - `["hiveio"]` — queries the recovery requests for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_collateralized_conversion_requests(
        self, *, account: str
    ) -> FindCollateralizedConversionRequestsResponse:
        """Parameters:

        - `account`: Anaccount name to query. Example:
          - `"hiveio"` — queries the recovery requests for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_comments(self, *, comments: Optional = None) -> FindCommentsResponse:
        """Parameters:

        - `comments`: A string array of pairs author/permlink
        """

    @endpoint_jsonrpc
    async def find_decline_voting_rights_requests(self, *, accounts: list) -> FindDeclineVotingRightsRequestsResponse:
        """Parameters:

        - `accounts`: An array of strings representing account names to query. Example:
          - `["hiveio"]` — queries the decline votings rights for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_escrows(self, *, from_: str) -> FindEscrowsResponse:
        """Parameters:

        - `from`: string representing account name to query. Example:
          - `"hiveio"` — queries the escrows for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_hbd_conversion_requests(self, *, account: str) -> FindHbdConversionRequestsResponse:
        """Parameters:

        - `account`: A string representing the account name to query for conversion requests. Examples:
          - `"hiveio"` — queries a conversion request for the account named "hiveio".
          - `"alice"` — queries a conversion request for the account named "alice".
        """

    @endpoint_jsonrpc
    async def find_limit_orders(self, *, account: str) -> FindLimitOrdersResponse:
        """Parameters:

        - `account`: string representing account name to query. Example:
          - `"hiveio"` — queries the limit orders for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_owner_histories(self, *, owner: str) -> FindOwnerHistoriesResponse:
        """Parameters:

        - `owner`: A string representing the account name to query for owner history. Examples:
          - `"hiveio"` — queries the owner history for the account named "hiveio".
          - `"alice"` — queries the owner history for the account named "alice".
        """

    @endpoint_jsonrpc
    async def find_proposals(self, *, proposal_ids: list) -> FindProposalsResponse:
        """Parameters:

        - `proposal_ids`: An array of int representing ids of proposals. Examples:
          - `[0]` — queries the id `0` proposal.
          - `[0,1,2]` — queries proposals with id `0,1,2`.
        """

    @endpoint_jsonrpc
    async def find_recurrent_transfers(self, *, from_: str) -> FindRecurrentTransfersResponse:
        """Parameters:

        - `from`: string representing account name to query. Example:
          - `"hiveio"` — queries the recurrent transfers for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_savings_withdrawals(self, *, account: str) -> FindSavingsWithdrawalsResponse:
        """Parameters:

        - `account`: A string representing the account name to query for savings withdrawals. Example:
          - `"hiveio"` — queries the savings withdrawals for the account named "hiveio".
        """

    @endpoint_jsonrpc
    async def find_vesting_delegation_expirations(self, *, account: str) -> FindVestingDelegationExpirationsResponse:
        """Returns the expiring vesting delegations for an account. Parameters:

        - `account`: A string representing the account name to query. Examples:
          - `"hiveio"` — queries for expiring vesting delegations for "hiveio".
          - `"alice"` — queries for expiring vesting delegations for "alice".
        """

    @endpoint_jsonrpc
    async def find_vesting_delegations(self, *, account: str) -> FindVestingDelegationsResponse:
        """Parameters:

        - `account`: A string representing the account name to query. Examples:
          - `"hiveio"` — queries for vesting details for "hiveio".
          - `"alice"` — queries for vesting details for "alice".
        """

    @endpoint_jsonrpc
    async def find_votes(self, *, author: str, permlink: str) -> FindVotesResponse:
        """Required (non-empty) parameters: author, permlink.

        - `author`: A string representing the author of the content. Examples:
          - `"hiveio"` — queries votes for content authored by "hiveio".
          - `"alice"` — queries votes for content authored by "alice".

        - `permlink`: A string representing the permalink of the content. Examples:
          - `"announcing-the-launch-of-hive-blockchain"` — for the post @hiveio/announcing-the-launch-of-hive-blockchain.
          - `"a-post-by-alice"` — for the post @alice/a-post-by-alice.
        """

    @endpoint_jsonrpc
    async def find_withdraw_vesting_routes(self, *, account: str, order: str) -> FindWithdrawVestingRoutesResponse:
        """Required (non-empty) parameters: author, permlink.

        - `account`: Anaccount name to query.
        - `order`: A string defining the sorting order.
        """

    @endpoint_jsonrpc
    async def find_witnesses(self, *, owners: list) -> FindWitnessesResponse:
        """Parameters:

        - `owners`: An array of strings representing account names to query. Example:
          - `["initminer"]` — queries for the account named "initminer".
          - `["initminer", "blocktrades"]` — queries for accounts "initminer" and "blocktrades".
        """

    @endpoint_jsonrpc
    async def get_active_witnesses(self) -> GetActiveWitnessesResponse: ...

    @endpoint_jsonrpc
    async def get_comment_pending_payouts(self, *, comments: list) -> GetCommentPendingPayoutsResponse:
        """Required (non-empty) parameters: author, permlink.

        - `author`: A string representing the author of the content. Examples:
          - `"hiveio"` — queries votes for content authored by "hiveio".
          - `"alice"` — queries votes for content authored by "alice".

        - `permlink`: A string representing the permalink of the content. Examples:
          - `"announcing-the-launch-of-hive-blockchain"` — for the post @hiveio/announcing-the-launch-of-hive-blockchain.
          - `"a-post-by-alice"` — for the post @alice/a-post-by-alice.
        """

    @endpoint_jsonrpc
    async def get_config(self) -> GetConfigResponse: ...

    @endpoint_jsonrpc
    async def get_current_price_feed(self) -> GetCurrentPriceFeedResponse: ...

    @endpoint_jsonrpc
    async def get_dynamic_global_properties(self) -> GetDynamicGlobalPropertiesResponse:
        """Dynamic Global Properties represents a set of values that are calculated during normal chain operations and reflect the current values of global blockchain properties."""

    @endpoint_jsonrpc
    async def get_feed_history(self) -> GetFeedHistoryResponse: ...

    @endpoint_jsonrpc
    async def get_hardfork_properties(self) -> GetHardforkPropertiesResponse: ...

    @endpoint_jsonrpc
    async def get_order_book(self, *, base: Base, quote: Quote, limit: int) -> GetOrderBookResponse: ...

    @endpoint_jsonrpc
    async def get_potential_signatures(self, *, trx: Trx1) -> GetPotentialSignaturesResponse:
        """This call can be used by wallets to filter their set of public keys to just the relevant subset prior to calling get_required_signatures to get the minimum subset."""

    @endpoint_jsonrpc
    async def get_required_signatures(self, *, trx: Trx2) -> GetPotentialSignaturesResponse:
        """This API will take a partially signed transaction and a set of public keys that the owner has the ability to sign for and return the minimal subset of public keys that should add signatures to the transaction."""

    @endpoint_jsonrpc
    async def get_reward_funds(self) -> GetRewardFundsResponse: ...

    @endpoint_jsonrpc
    async def get_transaction_hex(self, *, trx: Trx3) -> GetTransactionHexResponse: ...

    @endpoint_jsonrpc
    async def get_version(self) -> GetVersionResponse:
        """Also returns the boot time version of the chain id (may be different from compile time value only when looking at a testnet)"""

    @endpoint_jsonrpc
    async def get_witness_schedule(self) -> GetWitnessScheduleResponse: ...

    @endpoint_jsonrpc
    async def is_known_transaction(self, *, id: str) -> IsKnownTransactionResponse:
        """If this method is called with a VERY old transaction we will return false, use account_history_api.get_transaction."""

    @endpoint_jsonrpc
    async def list_account_recovery_requests(
        self, *, start: dict, limit: int, order: str
    ) -> ListAccountRecoveryRequestsResponse:
        """Parameters:

        - `start`: A string indicating the starting point for the query (optional).

        - `limit`: An integer specifying the maximum number of recovery requests to return; up to 1000.

        - `order`: A string determining how results are ordered. Possible values:
          - `by_account` — order by account name
          - `by_expiration` — order by expiration date

        Examples:

        - `start = "hiveio"`, `limit = 10`, `order = "by_account"` — queries recovery requests for account "hiveio", ordered by account name.

        - `start = ["1960-01-01T00:00:00"]`, `limit = 10`, `order = "by_expiration"` — queries recovery requests from the specified date, ordered by expiration.
        """

    @endpoint_jsonrpc
    async def list_accounts(
        self, *, start: dict, limit: int, order: str, delayed_votes_active: Optional = None
    ) -> ListAccountsResponse:
        """Parameters:

        - `start`: An object indicating the starting point for listing accounts.

        - `limit`: An integer specifying the maximum number of accounts to return; default is 1000.

        - `order`: A string defining the sorting order. Possible values:
          - `by_name` — order by account name
          - `by_proxy` — order by proxy
          - `by_next_vesting_withdrawal` — order by next vesting withdrawal

        - `delayed_votes_active`: A boolean indicating whether to filter for active delayed votes. Defaults to true (optional).
        """

    @endpoint_jsonrpc
    async def list_change_recovery_account_requests(
        self, *, start: dict, limit: int, order: str
    ) -> ListChangeRecoveryAccountRequestsResponse:
        """Parameters:

        - `start`: An object whose structure depends on the `order` parameter.
          - If `order` is `by_account`, `start` is a string representing the account name.
          - If `order` is `by_effective_date`, `start` is an array with two values: a timestamp and an account string.

        - `limit`: An integer specifying the maximum number of requests to return; up to 1000.

        - `order`: A string indicating the sorting method. Possible values:
          - `by_account` — sort by account; `start` is a string of account name.
          - `by_effective_date` — sort by effective date; `start` is an array: [timestamp, account].

        Examples:

        - `start = ""`, `limit = 10`, `order = "by_account"` — queries the first 10 requests sorted by account.

        - `start = ["1960-01-01T00:00:00", ""]`, `limit = 10`, `order = "by_effective_date"` — queries the first 10 requests sorted by effective date.
        """

    @endpoint_jsonrpc
    async def list_collateralized_conversion_requests(
        self, *, start: dict, limit: int, order: str
    ) -> ListCollateralizedConversionRequestsResponse: ...

    @endpoint_jsonrpc
    async def list_decline_voting_rights_requests(
        self, *, start: dict, limit: int, order: str
    ) -> ListDeclineVotingRightsRequestsResponse:
        """Parameters:

        - `start`: An object whose structure depends on the `order` parameter.
          - If `order` is `by_account`, `start` is a string representing the account name.
          - If `order` is `by_effective_date`, `start` is an array with two values: a timestamp and an account string.

        - `limit`: An integer specifying the maximum number of requests to return; up to 1000.

        - `order`: A string indicating the sorting method. Possible values:
          - `by_account` — sort by account; `start` is a string of account name.
          - `by_effective_date` — sort by effective date; `start` is an array: [timestamp, account].

        Examples:

        - `start = ""`, `limit = 10`, `order = "by_account"` — queries the first 10 requests sorted by account.

        - `start = ["1960-01-01T00:00:00", ""]`, `limit = 10`, `order = "by_effective_date"` — queries the first 10 requests sorted by effective date.
        """

    @endpoint_jsonrpc
    async def list_escrows(self, *, start: dict, limit: int, order: str) -> ListEscrowsResponse:
        """Parameters:

        - `start`: An array whose structure depends on the `order` parameter.
          - For `by_from_id`: `start` is an array of two values: `[account, escrow_id]`.
          - For `by_ratification_deadline`: `start` is an array of three values: `[is_approved, timestamp, escrow_id]`.

        - `limit`: An integer specifying the maximum number of requests to return; up to 1000.

        - `order`: A string indicating the sorting criteria. Possible values:
          - `by_from_id` — sort by ID.
          - `by_ratification_deadline` — sort by ratification deadline.

        Examples:

        - `start = ["alice", 99]`, `limit = 10`, `order = "by_from_id"` — queries the first 10 requests, sorted by ID.

        - `start = [true, "1960-01-01T00:00:00", 99]`, `limit = 10`, `order = "by_ratification_deadline"` — queries the first 10 requests, sorted by ratification deadline.
        """

    @endpoint_jsonrpc
    async def list_hbd_conversion_requests(
        self, *, start: dict, limit: int, order: str
    ) -> ListHbdConversionRequestsResponse:
        """Parameters:

        - `start`: An array whose structure depends on the `order` parameter.
          - For `by_account`: `start` is an array of two values: `[account, request_id]`.
          - For `by_conversion_date`: `start` is an array of two values: `[timestamp, request_id]`.

        - `limit`: An integer specifying the maximum number of results to return; up to 1000.

        - `order`: A string indicating the sorting criteria. Possible values:
          - `by_account` — order by account name.
          - `by_conversion_date` — order by conversion date.

        Examples:

        - `start = ["hiveio", 0]`, `limit = 10`, `order = "by_account"` — queries a conversion request for "hiveio", limited to 10 results, ordered by account name.

        - `start = ["2018-12-07T16:54:03", 0]`, `limit = 10`, `order = "by_conversion_date"` — queries a conversion request from the specified date, limited to 10 results, ordered by conversion date.
        """

    @endpoint_jsonrpc
    async def list_limit_orders(self, *, start: dict, limit: int, order: str) -> ListLimitOrdersResponse:
        """Parameters:

        - `start`: An array whose structure depends on the `order` parameter.
          - For `by_price`: `start` is an array of two values: `[price, order_type]`.
          - For `by_account`: `start` is an array of two values: `[account, order_id]`.

        - `limit`: An integer specifying the maximum number of results to return; up to 1000.

        - `order`: A string indicating the sorting criteria. Possible values:
          - `by_price` — order by price.
          - `by_account` — order by account.

        Examples:

        - `start = [{"base": {"amount": "85405", "precision": 3, "nai": "@@000000021"}, "quote": {"amount": "17192", "precision": 3, "nai": "@@000000013"}}, 0]`, `limit = 10`, `order = "by_price"` — queries the first 10 requests, sorted by price.

        - `start = ["alice", 0]`, `limit = 10`, `order = "by_account"` — queries the first 10 requests, sorted by account.
        """

    @endpoint_jsonrpc
    async def list_owner_histories(self, *, start: dict, limit: int) -> ListOwnerHistoriesResponse:
        """Parameters:

        - `start`: An array of two values.
          - Example: `["hiveio", "1970-01-01T00:00:00"]` — starts from account "hiveio" on the date "1970-01-01T00:00:00".
          - Example: `["alice", "1970-01-01T00:00:00"]` — starts from account "alice" on the same date.

        - `limit`: An integer specifying the maximum number of results to return; e.g., 10.
        """

    @endpoint_jsonrpc
    async def list_proposal_votes(
        self, *, start: dict, limit: int, order: str, order_direction: str, status: str
    ) -> ListProposalVotesResponse:
        """Parameters:

        - `start`: An array whose content depends on the `order` parameter.
          - If `order` is `by_voter_proposal`: `start` is an array with one element: voter account name string (e.g., `["alice"]`).
          - If `order` is `by_proposal_voter`: `start` is an array with one element: proposal id (integer) (e.g., `[10]`).

        - `limit`: An integer up to 1000, specifying the maximum number of results to return.

        - `order`: A string indicating the sorting order. Possible values:
          - `by_voter_proposal` — order by voter for each proposal.
          - `by_proposal_voter` — order by proposal id.

        - `order_direction`: A string determining the sort direction:
          - `ascending`
          - `descending`

        - `status`: A string filter for proposal status:
          - `all`
          - `inactive`
          - `active`
          - `expired`
          - `votable`

        Examples:

        - `start = ["alice"]`, `limit = 10`, `order = "by_voter_proposal"`, `order_direction = "ascending"`, `status = "active"` — list 10 proposals with active status, ordered by voter ascending.

        - `start = [10]`, `limit = 1000`, `order = "by_proposal_voter"`, `order_direction = "ascending"`, `status = "votable"` — list 1000 votes on proposal 10, ordered by proposal id ascending.
        """

    @endpoint_jsonrpc
    async def list_proposals(
        self, *, start: dict, limit: int, order: str, order_direction: str, status: str, last_id: Union = None
    ) -> ListProposalsResponse:
        """Parameters:

        - `start`: An array whose content depends on the `order` parameter.
          - For `by_creator`: `start` is an array with one element: creator account name string (e.g., `[""]`).
          - For `by_start_date`: `start` is an array with one element: start date string (e.g., `["2019-08-07T16:54:03"]`).
          - For `by_end_date`: `start` is an array with one element: end date string.
          - For `by_total_votes`: `start` is an array with one element: total votes (integer).

        - `limit`: An integer up to 1000, specifying the maximum number of proposals to return.

        - `order`: A string indicating the ordering criterion. Possible values:
          - `by_creator` — order by proposal creator.
          - `by_start_date` — order by proposal start date.
          - `by_end_date` — order by proposal end date.
          - `by_total_votes` — order by total votes.

        - `order_direction`: A string, either `ascending` or `descending`.

        - `status`: A string filter for proposal status:
          - `all`
          - `inactive`
          - `active`
          - `expired`
          - `votable`

        - `last_id` (optional): The ID of the last object from the previous page, used to paginate the next set of results.

        Examples:

        - `start = [""]`, `limit = 10`, `order = "by_creator"`, `order_direction = "ascending"`, `status = "active"` — list 10 active proposals ordered by creator.

        - `start = ["2019-08-07T16:54:03"]`, `limit = 1000`, `order = "by_start_date"`, `order_direction = "ascending"`, `status = "inactive"` — list 1000 proposals starting from the specified date, ordered by start date.

        - `start = ["a"]`, `limit = 1`, `order = "by_creator"`, `order_direction = "ascending"`, `status = "expired"` — list 1 expired proposal with creator starting with "a".

        - `start = ["alice"]`, `limit = 10`, `order = "by_creator"`, `order_direction = "ascending"`, `status = "all"` — list 10 proposals with any status, ordered by creator.

        - `start = [10]`, `limit = 1000`, `order = "by_total_votes"`, `order_direction = "ascending"`, `status = "votable"` — list 1000 votable proposals with at least 10 votes, ordered by total votes.
        """

    @endpoint_jsonrpc
    async def list_savings_withdrawals(self, *, start: dict, limit: int, order: str) -> ListSavingsWithdrawalsResponse:
        """Parameters:

        - `start`: An object whose structure depends on the `order` parameter.
          - For `by_from_id`: `start` is an array with two values: `[account, request_id]`.
          - For `by_complete_from_id`: `start` is an array with three values: `[timestamp, account, request_id]`.
          - For `by_to_complete`: `start` is an array with three values: `[account, timestamp, order_id]`.

        - `limit`: An integer up to 1000, specifying the maximum number of results to return.

        - `order`: A string indicating the sorting criteria. Possible values:
          - `by_from_id` — order by request ID.
          - `by_complete_from_id` — order by completed request ID.
          - `by_to_complete` — order by completed request.

        Examples:

        - `start = [0]`, `limit = 10`, `order = "by_from_id"` — queries savings withdrawal by request ID, limited to 10 results.

        - `start = ["2018-12-07T16:54:03", "hiveio", 0]`, `limit = 10`, `order = "by_complete_from_id"` — queries completed requests by ID, starting from specified timestamp and account.

        - `start = ["", "1970-01-01T00:00:00", 0]`, `limit = 10`, `order = "by_to_complete"` — queries completed savings withdrawals starting from the specified account and date.
        """

    @endpoint_jsonrpc
    async def list_vesting_delegation_expirations(
        self, *, start: dict, limit: int, order: str
    ) -> ListVestingDelegationExpirationsResponse:
        """Parameters:

        - `start`: An array whose structure depends on the `order` parameter.
          - For `by_expiration`: `start` is an array with two values: `[timestamp, expiration_id]`.
          - For `by_account_expiration`: `start` is an array with three values: `[account, timestamp, expiration_id]`.

        - `limit`: An integer up to 1000; specifies the maximum number of results to return.

        - `order`: A string indicating the sorting criteria. Possible values:
          - `by_expiration` — order by expiration.
          - `by_account_expiration` — order by account expiration.

        Examples:

        - `start = ["1970-01-01T00:00:00", 0]`, `limit = 10`, `order = "by_expiration"` — queries delegations, limited to 10, ordered by expiration.

        - `start = ["alice", "1970-01-01T00:00:00", 0]`, `limit = 10`, `order = "by_account_expiration"` — queries delegations from this date, limited to 10, ordered by account expiration.
        """

    @endpoint_jsonrpc
    async def list_vesting_delegations(self, *, start: dict, limit: int, order: str) -> ListVestingDelegationsResponse:
        """Parameters:

        - `start`: An array with two values: `[delegator, delegatee]`.
          - Example: `["", ""]` — starts from the beginning for delegations between any delegator and delegatee.

        - `limit`: An integer up to 1000, specifying the maximum number of results to return.

        - `order`: A string with value `"by_delegation"`, indicating results are ordered by delegation.

        Example:

        - `start = ["", ""]`, `limit = 10`, `order = "by_delegation"` — queries delegations, limited to 10 results, ordered by delegation.
        """

    @endpoint_jsonrpc
    async def list_votes(self, *, start: dict, limit: int, order: str) -> ListVotesResponse:
        """Parameters:

        - `start`: An array whose structure depends on the `order` parameter.
          - For `by_comment_voter`: `start` can contain three optional values: `[author, permlink, voter]`. If one is blank, then all three must be blank.
          - For `by_voter_comment`: `start` can contain three optional values: `[voter, author, permlink]`. If one is blank, then all three must be blank.

        - `limit`: An integer up to 1000, specifying the maximum number of results to return.

        - `order`: A string indicating the sorting method. Possible values:
          - `by_comment_voter` — order by comment voter.
          - `by_voter_comment` — order by voter comment.

        Examples:

        - `start = ["", "", ""]`, `limit = 10`, `order = "by_comment_voter"` — queries the first 10 votes, sorted by comment voter.

        - `start = ["", "", ""]`, `limit = 10`, `order = "by_voter_comment"` — queries the first 10 votes, sorted by voter comment.

        - `start = ["xeroc", "vanteem-config", ""]`, `limit = 10`, `order = "by_comment_voter"` — queries next 10 votes starting from the post @xeroc/vanteem-config, sorted by comment voter.

        - `start = ["alice", "xeroc", "vanteem-config"]`, `limit = 10`, `order = "by_voter_comment"` — queries next 10 votes starting at Alice on the post @xeroc/vanteem-config, sorted by voter comment.
        """

    @endpoint_jsonrpc
    async def list_withdraw_vesting_routes(
        self, *, start: dict, limit: int, order: str
    ) -> ListWithdrawVestingRoutesResponse:
        """Parameters:

        - `start`: An array whose structure depends on the `order` parameter.
          - For `by_withdraw_route`: `start` is an array of two values: `[from_account, to_account]`.
          - For `by_destination`: `start` is an array of two values: `[to_account, route_id]`.

        - `limit`: An integer up to 1000, specifying the maximum number of results to return.

        - `order`: A string indicating the sorting criteria. Possible values:
          - `by_withdraw_route` — order by withdraw route.
          - `by_destination` — order by destination.

        Examples:

        - `start = ["temp", ""]`, `limit = 10`, `order = "by_withdraw_route"` — queries the first 10 withdraw routes, sorted by withdraw route.

        - `start = ["", 0]`, `limit = 10`, `order = "by_destination"` — queries the first 10 routes, sorted by destination.
        """

    @endpoint_jsonrpc
    async def list_witness_votes(self, *, start: dict, limit: int, order: str) -> ListWitnessVotesResponse:
        """Parameters:

        - `start`: An array whose structure depends on the `order` parameter.
          - For `by_account_witness`: `start` is an array of two values: `[account, witness]`.
          - For `by_witness_account`: `start` is an array of two values: `[witness, account]`.

        - `limit`: An integer up to 1000, specifying the maximum number of results to return.

        - `order`: A string indicating the sorting criteria. Possible values:
          - `by_account_witness` — order by account witness.
          - `by_witness_account` — order by witness account.

        Examples:

        - `start = ["", ""]`, `limit = 10`, `order = "by_account_witness"` — queries first 10 votes, sorted by account witness.

        - `start = ["", ""]`, `limit = 10`, `order = "by_witness_account"` — queries first 10 votes, sorted by witness account.
        """

    @endpoint_jsonrpc
    async def list_witnesses(self, *, start: dict, limit: int, order: str) -> ListWitnessesResponse:
        """Parameters:

        - `start`: An object whose structure depends on the `order` parameter.
          - For `by_name`: `start` is an empty string or omitted.
          - For `by_vote_name`: `start` is an array of two values: `[votes, account]`.
          - For `by_schedule_time`: `start` is an array of two values: `[virtual_scheduled_time, account]`.

        - `limit`: An integer up to 1000, specifying the maximum number of witnesses to return.

        - `order`: A string indicating the sorting criterion. Possible values:
          - `by_name` — order by account name.
          - `by_vote_name` — order by vote count and name.
          - `by_schedule_time` — order by schedule time.

        Examples:

        - `start = ""`, `limit = 10`, `order = "by_name"` — queries first 10 witnesses, sorted by account name.

        - `start = [0, ""]`, `limit = 10`, `order = "by_vote_name"` — queries first 10 witnesses, sorted by votes.

        - `start = ["473718186844702107410533306", "alice"]`, `limit = 10`, `order = "by_schedule_time"` — queries first 10 witnesses, sorted by schedule.
        """

    @endpoint_jsonrpc
    async def verify_account_authority(self, *, account: str, signers: list) -> VerifyAccountAuthorityResponse: ...

    @endpoint_jsonrpc
    async def verify_authority(self, *, trx: Trx4, pack: str) -> VerifyAuthorityResponse:
        """Returns true if the transaction has all of the required signatures, otherwise throws an exception."""

    @endpoint_jsonrpc
    async def verify_signatures(
        self,
        *,
        hash: str,
        signatures: list,
        required_owner: list,
        required_active: list,
        required_posting: list,
        required_other: list,
    ) -> VerifySignaturesResponse:
        """This method validates if transaction was signed by person listed in required_owner, required_active or required_posting parameter.
        Hash is a mix of chain_id and transaction data.
        """
