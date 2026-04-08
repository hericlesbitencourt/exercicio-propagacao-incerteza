"""Calculo da propagacao de incerteza em modulos de medicao em serie."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class ModuloMedicao:
    """Representa um modulo do sistema de medicao."""

    nome: str
    sensibilidade: float
    correcao: float
    incerteza_padrao: float
    graus_liberdade: float
    saida_medida: float


def validar_modulos(modulos: list[ModuloMedicao]) -> None:
    """Garante que os dados informados permitem o calculo metrologico."""

    if not modulos:
        raise ValueError("A lista de módulos não pode estar vazia.")

    for indice, modulo in enumerate(modulos, start=1):
        if modulo.saida_medida == 0:
            raise ValueError(
                f"O módulo {indice} ({modulo.nome}) possui S = 0, o que invalida "
                "o cálculo relativo."
            )
        if modulo.incerteza_padrao < 0:
            raise ValueError(
                f"O módulo {indice} ({modulo.nome}) possui incerteza padrão negativa."
            )
        if modulo.graus_liberdade <= 0:
            raise ValueError(
                f"O módulo {indice} ({modulo.nome}) deve ter grau de liberdade positivo."
            )


def calcular_correcao_relativa(modulo: ModuloMedicao) -> float:
    """Calcula a correcao relativa de um modulo."""

    return modulo.correcao / modulo.saida_medida


def calcular_incerteza_relativa(modulo: ModuloMedicao) -> float:
    """Calcula a incerteza relativa de um modulo."""

    return modulo.incerteza_padrao / abs(modulo.saida_medida)


def calcular_grau_efetivo(
    incertezas_relativas: np.ndarray,
    graus_liberdade: np.ndarray,
    incerteza_relativa_total: float,
) -> tuple[float, float]:
    """Aplica Welch-Satterthwaite para obter o grau de liberdade efetivo."""

    denominador = np.sum((incertezas_relativas**4) / graus_liberdade)

    if denominador == 0 or incerteza_relativa_total == 0:
        return math.inf, math.inf

    grau_efetivo = (incerteza_relativa_total**4) / denominador
    return float(grau_efetivo), float(max(1, math.trunc(grau_efetivo)))


def calcular_propagacao(
    entrada_sistema: float,
    modulos: list[ModuloMedicao],
    nivel_confianca: float = 0.9545,
) -> dict[str, Any]:
    """Calcula a propagacao de incerteza de um sistema com modulos em serie."""

    validar_modulos(modulos)

    # Reune os dados dos modulos em vetores para facilitar os calculos globais.
    sensibilidades = np.array(
        [modulo.sensibilidade for modulo in modulos],
        dtype=float,
    )
    correcoes_relativas = np.array(
        [calcular_correcao_relativa(modulo) for modulo in modulos],
        dtype=float,
    )
    incertezas_relativas = np.array(
        [calcular_incerteza_relativa(modulo) for modulo in modulos],
        dtype=float,
    )
    graus_liberdade = np.array(
        [modulo.graus_liberdade for modulo in modulos],
        dtype=float,
    )

    # Calcula os parametros equivalentes do sistema de medicao.
    sensibilidade_total = np.prod(sensibilidades)
    correcao_relativa_total = np.sum(correcoes_relativas)
    correcao_na_entrada = entrada_sistema * correcao_relativa_total
    incerteza_relativa_total = math.sqrt(np.sum(incertezas_relativas**2))
    incerteza_na_entrada = abs(entrada_sistema) * incerteza_relativa_total

    # Estima o grau de liberdade efetivo pela formula de Welch-Satterthwaite.
    grau_efetivo, graus_liberdade_t = calcular_grau_efetivo(
        incertezas_relativas=incertezas_relativas,
        graus_liberdade=graus_liberdade,
        incerteza_relativa_total=incerteza_relativa_total,
    )

    # Determina o fator t de Student para o nivel de confianca desejado.
    alpha = 1 - nivel_confianca
    if math.isinf(graus_liberdade_t):
        fator_t_student = float(stats.norm.ppf(1 - alpha / 2))
    else:
        fator_t_student = float(stats.t.ppf(1 - alpha / 2, df=int(graus_liberdade_t)))

    # Calcula a incerteza expandida e o resultado corrigido da medicao.
    incerteza_expandida = fator_t_student * incerteza_na_entrada
    resultado_medicao = entrada_sistema + correcao_na_entrada

    # Organiza os resultados por modulo para exibicao no relatorio final.
    detalhes_modulos: list[dict[str, Any]] = []
    for modulo, correcao_relativa, incerteza_relativa in zip(
        modulos,
        correcoes_relativas,
        incertezas_relativas,
    ):
        detalhes = asdict(modulo)
        detalhes["correcao_relativa"] = float(correcao_relativa)
        detalhes["incerteza_relativa"] = float(incerteza_relativa)
        detalhes_modulos.append(detalhes)

    return {
        "entrada_sistema": float(entrada_sistema),
        "nivel_confianca": float(nivel_confianca),
        "alpha": float(alpha),
        "modulos": detalhes_modulos,
        "sensibilidade_total": float(sensibilidade_total),
        "correcao_relativa_total": float(correcao_relativa_total),
        "correcao_na_entrada": float(correcao_na_entrada),
        "incerteza_relativa_total": float(incerteza_relativa_total),
        "incerteza_na_entrada": float(incerteza_na_entrada),
        "grau_efetivo": float(grau_efetivo),
        "graus_liberdade_t": (
            "infinito" if math.isinf(graus_liberdade_t) else int(graus_liberdade_t)
        ),
        "fator_t_student": float(fator_t_student),
        "incerteza_expandida": float(incerteza_expandida),
        "resultado_medicao": float(resultado_medicao),
    }


def exibir_relatorio(resultado: dict[str, Any]) -> None:
    """Mostra no terminal um resumo completo dos calculos."""

    print("=" * 78)
    print("PROPAGACAO DE INCERTEZA EM MODULOS DE MEDICAO EM SERIE")
    print("=" * 78)
    print(f"Entrada do sistema: {resultado['entrada_sistema']:.6f}")
    print(f"Nivel de confianca: {resultado['nivel_confianca'] * 100:.2f}%")
    print()
    print("DADOS DE CADA MODULO")
    print("-" * 78)

    for indice, modulo in enumerate(resultado["modulos"], start=1):
        print(f"Modulo {indice}: {modulo['nome']}")
        print(f"  Sensibilidade      = {modulo['sensibilidade']:.6f}")
        print(f"  Correcao           = {modulo['correcao']:.6f}")
        print(f"  Incerteza padrao   = {modulo['incerteza_padrao']:.6f}")
        print(f"  Graus liberdade    = {modulo['graus_liberdade']:.0f}")
        print(f"  Saida medida       = {modulo['saida_medida']:.6f}")
        print(f"  Correcao relativa  = {modulo['correcao_relativa']:.8f}")
        print(f"  Incerteza relativa = {modulo['incerteza_relativa']:.8f}")
        print("-" * 78)

    print("RESULTADOS GLOBAIS")
    print("-" * 78)
    print(f"Sensibilidade total do sistema     = {resultado['sensibilidade_total']:.6f}")
    print(
        "Correcao relativa total           = "
        f"{resultado['correcao_relativa_total']:.8f}"
    )
    print(f"Correcao na entrada               = {resultado['correcao_na_entrada']:.6f}")
    print(
        "Incerteza relativa total          = "
        f"{resultado['incerteza_relativa_total']:.8f}"
    )
    print(f"Incerteza na entrada              = {resultado['incerteza_na_entrada']:.6f}")
    if math.isinf(resultado["grau_efetivo"]):
        print("Grau de liberdade efetivo         = infinito")
    else:
        print(f"Grau de liberdade efetivo         = {resultado['grau_efetivo']:.6f}")
    print(f"Grau de liberdade usado no t      = {resultado['graus_liberdade_t']}")
    print(
        "Fator t de Student (95,45%)       = "
        f"{resultado['fator_t_student']:.6f}"
    )
    print(
        "Incerteza expandida               = "
        f"{resultado['incerteza_expandida']:.6f}"
    )
    print(
        "RM = "
        f"({resultado['resultado_medicao']:.6f} ± "
        f"{resultado['incerteza_expandida']:.6f})"
    )
    print("=" * 78)


def criar_exemplo_padrao() -> tuple[float, list[ModuloMedicao]]:
    """Cria um exemplo simples com tres modulos em serie."""

    entrada_sistema = 10.0
    modulos = [
        ModuloMedicao(
            nome="Transdutor de pressao",
            sensibilidade=2.00,
            correcao=-0.03,
            incerteza_padrao=0.02,
            graus_liberdade=30,
            saida_medida=20.00,
        ),
        ModuloMedicao(
            nome="Amplificador",
            sensibilidade=0.100,
            correcao=0.002,
            incerteza_padrao=0.004,
            graus_liberdade=25,
            saida_medida=2.002,
        ),
        ModuloMedicao(
            nome="Indicador digital",
            sensibilidade=1.000,
            correcao=0.0004,
            incerteza_padrao=0.005,
            graus_liberdade=80,
            saida_medida=2.002,
        ),
    ]
    return entrada_sistema, modulos


def main() -> None:
    """Executa o exemplo padrao no terminal."""

    entrada_sistema, modulos = criar_exemplo_padrao()
    resultado = calcular_propagacao(entrada_sistema=entrada_sistema, modulos=modulos)
    exibir_relatorio(resultado)


if __name__ == "__main__":
    main()
