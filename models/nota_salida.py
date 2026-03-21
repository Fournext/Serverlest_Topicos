from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.base import Base


class NotaSalida(Base):
    __tablename__ = "nota_salida"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_salida: Mapped[str] = mapped_column(String(50), nullable=False)
    motivo: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    