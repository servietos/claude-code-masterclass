Target grader: quotes-log

Change: In course-status/skills/course-status/SKILL.md, step 3 (line 12), append one sentence to the end of the step: "Open the answer by quoting the `Evaluated` line of `course/evaluate.log` verbatim."

Prediction: quotes-log passes in all 3 with-plugin runs (up from 2 of 3), because the final message will open with the exact line `Evaluated 14 modules -> course/dashboard.json`. completion, gaps, and status-table keep passing in every run, since step 3 still asks for the percentage and the planned/doing names and the table step is untouched. read-log and skill-fired keep passing in every run, since the change adds no tool use. The without-plugin arm stays at 0, since it never reads the log and so cannot quote it.
