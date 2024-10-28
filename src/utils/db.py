"""
Generic database related utility functions.
"""
from typing import Any, Type, Sequence

from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm.attributes import InstrumentedAttribute


def get_object_with_pk_or_404(pk: str, session: Session, entity: Type, res: bool = True) -> Any:
    """
    Retrieve object directly from the database with its primary key,
    if not found. Choose to response with 404 when not found or receive `None`
    by setting the `res` argument.
    """
    object = session.get(entity, pk)
    if object is None and res:
        raise HTTPException(
            status_code=404,
            detail=f"{entity.__name__} with pk {pk} is not found."
        )
    return object

def get_object_or_404(
        session: Session,
        where_attr: InstrumentedAttribute,
        where_value: Any,
        res: bool = True
) -> Any:
    """
    Get an object by filtering using a single field.
    Field, `where_attr`, should be passed as sqlalchemy column object.
    Example: User.email for email field.
    It's very recommended to use indexed fields for efficient querying.
    """
    model_class = where_attr.class_
    statement = select(model_class).where(where_attr == where_value)
    object = session.exec(statement).first()
    if object is None and res:
        raise HTTPException(
            status_code=404,
            detail=f"{model_class.__name__} object not found."
        )
    return object


def get_objects(
        session: Session,
        where_attr: InstrumentedAttribute,
        where_value: Any 
) -> Sequence[Any] | None:
    statement = select(where_attr.class_).where(where_attr == where_value)
    objects = session.exec(statement).all()
    return objects


def delete_object(object: Any, session: Session, entity: Type) -> None:
    try:
        session.delete(object)
    except ValueError:
        raise ValueError("Invalid database model instance")

def save(session: Session, data: Any, refresh: bool = False) -> Any | None:
    session.add(data)
    session.commit()
    
    if refresh:
        session.refresh(data)
        return data
    