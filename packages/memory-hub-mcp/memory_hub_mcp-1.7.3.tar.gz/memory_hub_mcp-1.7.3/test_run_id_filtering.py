#!/usr/bin/env python3
"""Test script to verify run_id filtering in get_project_memories"""

import asyncio
import sys
from memory_hub.core.models import GetProjectMemoriesRequest
from memory_hub.core.handlers.memory_handlers import get_project_memories
from memory_hub.core.services import AppConfig
from memory_hub.core.config import QDRANT_URL, LM_STUDIO_BASE_URL
from qdrant_client import QdrantClient
import httpx

async def test_run_id_filtering():
    """Test that run_id filtering works correctly with cascade=false"""

    # Setup config
    config = AppConfig(
        qdrant_url=QDRANT_URL,
        lm_studio_url=LM_STUDIO_BASE_URL
    )

    # Initialize clients
    config.qdrant_client = QdrantClient(url=QDRANT_URL)
    config.http_client = httpx.AsyncClient(timeout=30.0)

    print("=" * 80)
    print("TEST 1: Query for run_id='initial-impl' with cascade=false")
    print("=" * 80)

    request1 = GetProjectMemoriesRequest(
        app_id="covenant",
        project_id="portal",
        ticket_id="auth-flow",
        run_id="initial-impl",
        cascade=False,
        return_format="chunks_only",
        limit=50
    )

    try:
        result1 = await get_project_memories(request1, config)
        print(f"\nFound {result1.total_results} memories")
        print("\nMemories returned:")
        for i, chunk in enumerate(result1.retrieved_chunks, 1):
            run_id = chunk.metadata.get('run_id', 'MISSING')
            mem_type = chunk.metadata.get('type', 'MISSING')
            print(f"  {i}. run_id: '{run_id}' | type: '{mem_type}'")

            # Check if this memory should be included
            if run_id != 'initial-impl':
                print(f"     ❌ ERROR: This memory has run_id='{run_id}' but we queried for 'initial-impl'")

        # Count how many are from the correct run
        correct_run = [c for c in result1.retrieved_chunks if c.metadata.get('run_id') == 'initial-impl']
        wrong_run = [c for c in result1.retrieved_chunks if c.metadata.get('run_id') != 'initial-impl']

        print(f"\n✅ Correct run_id ('initial-impl'): {len(correct_run)}")
        print(f"❌ Wrong run_id: {len(wrong_run)}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("TEST 2: Query for run_id='fix-validation' with cascade=false")
    print("=" * 80)

    request2 = GetProjectMemoriesRequest(
        app_id="covenant",
        project_id="portal",
        ticket_id="auth-flow",
        run_id="fix-validation",
        cascade=False,
        return_format="chunks_only",
        limit=50
    )

    try:
        result2 = await get_project_memories(request2, config)
        print(f"\nFound {result2.total_results} memories")
        print("\nMemories returned:")
        for i, chunk in enumerate(result2.retrieved_chunks, 1):
            run_id = chunk.metadata.get('run_id', 'MISSING')
            mem_type = chunk.metadata.get('type', 'MISSING')
            print(f"  {i}. run_id: '{run_id}' | type: '{mem_type}'")

            # Check if this memory should be included
            if run_id != 'fix-validation':
                print(f"     ❌ ERROR: This memory has run_id='{run_id}' but we queried for 'fix-validation'")

        # Count how many are from the correct run
        correct_run = [c for c in result2.retrieved_chunks if c.metadata.get('run_id') == 'fix-validation']
        wrong_run = [c for c in result2.retrieved_chunks if c.metadata.get('run_id') != 'fix-validation']

        print(f"\n✅ Correct run_id ('fix-validation'): {len(correct_run)}")
        print(f"❌ Wrong run_id: {len(wrong_run)}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    await http_client.aclose()
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_run_id_filtering())
