"""AI Interview Coach - A high-fidelity simulator for technical interview mastery."""

import argparse
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, TypedDict

from bindu.penguin.bindufy import bindufy  # type: ignore[import-untyped]
from dotenv import load_dotenv
from exa_py import Exa
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from mem0 import MemoryClient  # type: ignore[import-untyped]

# Load environment variables
load_dotenv()


# --- STATE DEFINITION ---
class InterviewState(TypedDict):
    """Schema for the Interview Coach state machine."""

    question: str
    user_memory: str  # Past user context retrieved from Mem0
    exa_research: str  # Real-world engineering context retrieved from Exa
    intent_summary: str
    narrative_script: str
    alternatives: str
    final_response: str


# --- GLOBAL SINGLETONS & CACHE ---
graph: Any = None
global_llm: ChatOpenAI | None = None
mem0_client: MemoryClient | None = None
exa_client: Exa | None = None
model_name: str | None = None
_initialized = False
_init_lock = asyncio.Lock()
_skills_cache: dict[str, str] = {}  # In-memory cache for prompt instructions


def load_skill(skill_name: str) -> str:
    """Extract persona instructions from skills.md with in-memory caching."""
    if skill_name in _skills_cache:
        return _skills_cache[skill_name]

    path = Path(__file__).parent / "skills" / "skills.md"
    if not path.exists():
        return "You are a professional technical interviewer."

    try:
        content = path.read_text(encoding="utf-8")
        pattern = rf"##\s+{re.escape(skill_name)}\s*\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        result = match.group(1).strip() if match else "Provide a detailed script."

    except Exception as e:
        print(f"⚠️ Error loading skill {skill_name}: {e}")
        return "Provide a professional response."

    else:
        _skills_cache[skill_name] = result
        return result


# --- GRAPH NODES ---


async def analyzer_node(state: InterviewState) -> dict[str, str]:
    """Identify intent and fetch real-world context via Exa."""
    print("\n" + "=" * 50)
    print("🔍 [STEP 1] ANALYZER: Identifying hidden intent & researching...")

    # 1. External Research: Exa Search for real-world grounding
    exa_context = "No external research needed."
    if exa_client:
        try:
            # Search for real engineering blog posts to authenticate the narrative
            search_query = f"engineering blog post incident report about: {state.get('question', '')}"
            exa_res = exa_client.search_and_contents(search_query, num_results=1, highlights=True)
            if exa_res.results:
                exa_context = f"Real-world inspiration: {exa_res.results[0].title} - {exa_res.results[0].url}"
                print(f"🌐 EXA FOUND: {exa_context}")
        except Exception as e:
            print(f"⚠️ Exa Search failed (skipping gracefully): {e}")

    # 2. LLM Intent Analysis
    sys_prompt = load_skill("🔍 Node 1: The Forensic Intent Miner")
    if global_llm is None:
        raise RuntimeError("LLM not initialized")  # noqa: TRY003

    # Inject cross-session user memory into the analysis context
    context = f"User History: {state.get('user_memory', 'None')}\nQuestion: {state.get('question', '')}"

    response = await global_llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=context)])

    content = str(response.content)
    print(f"DEBUG OUTPUT:\n{content}")
    return {"intent_summary": content, "exa_research": exa_context}


async def narrative_node(state: InterviewState) -> dict[str, str]:
    """Draft the core 30-second STAR response."""
    print("\n" + "=" * 50)
    print("🗣️ [STEP 2] NARRATIVE: Drafting first-person script...")
    sys_prompt = load_skill("🗣️ Node 2: The Battle-Hardened Storyteller")

    # Inject Exa Research into the narrative generation
    ctx = (
        f"Question: {state.get('question', '')}\n"
        f"Intent Analysis: {state.get('intent_summary', '')}\n"
        f"Real-World Context: {state.get('exa_research', '')}"
    )

    if global_llm is None:
        raise RuntimeError("LLM not initialized")  # noqa: TRY003
    response = await global_llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=ctx)])

    content = str(response.content)
    content = re.sub(r"\[.*?\]|\*.*?\*", "", content).strip()
    print(f"DEBUG OUTPUT:\n{content}")
    return {"narrative_script": content}


async def alternative_node(state: InterviewState) -> dict[str, str]:
    """Inject senior-level trade-off analysis with software-level guardrails."""
    print("\n" + "=" * 50)
    print("⚖️ [STEP 3] ALTERNATIVES: Adding seniority depth...")
    sys_prompt = load_skill("⚖️ Node 3: The Pragmatic Principal Architect")
    ctx = f"Core Answer: {state.get('narrative_script', '')}"

    if global_llm is None:
        raise RuntimeError("LLM not initialized")  # noqa: TRY003
    response = await global_llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=ctx)])

    content = str(response.content)

    # Apply strict formatting guardrails
    content = re.sub(r"\[.*?\]|\*.*?\*", "", content)
    content = re.sub(r"^[A-Za-z]+:\s*", "", content.strip()).strip()

    # Enforce mandatory opening phrase to prevent roleplay artifacts
    if not content.lower().startswith("we considered"):
        if "we considered" in content.lower():
            idx = content.lower().find("we considered")
            content = "W" + content[idx + 1 :]
        else:
            content = f"We considered alternative architectural strategies, but rejected them due to operational overhead. {content}"

    print(f"DEBUG OUTPUT:\n{content}")
    return {"alternatives": content}


async def polish_node(state: InterviewState) -> dict[str, str]:
    """Synthesize the final narrative for verbal delivery."""
    print("\n" + "=" * 50)
    print("✨ [STEP 4] POLISH: Finalizing interview-ready response...")
    sys_prompt = load_skill("✨ Node 4: The Executive Delivery Coach")
    ctx = f"Narrative: {state.get('narrative_script', '')}\nTrade-offs: {state.get('alternatives', '')}"

    if global_llm is None:
        raise RuntimeError("LLM not initialized")  # noqa: TRY003
    response = await global_llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=ctx)])

    content = str(response.content)
    content = re.sub(r"\[.*?\]|\*.*?\*", "", content).strip()
    print(f"DEBUG OUTPUT:\n{content}")
    print("=" * 50 + "\n")
    return {"final_response": content}


# --- ORCHESTRATION & INITIALIZATION ---


async def initialize_all(env: dict[str, str] | None = None) -> None:
    """Initialize LLM, Graph, Exa, and Mem0 clients."""
    global graph, global_llm, mem0_client, exa_client

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    mem0_api_key = os.getenv("MEM0_API_KEY")
    exa_api_key = os.getenv("EXA_API_KEY")

    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY required")  # noqa: TRY003

    print("🔧 Initializing Tools and Agent...")

    # 1. Initialize Mem0
    if mem0_api_key:
        mem0_client = MemoryClient(api_key=mem0_api_key)
        print("🧠 Mem0 memory enabled")

    # 2. Initialize Exa
    if exa_api_key:
        exa_client = Exa(api_key=exa_api_key)
        print("🌐 Exa Search enabled")

    # 3. Initialize LLM
    # Dictionary unpacking is used to safely bypass strict static type checking
    llm_kwargs: dict[str, Any] = {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": openrouter_api_key,
        "model": model_name or "anthropic/claude-3-haiku",
        "temperature": 0.7,
        "timeout": 45.0,
        "max_retries": 3,
    }
    global_llm = ChatOpenAI(**llm_kwargs)

    # 4. Compile State Graph
    builder = StateGraph(InterviewState)  # type: ignore[arg-type]
    builder.add_node("analyzer", analyzer_node)
    builder.add_node("narrative", narrative_node)
    builder.add_node("alternative", alternative_node)
    builder.add_node("polish", polish_node)

    builder.set_entry_point("analyzer")
    builder.add_edge("analyzer", "narrative")
    builder.add_edge("narrative", "alternative")
    builder.add_edge("alternative", "polish")
    builder.add_edge("polish", END)

    graph = builder.compile()
    print("✅ Interview Graph Compiled")


async def run_agent(messages: list[dict[str, str]]) -> Any:
    """Execute the graph with Memory and Search integration."""
    user_input = messages[-1].get("content", "").strip()

    # TODO: Replace with dynamic user ID from authentication context
    user_id = "bindu_candidate_default"

    # Input validation and sanitization
    if not user_input:
        return "Please provide an interview question."
    if len(user_input) > 1500:
        print("⚠️ Warning: Truncated excessively long user input.")
        user_input = user_input[:1500] + "..."

    # Fetch prior cross-session user interactions
    past_memory = ""
    if mem0_client:
        try:
            memories = mem0_client.search(user_input, user_id=user_id)
            if memories:
                past_memory = "\n".join([m["memory"] for m in memories])
        except Exception as e:
            print(f"⚠️ Mem0 fetch failed: {e}")

    try:
        # Execute the primary state graph
        result = await graph.ainvoke({"question": user_input, "user_memory": past_memory})
        final_answer = result.get("final_response", "Error generating response.")

        # Persist the current interaction to memory
        if mem0_client:
            try:
                mem0_client.add(
                    [{"role": "user", "content": user_input}, {"role": "assistant", "content": final_answer}],
                    user_id=user_id,
                )
            except Exception as e:
                print(f"⚠️ Mem0 save failed: {e}")

    except Exception as e:
        print(f"❌ Graph Execution Error: {e!s}")
        return "Operational Error: Unable to process the interview request at this time."

    return final_answer


async def handler(messages: list[dict[str, str]]) -> Any:
    """Bindu protocol handler."""
    global _initialized
    async with _init_lock:
        if not _initialized:
            await initialize_all()
            _initialized = True
    return await run_agent(messages)


def main() -> None:
    """CLI entry point."""
    global model_name
    parser = argparse.ArgumentParser(description="AI Interview Coach")
    parser.add_argument("--model", type=str, default="anthropic/claude-3-haiku")
    args = parser.parse_args()
    model_name = args.model

    config_path = Path(__file__).parent / "agent_config.json"
    with open(config_path) as f:
        config = json.load(f)

    print(f"🤖 Coaching with model: {model_name}")
    try:
        bindufy(config, handler)
    finally:
        print("\n🧹 Session ended. Resources released.")


if __name__ == "__main__":
    main()
