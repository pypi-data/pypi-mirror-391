from transaction_status_api.transaction_status_api_description import FindTransactionResponse
from beekeepy._apis.abc.api import AbstractAsyncApi


class TransactionStatusApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def find_transaction(self, *, transaction_id: str, expiration: str) -> FindTransactionResponse:
        """Parameters:

        - `trx_id`: A string representing the transaction ID to query.
        - `expiration`: A timestamp indicating the expiration time of the transaction (optional).

        The result will contain one of the following status values:
        - `unknown`: Expiration time in future, transaction not included in block or mempool.
        - `within_mempool`: Transaction in mempool.
        - `within_reversible_block`: Transaction has been included in block, block not irreversible.
        - `within_irreversible_block`: Transaction has been included in block, block is irreversible.
        - `expired_reversible`: Transaction has expired, transaction is not irreversible (transaction could be in a fork).
        - `expired_irreversible`: Transaction has expired, transaction is irreversible (transaction cannot be in a fork).
        - `too_old`: Transaction is too old, I don’t know about it."""
