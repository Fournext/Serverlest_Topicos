from sqlalchemy import ForeignKey, Integer, String, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.base import Base


class DetalleVenta(Base):
    __tablename__ = "detalles_ventas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="activo")
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False) 
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    venta = relationship("Venta", backref="detalles")
    producto = relationship("Producto", backref="detalles_ventas")
