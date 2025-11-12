"""Tests for GlamClient class."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from solana.rpc.api import Client as RpcClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey

from glam.client import GlamClient
from glam.protocol.accounts.stateAccount import StateAccount


class TestGlamClient:
    """Test suite for GlamClient class."""

    @pytest.fixture
    def mock_rpc_client(self):
        """Create a mock RPC client."""
        client = MagicMock()
        client._provider.endpoint_uri = "https://api.mainnet-beta.solana.com"
        return client

    @pytest.fixture
    def test_pubkey(self):
        """Create a test pubkey."""
        return Pubkey.from_string("AK2c89yrVsPpFUcb9AwqhYLU1xE7atjSvmfBNzyZ75Qh")

    @pytest.fixture
    def glam_client(self, mock_rpc_client, test_pubkey):
        """Create a GlamClient instance for testing."""
        return GlamClient(mock_rpc_client, test_pubkey)

    def test_init(self, mock_rpc_client, test_pubkey):
        """Test GlamClient initialization."""
        client = GlamClient(mock_rpc_client, test_pubkey)

        assert client.connection == mock_rpc_client
        assert client.vault_state == test_pubkey
        assert client._async_client is None

    @pytest.mark.asyncio
    async def test_async_context_manager(self, glam_client):
        """Test async context manager functionality."""
        async with glam_client as client:
            assert client is glam_client

        # Should be closed after exiting context
        assert glam_client._async_client is None

    @pytest.mark.asyncio
    async def test_get_async_client_creates_new_client(self, glam_client):
        """Test that _get_async_client creates a new AsyncClient when none exists."""
        with patch("glam.client.AsyncClient") as mock_async_client_class:
            mock_instance = AsyncMock()
            mock_async_client_class.return_value = mock_instance

            result = await glam_client._get_async_client()

            mock_async_client_class.assert_called_once_with(
                glam_client.connection._provider.endpoint_uri
            )
            assert result == mock_instance
            assert glam_client._async_client == mock_instance

    @pytest.mark.asyncio
    async def test_get_async_client_reuses_existing_client(self, glam_client):
        """Test that _get_async_client reuses existing AsyncClient."""
        mock_client = AsyncMock()
        glam_client._async_client = mock_client

        result = await glam_client._get_async_client()

        assert result == mock_client
        assert glam_client._async_client == mock_client

    @pytest.mark.asyncio
    async def test_close_with_existing_client(self, glam_client):
        """Test closing when async client exists."""
        mock_client = AsyncMock()
        glam_client._async_client = mock_client

        await glam_client.close()

        mock_client.close.assert_called_once()
        assert glam_client._async_client is None

    @pytest.mark.asyncio
    async def test_close_with_no_client(self, glam_client):
        """Test closing when no async client exists."""
        assert glam_client._async_client is None

        # Should not raise an exception
        await glam_client.close()

        assert glam_client._async_client is None

    @pytest.mark.asyncio
    async def test_get_state_account_success(self, glam_client):
        """Test successful state account retrieval."""
        mock_async_client = AsyncMock()
        mock_state_account = MagicMock(spec=StateAccount)

        with patch.object(glam_client, "_get_async_client", return_value=mock_async_client):
            with patch.object(StateAccount, "fetch", return_value=mock_state_account) as mock_fetch:
                result = await glam_client.get_state_account()

                mock_fetch.assert_called_once_with(
                    conn=mock_async_client, address=glam_client.vault_state, commitment=None
                )
                assert result == mock_state_account

    @pytest.mark.asyncio
    async def test_get_state_account_with_commitment(self, glam_client):
        """Test state account retrieval with commitment parameter."""
        mock_async_client = AsyncMock()
        mock_state_account = MagicMock(spec=StateAccount)
        commitment = Commitment("confirmed")

        with patch.object(glam_client, "_get_async_client", return_value=mock_async_client):
            with patch.object(StateAccount, "fetch", return_value=mock_state_account) as mock_fetch:
                result = await glam_client.get_state_account(commitment=commitment)

                mock_fetch.assert_called_once_with(
                    conn=mock_async_client, address=glam_client.vault_state, commitment=commitment
                )
                assert result == mock_state_account

    @pytest.mark.asyncio
    async def test_get_state_account_exception_handling(self, glam_client, capsys):
        """Test exception handling in get_state_account."""
        mock_async_client = AsyncMock()

        with patch.object(glam_client, "_get_async_client", return_value=mock_async_client):
            with patch.object(StateAccount, "fetch", side_effect=Exception("Test error")):
                result = await glam_client.get_state_account()

                assert result is None
                captured = capsys.readouterr()
                assert "Error fetching state model: Test error" in captured.out

    def test_get_vault_pda(self, glam_client):
        """Test vault PDA calculation."""
        expected_seeds = [
            b"\x76\x61\x75\x6c\x74",  # "vault" seed
            bytes(glam_client.vault_state),
        ]

        with patch("glam.client.Pubkey.find_program_address") as mock_find_pda:
            mock_pda = Pubkey.from_string("GrVK5Jjm1ipfQ9doigAXXS3KDoXYBFa3Jg6aKAqhRUuC")
            mock_find_pda.return_value = (mock_pda, 255)

            result = glam_client.get_vault_pda()

            # Verify the call was made with correct parameters
            mock_find_pda.assert_called_once()
            call_args = mock_find_pda.call_args[0]

            # Check seeds
            assert call_args[0] == expected_seeds

            # Check program ID (imported in the method)
            from glam.protocol.program_id import GLAM_PROTOCOL_PROGRAM_ADDRESS

            assert call_args[1] == GLAM_PROTOCOL_PROGRAM_ADDRESS

            assert result == mock_pda

    @pytest.mark.asyncio
    async def test_full_workflow_with_context_manager(self, mock_rpc_client, test_pubkey):
        """Test complete workflow using context manager."""
        mock_state_account = MagicMock(spec=StateAccount)
        mock_vault_pda = Pubkey.from_string("GrVK5Jjm1ipfQ9doigAXXS3KDoXYBFa3Jg6aKAqhRUuC")

        with patch.object(StateAccount, "fetch", return_value=mock_state_account):
            with patch(
                "glam.client.Pubkey.find_program_address", return_value=(mock_vault_pda, 255)
            ):
                async with GlamClient(mock_rpc_client, test_pubkey) as client:
                    # Test state account retrieval
                    state_account = await client.get_state_account()
                    assert state_account == mock_state_account

                    # Test vault PDA calculation
                    vault_pda = client.get_vault_pda()
                    assert vault_pda == mock_vault_pda

                    # Verify async client was created
                    assert client._async_client is not None

    @pytest.mark.asyncio
    async def test_connection_reuse(self, glam_client):
        """Test that async client connection is reused across multiple calls."""
        mock_async_client = AsyncMock()
        mock_state_account = MagicMock(spec=StateAccount)

        with patch("glam.client.AsyncClient", return_value=mock_async_client) as mock_client_class:
            with patch.object(StateAccount, "fetch", return_value=mock_state_account):
                # First call
                result1 = await glam_client.get_state_account()
                # Second call
                result2 = await glam_client.get_state_account()

                # AsyncClient should only be created once
                mock_client_class.assert_called_once()

                # Both calls should succeed
                assert result1 == mock_state_account
                assert result2 == mock_state_account

                # Same client instance should be reused
                assert glam_client._async_client == mock_async_client

    def test_vault_state_property_access(self, glam_client, test_pubkey):
        """Test that vault_state property is accessible."""
        assert glam_client.vault_state == test_pubkey

    def test_connection_property_access(self, glam_client, mock_rpc_client):
        """Test that connection property is accessible."""
        assert glam_client.connection == mock_rpc_client


class TestGlamClientIntegration:
    """Integration tests for GlamClient (these would require actual network access)."""

    def __init__(self):
        self.rpc_client = RpcClient("https://api.mainnet-beta.solana.com")
        self.test_pubkey = Pubkey.from_string("AK2c89yrVsPpFUcb9AwqhYLU1xE7atjSvmfBNzyZ75Qh")

    @pytest.mark.asyncio
    async def test_real_state_account_fetch(self):
        """Test fetching a real state account from mainnet."""

        async with GlamClient(self.rpc_client, self.test_pubkey) as client:
            state_account = await client.get_state_account()

            # If the account exists, it should be a StateAccount instance
            if state_account is not None:
                assert isinstance(state_account, StateAccount)
                assert hasattr(state_account, "integrationAcls")
                assert hasattr(state_account, "delegateAcls")

    def test_real_vault_pda_calculation(self):
        """Test calculating a real vault PDA."""
        client = GlamClient(self.rpc_client, self.test_pubkey)
        vault_pda = client.get_vault_pda()

        # Should return a valid Pubkey
        assert isinstance(vault_pda, Pubkey)
        # Should be deterministic
        vault_pda2 = client.get_vault_pda()
        assert vault_pda == vault_pda2
