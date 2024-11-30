from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Dict
from pathlib import Path 
from dataclasses import dataclass
import logging

from jwt.exceptions import InvalidTokenError
import jwt
import requests
from jinja2 import Template
from pydantic import EmailStr
from fastapi import HTTPException
import emails

from src.core.config import settings
from src.core.security import ALGORITHM


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    
    html_content = Template(template_str).render(context)
    return html_content


def generate_password_reset_email(email_to: EmailStr, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    url = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    
    html_content = render_email_template(
        template_name="password_reset.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
            "link": settings.FRONTEND_HOST,
        },
        
    )
    
    return EmailData(html_content=html_content, subject=subject)


def send_email(
    email_to: str,
    subject: str = "",
    html_content: str = ""
) -> None:
    assert settings.emails_enabled, "No provided configurations for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)
    )
    
    # SMTP configurations
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    
    response = message.send(to=email_to, smtp=smtp_options)
    logging.info(f"Send email results: {response}")
    
def generate_jwt_token(sub: str| Any, duration: timedelta) -> str:
    expire = datetime.now(timezone.utc) + duration
    
    endcoded_jwt = jwt.encode(
        {"sub": str(sub), "nbf": datetime.now(), "exp": expire},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    
    return endcoded_jwt

def generate_email_verification_url(email: EmailStr) -> str:
    duration = timedelta(
        hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
    )
    
    token = generate_jwt_token(sub=email, duration=duration)
    
    FRONTEND_URL = "https://shelfie.com/email/verify"
    # TODO: Reference FRONTEND_URL from settings
    url = FRONTEND_URL + f"?token={token}"
    
    return  url

def generate_password_reset_url(email: EmailStr) -> str:
    duration = timedelta(
        hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
    )
    
    token = generate_jwt_token(sub=email, duration=duration)
    
    url = settings.FRONTEND_HOST + f"/reset-password?token={token}"
    
    return url


def verify_jwt_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        return str(decoded_token["sub"]) 
    
    except InvalidTokenError:
        return None


def offset_pagination_metadata(offset: int, limit: int, total: int, trailing_url: str) -> dict:
    """
    Generates offset-based pagination metadata for response.
    """
    
    next_offset = offset + limit if (offset + limit) < total else None
    previous_offset = offset - limit if (offset - limit) >= 0 else None
    
    return {
        "total_items": total,
        "limit": limit,
        "offset": offset,
        "next": (
             f"{trailing_url}?limit={limit}&offset={next_offset}"
             if next_offset is not None
             else None
         ),
        "prev": (
            f"{trailing_url}?limit={limit}&offset={previous_offset}"
            if previous_offset is not None
            else None
        )
   }
    
    

def make_request(
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Makes an HTTP request.
    
    Args:
       method: HTTP method(GET, PUT, POST, DELETE, etc.).
       url: Full URL of the endpoint.
       params: Query parameters for GET requests.
       data: Form data for POST/PUT requests.
       json: JSON data for POST/PUT requests.
       headers: Additional HTTP headers.
    
    Returns:
        Parsed JSON response or raw text.
    """
    try:
        response = requests.request(
            method, url,
            params=params, data=data,
            json=json, headers=headers
        )
        
        response.raise_for_status()
        return response.json() # Parse json if possible
    
    except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"""HTTP error: {response.status_code} -
                               {response.text}""") from e
    except ValueError:
        # Return raw text if json parsing fails.
        return response.text
    