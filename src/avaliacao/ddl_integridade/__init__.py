"""Item 1 da Avaliação: DDL e Restrições de Integridade (Cap. 1, 2, 3 e 4)."""
from .validador_restricoes import (
    demonstrar_pk_simples_e_composta,
    demonstrar_fk_1_1_1_n_n_m,
    demonstrar_acoes_cascata,
    demonstrar_set_null_e_set_default,
    demonstrar_unique_e_not_null,
    demonstrar_check_faixa_e_lista,
    demonstrar_valores_default,
    demonstrar_alter_table_add_drop,
    executar_bateria_completa_ddl,
)

__all__ = [
    "demonstrar_pk_simples_e_composta",
    "demonstrar_fk_1_1_1_n_n_m",
    "demonstrar_acoes_cascata",
    "demonstrar_set_null_e_set_default",
    "demonstrar_unique_e_not_null",
    "demonstrar_check_faixa_e_lista",
    "demonstrar_valores_default",
    "demonstrar_alter_table_add_drop",
    "executar_bateria_completa_ddl",
]
