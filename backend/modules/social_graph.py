<<<<<<< HEAD
from typing import Any


def get_social_graph_score(merchant_id: str) -> dict[str, Any]:
    return {
        "merchant_id": merchant_id,
        "social_score": 0.62,
        "signals": {
            "connections": 18,
            "community_score": 0.7,
        },
        "status": "stub",
    }
=======
# backend/modules/social_graph.py
# TyasaaTrust - Social Graph Engine
#
# Responsibilities:
#   1. Build a transaction graph from merchant-to-merchant transactions.
#   2. Detect fraud rings: k-core candidate filter + directed-cycle confirmation.
#   3. Detect repeated ring formation in a short window (40% penalty trigger).
#   4. Produce a transparent social/reputation score in the range 0 - 1000.
#
# Design notes:
#   - k-core finds the densely connected group. On this data the legitimate
#     activity is a star (degree-1 sinks) and the ring is a closed loop, so
#     the 2-core is exactly the ring. k-core alone only proves density, not
#     fraud, so every k-core candidate is confirmed with directed cycle
#     detection before any penalty is applied. This avoids flagging genuine
#     dense merchant communities as fraud.
#   - The score is built additively from explainable parts so a judge or a
#     loan officer can read exactly why a merchant scored what they did.
#   - Pure Python + NetworkX. No FastAPI, no Redis, no DB. The analysis
#     function accepts injected transactions so it can later be fed from the
#     ingestion endpoint / Postgres instead of the mock generator.

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import networkx as nx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Tunable parameters
# ---------------------------------------------------------------------------

SCORE_FLOOR:    int = 0
SCORE_CEILING:  int = 1000
BASELINE_SCORE: int = 500          # neutral start (also the cold-start score)

# Reputation bonus (added to baseline for clean merchants), max +500.
MAX_BREADTH_BONUS:    int = 300    # from number of distinct legitimate partners
MAX_CENTRALITY_BONUS: int = 200    # from PageRank position in the legit network
BREADTH_SATURATION:   int = 6      # distinct partners needed for full breadth bonus

# Fraud penalties.
RING_BASE_PENALTY:   int   = 250   # flat hit for being in a confirmed ring
REPEAT_RING_PENALTY: float = 0.40  # 40% multiplicative penalty for repeat rings

# k-core candidate filter.
KCORE_K: int = 2                   # minimum coreness to be a fraud candidate

# Ring-timing parameters.
ROUND_WINDOW_DAYS:  int = 7        # transactions this close = one ring formation
REPEAT_WINDOW_DAYS: int = 120      # >=2 formations within this span = "repeat"

# Wash-trading amount tolerance: edges whose amounts are within this fraction
# of each other look like equal-amount circular transfers.
EQUAL_AMOUNT_TOLERANCE: float = 0.10


async def fetch_transactions_from_db(db: AsyncSession) -> list[dict]:
    rows = await db.execute(text("""
        SELECT transaction_id, initiating_merchant_id, receiving_merchant_id,
               transaction_amount, transaction_date
        FROM transactions
    """))
    return [
        {
            "transaction_id": str(r.transaction_id),
            "initiating_merchant_id": r.initiating_merchant_id,
            "receiving_merchant_id": r.receiving_merchant_id,
            "transaction_amount": float(r.transaction_amount),
            "transaction_date": r.transaction_date.isoformat(),
        }
        for r in rows.all()
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def _build_digraph(transactions: list[dict]) -> nx.MultiDiGraph:
    """Directed multigraph: one edge per transaction, carrying date + amount."""
    graph = nx.MultiDiGraph()
    for tx in transactions:
        graph.add_edge(
            tx["initiating_merchant_id"],
            tx["receiving_merchant_id"],
            amount=float(tx["transaction_amount"]),
            tx_date=_parse_date(tx["transaction_date"]),
        )
    return graph


def _undirected_simple(graph: nx.MultiDiGraph) -> nx.Graph:
    """Undirected simple graph for k-core (k-core ignores direction/parallels)."""
    simple = nx.Graph()
    simple.add_nodes_from(graph.nodes())
    for u, v in graph.edges():
        if u != v:
            simple.add_edge(u, v)
    return simple


def _group_into_formations(tx_dates: list[date]) -> list[list[date]]:
    """Cluster transaction dates into ring 'formations' by time proximity."""
    if not tx_dates:
        return []
    ordered = sorted(tx_dates)
    formations: list[list[date]] = [[ordered[0]]]
    for current in ordered[1:]:
        if (current - formations[-1][-1]).days <= ROUND_WINDOW_DAYS:
            formations[-1].append(current)
        else:
            formations.append([current])
    return formations


def _has_repeat_within_window(formations: list[list[date]]) -> bool:
    """True if two consecutive formations fall within REPEAT_WINDOW_DAYS."""
    if len(formations) < 2:
        return False
    starts = [f[0] for f in formations]
    return any(
        (starts[i + 1] - starts[i]).days <= REPEAT_WINDOW_DAYS
        for i in range(len(starts) - 1)
    )


# ---------------------------------------------------------------------------
# Fraud-ring detection
# ---------------------------------------------------------------------------

def _detect_fraud_rings(graph: nx.MultiDiGraph) -> list[dict[str, Any]]:
    """
    Find fraud rings using k-core candidate filtering + cycle confirmation.

    Returns one record per confirmed ring:
        {
          "members":      [ids in the cycle],
          "formations":   int,   # how many times the ring re-formed
          "repeat":       bool,  # >=2 formations within REPEAT_WINDOW_DAYS
          "equal_amount": bool,  # circular transfers are near-equal amounts
        }
    """
    if graph.number_of_nodes() == 0:
        return []

    # --- Step 1: k-core candidate filter ------------------------------------
    undirected = _undirected_simple(graph)
    core_numbers = nx.core_number(undirected)
    candidate_nodes = {n for n, c in core_numbers.items() if c >= KCORE_K}
    if not candidate_nodes:
        return []

    # --- Step 2: confirm with directed cycles inside the candidate set ------
    candidate_digraph = nx.DiGraph()
    candidate_digraph.add_nodes_from(candidate_nodes)
    for u, v in graph.edges():
        if u in candidate_nodes and v in candidate_nodes and u != v:
            candidate_digraph.add_edge(u, v)

    rings: list[dict[str, Any]] = []
    seen: set[frozenset] = set()

    for cycle in nx.simple_cycles(candidate_digraph):
        if len(cycle) < 2:
            continue
        key = frozenset(cycle)
        if key in seen:
            continue
        seen.add(key)

        ring_set = set(cycle)

        # Collect every transaction that flows along a cycle edge.
        cycle_edges = {
            (cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))
        }
        amounts: list[float] = []
        tx_dates: list[date] = []
        for u, v, data in graph.edges(data=True):
            if (u, v) in cycle_edges:
                amounts.append(data["amount"])
                tx_dates.append(data["tx_date"])

        formations = _group_into_formations(tx_dates)
        repeat = _has_repeat_within_window(formations)

        equal_amount = False
        if amounts:
            lo, hi = min(amounts), max(amounts)
            equal_amount = hi > 0 and (hi - lo) / hi <= EQUAL_AMOUNT_TOLERANCE

        rings.append(
            {
                "members": sorted(ring_set),
                "formations": len(formations),
                "repeat": repeat,
                "equal_amount": equal_amount,
            }
        )

    return rings


# ---------------------------------------------------------------------------
# Reputation (legitimate network position)
# ---------------------------------------------------------------------------

def _legit_subgraph(graph: nx.MultiDiGraph, fraud_nodes: set[str]) -> nx.DiGraph:
    """Directed graph with all fraud-ring nodes removed, edges deduplicated."""
    legit = nx.DiGraph()
    legit.add_nodes_from(n for n in graph.nodes() if n not in fraud_nodes)
    for u, v in graph.edges():
        if u not in fraud_nodes and v not in fraud_nodes and u != v:
            legit.add_edge(u, v)
    return legit


def _reputation_bonus(
    merchant_id: str,
    legit: nx.DiGraph,
    pagerank: dict[str, float],
    max_pr: float,
) -> dict[str, Any]:
    """Compute the additive reputation bonus (0 .. 500) for a clean merchant."""
    if merchant_id in legit:
        distinct_partners = legit.out_degree(merchant_id) + legit.in_degree(merchant_id)
    else:
        distinct_partners = 0

    breadth_ratio = min(distinct_partners, BREADTH_SATURATION) / BREADTH_SATURATION
    breadth_bonus = breadth_ratio * MAX_BREADTH_BONUS

    pr = pagerank.get(merchant_id, 0.0)
    centrality_ratio = (pr / max_pr) if max_pr > 0 else 0.0
    centrality_bonus = centrality_ratio * MAX_CENTRALITY_BONUS

    return {
        "distinct_legit_partners": distinct_partners,
        "breadth_bonus": round(breadth_bonus, 1),
        "centrality_bonus": round(centrality_bonus, 1),
        "total": round(breadth_bonus + centrality_bonus, 1),
    }


# ---------------------------------------------------------------------------
# Full analysis (compute once, score any merchant)
# ---------------------------------------------------------------------------

def analyze_social_graph(transactions: list[dict]) -> dict[str, Any]:
    """
    Run the full social-graph analysis over a transaction set.

    Returns a reusable analysis object containing every merchant's score and
    the detected rings. The ingestion endpoint can call this once and serve
    many merchant lookups from the result.
    """
    graph = _build_digraph(transactions)
    rings = _detect_fraud_rings(graph)

    fraud_nodes: set[str] = set()
    repeat_nodes: set[str] = set()
    for ring in rings:
        fraud_nodes.update(ring["members"])
        if ring["repeat"]:
            repeat_nodes.update(ring["members"])

    legit = _legit_subgraph(graph, fraud_nodes)
    pagerank = nx.pagerank(legit) if legit.number_of_edges() > 0 else {}
    max_pr = max(pagerank.values()) if pagerank else 0.0

    merchant_scores: dict[str, dict[str, Any]] = {}
    for merchant_id in graph.nodes():
        merchant_scores[merchant_id] = _score_merchant(
            merchant_id, legit, pagerank, max_pr, fraud_nodes, repeat_nodes, rings
        )

    return {
        "rings": rings,
        "fraud_nodes": sorted(fraud_nodes),
        "repeat_nodes": sorted(repeat_nodes),
        "merchant_scores": merchant_scores,
    }


def _score_merchant(
    merchant_id: str,
    legit: nx.DiGraph,
    pagerank: dict[str, float],
    max_pr: float,
    fraud_nodes: set[str],
    repeat_nodes: set[str],
    rings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the 0-1000 social score for one merchant with full reasoning."""
    in_ring = merchant_id in fraud_nodes
    repeat = merchant_id in repeat_nodes

    if in_ring:
        # Ring members get the flat penalty and no reputation credit. The
        # partners they "trade" with are fraudulent, so they earn no breadth.
        raw_score = BASELINE_SCORE - RING_BASE_PENALTY
        reputation = {
            "distinct_legit_partners": 0,
            "breadth_bonus": 0.0,
            "centrality_bonus": 0.0,
            "total": 0.0,
        }
    else:
        reputation = _reputation_bonus(merchant_id, legit, pagerank, max_pr)
        raw_score = BASELINE_SCORE + reputation["total"]

    # Repeated ring formation in a short window: 40% multiplicative penalty.
    repeat_applied = False
    if repeat:
        raw_score = raw_score * (1 - REPEAT_RING_PENALTY)
        repeat_applied = True

    final_score = int(round(max(SCORE_FLOOR, min(SCORE_CEILING, raw_score))))
    member_of = [r for r in rings if merchant_id in r["members"]]

    return {
        "merchant_id": merchant_id,
        "social_score": final_score,                                        # 0 - 1000 headline
        "social_score_normalized": round(final_score / SCORE_CEILING, 4),   # 0 - 1 for fusion
        "is_fraud_ring_member": in_ring,
        "repeat_ring_penalty_applied": repeat_applied,
        "rings": member_of,
        "reputation": reputation,
        "status": "scored",
    }


# ---------------------------------------------------------------------------
# Public API - the surface the router / fusion touches
# ---------------------------------------------------------------------------

def get_social_graph_score(
    merchant_id: str,
    transactions: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Return the social-graph score for a single merchant.

    If `transactions` is omitted, the deterministic mock data from
    mock_generator is used (drop-in compatible with the old stub).

    A merchant with no transactions returns the neutral baseline (cold-start),
    the intended behaviour for a brand-new unbanked merchant.
    """
    if transactions is None:
        from data.mock_generator import generate_transactions
        transactions = generate_transactions()
    txns = transactions
    analysis = analyze_social_graph(txns)

    if merchant_id in analysis["merchant_scores"]:
        return analysis["merchant_scores"][merchant_id]

    return {
        "merchant_id": merchant_id,
        "social_score": BASELINE_SCORE,
        "social_score_normalized": round(BASELINE_SCORE / SCORE_CEILING, 4),
        "is_fraud_ring_member": False,
        "repeat_ring_penalty_applied": False,
        "rings": [],
        "reputation": {
            "distinct_legit_partners": 0,
            "breadth_bonus": 0.0,
            "centrality_bonus": 0.0,
            "total": 0.0,
        },
        "status": "cold_start_no_history",
    }


if __name__ == "__main__":
    import json
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from data.mock_generator import generate_transactions, MERCHANTS

    txns = generate_transactions()
    print(f"Loaded {len(txns)} transactions covering {len(MERCHANTS)} merchants\n")

    result = analyze_social_graph(txns)

    # ── Fraud rings ──────────────────────────────────────────────
    rings = result["rings"]
    print(f"{'='*60}")
    print(f"FRAUD RINGS DETECTED: {len(rings)}")
    print(f"{'='*60}")
    for i, ring in enumerate(rings, 1):
        print(f"\n  Ring {i}:")
        print(f"    Members      : {', '.join(ring['members'])}")
        print(f"    Formations   : {ring['formations']}")
        print(f"    Repeat ring  : {ring['repeat']}")
        print(f"    Equal amounts: {ring['equal_amount']}")

    print(f"\nFraud nodes  : {result['fraud_nodes']}")
    print(f"Repeat nodes : {result['repeat_nodes']}")

    # ── Per-merchant scores ──────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"MERCHANT SCORES")
    print(f"{'='*60}")
    print(f"{'Merchant ID':<16} {'Name':<22} {'Score':>6}  {'Fraud':>5}  {'Repeat':>6}  Status")
    print(f"{'-'*16} {'-'*22} {'-'*6}  {'-'*5}  {'-'*6}  {'-'*20}")

    for mid, s in sorted(result["merchant_scores"].items(), key=lambda x: -x[1]["social_score"]):
        name = MERCHANTS.get(mid, "unknown")
        fraud = "YES" if s["is_fraud_ring_member"] else "no"
        repeat = "YES" if s["repeat_ring_penalty_applied"] else "no"
        print(
            f"{mid:<16} {name:<22} {s['social_score']:>6}  {fraud:>5}  {repeat:>6}  {s['status']}"
        )
>>>>>>> fb57974 (Add social graph fraud-ring engine and transaction seed data)
