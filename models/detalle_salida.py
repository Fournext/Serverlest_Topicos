from sqlalchemy import Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.base import Base


class DetalleSalida(Base):
    __tablename__ = "detalle_salida"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad_salida: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ubicacion_salida: Mapped[str] = mapped_column(String(100), nullable=True)
    id_producto: Mapped[int] = mapped_column(Integer, ForeignKey("productos.id"), nullable=False)
    id_nota_salida: Mapped[int] = mapped_column(Integer, ForeignKey("nota_salida.id"), nullable=False)
    