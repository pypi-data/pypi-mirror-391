# aui-client

[![PyPI version](https://img.shields.io/pypi/v/aui-client)](https://pypi.org/project/aui-client)
[![Built with Fern](https://img.shields.io/badge/Built%20with-Fern-brightgreen)](https://buildwithfern.com)

> **Official Python SDK for AUI APIs** - Provides REST and WebSocket support for intelligent agent communication.

## 🚀 Installation

```bash
pip install aui-client
```

## ⚡ Quick Start

### Initialize Client

```python
from aui import ApolloClient

# Connect to production
client = ApolloClient(
    network_api_key='API_KEY_YOUR_KEY_HERE'
)

# This connects to production:
# - REST API: https://azure.aui.io/api/ia-controller
# - WebSocket: wss://api.aui.io/ia-controller/api/v1/external/session
```

### REST API - Create and Manage Tasks

```python
# Create a new task
task_response = client.controller_api.create_task(
    user_id='user123'
)

task_id = task_response.id
print(f'Task ID: {task_id}')
print(f'Welcome: {task_response.welcome_message}')

# Get all messages for a task
messages = client.controller_api.get_task_messages(task_id=task_id)
print(f'Total messages: {len(messages)}')

# Submit a message to an existing task
message_response = client.controller_api.send_message(
    task_id=task_id,
    text='Looking for a microwave with at least 20 liters capacity',
    is_external_api=True
)

print(f'Agent response: {message_response.text}')

# Get all tasks for a user
tasks_response = client.controller_api.list_user_tasks(
    user_id='user123',
    page=1,
    size=10
)

print(f'Total tasks: {tasks_response.total}')
```

### WebSocket - Real-time Agent Communication

```python
import asyncio
from aui import ApolloClient

async def chat_with_agent():
    client = ApolloClient(
        network_api_key='API_KEY_YOUR_KEY_HERE'
    )
    
    # Connect to WebSocket
    socket = await client.apollo_ws_session.connect()
    
    # Listen for connection open
    @socket.on('open')
    async def on_open():
        print('✅ Connected to agent')
        
        # Send a message
        await socket.send_user_message({
            'task_id': 'your-task-id',
            'text': 'I need product recommendations for gaming laptops'
        })
    
    # Handle streaming responses
    @socket.on('message')
    async def on_message(message):
        # Streaming updates (partial responses)
        if message['type'] == 'streaming_update':
            print(f"Agent is typing: {message['data']['text']}")
        
        # Final message with complete response
        elif message['type'] == 'final_message':
            print(f"Complete response: {message['data']['text']}")
            
            # Handle product recommendations (if any)
            if 'product_cards' in message['data']:
                for product in message['data']['product_cards']:
                    print(f"{product['title']} - ${product['price']}")
            
            # Close connection
            await socket.close()
        
        # Error messages
        elif message['type'] == 'error':
            print(f"Agent error: {message['data']['message']}")
    
    # Handle errors
    @socket.on('error')
    async def on_error(error):
        print(f'WebSocket error: {error}')
    
    # Handle connection close
    @socket.on('close')
    async def on_close(code, reason):
        print(f'Connection closed: {code}')

# Run the async function
asyncio.run(chat_with_agent())
```

## 📖 API Reference

### Client Configuration

```python
from aui import ApolloClient
from aui.environment import ApolloClientEnvironment

client = ApolloClient(
    network_api_key: str,                    # Your API key (required)
    environment: ApolloClientEnvironment,    # Environment (default: production)
    timeout: Optional[float],                # Request timeout (default: 60)
    headers: Optional[Dict[str, str]],       # Additional headers
    follow_redirects: Optional[bool],        # Follow redirects (default: True)
    httpx_client: Optional[httpx.Client]     # Custom HTTP client
)
```

---

### REST API Methods

All methods are accessed via `client.controller_api.*`

#### `create_task(user_id)` - Create Task

```python
task_response = client.controller_api.create_task(
    user_id='user123'
)
# Returns: CreateTaskResponse with id, user_id, title, welcome_message
```

#### `get_task_messages(task_id)` - Get Task Messages

```python
messages = client.controller_api.get_task_messages(
    task_id='task_id_here'
)
# Returns: List[Message]
```

#### `send_message(task_id, text)` - Send Message

```python
message_response = client.controller_api.send_message(
    task_id='task_id_here',
    text='Your message here',
    is_external_api=True  # Optional
)
# Returns: Message - Complete agent response with optional product cards
```

#### `list_user_tasks(user_id, page, size)` - List User Tasks

```python
tasks_response = client.controller_api.list_user_tasks(
    user_id='user123',
    page=1,
    size=10
)
# Returns: ListTasksResponse with tasks, total, page, size
```

---

### WebSocket API

All WebSocket methods are accessed via `client.apollo_ws_session.*`

#### `connect()` - Establish Connection

```python
socket = await client.apollo_ws_session.connect()
```

#### Socket Event Handlers

```python
@socket.on('open')
async def on_open():
    pass

@socket.on('message')
async def on_message(message: dict):
    pass

@socket.on('error')
async def on_error(error):
    pass

@socket.on('close')
async def on_close(code: int, reason: str):
    pass
```

#### Socket Methods

```python
# Send a message
await socket.send_user_message({
    'task_id': 'task_id_here',
    'text': 'Your message'
})

# Close connection
await socket.close()
```

---

## 🎯 Complete Example

```python
from aui import ApolloClient
import asyncio

client = ApolloClient(
    network_api_key='API_KEY_YOUR_KEY_HERE'
)

async def search_products(user_id: str, query: str):
    # Step 1: Create a task
    task_response = client.controller_api.create_task(user_id=user_id)
    task_id = task_response.id
    print(f'Created task: {task_id}')
    
    # Step 2: Connect to WebSocket
    socket = await client.apollo_ws_session.connect()
    
    @socket.on('open')
    async def on_open():
        print('Connected! Sending query...')
        await socket.send_user_message({
            'task_id': task_id,
            'text': query
        })
    
    @socket.on('message')
    async def on_message(message):
        # Streaming updates
        if hasattr(message, 'channel') and message.channel:
            if message.channel.event_name == 'thread-message-text-content-updated':
                print(f"Agent: {message.data.text if hasattr(message, 'data') else ''}")
        
        # Final message
        elif hasattr(message, 'id') and hasattr(message, 'text'):
            print(f"\n✅ Final Response: {message.text}")
            
            if hasattr(message, 'cards') and message.cards:
                print('\n🛍️ Product Recommendations:')
                for i, card in enumerate(message.cards, 1):
                    print(f"{i}. {card.name}")
                    print(f"   Product ID: {card.id}")
            
            await socket.close()
    
    @socket.on('error')
    async def on_error(error):
        print(f'Error: {error}')

# Usage
asyncio.run(search_products('user123', 'I need a gaming laptop under $1500'))
```

## 🐛 Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'aui'`

**Solution:** Install the package:
```bash
pip install aui-client
```

### Authentication Errors (401/403)

**Problem:** Getting `401 Unauthorized` or `403 Forbidden` errors

**Solution:** Verify your API key:
```python
client = ApolloClient(
    network_api_key='API_KEY_YOUR_KEY_HERE'  # Double-check this value
)

# The key should start with "API_KEY_"
# Example: API_KEY_01K92N5BD5M7239VRK7YTK4Y6N
```

### WebSocket Connection Issues

**Problem:** WebSocket connection fails

**Solution:** Ensure you're using `asyncio` properly:
```python
import asyncio

async def main():
    socket = await client.apollo_ws_session.connect()
    # ... your code

asyncio.run(main())
```

## 🔗 Resources

- **GitHub Repository:** [aui-io/aui-client-python](https://github.com/aui-io/aui-client-python)
- **PyPI Package:** [aui-client](https://pypi.org/project/aui-client)
- **TypeScript SDK:** [@aui.io/aui-client](https://www.npmjs.com/package/@aui.io/aui-client)
- **API Documentation:** [Full API Reference](https://docs.aui.io)
- **Report Issues:** [GitHub Issues](https://github.com/aui-io/aui-client-python/issues)

## 📄 License

This SDK is proprietary software. Unauthorized copying or distribution is prohibited.

## 🤝 Support

For support, please contact your AUI representative or open an issue on GitHub.

---

**Built with ❤️ by the AUI team**




