"""FastAPI application exposing health summaries and metrics."""

from __future__ import annotations

import logging
import os
from typing import Iterable

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_session
from .health import build_health_summary
from .metrics import record_parse_result
from .models import SourceStatus
from .schemas import HealthSummary, ParseResult, SourceStatusCreate, SourceStatusRead

logger = logging.getLogger("solid-memory")
logging.basicConfig(level=logging.INFO)

resource = Resource.create({"service.name": "solid-memory"})
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

trace.set_tracer_provider(tracer_provider)
LoggingInstrumentor().instrument(set_logging_format=True)

app = FastAPI(title="Solid Memory", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

Base.metadata.create_all(bind=engine)


def get_db_session() -> Iterable[Session]:
    with get_session() as session:
        yield session


@app.post("/sources", response_model=SourceStatusRead, status_code=status.HTTP_201_CREATED)
def register_source(payload: SourceStatusCreate, session: Session = Depends(get_db_session)) -> SourceStatus:
    existing = session.scalar(select(SourceStatus).where(SourceStatus.source_name == payload.source_name))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Source already registered")
    source = SourceStatus(source_name=payload.source_name, notes=payload.notes, status="unknown")
    session.add(source)
    session.flush()
    logger.info("Registered source %s", payload.source_name)
    return source


@app.post("/sources/{source_name}/parse", response_model=SourceStatusRead)
def report_parse_result(
    source_name: str, payload: ParseResult, session: Session = Depends(get_db_session)
) -> SourceStatus:
    source = session.scalar(select(SourceStatus).where(SourceStatus.source_name == source_name))
    if not source:
        source = SourceStatus(source_name=source_name)
        session.add(source)
        session.flush()

    source.mark_attempt()
    if payload.success:
        source.mark_success()
    else:
        source.mark_failure(payload.notes)
    record_parse_result(source_name, payload.success)
    logger.info(
        "Recorded parse result for %s: %s", source_name, "success" if payload.success else "failure"
    )
    return source


@app.get("/health", response_model=HealthSummary)
def health(session: Session = Depends(get_db_session)) -> HealthSummary:
    sources = session.scalars(select(SourceStatus)).all()
    return build_health_summary(sources)


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/sources", response_model=list[SourceStatusRead])
def list_sources(session: Session = Depends(get_db_session)) -> list[SourceStatus]:
    return session.scalars(select(SourceStatus)).all()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)
