from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Project, User
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
def list_projects(user_id: int, db: Session = Depends(get_db)) -> list[ProjectResponse]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    projects = db.query(Project).filter(Project.user_id == user_id).all()
    return [
        ProjectResponse(
            id=project.id,
            user_id=project.user_id,
            title=project.title,
            description=project.description,
            status=project.status,
        )
        for project in projects
    ]


@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, user_id: int, db: Session = Depends(get_db)) -> ProjectResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    project = Project(user_id=user.id, title=payload.title, description=payload.description, status="draft")
    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        title=project.title,
        description=project.description,
        status=project.status,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, user_id: int, db: Session = Depends(get_db)) -> ProjectResponse:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        title=project.title,
        description=project.description,
        status=project.status,
    )
