<p align="center">
  <img src="https://raw.githubusercontent.com/getbindu/create-bindu-agent/refs/heads/main/assets/light.svg" alt="bindu Logo" width="200">
</p>

<h1 align="center">ai-interview-coach</h1>

<p align="center">
  <strong>An AI agent that simulates professional responses for technical interviews, demonstrating depth, real-world experience, and architectural trade-offs.</strong>
</p>

<p align="center">
  <a href="https://github.com/chandan-1427/ai-interview-coach/actions/workflows/main.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/chandan-1427/ai-interview-coach/main.yml?branch=main" alt="Build status">
  </a>
  <a href="https://img.shields.io/github/license/chandan-1427/ai-interview-coach">
    <img src="https://img.shields.io/github/license/chandan-1427/ai-interview-coach" alt="License">
  </a>
</p>

---

## 📖 Overview

Built on the [Bindu Agent Framework](https://github.com/getbindu/bindu), this agent helps technical candidates master interview narratives by providing concise, 30-second STAR method responses.

**Key Capabilities:**
- 🔍 Analyzes interview questions for hidden intent and risks
- 🗣️ Crafts first-person narratives with quantified results
- ⚖️ Explores alternative approaches with trade-offs
- 📚 Integrates real-world engineering context via Exa
- 🧠 Maintains user memory across sessions with Mem0

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- API keys: OpenRouter (required), Mem0 and Exa (optional)

### Installation
```bash
git clone https://github.com/chandan-1427/ai-interview-coach.git
cd ai-interview-coach
uv venv --python 3.12.9
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync
cp .env.example .env
```

### Configuration
Edit `.env` with your API keys:
- `OPENROUTER_API_KEY`: Required for LLM
- `MEM0_API_KEY`: For user memory
- `EXA_API_KEY`: For research

### Run
```bash
uv run python -m ai_interview_coach
# Agent runs at http://localhost:3773
```

---

## 💡 Usage

### Example Queries
- "How do you handle dependency conflicts?"
- "Describe a time you optimized database performance."

### Input/Output
- **Input**: Plain text interview question
- **Output**: Structured response with narrative, alternatives, and final script

---

## 🔌 API Usage
RESTful API at `http://localhost:3773`. See [Bindu API Reference](https://docs.getbindu.com/api-reference/all-the-tasks/send-message-to-agent) for details.

---

## 🎯 Skills
**ai_interview_coach (v1.0.0)**: Simulates senior engineer responses using LangGraph workflow with intent analysis, narrative crafting, trade-off evaluation, and final polishing.

**Best Used For:** Technical interview preparation, behavioral questions, system design discussions.

---

## 🐳 Docker
```bash
docker-compose up --build
# Runs at http://localhost:3773
```

---

## 🛠️ Development
- Tests: `make test`
- Lint: `make lint`
- Format: `make format`

---

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License
MIT License - see [LICENSE](LICENSE).

---

## 🙏 Powered by Bindu
Built with [Bindu Agent Framework](https://github.com/getbindu/bindu).

---

## 🌐 Deploy to bindus.directory

Make your agent discoverable worldwide and enable agent-to-agent collaboration.

### Setup GitHub Secrets

```bash
# Authenticate with GitHub
gh auth login

# Set deployment secrets
gh secret set BINDU_API_TOKEN --body "<your-bindu-api-key>"
gh secret set DOCKERHUB_TOKEN --body "<your-dockerhub-token>"
```

Get your keys:
- **Bindu API Key**: [bindus.directory](https://bindus.directory) dashboard
- **Docker Hub Token**: [Docker Hub Security Settings](https://hub.docker.com/settings/security)

### Deploy

```bash
# Push to trigger automatic deployment
git push origin main
```

GitHub Actions will automatically:
1. Build your agent
2. Create Docker container
3. Push to Docker Hub
4. Register on bindus.directory

---

## 🛠️ Development

### Project Structure

```
ai-interview-coach/
├── ai_interview_coach/
│   ├── skills/
│   │   └── ai_interview_coach/
│   │       ├── skill.yaml          # Skill configuration
│   │       └── __init__.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py                     # Agent entry point
│   └── agent_config.json           # Agent configuration
├── tests/
│   └── test_main.py
├── .env.example
├── docker-compose.yml
├── Dockerfile.agent
└── pyproject.toml
```

### Running Tests

```bash
make test              # Run all tests
make test-cov          # With coverage report
```

### Code Quality

```bash
make format            # Format code with ruff
make lint              # Run linters
make check             # Format + lint + test
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run manually
uv run pre-commit run -a
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Powered by Bindu

Built with the [Bindu Agent Framework](https://github.com/getbindu/bindu)

**Why Bindu?**
- 🌐 **Internet of Agents**: A2A, AP2, X402 protocols for agent collaboration
- ⚡ **Zero-config setup**: From idea to production in minutes
- 🛠️ **Production-ready**: Built-in deployment, monitoring, and scaling

**Build Your Own Agent:**
```bash
uvx cookiecutter https://github.com/getbindu/create-bindu-agent.git
```

---

## 📚 Resources

- 📖 [Full Documentation](https://chandan-1427.github.io/ai-interview-coach/)
- 💻 [GitHub Repository](https://github.com/chandan-1427/ai-interview-coach/)
- 🐛 [Report Issues](https://github.com/chandan-1427/ai-interview-coach/issues)
- 💬 [Join Discord](https://discord.gg/3w5zuYUuwt)
- 🌐 [Agent Directory](https://bindus.directory)
- 📚 [Bindu Documentation](https://docs.getbindu.com)

---

<p align="center">
  <strong>Built with 💛 by the team from Amsterdam 🌷</strong>
</p>

<p align="center">
  <a href="https://github.com/chandan-1427/ai-interview-coach">⭐ Star this repo</a> •
  <a href="https://discord.gg/3w5zuYUuwt">💬 Join Discord</a> •
  <a href="https://bindus.directory">🌐 Agent Directory</a>
</p>
