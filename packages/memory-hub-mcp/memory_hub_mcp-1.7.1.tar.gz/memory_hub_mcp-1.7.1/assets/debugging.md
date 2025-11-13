🔴 Issue Found: run_id Filtering Not Working

  I discovered a critical bug in the Memory Hub 1.7 implementation:

  Expected Behavior

  When querying with run_id specified and cascade: false:
  - Should return ONLY memories from that specific run
  - Isolated run queries should not see other runs' data

  Actual Behavior

  Both queries returned the same 5 memories (all memories from both runs):

  Query 1: run_id: "initial-impl" → Got 5 memories (2 from fix-validation + 3 from initial-impl)
  Query 2: run_id: "fix-validation" → Got 5 memories (2 from fix-validation + 3 from initial-impl)

  What Should Have Happened

  Query for run_id: "initial-impl" should return only:
  1. ✅ type: "plan" from initial-impl
  2. ✅ type: "backend-result" from initial-impl
  3. ✅ type: "frontend-result" from initial-impl

  Query for run_id: "fix-validation" should return only:
  1. ✅ type: "plan" from fix-validation
  2. ✅ type: "frontend-result" from fix-validation

  Root Cause

  It appears the run_id filter in get_project_memories is not being applied to the Qdrant query. The function is ignoring the run_id parameter and returning all memories that match app_id + project_id 
  + ticket_id.

  Fix Needed in Memory Hub

  The Qdrant metadata filter needs to include run_id when it's provided:

  # Current (broken) - likely missing run_id filter
  filter_conditions = {
      "app_id": app_id,
      "project_id": project_id,
      "ticket_id": ticket_id
  }

  # Should be (with run_id)
  filter_conditions = {
      "app_id": app_id,
      "project_id": project_id,
      "ticket_id": ticket_id,
      "run_id": run_id  # ADD THIS when run_id parameter is provided
  }
