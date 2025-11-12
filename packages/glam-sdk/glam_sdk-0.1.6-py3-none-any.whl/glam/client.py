import asyncio
import sys
from typing import Optional

from solana.rpc.api import Client as RpcClient
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey

from .protocol.accounts.stateAccount import StateAccount


class GlamClient:
    def __init__(self, connection: RpcClient, vault_state: Pubkey):
        self.connection = connection
        self.vault_state = vault_state
        self._async_client: Optional[AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._async_client = AsyncClient(self.connection._provider.endpoint_uri)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - automatically closes connection"""
        if self._async_client is not None:
            await self._async_client.close()
            self._async_client = None

    async def get_state_account(
        self, commitment: Optional[Commitment] = None
    ) -> Optional[StateAccount]:
        """Fetch account data from solana at self.vault_state and return a state model"""
        try:
            state_account = await StateAccount.fetch(
                conn=self._async_client, address=self.vault_state, commitment=commitment
            )

            return state_account

        except Exception as e:
            print(f"Error fetching state model: {e}")
            return None

    def get_vault_pda(self) -> Pubkey:
        """Get the PDA of the vault account"""
        from .protocol.program_id import GLAM_PROTOCOL_PROGRAM_ADDRESS

        seeds = [b"vault", bytes(self.vault_state)]

        pda, _bump = Pubkey.find_program_address(seeds, GLAM_PROTOCOL_PROGRAM_ADDRESS)
        return pda


async def main():
    # Get state pubkey from command line argument or use default
    if len(sys.argv) > 1:
        state_pubkey_str = sys.argv[1]
    else:
        sys.exit("Usage: python -m glam.client <vault_state>")

    try:
        state_pubkey = Pubkey.from_string(state_pubkey_str)
    except Exception as e:
        print(f"Error: Invalid pubkey '{state_pubkey_str}': {e}")
        print("Usage: python -m glam.client <vault_state>")
        return

    async with GlamClient(
        RpcClient("https://mainnet.helius-rpc.com/?api-key=4ddc4f7c-e67e-4e15-8604-7bd14f7d4d15"),
        state_pubkey,
    ) as client:
        state_account = await client.get_state_account()
        integration_acls = state_account.integrationAcls

        print(f"Vault PDA: {client.get_vault_pda()}")
        print(f"Found {len(integration_acls)} integration ACLs:")

        for i, integration_acl in enumerate(integration_acls):
            print(f"ACL {i + 1}: {integration_acl}")

        delegate_acls = state_account.delegateAcls
        print(f"Found {len(delegate_acls)} delegate ACLs:")

        for i, delegate_acl in enumerate(delegate_acls):
            print(f"ACL {i + 1}: {delegate_acl}")


if __name__ == "__main__":
    asyncio.run(main())
