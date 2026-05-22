# 🚀 Enterprise AI Agent Architecture: MAF + ContextForge + Phoenix + LM Studio

This repository demonstrates a production-grade, locally hosted AI Agent architecture. It uses the **Microsoft Agent Framework (MAF)** for orchestration, **IBM ContextForge** as a secure Model Context Protocol (MCP) gateway, **Arize Phoenix** for OpenTelemetry observability, and **LM Studio** for local LLM inference.

---

## 📁 Repository Structure

```text
monitoring/
│
├── docker-compose.yml          # Infrastructure setup (Phoenix + ContextForge)
├── .env                        # Environment configuration
├── README.md                   # Setup and usage guide
│
├── mcp_tools/                  # Standalone tool servers
│   └── search_tool.py          # FastMCP server running over SSE (HTTP)
│
├── gateway_config/             # ContextForge configurations
│   └── contextforge.yaml       # Registers tools and configures telemetry
│
├── skills/                     # Agent skills (agentskills.io compliant)
│   └── financial-research/
│       └── SKILL.md            # Skill instructions & frontmatter
│
└── src/                        # The MAF Application
    ├── context_providers.py    # Custom compliance & context injector
    └── agent_orchestrator.py   # Main agent orchestration logic
```

---

## 🛠️ Step 1: Set Up LM Studio (The Local Brain)

1. Download and install [LM Studio](https://lmstudio.ai/) for Windows.
2. Search and download the **Qwen/Qwen3.6-27B** (or similar) instruction-tuned model.
3. Navigate to the **Local Server** tab (represented by the `<->` icon on the left panel).
4. Set the port to `1234` and click **Start Server**.
5. The API is now available at `http://127.0.0.1:1234/v1` and perfectly mimics the OpenAI API schema.

---

## 🐳 Step 2: Spin Up the Infrastructure

The infrastructure runs inside Docker to ensure your Windows host remains clean and to mimic production microservices.

Start Arize Phoenix and ContextForge by running:

```powershell
docker-compose up -d
```

### Verification
- **Arize Phoenix Web UI**: Open [http://localhost:6006](http://localhost:6006) in your browser.
- **ContextForge Gateway**: Listening on port `4444`.

---

## 🔧 Step 3: Run the MCP Tool Server

The MCP tool server runs locally on Windows on port `8000`. To allow ContextForge (inside Docker) to talk to the local tool, we expose it over HTTP/SSE instead of stdio.

1. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install Python dependencies:
   ```powershell
   pip install agent-framework mcp uvicorn requests opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
   ```
3. Run the tool server:
   ```powershell
   python mcp_tools/search_tool.py
   ```

---

## 🎛️ Step 4: Configure ContextForge

ContextForge routes requests from the Docker container back to your Windows host using the Docker-specific DNS name `host.docker.internal`.

**gateway_config/contextforge.yaml**:
```yaml
version: "1.0"
servers:
  internal_database:
    url: "http://host.docker.internal:8000/sse"
    transport: "sse"
```

---

## 🧠 Step 5: Agent Skills Definition

Skills are defined in a standardized markdown package. The agent reads `SKILL.md` to learn about the task and allowed tools.

**skills/financial-research/SKILL.md**:
```yaml
---
name: financial-research
description: Analyze a company by querying the internal database. Use this skill when asked about company performance or risks.
allowed-tools: search_company_database
---
# Financial Research Protocol

## Instructions
1. First, invoke the `search_company_database` tool using the exact stock ticker.
2. Analyze the returned internal data.
3. Formulate a final response formatted strictly as a Markdown table.
4. Include a "Risk Level" row based on your analysis of the data.
```

---

## 🏗️ Step 6: Execute the Orchestrator

With LM Studio, Docker Compose, and the Tool Server running, execute the MAF Orchestrator:

```powershell
python src/agent_orchestrator.py
```

### What happens under the hood:
1. **Compliance Context Injection**: Rules from `ComplianceContextProvider` are injected.
2. **Skill Loading**: The framework loads `skills/financial-research/SKILL.md` and discloses instructions to the agent.
3. **Execution**: The local LLM decides to call `search_company_database`.
4. **OTLP Telemetry Export**: OpenTelemetry trace spans are exported to Arize Phoenix.

---

## 📊 View Traces in Arize Phoenix

Open [http://localhost:6006](http://localhost:6006) to explore a nested telemetry trace waterfall:
1. **Workflow execution** span.
2. **Injected compliance rules** span.
3. **LLM inference** span (detailed prompt structure, tokens, model name).
4. **Tool invocation** span.
