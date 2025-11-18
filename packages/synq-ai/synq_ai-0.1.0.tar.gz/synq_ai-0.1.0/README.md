# Synq - Multi-Agent AI Interaction System

A powerful platform for simulating interactions between AI agents at scale. Synq enables you to create AI personas that interact with each other in isolated "synqes" to test compatibility, explore scenarios, or simulate conversations before real-world engagement.

## Overview

Synq is a general-purpose multi-agent coordination system where:
- **AI Agents** represent different personas, personalities, or roles
- **Synqes** are isolated environments where agents interact
- **Real-time conversations** powered by OpenAI's GPT models
- **Scalable architecture** for running thousands of conversations in parallel

## Key Features

✨ **AI Agent Management**
- Create unlimited AI agents with custom personalities
- Each agent maintains conversation history and context
- Powered by OpenAI's GPT models (GPT-4o-mini by default)

🔒 **Isolated Synqes**
- Agents interact in controlled environments
- Automatic expiration with configurable TTL
- Manual synq closure when needed

💬 **Real-time Interactions**
- Watch agents converse naturally
- Trigger responses from specific agents
- Continue conversations dynamically

📋 **Structured Output Formats** ⭐ NEW
- Define output format for agent collaboration results
- Multiple format types: Summary, Decision, JSON, Custom
- Extract structured data from conversations
- Perfect for programmatic analysis

🎯 **Vector-Based Matching**
- Semantic similarity search using embeddings
- Quick filtering before full conversations
- Efficient at scale

🌐 **Beautiful Web UI**
- Real-time dashboard
- Live conversation viewing
- Easy agent management

## Use Cases

### 1. **Dating & Compatibility Matching**
AI agents represent real people and interact to determine compatibility before meeting in person. See [DATING_APP_GUIDE.md](DATING_APP_GUIDE.md) for details.

### 2. **Team Formation**
Simulate team dynamics by having AI agents represent different work styles and personalities to find optimal team combinations.

### 3. **Customer Service Training**
Create AI customers with various personalities and scenarios to train chatbots or test customer service responses.

### 4. **Content Testing**
Have AI agents represent different audience segments to test how content resonates before release.

### 5. **Negotiation Simulation**
Simulate business negotiations by having agents with different goals and strategies interact.

### 6. **Social Network Simulation**
Model social dynamics at scale by having thousands of AI agents interact in various scenarios.

## Quick Start

### 1. Setup
```bash
# Add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Build the application
go build -o synq cmd/synq/main.go

# Run the server
./synq
```

### 2. Open Web UI
Navigate to http://localhost:8080

### 3. Create Agents
The system includes 3 example agents:
- **sarah_ai** - Creative, empathetic personality
- **marcus_ai** - Ambitious, goal-oriented personality
- **maya_ai** - Warm, spiritually-minded personality

### 4. Create a Synq
- Go to "Create Synq" tab
- Add agent IDs (comma-separated)
- Set TTL (time-to-live in seconds)
- Click "Create Synq"

### 5. Start Interactions
- Click on a synq to open it
- Use "Start AI Conversation" for automatic multi-agent chat
- Or select an agent and send a specific message

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Web UI                        │
│        (Real-time dashboard & controls)         │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────┐
│              API Server (Go)                    │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   Registry   │  │   Synq Manager        │ │
│  │  (Agents)    │  │  (Isolated Environments) │ │
│  └──────────────┘  └──────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Vector Index │  │   Message Bus            │ │
│  │ (Embeddings) │  │   (Communication)        │ │
│  └──────────────┘  └──────────────────────────┘ │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────┐
│              OpenAI API                         │
│         (GPT-4o-mini by default)                │
└─────────────────────────────────────────────────┘
```

## API Reference

### Create a Synq
```bash
curl -X POST http://localhost:8080/synq/create \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_synq",
    "agents": ["sarah_ai", "marcus_ai"],
    "ttl_seconds": 3600
  }'
```

### Create a Synq with Output Format
```bash
curl -X POST http://localhost:8080/synq/create \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_synq",
    "agents": ["sarah_ai", "marcus_ai"],
    "ttl_seconds": 3600,
    "output_format": {
      "type": "summary",
      "instructions": "Focus on compatibility and shared interests"
    }
  }'
```

### Generate Formatted Output
```bash
curl http://localhost:8080/synq/generate-output?synq_id=my_synq
```

### Trigger Agent Response
```bash
curl -X POST http://localhost:8080/synq/agent-respond \
  -H "Content-Type: application/json" \
  -d '{
    "synq_id": "my_synq",
    "agent_id": "sarah_ai",
    "message": "Hello! How are you?"
  }'
```

### Get Synq Messages
```bash
curl http://localhost:8080/synq/messages?id=my_synq
```

### Close a Synq
```bash
curl -X POST http://localhost:8080/synq/close \
  -H "Content-Type: application/json" \
  -d '{
    "synq_id": "my_synq"
  }'
```

### List All Agents
```bash
curl http://localhost:8080/agents
```

### List All Synqes
```bash
curl http://localhost:8080/synqes
```

## Creating Custom Agents

Edit `cmd/synq/main.go` to add your own agents:

```go
customAgent := registry.NewOpenAIAgent(
    "agent_id",
    "agent_type",
    `You are [description]. Your personality:
- Trait 1
- Trait 2
- Values: [values]
- Looking for: [goals]

When chatting, [behavioral guidelines]. Keep responses [length guidance].`,
    []float64{0.8, 0.6, 0.7}, // embedding vector
)
reg.RegisterOpenAIAgent(customAgent)
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - Your OpenAI API key (required)

### Adjustable Settings
- **Auto-cleanup interval**: Edit `cmd/synq/main.go` line 23 (default: 30 seconds)
- **OpenAI model**: Edit `internal/registry/openai_agent.go` line 35 (default: GPT-4o-mini)
- **Temperature**: Edit `internal/registry/openai_agent.go` line 46 (default: 0.7)

## Cost Considerations

Using GPT-4o-mini (default):
- ~$0.15 per 1M input tokens
- ~$0.60 per 1M output tokens
- Average 20-message conversation: ~$0.02
- 100 conversations: ~$2.00

For production at scale, consider:
- Caching common responses
- Using fine-tuned models
- Implementing rate limiting
- Batching API calls

## Features

### Automatic Synq Cleanup
Synqes automatically expire after their TTL. The system checks every 30 seconds and removes expired synqes.

### Manual Synq Closure
Users can manually close synqes at any time through the UI or API.

### Conversation Memory
Each agent maintains full conversation history within a synq, enabling contextual responses.

### Real-time Updates
The UI auto-refreshes every 5 seconds and messages refresh every 2 seconds when viewing a synq.

## Tech Stack

- **Backend**: Go 1.25
- **AI**: OpenAI GPT-4o-mini
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Architecture**: RESTful API

## Dependencies

```
github.com/sashabaranov/go-openai
github.com/joho/godotenv
github.com/google/uuid
```

## Project Structure

```
synq/
├── cmd/
│   └── synq/
│       └── main.go          # Entry point, agent initialization
├── internal/
│   ├── bus/                 # Message bus for inter-agent communication
│   ├── registry/            # Agent management and OpenAI integration
│   ├── synq/             # Synq creation and lifecycle management
│   └── vector/              # Vector index for similarity search
├── ui/
│   └── server.go            # Web UI and API endpoints
├── .env                     # Environment variables (not committed)
├── .gitignore
└── README.md
```

## Contributing

This is a demonstration project. To extend it:

1. Add new agent types in `internal/registry/`
2. Create custom synq behaviors in `internal/synq/`
3. Extend the API in `ui/server.go`
4. Customize the UI within the HTML template

## License

MIT License - Feel free to use this for any purpose.

## Learn More

- [Dating App Use Case Guide](DATING_APP_GUIDE.md) - Detailed example of using Synq for compatibility matching
- [Output Format Guide](OUTPUT_FORMAT_GUIDE.md) - Complete guide to structured output generation ⭐ NEW
- [UI Guide](UI_GUIDE.md) - Complete UI documentation
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)

## Support

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ using Go and OpenAI**

