#!/usr/bin/env python3
"""
ModelRed SDK end-to-end test harness (LIVE ONLY)

This script exercises both the sync and async clients against your live API.
It will:
  1) Print available models (so you can copy an ID)
  2) Auto-pick TWO probe packs (first from owned + first from imported; falls back
     to next available if one category is empty)
  3) Create an assessment with your selected model and those packs
  4) List assessments
  5) Fetch assessment details
  6) Attempt to cancel (expected to be forbidden for API-key users)

Required environment variables:
  - MODELRED_API_KEY     : your ModelRed API key (mr_...)
  - DETECTOR_PROVIDER    : "openai" or "anthropic"
  - DETECTOR_API_KEY     : detector LLM key
  - DETECTOR_MODEL       : detector model string (e.g., "gpt-4o-mini", "claude-3-5-sonnet-20241022")
  - TEST_MODEL_ID        : an existing registered model ID in your org (see printed list)

Usage:
  uv run python src/test_runner.py
  # or
  python src/test_runner.py
"""
from __future__ import annotations

import os
import sys
import asyncio
import logging
from typing import Any, Dict, List, Tuple

# ---- logging setup ----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("modelred-tests")

# Import your SDK (assumes it's importable in PYTHONPATH)
try:
    from modelred import ModelRed, AsyncModelRed, __version__
    from modelred.errors import ModelRedError
except Exception as e:
    log.error("Failed to import modelred SDK. Ensure it's installed and on PYTHONPATH.")
    raise


# ------------------
# Utilities
# ------------------
def banner(title: str):
    line = "=" * 80
    log.info("\n%s\n%s\n%s", line, title, line)


def require_env(name: str) -> str:
    val = os.getenv(name, "").strip()
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def pick_two_probe_packs(
    owned: Dict[str, Any], imported: Dict[str, Any]
) -> Tuple[str, str]:
    """
    Choose two distinct probe pack IDs, preferring one owned + one imported.
    If one category is empty, take the first two from the other.
    """
    owned_list = owned.get("data") or []
    imported_list = imported.get("data") or []

    candidates: List[str] = []
    if owned_list:
        candidates.append(owned_list[0]["id"])
    if imported_list:
        candidates.append(imported_list[0]["id"])

    if len(candidates) < 2:
        # Fill from remaining items across both lists (skip duplicates)
        all_ids = [p["id"] for p in owned_list] + [p["id"] for p in imported_list]
        for pid in all_ids:
            if pid not in candidates:
                candidates.append(pid)
            if len(candidates) >= 2:
                break

    if len(candidates) < 2:
        raise RuntimeError(
            "Could not find two probe packs (owned/imported). Please create/import more packs."
        )

    return candidates[0], candidates[1]


# ------------------
# Sync tests
# ------------------
def run_sync_tests():
    banner("SYNC CLIENT TESTS")

    client = ModelRed(
        api_key=require_env("MODELRED_API_KEY"),
        timeout=20.0,
    )

    # List models and print them so you can copy an ID
    log.info("Listing models...")
    models = client.list_models()
    if not (isinstance(models, dict) and models.get("success")):
        raise RuntimeError(f"Unexpected models response: {models!r}")

    model_items = models.get("data") or []
    log.info("Found %d models:", len(model_items))
    for m in model_items:
        log.info(
            "  → ID: %s | Name: %s | Provider: %s",
            m.get("id"),
            m.get("displayName") or m.get("modelName"),
            m.get("provider"),
        )

    model_id = require_env("TEST_MODEL_ID")

    # List probe packs (owned + imported)
    log.info("Listing owned probe packs...")
    owned = client.list_owned_probes(page_size=10)
    if not (isinstance(owned, dict) and owned.get("success")):
        raise RuntimeError(f"Unexpected owned packs response: {owned!r}")
    log.info("Owned packs count: %d", len(owned.get("data") or []))

    log.info("Listing imported probe packs...")
    imported = client.list_imported_probes(page_size=10)
    if not (isinstance(imported, dict) and imported.get("success")):
        raise RuntimeError(f"Unexpected imported packs response: {imported!r}")
    log.info("Imported packs count: %d", len(imported.get("data") or []))

    # Select two packs automatically
    pack_a, pack_b = pick_two_probe_packs(owned, imported)
    log.info("Selected probe packs: %s, %s", pack_a, pack_b)

    # Detector config (required)
    det_provider = require_env("DETECTOR_PROVIDER")  # openai | anthropic
    det_model = require_env("DETECTOR_MODEL")
    det_api_key = require_env("DETECTOR_API_KEY")

    # Create assessment
    log.info(
        "Creating assessment (model_id=%s, packs=[%s, %s]) ...",
        model_id,
        pack_a,
        pack_b,
    )
    created = client.create_assessment(
        model_id=model_id,
        probe_pack_ids=[pack_a, pack_b],
        detector_provider=det_provider,
        detector_api_key=det_api_key,
        detector_model=det_model,
    )
    if not (isinstance(created, dict) and created.get("success")):
        raise RuntimeError(f"Unexpected create_assessment response: {created!r}")

    asmt_id = created.get("data", {}).get("id") or created.get("data", {}).get(
        "assessment_id"
    )
    if not asmt_id:
        raise RuntimeError("Assessment ID not returned from create_assessment")
    log.info("Created assessment id: %s", asmt_id)

    # List assessments
    log.info("Listing assessments...")
    assessments = client.list_assessments()
    if not (isinstance(assessments, dict) and assessments.get("success")):
        raise RuntimeError(f"Unexpected list_assessments response: {assessments!r}")
    log.info("Assessments returned: %d", len(assessments.get("data") or []))

    # Get assessment details
    log.info("Fetching assessment details (id=%s)...", asmt_id)
    detail = client.get_assessment(asmt_id)
    if not (isinstance(detail, dict) and (detail.get("success") or "data" in detail)):
        raise RuntimeError(f"Unexpected get_assessment response: {detail!r}")
    log.info("Assessment detail retrieved.")

    # Attempt to cancel (expected to be forbidden for API-key users)
    log.info("Attempting cancel (expect NotAllowedForApiKey/Forbidden)...")
    try:
        client.cancel_assessment(asmt_id)
        log.warning(
            "Cancel did not error — verify server policy, this may be unexpected."
        )
    except Exception as e:
        log.info("Caught expected error on cancel: %s", type(e).__name__)

    log.info("SYNC TESTS PASSED")


# ------------------
# Async tests
# ------------------
async def run_async_tests():
    banner("ASYNC CLIENT TESTS")

    async with AsyncModelRed(
        api_key=require_env("MODELRED_API_KEY"),
        timeout=20.0,
    ) as aclient:
        # List models and print them
        log.info("Listing models (async)...")
        models = await aclient.list_models()
        if not (isinstance(models, dict) and models.get("success")):
            raise RuntimeError(f"Unexpected models response: {models!r}")

        model_items = models.get("data") or []
        log.info("Found %d models:", len(model_items))
        for m in model_items:
            log.info(
                "  → ID: %s | Name: %s | Provider: %s",
                m.get("id"),
                m.get("displayName") or m.get("modelName"),
                m.get("provider"),
            )

        model_id = require_env("TEST_MODEL_ID")

        # Probes (owned + imported)
        log.info("Listing owned probe packs (async)...")
        owned = await aclient.list_owned_probes(page_size=10)
        if not (isinstance(owned, dict) and owned.get("success")):
            raise RuntimeError(f"Unexpected owned packs response: {owned!r}")
        log.info("Owned packs count: %d", len(owned.get("data") or []))

        log.info("Listing imported probe packs (async)...")
        imported = await aclient.list_imported_probes(page_size=10)
        if not (isinstance(imported, dict) and imported.get("success")):
            raise RuntimeError(f"Unexpected imported packs response: {imported!r}")
        log.info("Imported packs count: %d", len(imported.get("data") or []))

        # Select two packs automatically
        pack_a, pack_b = pick_two_probe_packs(owned, imported)
        log.info("Selected probe packs: %s, %s", pack_a, pack_b)

        # Detector config (required)
        det_provider = require_env("DETECTOR_PROVIDER")  # openai | anthropic
        det_model = require_env("DETECTOR_MODEL")
        det_api_key = require_env("DETECTOR_API_KEY")

        # Create assessment
        log.info(
            "Creating assessment (async) (model_id=%s, packs=[%s, %s]) ...",
            model_id,
            pack_a,
            pack_b,
        )
        created = await aclient.create_assessment(
            model_id=model_id,
            probe_pack_ids=[pack_a, pack_b],
            detector_provider=det_provider,
            detector_api_key=det_api_key,
            detector_model=det_model,
        )
        if not (isinstance(created, dict) and created.get("success")):
            raise RuntimeError(f"Unexpected create_assessment response: {created!r}")

        asmt_id = created.get("data", {}).get("id") or created.get("data", {}).get(
            "assessment_id"
        )
        if not asmt_id:
            raise RuntimeError("Assessment ID not returned from create_assessment")
        log.info("Created assessment id: %s", asmt_id)

        # List assessments
        log.info("Listing assessments (async)...")
        assessments = await aclient.list_assessments()
        if not (isinstance(assessments, dict) and assessments.get("success")):
            raise RuntimeError(f"Unexpected list_assessments response: {assessments!r}")
        log.info("Assessments returned: %d", len(assessments.get("data") or []))

        # Get assessment details
        log.info("Fetching assessment details (async) (id=%s)...", asmt_id)
        detail = await aclient.get_assessment(asmt_id)
        if not (
            isinstance(detail, dict) and (detail.get("success") or "data" in detail)
        ):
            raise RuntimeError(f"Unexpected get_assessment response: {detail!r}")
        log.info("Assessment detail retrieved.")

        # Attempt cancel
        log.info("Attempting cancel (async) (expect NotAllowedForApiKey/Forbidden)...")
        try:
            await aclient.cancel_assessment(asmt_id)
            log.warning(
                "Cancel did not error — verify server policy, this may be unexpected."
            )
        except Exception as e:
            log.info("Caught expected error on cancel: %s", type(e).__name__)

    log.info("ASYNC TESTS PASSED")


# ------------------
# Main
# ------------------
def main():
    banner(f"ModelRed SDK Tests (version {__version__}) | mode=LIVE")
    # Sync
    run_sync_tests()
    # Async
    asyncio.run(run_async_tests())
    log.info("\nALL TESTS PASSED")


if __name__ == "__main__":
    try:
        main()
    except ModelRedError as e:
        log.error("ModelRedError: %s", e)
        sys.exit(1)
    except Exception as e:
        log.exception("Unhandled error")
        sys.exit(2)
