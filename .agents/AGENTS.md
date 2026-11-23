# Workflow Constraints and Rules

You must strictly adhere to the following workflow rules in this workspace:

1. **Never "Jump the Gun"**: Do not proceed to execute new phases of a project without EXPLICIT verbal confirmation ("green light") from the user. Even if the user tells you to "move to the next phase", you must first update the `implementation_plan.md` for that phase and STOP completely. Wait for the user to read it and say "approved" before making any code changes.
2. **Explicit Execution Approval**: Before executing ANY code (including `pytest`, Python scripts, or terminal commands), you must tell the user what command you intend to run in text and wait for their explicit permission to run it.
3. **Test-Driven Requirements**: No code can be trusted unless there are test cases written around it and explicitly tested. All new hooks and environment additions must have corresponding tests.
