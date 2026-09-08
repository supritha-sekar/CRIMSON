from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Subject, Case, Evidence, Relationship
from app.schemas import GraphData, GraphNode, GraphEdge, RelationshipOut, RelationshipCreate

router = APIRouter(prefix="/network", tags=["Network Analysis"])

@router.get("/graph", response_model=GraphData)
def get_network_graph(
    case_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
    seen_nodes = set()

    # Fetch subjects
    subj_query = db.query(Subject)
    if entity_type and entity_type != "ALL":
        subj_query = subj_query.filter(Subject.entity_type == entity_type)
    subjects = subj_query.all()

    for s in subjects:
        nid = f"SUBJ-{s.id}"
        seen_nodes.add(nid)
        nodes.append(GraphNode(
            id=nid,
            label=s.name,
            type=s.entity_type,
            risk_level=s.risk_level,
            details={"description": s.description, "risk_score": s.risk_score}
        ))

    # Fetch cases
    cases = db.query(Case).all()
    for c in cases:
        nid = f"CASE-{c.id}"
        seen_nodes.add(nid)
        nodes.append(GraphNode(
            id=nid,
            label=f"{c.case_number}: {c.title}",
            type="Case",
            risk_level=c.priority,
            details={"category": c.category, "status": c.status}
        ))

    # Fetch evidence items
    evidences = db.query(Evidence).all()
    for e in evidences:
        nid = f"EVI-{e.id}"
        seen_nodes.add(nid)
        nodes.append(GraphNode(
            id=nid,
            label=f"{e.evidence_number}: {e.title}",
            type="Evidence",
            risk_level="MEDIUM",
            details={"type": e.evidence_type, "source": e.source}
        ))

        # Case to Evidence automatically linked
        case_node_id = f"CASE-{e.case_id}"
        if case_node_id in seen_nodes:
            edges.append(GraphEdge(
                id=f"edge-c{e.case_id}-e{e.id}",
                source=case_node_id,
                target=nid,
                label="contains_evidence",
                confidence=1.0
            ))

    # Fetch DB Relationships
    db_rels = db.query(Relationship).all()
    for r in db_rels:
        prefix_map = {"Subject": "SUBJ", "Case": "CASE", "Evidence": "EVI"}
        s_prefix = prefix_map.get(r.source_type, "SUBJ")
        t_prefix = prefix_map.get(r.target_type, "SUBJ")

        s_id = f"{s_prefix}-{r.source_id}"
        t_id = f"{t_prefix}-{r.target_id}"

        if s_id in seen_nodes and t_id in seen_nodes:
            edges.append(GraphEdge(
                id=f"edge-rel-{r.id}",
                source=s_id,
                target=t_id,
                label=r.relation_type,
                confidence=r.confidence
            ))

    return GraphData(nodes=nodes, edges=edges)

@router.post("/relationships", response_model=RelationshipOut, status_code=201)
def create_relationship(rel_in: RelationshipCreate, db: Session = Depends(get_db)):
    db_rel = Relationship(
        source_type=rel_in.source_type,
        source_id=rel_in.source_id,
        target_type=rel_in.target_type,
        target_id=rel_in.target_id,
        relation_type=rel_in.relation_type,
        confidence=rel_in.confidence,
        notes=rel_in.notes
    )
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel
