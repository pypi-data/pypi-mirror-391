 Still seeing the same issue - I'm getting all 5 memories from both runs. Let me verify what I should be seeing:

  Query: run_id: "initial-impl" with cascade: false

  Expected (3 memories):
  - Memory 3: initial-impl → frontend-result ✅
  - Memory 4: initial-impl → backend-result ✅
  - Memory 5: initial-impl → plan ✅

  Should NOT include (2 memories):
  - Memory 1: fix-validation → frontend-result ❌ (wrong run)
  - Memory 2: fix-validation → plan ❌ (wrong run)

  The filter is still not working - I'm getting memories 1 and 2 which have run_id: "fix-validation" when I explicitly queried for run_id: "initial-impl".

  Looking at the metadata in the results:
  - Memory 1: 'run_id': 'fix-validation' ← Should be filtered out
  - Memory 2: 'run_id': 'fix-validation' ← Should be filtered out
  - Memory 3: 'run_id': 'initial-impl' ← Correct
  - Memory 4: 'run_id': 'initial-impl' ← Correct
  - Memory 5: 'run_id': 'initial-impl' ← Correct

  It seems the run_id is being stored correctly in the metadata, but the query filter isn't excluding memories with different run_ids.