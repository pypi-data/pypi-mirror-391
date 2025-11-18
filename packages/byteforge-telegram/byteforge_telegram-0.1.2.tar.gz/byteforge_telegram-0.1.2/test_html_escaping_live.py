#!/usr/bin/env python3
"""
Live test script to verify HTML escaping fix with real Telegram messages.
This reproduces the bug scenario from the bug report.
"""
import os
from byteforge_telegram.notifier import TelegramBotController

# Get credentials from environment
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    print("ERROR: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
    exit(1)

print("Testing HTML escaping fix...")
print(f"Bot token: {BOT_TOKEN[:10]}...")
print(f"Chat ID: {CHAT_ID}")

controller = TelegramBotController(BOT_TOKEN)

# Test 1: The exact scenario from the bug report
print("\n=== Test 1: Bug report scenario (comparison operators) ===")
result = controller.send_message_sync(
    text="""🎯 New Prompt Created
• TA-Lib adoption <10% → target 40%
• Expected: >30% performance improvement""",
    chat_ids=[CHAT_ID]
)
print(f"Result: {result}")
print(f"Success: {result.get(CHAT_ID, False)}")
if result.get(CHAT_ID, False):
    print("✅ Bug is fixed! Message with <10% and >30% sent successfully")
else:
    print("❌ Still failing - bug not fixed")

# Test 2: Ampersand character
print("\n=== Test 2: Ampersand character ===")
result = controller.send_message_sync(
    text="Testing ampersand: R&D department, A&B testing, 50% & growing",
    chat_ids=[CHAT_ID]
)
print(f"Result: {result}")
print(f"Success: {result.get(CHAT_ID, False)}")

# Test 3: All special characters together
print("\n=== Test 3: All special characters together ===")
result = controller.send_message_sync(
    text="Complex: <10% & >5% improvement in A&B testing",
    chat_ids=[CHAT_ID]
)
print(f"Result: {result}")
print(f"Success: {result.get(CHAT_ID, False)}")

# Test 4: send_formatted with special characters
print("\n=== Test 4: Formatted message with special characters ===")
result = controller.send_formatted_sync(
    title="Performance Metrics <10%",
    fields={
        "Adoption Rate": "<10% → target 40%",
        "Expected Growth": ">30% improvement",
        "R&D Team": "A&B testing in progress"
    },
    chat_ids=[CHAT_ID],
    emoji="📊",
    footer="Success rate >90% & improving"
)
print(f"Result: {result}")
print(f"Success: {result.get(CHAT_ID, False)}")

# Test 5: Verify HTML formatting still works in send_formatted
print("\n=== Test 5: HTML formatting preserved in send_formatted ===")
result = controller.send_formatted_sync(
    title="Test Bold & Italic",
    fields={
        "Status": "Active",
        "Progress": "75%"
    },
    chat_ids=[CHAT_ID],
    emoji="🔧",
    footer="This should have bold title & italic footer"
)
print(f"Result: {result}")
print(f"Success: {result.get(CHAT_ID, False)}")

print("\n✅ All tests completed! Check your Telegram to verify:")
print("1. Messages with <, >, & characters display correctly")
print("2. Bold and italic formatting in send_formatted still works")
print("3. No 'Can't parse entities' errors in the logs")
