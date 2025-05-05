from fastmcp import FastMCP
from typing import List, Optional
import random

# Initialize MCP server
authority = "Utilities"  # server name for grouping
mcp = FastMCP(authority)

# Dummy implementations
@mcp.tool(name="Email", description="Send an email to recipients")
def send_email(to: List[str], subject: str, body: str) -> dict:
    """
    Pretend to send an email. Returns a status dict.
    """
    print(f"[debug-server] send_email(to={to}, subject={subject})")
    message_id = f"msg_{random.randint(1000,9999)}"
    return {"status": "sent", "message_id": message_id, "recipients": to}

@mcp.tool(name="Summarize", description="Summarize a block of text")
def summarize_text(text: str, max_sentences: Optional[int] = 2) -> str:
    """
    Return the first `max_sentences` sentences of `text` as a summary.
    """
    print(f"[debug-server] summarize_text(text={{...}}, max_sentences={max_sentences})")
    sentences = text.split('.')
    summary = '.'.join(sentences[:max_sentences]).strip()
    if not summary.endswith('.'):
        summary += '.'
    return summary

@mcp.tool(name="Translation", description="Translate text into another language")
def translate_text(text: str, target_language: str) -> str:
    """
    Dummy translation: just wrap the text.
    """
    print(f"[debug-server] translate_text(text={{...}}, target_language={target_language})")
    return f"[Translated to {target_language}]: {text}"

@mcp.tool(name="NoteAggregation", description="Aggregate multiple note snippets into one document")
def aggregate_notes(notes: List[str]) -> str:
    """
    Concatenate notes with headings.
    """
    print(f"[debug-server] aggregate_notes(notes count={len(notes)})")
    aggregated = "\n---\n".join(notes)
    return aggregated

@mcp.tool(name="MeetingManager", description="Schedule or list meetings")
def manage_meeting(action: str, title: Optional[str] = None, time: Optional[str] = None) -> dict:
    """
    If action=='schedule', schedule a dummy meeting; if 'list', return a fixed list.
    """
    print(f"[debug-server] manage_meeting(action={action}, title={title}, time={time})")
    if action == 'schedule' and title and time:
        meeting_id = f"mtg_{random.randint(100,999)}"
        return {"status": "scheduled", "meeting_id": meeting_id, "title": title, "time": time}
    elif action == 'list':
        return {"meetings": [
            {"meeting_id":"mtg_123", "title":"Team Sync", "time":"2025-05-05T10:00:00"},
            {"meeting_id":"mtg_456", "title":"Project Kickoff", "time":"2025-05-06T15:00:00"}
        ]}
    else:
        return {"error": "Invalid action or missing parameters"}
    
@mcp.tool(name="WealthOutlook", description="Answer research queries on stock and market outlooks")
def wealth_outlook(query: str) -> str:
    """
    Dummy QnA: Returns a canned outlook based on the input query.
    """
    print(f"[debug-server] wealth_outlook(query={{...}})")
    # In a real implementation you'd hook into research data or an LLM here.
    return (
        f"[Outlook for “{query}”]: "
        "Based on historical trends and current market conditions, "
        "we expect moderate growth with occasional volatility. "
        "Please consult your advisor for tailored guidance."
    )


# Run the MCP server with SSE transport
if __name__ == "__main__":
    print("Starting Utilities MCP Server (SSE transport) on port 8001...")
    print("SSE endpoint: http://localhost:8001/sse")
    # Listen by default on port 8001 to avoid conflict
    mcp.run(transport="sse", host="0.0.0.0", port=8001)
