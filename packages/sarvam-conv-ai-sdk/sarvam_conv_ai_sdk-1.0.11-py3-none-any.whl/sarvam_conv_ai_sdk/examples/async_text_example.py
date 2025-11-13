"""Example using async client with text I/O over text channel.

This example demonstrates:
1. Using AsyncSamvaadAgent with text_callback for receiving text
2. Sending text messages using send_text() (supports both str and JSON)
3. Working with the TEXT interaction type
4. Handling both text and events in async context

Requirements:
    pip install sarvam-conv-ai-sdk

Usage:
    python async_text_example.py
"""

import asyncio
import logging
import os
import sys

from pydantic import SecretStr

from sarvam_conv_ai_sdk import (
    AsyncSamvaadAgent,
    InteractionConfig,
    InteractionType,
    ServerEventBase,
    ServerTextMsgType,
)
from sarvam_conv_ai_sdk.messages.types import UserIdentifierType
from sarvam_conv_ai_sdk.tool import SarvamToolLanguageName

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # But keep INFO for our logger


# TODO: Focus on this example
async def main(api_key: SecretStr):
    """Main async function demonstrating text conversation."""

    logger.info("=" * 60)
    logger.info("Async Text Example - Text Conversation")
    logger.info("=" * 60)

    # Configure the conversation
    config = InteractionConfig(
        user_identifier="demo_user_async",
        user_identifier_type=UserIdentifierType.CUSTOM,
        app_id="app_id",
        org_id="org_id",
        workspace_id="workspace_id",
        interaction_type=InteractionType.TEXT,
        agent_variables={
            "agent_variable1": "value",
            "agent_variable2": "value",
        },
        initial_language_name=SarvamToolLanguageName.HINDI,
        initial_state_name="initial_state_name",
        sample_rate=16000,
    )

    # Track conversation state
    conversation_messages = []

    # Define text callback to handle incoming text
    async def handle_text(text_msg: ServerTextMsgType):
        """Handle text messages from the agent."""
        print(f"\n🤖 Agent: {text_msg.text}")
        conversation_messages.append({"role": "agent", "text": text_msg.text})

    # Define event callback to handle events
    async def handle_event(event: ServerEventBase):
        """Handle events from the agent."""
        logger.info(f"📢 Event: {event.type}")

    # Create async agent with text callback
    logger.info("Creating agent...")
    agent = AsyncSamvaadAgent(
        api_key=api_key,
        config=config,
        text_callback=handle_text,
        event_callback=handle_event,
        base_url="https://apps.sarvam.ai/api/app-runtime/",
    )

    try:
        # Start agent (connection happens asynchronously in background)
        logger.info("Starting agent...")
        await agent.start()
        logger.info("✅ Agent started! Connection establishing in background...")  # noqa

        # Wait for connection to be established
        logger.info("Waiting for WebSocket connection...")
        connected = await agent.wait_for_connect(timeout=5.0)
        if not connected:
            logger.error("Failed to connect within timeout")
            return

        logger.info(f"✅ Connected! Interaction ID: {agent.get_interaction_id()}")  # noqa
        print_text = "\n" + "=" * 60 + "\n"
        print_text += "🎉 Text conversation active!\n"
        print_text += "   Type messages to interact with the agent.\n"
        print_text += "   Type 'quit' or 'exit' to stop.\n"
        print_text += "=" * 60 + "\n"

        # Interactive loop for continuous text conversation
        loop = asyncio.get_event_loop()

        while True:
            try:
                user_input = await loop.run_in_executor(None, input, "👤 You: ")
                if user_input.lower() in ["quit", "exit"]:
                    logger.info("Exiting conversation...")
                    break

                if not user_input.strip():
                    continue

                conversation_messages.append({"role": "user", "text": user_input})  # noqa: E501
                await agent.send_text(user_input)

                # Wait a bit for agent response before next prompt
                await asyncio.sleep(1.0)

            except EOFError:
                logger.info("Input stream closed. Exiting...")
                break

        # Print conversation summary
        if conversation_messages:
            logger.info("\n" + "=" * 60)
            logger.info("Conversation Summary:")
            logger.info("=" * 60)
            for msg in conversation_messages:
                role = "🤖 Agent" if msg["role"] == "agent" else "👤 User"
                logger.info(f"{role}: {msg['text']}")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping conversation...")

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)

    finally:
        # Cleanup
        logger.info("Stopping agent...")
        await agent.stop()
        logger.info("✅ Cleaned up successfully!")


if __name__ == "__main__":
    API_KEY_STR = os.getenv("SARVAM_API_KEY")
    if not API_KEY_STR:
        logger.error("API key not set. Set SARVAM_API_KEY in the environment.")
        sys.exit(1)

    asyncio.run(main(SecretStr(API_KEY_STR)))
