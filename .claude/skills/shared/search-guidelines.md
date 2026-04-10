# Research Search Guidelines (Shared Reference)

## Query Construction
- Convert the user's Japanese research topic into effective search terms
- Use both Japanese AND English queries to maximize coverage
- Include field-specific terms (economics, econometrics, household consumption, etc.)
- Add methodological terms when relevant (difference-in-differences, panel data, etc.)

## Result Formatting
- Return results as a concise markdown table or bullet list
- Each result: title, authors (abbreviated), year, source, 1-line relevance note
- Maximum 10 results per query unless user requests more
- Flag open-access availability when detectable

## Token Efficiency
- Do NOT paste full abstracts — summarize relevance in 1 sentence
- Do NOT include URLs unless the user asks
- Group results by relevance, most relevant first
- If no results found, suggest query refinements rather than returning empty

## Importance Stratification
- **High**: Directly addresses this thesis's research question, uses similar methodology or data
- **Medium**: Related topic or methodology, partially applicable
- **Low**: Tangentially related, background knowledge

## Verification
- Before reporting a paper, confirm it appears in search results (not hallucinated)
- If a paper cannot be verified via WebSearch, mark it as `【未検証】`
- Never fabricate DOIs, journal names, or page numbers
