import os
import asyncio
from agent_framework import Agent, WorkflowBuilder, Executor, handler, WorkflowContext, SkillsProvider, InMemoryHistoryProvider
from agent_framework.openai import OpenAIChatClient
from agent_framework.observability import configure_otel_providers
from context_providers import ComplianceContextProvider

# 1. SETUP OBSERVABILITY (Route MAF traces to local Phoenix Docker)
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
configure_otel_providers()

# 2. LOAD SKILLS (Absolute path resolution)
current_dir = os.path.dirname(os.path.abspath(__file__))
skills_path = os.path.join(current_dir, "..", "skills")
skills_provider = SkillsProvider.from_paths([skills_path])

# Load skill content for agent instructions
skills = asyncio.run(skills_provider._source.get_skills())
finance_skill = next(s for s in skills if s.frontmatter.name == "financial-research")
instructions = finance_skill.content

# 3. MOCK CONTEXTFORGE TOOL BINDING 
# In a real app, this connects to http://localhost:4444. 
# Here we define the tool signature the agent will request.
def search_company_database(ticker: str) -> str:
    """Search company database. Handled by ContextForge."""
    import requests
    # Requesting the ContextForge Gateway endpoint
    # (Mocked for this example, replace with actual ContextForge API call)
    return "Data requested via ContextForge."

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
    print(result.text)

if __name__ == "__main__":
    asyncio.run(main())
