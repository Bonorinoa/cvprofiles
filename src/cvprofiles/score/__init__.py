"""SCORE state — ingest / validate / normalize / freeze."""

from __future__ import annotations

from cvprofiles.score.pipeline import ScoreResult, run_score, write_score_artifacts

__all__ = ["ScoreResult", "run_score", "write_score_artifacts"]
