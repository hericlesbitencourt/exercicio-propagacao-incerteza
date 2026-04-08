import math
import unittest

from main import ModuloMedicao, calcular_propagacao


class PropagacaoIncertezaTests(unittest.TestCase):
    def test_exemplo_da_aula_3_reproduz_resultado_aproximado(self) -> None:
        modulos = [
            ModuloMedicao(
                nome="Transdutor indutivo",
                sensibilidade=5.0,
                correcao=-1.0,
                incerteza_padrao=2.0,
                graus_liberdade=16,
                saida_medida=25.0,
            ),
            ModuloMedicao(
                nome="Amplificador",
                sensibilidade=0.1,
                correcao=0.0,
                incerteza_padrao=(0.2 / 100) * 0.20,
                graus_liberdade=20,
                saida_medida=2.5,
            ),
            ModuloMedicao(
                nome="Voltimetro digital",
                sensibilidade=1.0,
                correcao=(0.02 / 100) * 2.5,
                incerteza_padrao=5 / 1000,
                graus_liberdade=96,
                saida_medida=2.5,
            ),
        ]

        resultado = calcular_propagacao(entrada_sistema=5.0, modulos=modulos)

        self.assertAlmostEqual(resultado["sensibilidade_total"], 0.5, places=12)
        self.assertAlmostEqual(resultado["correcao_relativa_total"], -0.0398, places=6)
        self.assertAlmostEqual(resultado["correcao_na_entrada"], -0.199, places=3)
        self.assertAlmostEqual(
            resultado["incerteza_relativa_total"], 0.080025, places=6
        )
        self.assertAlmostEqual(
            resultado["incerteza_na_entrada"], 0.400125780224169, places=12
        )
        self.assertEqual(resultado["graus_liberdade_t"], 16)
        self.assertAlmostEqual(resultado["incerteza_expandida"], 0.868, places=3)
        self.assertAlmostEqual(resultado["resultado_medicao"], 4.801, places=3)

    def test_lista_vazia_dispara_erro(self) -> None:
        with self.assertRaisesRegex(ValueError, "não pode estar vazia"):
            calcular_propagacao(entrada_sistema=1.0, modulos=[])

    def test_saida_igual_a_zero_dispara_erro(self) -> None:
        modulos = [
            ModuloMedicao(
                nome="Modulo invalido",
                sensibilidade=1.0,
                correcao=0.0,
                incerteza_padrao=0.1,
                graus_liberdade=10,
                saida_medida=0.0,
            )
        ]
        with self.assertRaisesRegex(ValueError, "S = 0"):
            calcular_propagacao(entrada_sistema=1.0, modulos=modulos)

    def test_incerteza_negativa_dispara_erro(self) -> None:
        modulos = [
            ModuloMedicao(
                nome="Modulo invalido",
                sensibilidade=1.0,
                correcao=0.0,
                incerteza_padrao=-0.1,
                graus_liberdade=10,
                saida_medida=1.0,
            )
        ]
        with self.assertRaisesRegex(ValueError, "negativa"):
            calcular_propagacao(entrada_sistema=1.0, modulos=modulos)

    def test_grau_de_liberdade_invalido_dispara_erro(self) -> None:
        modulos = [
            ModuloMedicao(
                nome="Modulo invalido",
                sensibilidade=1.0,
                correcao=0.0,
                incerteza_padrao=0.1,
                graus_liberdade=0,
                saida_medida=1.0,
            )
        ]
        with self.assertRaisesRegex(ValueError, "grau de liberdade positivo"):
            calcular_propagacao(entrada_sistema=1.0, modulos=modulos)

    def test_incerteza_relativa_usa_valor_absoluto_da_saida(self) -> None:
        modulos = [
            ModuloMedicao(
                nome="Modulo com saida negativa",
                sensibilidade=1.0,
                correcao=-0.2,
                incerteza_padrao=0.1,
                graus_liberdade=15,
                saida_medida=-2.0,
            )
        ]

        resultado = calcular_propagacao(entrada_sistema=3.0, modulos=modulos)

        self.assertAlmostEqual(
            resultado["modulos"][0]["correcao_relativa"], 0.1, places=12
        )
        self.assertAlmostEqual(
            resultado["modulos"][0]["incerteza_relativa"], 0.05, places=12
        )
        self.assertTrue(
            math.isclose(resultado["correcao_na_entrada"], 0.3, rel_tol=1e-12)
        )


if __name__ == "__main__":
    unittest.main()
