from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .extensions import db
from .models import Task

tasks_bp = Blueprint("tasks", __name__)

ALLOWED_STATUSES = {"new", "in_progress", "done"}
ALLOWED_PRIORITIES = {"low", "medium", "high"}


def get_current_user_id() -> int:
    return int(get_jwt_identity())


def validate_title(title: str) -> str | None:
    if not title:
        return "Title is required"
    if len(title) < 1 or len(title) > 80:
        return "Title must be from 1 to 80 characters"
    return None


def validate_description(description: str) -> str | None:
    if len(description) > 500:
        return "Description must be up to 500 characters"
    return None


def validate_priority(priority: str) -> str | None:
    if priority not in ALLOWED_PRIORITIES:
        return "Priority must be low, medium or high"
    return None


def validate_status(status: str) -> str | None:
    if not status:
        return "Status is required"
    if status not in ALLOWED_STATUSES:
        return "Invalid status"
    return None


def parse_deadline(deadline_raw: str | None):
    if deadline_raw in (None, ""):
        return None, None

    try:
        normalized = deadline_raw.replace("Z", "+00:00")
        deadline = datetime.fromisoformat(normalized)
        return deadline, None
    except ValueError:
        return None, "Deadline must be a valid ISO datetime"
    
def validate_deadline(deadline):
    if deadline is None:
        return None

    if deadline.tzinfo is None:
        deadline_utc = deadline.replace(tzinfo=timezone.utc)
    else:
        deadline_utc = deadline.astimezone(timezone.utc)

    min_allowed_deadline = datetime.now(timezone.utc) + timedelta(minutes=30)

    if deadline_utc < min_allowed_deadline:
        return "Deadline must be at least 30 minutes later than current time"

    return None


def get_user_task_or_404(task_id: int, current_user_id: int):
    task = db.session.get(Task, task_id)

    if not task:
        return None, (jsonify({"message": "Task not found"}), 404)

    if task.user_id != current_user_id:
        return None, (jsonify({"message": "Forbidden"}), 403)

    return task, None


@tasks_bp.get("/tasks")
@jwt_required()
def get_tasks():
    current_user_id = get_current_user_id()

    status = (request.args.get("status") or "").strip().lower()
    search = (request.args.get("search") or "").strip()

    query = Task.query.filter_by(user_id=current_user_id)

    if status:
        status_error = validate_status(status)
        if status_error:
            return jsonify({"message": status_error}), 400
        query = query.filter(Task.status == status)

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Task.title.ilike(like_pattern),
                Task.description.ilike(like_pattern),
            )
        )

    tasks = query.order_by(Task.created_at.desc()).all()

    return jsonify([task.to_dict() for task in tasks]), 200


@tasks_bp.get("/tasks/<int:task_id>")
@jwt_required()
def get_task(task_id: int):
    current_user_id = get_current_user_id()

    task, error_response = get_user_task_or_404(task_id, current_user_id)
    if error_response:
        return error_response

    return jsonify(task.to_dict()), 200


@tasks_bp.post("/tasks")
@jwt_required()
def create_task():
    current_user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    priority = (data.get("priority") or "medium").strip().lower()
    deadline_raw = data.get("deadline")

    title_error = validate_title(title)
    if title_error:
        return jsonify({"message": title_error}), 400

    description_error = validate_description(description)
    if description_error:
        return jsonify({"message": description_error}), 400

    priority_error = validate_priority(priority)
    if priority_error:
        return jsonify({"message": priority_error}), 400

    deadline, deadline_error = parse_deadline(deadline_raw)
    
    if deadline_error:
        return jsonify({"message": deadline_error}), 400
    deadline_validation_error = validate_deadline(deadline)
    if deadline_validation_error:
        return jsonify({"message": deadline_validation_error}), 400

    task = Task(
        user_id=current_user_id,
        title=title,
        description=description,
        status="new",
        priority=priority,
        deadline=deadline,
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201
    


@tasks_bp.patch("/tasks/<int:task_id>")
@jwt_required()
def update_task(task_id: int):
    current_user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}

    task, error_response = get_user_task_or_404(task_id, current_user_id)
    if error_response:
        return error_response

    if "title" in data:
        title = (data.get("title") or "").strip()
        title_error = validate_title(title)
        if title_error:
            return jsonify({"message": title_error}), 400
        task.title = title

    if "description" in data:
        description = (data.get("description") or "").strip()
        description_error = validate_description(description)
        if description_error:
            return jsonify({"message": description_error}), 400
        task.description = description

    if "priority" in data:
        priority = (data.get("priority") or "").strip().lower()
        priority_error = validate_priority(priority)
        if priority_error:
            return jsonify({"message": priority_error}), 400
        task.priority = priority

    if "deadline" in data:
        deadline_raw = data.get("deadline")
        deadline, deadline_error = parse_deadline(deadline_raw)
        if deadline_error:
            return jsonify({"message": deadline_error}), 400

        deadline_validation_error = validate_deadline(deadline)
        if deadline_validation_error:
            return jsonify({"message": deadline_validation_error}), 400

        task.deadline = deadline

    db.session.commit()

    return jsonify(task.to_dict()), 200


@tasks_bp.patch("/tasks/<int:task_id>/status")
@jwt_required()
def update_task_status(task_id: int):
    current_user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}

    status = (data.get("status") or "").strip().lower()

    status_error = validate_status(status)
    if status_error:
        return jsonify({"message": status_error}), 400

    task, error_response = get_user_task_or_404(task_id, current_user_id)
    if error_response:
        return error_response

    task.status = status
    db.session.commit()

    return jsonify(task.to_dict()), 200


@tasks_bp.delete("/tasks/<int:task_id>")
@jwt_required()
def delete_task(task_id: int):
    current_user_id = get_current_user_id()

    task, error_response = get_user_task_or_404(task_id, current_user_id)
    if error_response:
        return error_response

    db.session.delete(task)
    db.session.commit()

    return "", 204