
from sqlmodel import create_engine, SQLModel, Session
 
from src.core.config import settings
from src.users import models as user_models
from src.institutions import models as school_models
from src.jobs import models as job_models
from src.proposals import models as proposal_models


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))



def init_db() -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)
    


