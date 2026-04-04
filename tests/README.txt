Files are split by backend endpoint.

Included files:
- test_register.py           -> POST /register
- test_login.py              -> POST /login
- test_tasks_get.py          -> GET /tasks
- test_task_get_by_id.py     -> GET /tasks/<id> (template)
- test_tasks_create.py       -> POST /tasks
- test_task_update.py        -> PATCH /tasks/<id> (template)
- test_tasks_status.py       -> PATCH /tasks/<id>/status
- test_tasks_delete.py       -> DELETE /tasks/<id>

Notes:
- Empty endpoint files contain imports + helper functions so you can start writing right away.
- The duplicate test name in test_login.py was kept as in the original source to avoid changing behavior.
