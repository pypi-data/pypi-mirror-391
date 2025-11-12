
import datetime
import uuid

from nsj_rest_lib.decorator.entity import Entity
from nsj_rest_lib.entity.entity_base import EntityBase


@Entity(
    table_name="estoque.beneficios_fiscais",
    pk_field="beneficio_fiscal",
    default_order_fields=["codigo"],
)
class BeneficioFiscaiEntity(EntityBase):
    beneficio_fiscal: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    data_inicio: datetime.datetime = None
    data_fim: datetime.datetime = None
    lastupdate: datetime.datetime = None
    uf: str = None
    cst_00: bool = None
    cst_10: bool = None
    cst_20: bool = None
    cst_30: bool = None
    cst_40: bool = None
    cst_41: bool = None
    cst_50: bool = None
    cst_51: bool = None
    cst_60: bool = None
    cst_70: bool = None
    cst_90: bool = None
    ativo: bool = None
    anotacoes_nf: str = None
    levar_somente_texto_para_nota: bool = None
    creditopresumido: uuid.UUID = None
