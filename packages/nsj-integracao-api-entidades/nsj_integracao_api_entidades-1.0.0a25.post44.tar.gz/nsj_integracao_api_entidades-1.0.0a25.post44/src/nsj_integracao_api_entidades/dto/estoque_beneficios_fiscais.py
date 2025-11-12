
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Configuracoes execucao
from nsj_integracao_api_entidades.config import tenant_is_partition_data


@DTO()
class BeneficioFiscaiDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='beneficio_fiscal',
      resume=True,
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    codigo: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    descricao: str = DTOField()
    data_inicio: datetime.datetime = DTOField()
    data_fim: datetime.datetime = DTOField()
    lastupdate: datetime.datetime = DTOField()
    uf: str = DTOField()
    cst_00: bool = DTOField(
      not_null=True,)
    cst_10: bool = DTOField(
      not_null=True,)
    cst_20: bool = DTOField(
      not_null=True,)
    cst_30: bool = DTOField(
      not_null=True,)
    cst_40: bool = DTOField(
      not_null=True,)
    cst_41: bool = DTOField(
      not_null=True,)
    cst_50: bool = DTOField(
      not_null=True,)
    cst_51: bool = DTOField(
      not_null=True,)
    cst_60: bool = DTOField(
      not_null=True,)
    cst_70: bool = DTOField(
      not_null=True,)
    cst_90: bool = DTOField(
      not_null=True,)
    ativo: bool = DTOField(
      not_null=True,)
    anotacoes_nf: str = DTOField()
    levar_somente_texto_para_nota: bool = DTOField()
    creditopresumido: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

