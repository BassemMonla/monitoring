from agent_framework import ContextProvider

class ComplianceContextProvider(ContextProvider):
    """Proactively injects compliance rules before every LLM call."""
    
    def __init__(self):
        super().__init__(source_id="compliance_rules")
        
    async def before_run(self, *, agent, session, context, state) -> None:
        compliance_rule = (
            "SYSTEM DIRECTIVE: You are a strict financial analyst. "
            "Never guess financial numbers. If the tool returns no data, state 'UNAVAILABLE'."
        )
        context.extend_instructions(self.source_id, compliance_rule)
