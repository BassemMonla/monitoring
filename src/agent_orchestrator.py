import os
import asyncio

# 1. SETUP OBSERVABILITY
# Must be set BEFORE importing agent_framework
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318" 

from agent_framework import Agent, WorkflowBuilder, Executor, handler, WorkflowContext, SkillsProvider, InMemoryHistoryProvider
from agent_framework.openai import OpenAIChatClient
from agent_framework.observability import configure_otel_providers
from context_providers import ComplianceContextProvider

configure_otel_providers()

# 2. LOAD SKILLS (Absolute path resolution)
current_dir = os.path.dirname(os.path.abspath(__file__))
skills_path = os.path.join(current_dir, "..", "skills")
skills_provider = SkillsProvider.from_paths([skills_path])

# Load skill content for agent instructions
skills = asyncio.run(skills_provider._source.get_skills())
finance_skill = next(s for s in skills if s.frontmatter.name == "financial-research")
instructions = finance_skill.content

# 3. CONTEXTFORGE TOOL BINDING 
from mcp import ClientSession
from mcp.client.sse import sse_client

async def search_company_database(ticker: str) -> str:
    """Search company database."""
    print(f"[Agent] Routing tool execution to internal database MCP for {ticker}...")
    url = "http://localhost:24444/sse"
    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Execute the tool on the gateway
                result = await session.call_tool("search_company_database", {"ticker": ticker})
                return result.content[0].text
    except Exception as e:
        return f"Error communicating with ContextForge Gateway: {str(e)}"

class FinancialAnalystExecutor(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configure LM Studio local LLM
        lm_studio_client = OpenAIChatClient(
            api_key="lm-studio", 
            base_url="http://127.0.0.1:1234/v1",
            model="qwen/qwen3.6-27b" # LM Studio local model
        )

        self.agent = Agent(
            client=lm_studio_client,
            instructions=instructions,               # From SKILL.md
            tools=[search_company_database],         # Routed through Gateway
            context_providers=[
                InMemoryHistoryProvider(),           # Memory
                ComplianceContextProvider()          # Custom Context
            ]
        )

    @handler
    async def run_analysis(self, query: str, ctx: WorkflowContext[str]):
        print(f"--> [MAF] Routing user query: '{query}'")
        result = await self.agent.run(query)
        await ctx.yield_output(result.text)

async def main():
    executor = FinancialAnalystExecutor(id="analyst_agent")
    workflow = WorkflowBuilder(start_executor=executor).build()
    
    print("\nStarting Agent Workflow...\n")
    result = await workflow.run("Please research NVDA and provide a report.")
    
    print("\n=== FINAL RESULT ===")
    print(getattr(result, "output", result))

if __name__ == "__main__":
    asyncio.run(main())
