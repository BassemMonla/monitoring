import uvicorn
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("Internal Database Server")

@mcp.tool()
def search_company_database(ticker: str) -> str:
    """Securely query the internal financial database for a stock ticker."""
    db = {
        "NVDA": "Internal Data: Q1 Revenue up 18%. High reliance on data center spend.",
        "MSFT": "Internal Data: Cloud segment stabilizing. AI integration complete."
    }
    return db.get(ticker.upper(), f"No internal data found for {ticker}.")

if __name__ == "__main__":
    # Run an SSE server on port 8000. 
    # Use 0.0.0.0 so the Docker container can access it via host.docker.internal
    mcp.run(transport="sse")
