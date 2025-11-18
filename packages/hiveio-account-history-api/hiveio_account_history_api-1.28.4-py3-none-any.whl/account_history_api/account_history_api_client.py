from account_history_api.account_history_api_description import EnumVirtualOpsResponse
from account_history_api.account_history_api_description import GetAccountHistoryResponse
from account_history_api.account_history_api_description import GetOpsInBlockResponse
from account_history_api.account_history_api_description import GetTransactionResponse
from typing import Optional
from typing import Union
from beekeepy._apis.abc.api import AbstractAsyncApi


class AccountHistoryApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def enum_virtual_ops(
        self,
        *,
        block_range_begin: int,
        block_range_end: int,
        include_reversible: Optional = None,
        group_by_block: Optional = None,
        operation_begin: Union = None,
        limit: Optional = None,
        filter: Union = None,
    ) -> EnumVirtualOpsResponse:
        """Parameters:

        - `block_range_begin`: An integer representing the starting block number (inclusive) for the search.

        - `block_range_end`: An integer representing the last block number (exclusive) for the search.

        - `include_reversible`: A boolean (optional). If set to true, operations from reversible blocks will be included if `block_num` points to such a block.

        - `group_by_block`: A boolean (optional). Determines whether to group results by block.

        - `operation_begin`: An integer (optional). The starting virtual operation in the given block (inclusive).

        - `limit`: An integer (optional). Specifies the maximum number of operations to retrieve.

        - `filter`: An integer (optional). A bitwise filter that determines which operations to match. Use the following values for filtering:
          - `fill_convert_request_operation` = 0x000001
          - `author_reward_operation` = 0x000002
          - `curation_reward_operation` = 0x000004
          - `comment_reward_operation` = 0x000008
          - `liquidity_reward_operation` = 0x000010
          - `interest_operation` = 0x000020
          - `fill_vesting_withdraw_operation` = 0x000040
          - `fill_order_operation` = 0x000080
          - `shutdown_witness_operation` = 0x000100
          - `fill_transfer_from_savings_operation` = 0x000200
          - `hardfork_operation` = 0x000400
          - `comment_payout_update_operation` = 0x000800
          - `return_vesting_delegation_operation` = 0x001000
          - `comment_benefactor_reward_operation` = 0x002000
          - `producer_reward_operation` = 0x004000
          - `clear_null_account_balance_operation` = 0x008000
          - `proposal_pay_operation` = 0x010000
          - `sps_fund_operation` = 0x020000
          - `hardfork_hive_operation` = 0x040000
          - `hardfork_hive_restore_operation` = 0x080000
          - `delayed_voting_operation` = 0x100000
          - `consolidate_treasury_balance_operation` = 0x200000
          - `effective_comment_vote_operation` = 0x400000
          - `ineffective_delete_comment_operation` = 0x800000
          - `sps_convert_operation` = 0x1000000
          - `dhf_funding_operation` = 0x0020000
          - `dhf_conversion_operation` = 0x1000000
          - `expired_account_notification_operation` = 0x2000000
          - `changed_recovery_account_operation` = 0x4000000
          - `transfer_to_vesting_completed_operation` = 0x8000000
          - `pow_reward_operation` = 0x10000000
          - `vesting_shares_split_operation` = 0x20000000
          - `account_created_operation` = 0x40000000
          - `fill_collateralized_convert_request_operation` = 0x80000000
          - `system_warning_operation` = 0x100000000
          - `fill_recurrent_transfer_operation` = 0x200000000
          - `failed_recurrent_transfer_operation` = 0x400000000
          - `limit_order_cancelled_operation` = 0x800000000
          - `producer_missed_operation` = 0x1000000000
          - `proposal_fee_operation` = 0x2000000000
          - `collateralized_convert_immediate_conversion_operation` = 0x4000000000
          - `escrow_approved_operation` = 0x8000000000
          - `escrow_rejected_operation` = 0x10000000000
          - `proxy_cleared_operation` = 0x20000000000
        """

    @endpoint_jsonrpc
    async def get_account_history(
        self,
        *,
        account: str,
        start: int,
        limit: int,
        include_reversible: Optional = None,
        operation_filter_low: Optional = None,
        operation_filter_high: Optional = None,
    ) -> GetAccountHistoryResponse:
        """Parameters:

        - `account`: A string representing the account name to query.

        - `start`: An integer indicating the starting point for the query. Use `-1` for reverse history or any positive number for a specific starting point.

        - `limit`: An integer up to 1000 specifying the maximum number of results to return.

        - `include_reversible`: A boolean (optional) that, if set to true, includes operations from reversible blocks.

        - `operation_filter_low`: An integer (optional) used to filter the first 64 operations based on a bitwise mask.

        - `operation_filter_high`: An integer (optional) used to filter higher-numbered operations with a 128-bit bitmask composed of {operation_filter_high, operation_filter_low}.

        If `operation_filter_low` or `operation_filter_high` are set, the response will only include operations matching the bitwise filter.

        Examples:

        - **`account = "hiveio"`**, **`start = 1000`**, **`limit = 1000`**: Queries the latest items in history for the account "hiveio", with up to 1,000 results.

        - **`account = "alice"`**, **`start = -1`**, **`limit = 1000`**: Queries the oldest items in history for the account "alice", with up to 1,000 results.

        - **`account = "bob"`**, **`start = -1`**, **`limit = 1000`**, **`include_reversible = true`**, **`operation_filter_low = 1`**: Queries only vote operations for "bob" from the oldest item, up to 1,000 results.

        - **`account = "charlie"`**, **`start = -1`**, **`limit = 1000`**, **`include_reversible = true`**, **`operation_filter_low = 262144`**: Queries only custom JSON operations for "charlie" from the oldest item, up to 1,000 results.

        - **`account = "emma"`**, **`start = -1`**, **`limit = 1000`**, **`include_reversible = true`**, **`operation_filter_low = 0`**, **`operation_filter_high = 1`**: Queries only proposal payments to "emma" from the oldest item, up to 1,000 results.
        """

    @endpoint_jsonrpc
    async def get_ops_in_block(
        self, *, block_num: int, only_virtual: bool, include_reversible: Optional = None
    ) -> GetOpsInBlockResponse:
        """Parameter:

        - `block_num`: An integer representing the specific block number to retrieve operations for.

        - `only_virtual`: A boolean indicating whether to include only virtual operations.

        - `include_reversible`: A boolean (optional) that, if set to true, includes operations from reversible blocks if `block_num` points to such a block.
        """

    @endpoint_jsonrpc
    async def get_transaction(self, *, id: str, include_reversible: Optional = None) -> GetTransactionResponse:
        """Parameters:

        - `id`: A string representing the transaction ID (`trx_id`) of the expected transaction.

        - `include_reversible`: A boolean (optional) that, if set to true, includes operations from reversible blocks if the transaction's block number points to such a block.
        """
