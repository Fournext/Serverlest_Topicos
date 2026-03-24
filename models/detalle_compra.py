from sqlalchemy import Column, Integer, String, func, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.base import Base


class DetallaCompra(Base):
    __tablename__ = "detalles_compra"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    compra_id: Mapped[int] = mapped_column(ForeignKey("compras.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="activo")   
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())