from sqlalchemy import Integer, String, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column
from common.base import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    contacto: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
