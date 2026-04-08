# Exercício Propagação de Incerteza em Módulos de Medição

Este projeto implementa, em Python, o cálculo da propagação de incerteza em um sistema de medição com múltiplos módulos em série.

## Exercício 1

Enunciado de referência considerado para a entrega:

Em uma empresa do setor petroquímico deseja seguir a Norma Reguladora NR13
sobre vasos de pressão, e está utilizando um manômetro que foi construído com
estes módulos, para a tomada de valores a cada minuto e enviar em tempo real para
a nuvem e processá-los:

- Transdutor extensométrico
- Amplificador
- Indicador digital

O código deste projeto implementa a metodologia geral da aula 3 para resolver esse
tipo de problema com módulos em série. O exemplo numérico do programa permanece
fictício e didático, como solicitado, mas a estrutura foi pensada para ser aplicada ao
Exercício 1 com a troca dos valores de entrada.

O programa segue a abordagem da aula 3 e calcula, a partir dos dados de cada módulo:

- Correção relativa
- Incerteza relativa
- Sensibilidade total
- Correção relativa total
- Correção na entrada
- Incerteza relativa total
- Incerteza na entrada
- Grau de liberdade efetivo pelo método de Welch-Satterthwaite
- Fator `t` de Student para 95,45% de confiança
- Incerteza expandida
- Resultado final da medição no formato `RM = (valor ± incerteza)`

## Requisitos

- Python 3.13 ou compatível
- `numpy`
- `scipy`

As dependências estão listadas em [requirements.txt](/home/hericles/code/personal/exercicio-propagacao-incerteza/requirements.txt).

## Estrutura do projeto

- [main.py](/home/hericles/code/personal/exercicio-propagacao-incerteza/main.py): arquivo principal com a modelagem dos módulos, funções de cálculo, relatório e exemplo padrão
- [test_propagacao_incerteza.py](/home/hericles/code/personal/exercicio-propagacao-incerteza/test_propagacao_incerteza.py): testes automatizados
- [requirements.txt](/home/hericles/code/personal/exercicio-propagacao-incerteza/requirements.txt): dependências do projeto

## Como instalar

No diretório do projeto, execute:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Se preferir usar o Python do sistema, basta instalar as dependências no ambiente que você já utiliza.

## Como executar

Para rodar o exemplo padrão:

```bash
.venv/bin/python main.py
```

Se você não estiver usando ambiente virtual:

```bash
python3 main.py
```

## Como executar os testes

```bash
.venv/bin/python -m unittest -v
```

Ou, sem ambiente virtual:

```bash
python3 -m unittest -v
```

## Como o código funciona

O projeto trabalha com os seguintes dados em cada módulo de medição:

- `nome`
- `sensibilidade`
- `correcao`
- `incerteza_padrao`
- `graus_liberdade`
- `saida_medida`

Depois disso, o programa:

1. Valida os dados de entrada
2. Calcula a correção relativa e a incerteza relativa de cada módulo
3. Combina os módulos em série
4. Calcula a incerteza combinada do sistema
5. Calcula o grau de liberdade efetivo
6. Obtém o fator `t` para o nível de confiança configurado
7. Mostra o resultado final em formato legível no terminal

## Exemplo usado no projeto

O `main.py` já traz um exemplo fictício com três módulos:

- Transdutor de pressão
- Amplificador
- Indicador digital

Esse exemplo pode ser alterado diretamente no arquivo principal para representar outros exercícios ou outros sistemas de medição.

## Saída esperada

Ao executar o programa, o terminal exibirá:

- Os dados de cada módulo
- A correção relativa de cada módulo
- A incerteza relativa de cada módulo
- Os resultados globais do sistema
- O resultado final da medição

## Observações

- A incerteza relativa é calculada com base no valor absoluto da saída medida, para manter o valor positivo.
- A correção relativa preserva o sinal da razão entre correção e saída medida.
- O grau de liberdade efetivo é truncado antes do cálculo do fator `t`, seguindo a abordagem adotada na aula de referência.
