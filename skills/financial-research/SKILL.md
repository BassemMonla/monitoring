---
name: financial-research
description: >-
  Analyze a company by querying the internal database. Use this skill when asked about company performance or risks.
allowed-tools: search_company_database
---
# Financial Research Protocol

## Instructions
1. First, invoke the `search_company_database` tool using the exact stock ticker.
2. Analyze the returned internal data.
3. Formulate a final response formatted strictly as a Markdown table.
4. Include a "Risk Level" row based on your analysis of the data.
