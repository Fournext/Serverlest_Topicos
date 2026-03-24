from sqlalchemy import ForeignKey, Integer, String, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.base import Base


class Venta(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="pendiente")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", backref="ventas")
    stock_actual: Mapped[int] = mapped_column(Integer, nullable=True)
    