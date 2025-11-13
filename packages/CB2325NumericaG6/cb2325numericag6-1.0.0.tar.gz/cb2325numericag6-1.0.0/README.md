# Esse projeto está em desenvolvimento:
Esse projeto foi desenvolvido pelo Grupo 6 para a disciplina de Programação 2 (CB23) do IMPA Tech

Feito por:
<ul>
    <li>Arthur Barbosa Pinheiro</li>
    <li>Daniel Rodrigues Serqueira</li>
    <li>Gabriel Colatusso Castro Da Cruz</li>
    <li>Manuela Abati Bordeaux Ronconi</li>
    <li>Marcelo Miguel Alves Da Silva</li>
    <li>Mateus Almeida Oliveira</li>
    <li>Ryan Kevin Da Costa Felinto</li>
    <li>Sérgio Teixeira Rosa</li>
    <li>Thierry Ventura Marcolino Da Silva</li>
    <li>Vinícius Flesch Kern</li>
</ul>

<br/>

# Versão do projeto: v0.0.5
Added erros/raizes/interpolacao methods

# Documentação

A biblioteca CB2325NumericaG6 é uma biblioteca de cálculo numérico para python que trabalha com funções de interpolação, aproximação, integração, busca de raízes, polinômios, etc.

## Instalação:
```shell
pip install CB2325NumericaG6
```

# Módulos:

- aproximacao
- core
- erros
- integracao
- interpolacao
- polinomios
- raizes

# Aproximação (.aproximacao)

Esse módulo é direcionado a funções de aproximação numérica.

## Funções:

`ajuste_linear(x, y)`:

[✅] Status: Concluído

```python
ajuste_linear(x: list[float], y: list[float]) -> Polinomio
```
**Entrada:**

A função recebe duas listas de variáveis, uma de coordenadas X e outra de coordenadas Y correspondentes.

As listas devem ter tamanhos iguais, pois cada ponto Y corresponde ao respectivo ponto X.

**Retorno:**
A função retorna o ajuste linear $y = ax + b$ da série de pontos por meio de um `Polinomio` [a,b]

`ajuste_polinomial(x, y, n)`:

[✅] Status: Concluído

```python
ajuste_polinomial(x: list[float], y: list[float], n: int) -> Polinomio
```
**Entrada:**

A função recebe duas listas de variáveis, uma de coordenadas X e outra de coordenadas Y correspondentes e o inteiro n que diz o grau do polinomilo.
As listas devem ter tamanhos iguais, pois cada ponto Y corresponde ao respectivo ponto X.

**Retorno:**
A função retorna o ajuste polinomial $y = a_0*x^n + a_1*x^(n-1) + ... + a_n$ da série de pontos por meio de um `Polinomio`.

# Core (.core)

Esse módulo constitue classes genéricas para o funcionamento dos demais módulos.

## Classes:

`Domain` (Classe abstrata)

[✅] Status: Concluído

`Interval(Domain)`

[✅] Status: Concluído

**\_\_init\_\_(p1,p2)**: Cria um intervalo com ponto mínimo p1, e ponto máximo p2.

### Métodos mágicos:
- **\_\_contains\_\_**: Verifica se um intervalo está contido no outro, ou seja se [a,b] está contido [c,d].
- **\_\_str\_\_**
- **\_\_repr\_\_**

### Propriedades:
- **min**: Retorna o infimo do intervalo.
- **max**: Retorna o supremo do intervalo.
- **size**: Retorna o tamanho do intervalo.
- **half**: Retorna o ponto central do intervalo.

### Métodos:
- **copy()**: Retorna uma cópia do intervalo.
- **intersect(other: Interval) -> Optional[Interval]**: (⚠️ Use core.safe_intersect) Retorna a intersecção do intervalo com outro. Se a intersecção for nula, retorna None.

`RealFunction` (Classe abstrata)

[✅] Status: Concluído

### Atributos
- f: Callable[[float], float]: Função principal
- prime: Optional[Callable[[float], float]]: Derivada da função (Opcional)
- domain: Optional[Interval]: Domínio da função (Opcional)

### Métodos mágicos:
- **\_\_call\_\_(x)**: Calcula o valor da função no ponto x. 

### Métodos:
- **eval_safe(x)**: Calcula o valor da função no ponto x se estiver no dominio ou se ele for None.
- **prime_safe(x)**: Calcula o valor da derivada da função no ponto x se a derivada existir, e se estiver no dominio ou se o dominio for None.
- **plot(intervalo: Interval = None, pontos: int = 100) -> tuple(plt.Figure, plt.Axes)**: Retorna o plot da função

## Funções

`linspace(min, max, points)`

Cria uma lista com `points` pontos igualmente distribuídos por um intervalo [min,max].

[✅] Status: Concluído

```python
linspace(min: float, max: float, points: int) -> list[float]
```

**Entrada:**
- min (float): Valor mínimo do intervalo de pontos
- max (float): Vamor máximo do intervalo de pontos
- points (int): Quantidade de pontos

**Retorno:**
- list[float]: Lista de pontos igualmente distribuídos no intervalo

`safe_intersect(d1, d2)`

Faz a intersecção de dois intervalos, tratando o caso de um dos dois serem None.

[✅] Status: Concluído

```python
safe_intersect(d1: Optional['Interval'], d2: Optional['Interval']) -> Optional['Interval']
```

**Entrada:**
- d1 (Interval ou None)
- d2 (Interval ou None)

**Retorno:**
- Interval: Intersecção dos dois intervalos, ou se um deles ou a intersecção for None, retorna None.

# Erros (.erros)

Esse módulo é destinado ao cálculo de erros numéricos.

## Funções

`erro_absoluto(valor_real, valor_aproximado)`:

Calcula o erro absoluto entre um ou mais valores reais e aproximados.    
Esta função é 'vectorizada': ela aceita tanto números únicos
quanto arrays NumPy.

Fórmula: ea = |valor_real - valor_aprox|

[✅] Status: Concluído

```python
erro_absoluto(valor_real, valor_aprox)
```

**Entrada:**
- valor_real (float ou np.ndarray): O valor exato ou de referência.
- valor_aprox (float ou np.ndarray): O valor obtido ou medido.

**Retorno:**
- float ou np.ndarray: O erro absoluto.

`erro_relativo(valor_real, valor_aproximado)`:

Calcula o erro relativo entre um ou mais valores reais e aproximados.    
Esta função é 'vectorizada': ela aceita tanto números únicos
quanto arrays NumPy.

Fórmula: er = |valor_real - valor_aprox| / |valor_real|

[✅] Status: Concluído

```python
erro_absoluto(valor_real, valor_aprox)
```

**Entrada:**
- valor_real (float ou np.ndarray): O valor exato ou de referência.
- valor_aprox (float ou np.ndarray): O valor obtido ou medido.

**Retorno:**
- float ou np.ndarray: O erro relativo.

[✅] Status: Concluído

# Integração (.integracao)

Módulo que compõe as funções de integração.

## Funções

`integral(f, start, end, divisions)`

[✅] Status: Concluído

```python
integral(f:Callable, start: float, end: float, divisions: int) -> float
```

**Entrada:**
- f (Callable): Função a ser integrada
- start (float): Ponto inicial do intervalo
- end (float): Ponto final do intervalo
- divisions (int): Número de subdivisões do intervalo: números maiores implicam uma aproximação mais precisa, mas também consome mais CPU.

**Retorno:**
- float: Valor da integral.

# Interpolação (.interpolacao)

Módulo que compõe as funções de interpolação.

`Interpolator` é um `callable` que recebe `float` e retorna `float`

## Classes:

`PiecewiseLinearFunction(RealFunction)`

[✅] Status: Concluído

**\_\_init\_\_(X,Y, domain: Optional[Interval])**: Cria uma interpolação linear por partes a partir da lista de pontos X, Y

### Atributos
- f: Callable[[float], float]: Função principal
- domain: Optional[Interval]: Domínio da função (Opcional)
- X: Sequence[float]: Lista de valores X
- Y: Sequence[float]: Lista de valores Y

### Propriedades:
- **prime**: Retorna uma função da derivada da interpolação linear.

### Métodos:
- **evaluate(v: float) -> float**: Calcula o valor interpolado linearmente entre os pontos.
- **makePolynomialSegment(x1, x2, y1, y2) -> Polinomio**: Retorna um polinomio linear para os pontos dados.
- **find_root_segments() -> List[Tuple[float,float]]**: Retorna uma lista com todos os intervalos [a,b] que contém raízes.

## Funções

`linear_interp(x, y)`, `poly_interp(x, y)`

[✅] Status: Concluído

```python
linear_interp(x: Sequence, y: Sequence) -> PiecewiseLinearFunction
poly_interp(x: Sequence[float], y: Sequence[float]) -> Interpolator
```

**Entrada:**

- x (Sequence): Lista de coordenadas do eixo X (estritamente crescente)
- y (Sequence): Lista de coordenadas do eixo Y

**Retorno:**
- PiecewiseLinearFunction.
- Interpolator: Uma função que retorna o valor interpolado linearmente baseado nos valores X, Y.

`hermite_interp(x, y, dy)`

[✅] Status: Concluído

```python
hermite_interp(x: Sequence[float], y: Sequence[float], dy: Sequence[float]) -> Interpolator
```

**Entrada:**

- x (Sequence): Lista de coordenadas do eixo X (estritamente crescente)
- y (Sequence): Lista de coordenadas do eixo Y
- dy (Sequence): Derivada dos valores para cada Y.

**Retorno:**
- Interpolator: Uma função que retorna o valor em um ponto pela interpolação de hermite baseado nos valores X, Y, dy.

# Polinomios (.polinomios)

Módulo para definição e cálculo de polinomios.

## Classes:

`Polinomio(RealFunction)`

[✅] Status: Concluído

### Métodos mágicos:
- **\_\_init\_\_(values: List[float])**
- **\_\_repr\_\_**
- **\_\_len\_\_**
- **\_\_getitem\_\_**
- **\_\_setitem\_\_**
- **\_\_mul\_\_, \_\_rmul\_\_**
- **\_\_neg\_\_**
- **\_\_add\_\_**
- **\_\_sub\_\_**
- **\_\_eq\_\_**

### Propriedades:
- **degree**: (int) Retorna o grau do polinômio
- **isZero**: (bool) Retorna True se o polinômio é nulo `[0.0]` ou False caso contrário.
- **prime**: (Polinomio) Retorna o polinomio derivado do polinomio.

### Métodos:
- **evaluate(x: float) -> float**: Calcula o valor do polinômio em um determinado ponto.
- **divideBy(divisor: Polinomio) -> Tuple[Polinomio, Polinomio]**: Realiza a divisão do polinomio por outro polinomio e retorna uma tupla da forma (Polinomio dividido, resto).
- **getRealRootBounds() -> tuple[float, float]**: Calcula os limites inferior e superior no quais estão todas as raízes reais positivas do polinômio;
- **diff() -> Polinomio**: Calcula a derivada do polinomio e retorna um objeto Polinomio correspondente.

## Funções

`lambdify(P)`

[✅] Status: Concluído

```python
lambdify(P: 'Polinomio') -> Callable[[float], float]:
```

**Entrada:**

- P (Polinomio): O objeto Polinomio a ser convertido.

**Retorno:**

- Callable[[float], float]: Uma função lambda que recebe x (float) e retorna P(x) (float). *É apenas um wrapper do método evaluate que pode ser passadas para funções como `integral`*

# Raízes (.raizes)

Módulo com funções de busca de raíz e cálculo de número de raízes.


## Funções

`secante(f, a, b, tol)`, `bissecao(f, a, b, tol)`

[✅] Status: Concluído

```python
secante(f: Callable, a: float, b: float, tol: float) -> float
bissecao(f: Callable, a: float, b: float, tol: float) -> float
```

**Entrada:**
- f: Função a ser analizada
- a: Intervalo inicial da função f
- b: Intervalo final da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- float: Aproximação da raiz da função no intervalo [a, b]

`plot_secante(f, intervalo, a, b, tol)`, `plot_bisseccao(f, intervalo, a, b, tol)`

[✅] Status: Concluído

```python
plot_secante(f: Callable, intervalo:tuple[float, float], a: float, b: float, tol: float = 1e-6) -> Figure

plot_bisseccao(f: Callable, intervalo:tuple[float, float], a: float, b: float, tol: float = 1e-6) -> Figure
```

**Entrada:**
- f: Função a ser analizada
- intervalo: Intervalo de plotagem
- a: Ponto inicial da função f
- b: Ponto final da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- fig: Imagem da plotagem gerada.

`newton_raphson(f, df, a, tol)`

[✅] Status: Concluído

```python
newton_raphson(f: Callable, df: Callable, a:float, tol: float)
```

**Entrada:**
- f: Função a ser analizada
- df: Derivada de f
- a: Ponto inicial da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- float: Aproximação da raiz da função encontrada.

`plot_newton_raphson(f, intervalo, df, a, tol)`

[✅] Status: Concluído

```python
plot_newton_raphson(f: Callable, intervalo:tuple[float, float], df: Callable, a:float, tol: float = 1e-6) -> Figure
```

**Entrada:**
- f: Função a ser analizada
- intervalo: Intervalo de plotagem
- df: Primeira derivada de f
- a: Ponto inicial da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- fig: Imagem da plotagem gerada.

