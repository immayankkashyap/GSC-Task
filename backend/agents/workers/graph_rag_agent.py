from graph.state import Evidence, AgentStep, GraphState

# Hardcoded knowledge graph for Task 1.
# This will be replaced by a real graph DB (e.g. Neo4j) in a later task.
ENTITY_GRAPH: dict[str, dict] = {
    "infosys": {"sector": "IT", "risks": ["currency", "visa_policy"]},
    "hdfc bank": {"sector": "Banking", "risks": ["interest_rate", "NPA"]},
    "reliance": {"sector": "Conglomerate", "risks": ["oil_price", "regulatory"]},
    "tcs": {"sector": "IT", "risks": ["currency", "attrition"]},
    "nsei": {"sector": "Index", "risks": ["macro", "FII_flows"]},
    "nifty": {"sector": "Index", "risks": ["macro", "FII_flows"]},
}


async def graph_rag_node(state: GraphState) -> dict:
    """
    Entity-level knowledge graph traversal worker.
    Looks up entities mentioned in the query and returns their sector/risk profile.
    Returns only the keys this node updates.
    """
    step = AgentStep(
        agent_name="graph_rag",
        status="running",
        summary="Traversing entity knowledge graph...",
        detail="Multi-hop entity relationship lookup",
    )

    query_lower = state["query"].lower()
    evidence: list[Evidence] = []

    for entity, props in ENTITY_GRAPH.items():
        if entity in query_lower:
            passage = (
                f"{entity.title()}: sector={props['sector']}, "
                f"key_risks={props['risks']}"
            )
            evidence.append(
                Evidence(
                    source=f"Knowledge Graph: {entity.title()}",
                    passage=passage,
                    relevance_score=0.85,
                )
            )

    step["status"] = "done"
    step["summary"] = f"Entity relationships mapped ({len(evidence)} entities found)"

    return {"evidence": evidence, "steps": [step]}
