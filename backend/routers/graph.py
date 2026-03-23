import logging
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.dependencies import neo4j_manager, state
from backend.config import QUERY_TOP_K

# Create the router instance
router = APIRouter(tags=["Graph & Query"])


class QueryRequest(BaseModel):
    question: str
    mode: str = "mix"
    only_need_context: bool = False
    return_nodes: bool = False


class QueryLogCapture(logging.Handler):
    """Captures the 'Query nodes:' log line emitted by LightRAG during a query."""

    _QUERY_NODES_RE = re.compile(r"Query nodes?:\s*(.+?)(?:\s*\(top_k|$)")

    def __init__(self):
        super().__init__()
        self.entity_names: list[str] = []

    def emit(self, record: logging.LogRecord):
        msg = record.getMessage()
        m = self._QUERY_NODES_RE.search(msg)
        if m:
            raw = m.group(1)
            self.entity_names = [e.strip() for e in raw.split(",") if e.strip()]


@router.get("/graph")
async def get_graph(limit: int = 300, search: str = ""):
    try:
        return await neo4j_manager.get_graph(limit, search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query(req: QueryRequest):
    if state.rag is None:
        raise HTTPException(status_code=503, detail="RAGAnything not initialised yet")

    capture = QueryLogCapture() if req.return_nodes else None
    if capture:
        for name in ["lightrag", "raganything"]:
            logging.getLogger(name).addHandler(capture)
    try:
        answer = await state.rag.aquery(
            req.question, mode=req.mode, top_k=QUERY_TOP_K, vlm_enhanced=False
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    finally:
        if capture:
            for name in ["lightrag", "raganything"]:
                logging.getLogger(name).removeHandler(capture)

    if req.only_need_context:
        if not answer:
            return {"context": "No relevant information found.", "mode": req.mode}
        return {"context": str(answer), "mode": req.mode}

    result: dict = {
        "answer": str(answer) if answer else "No results found.",
        "mode": req.mode,
    }

    if req.return_nodes and capture:
        result["highlighted_nodes"] = await neo4j_manager.resolve_node_ids(
            capture.entity_names
        )

    return result
