"""Basic functionality tests for iFlow SDK."""

import asyncio
import pytest
from src.iflow_sdk import (
    IFlowClient,
    IFlowOptions,
    AssistantMessage,
    ToolCallMessage,
    TaskFinishMessage,
    ErrorMessage,
    ApprovalMode,
)


@pytest.mark.asyncio
async def test_connection():
    """Test basic connection to iFlow."""
    async with IFlowClient() as client:
        assert client._connected
        assert client._session_id is not None


@pytest.mark.asyncio
async def test_simple_message():
    """Test sending and receiving a simple message."""
    async with IFlowClient() as client:
        await client.send_message("What is 2 + 2?")

        received_messages = []
        timeout = 5
        start_time = asyncio.get_event_loop().time()

        async for message in client.receive_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            received_messages.append(message)

            if isinstance(message, TaskFinishMessage):
                break

        # Should receive at least one assistant message
        assistant_messages = [m for m in received_messages if isinstance(m, AssistantMessage)]
        assert len(assistant_messages) > 0

        # Should receive a task finish message
        finish_messages = [m for m in received_messages if isinstance(m, TaskFinishMessage)]
        assert len(finish_messages) == 1


@pytest.mark.asyncio
async def test_tool_call():
    """Test tool call messages."""
    async with IFlowClient() as client:
        await client.send_message("List files in current directory")

        tool_calls = []
        timeout = 5
        start_time = asyncio.get_event_loop().time()

        async for message in client.receive_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            if isinstance(message, ToolCallMessage):
                tool_calls.append(message)
            elif isinstance(message, TaskFinishMessage):
                break

        # Should receive at least one tool call
        assert len(tool_calls) > 0

        # Tool calls should have required attributes
        for tool_call in tool_calls:
            assert tool_call.id is not None
            assert tool_call.label is not None
            assert tool_call.status is not None


@pytest.mark.asyncio
async def test_options():
    """Test client with custom options."""
    options = IFlowOptions(approval_mode=ApprovalMode.AUTO_EDIT, timeout=10.0, log_level="DEBUG")

    async with IFlowClient(options) as client:
        assert client.options.permission_mode == ApprovalMode.AUTO_EDIT
        assert client.options.timeout == 10.0




if __name__ == "__main__":
    # Run tests
    asyncio.run(test_connection())
    asyncio.run(test_simple_message())
    asyncio.run(test_tool_call())
    asyncio.run(test_options())
    print("✅ All basic tests passed!")
