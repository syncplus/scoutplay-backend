# Importa todos os models para registrá-los no metadata do SQLAlchemy
# (necessário para o autogenerate do Alembic e para resolver os relationships).
from app.models.user import User, UserRole  # noqa: F401
from app.models.partida import Partida, PartidaStatus, PartidaLado  # noqa: F401
from app.models.partida_set import PartidaSet  # noqa: F401
from app.models.partida_lancamento import (  # noqa: F401
    PartidaLancamento,
    AtaqueTipo,
    AtaqueQualidade,
)
