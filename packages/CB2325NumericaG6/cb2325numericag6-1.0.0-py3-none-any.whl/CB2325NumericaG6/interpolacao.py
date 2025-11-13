from typing import Callable, Sequence, Optional, List, Tuple
from .core import RealFunction, Interval
from .polinomios import Polinomio
import matplotlib.pyplot as plt

class HermiteInterpolation(RealFunction):
    def __init__(self, x: Sequence[float], y: Sequence[float], dy: Sequence[float], domain: Optional[Interval] = None):
        self.X = x
        self.Y = y
        self.DY = dy
        self.domain = domain 
        self.f = self._coeficientes() # O Callable principal para RealFunction

    def _coeficientes(self):
        if len(self.X) != len(self.Y) or len(self.X) != len(self.DY) or len(self.X) < 2:
            raise ValueError("x, y, dy devem ter mesmo tamanho e conter ao menos dois pontos.")

        n = len(self.X)
        coef = [0.0 for _ in range(2*n)]

        for i in range(n):
            Li = [1.0]
            denom = 1.0
            for j in range(n):
                if j != i:
                    novo = [0.0 for _ in range(len(Li)+1)]
                    for k in range(len(Li)):
                        novo[k] -= Li[k] * self.X[j]
                        novo[k+1] += Li[k]
                    Li = novo
                    denom *= (self.X[i] - self.X[j])
            Li = [a / denom for a in Li]

            Li_prime = sum(1 / (self.X[i] - self.X[m]) for m in range(n) if m != i)

            Li2 = [0.0]*(2*len(Li)-1)
            for p in range(len(Li)):
                for q in range(len(Li)):
                    Li2[p+q] += Li[p]*Li[q]

            Ki = [0.0]*(len(Li2)+1)
            for k in range(len(Li2)):
                Ki[k] -= Li2[k] * self.X[i]
                Ki[k+1] += Li2[k]

            Hi = [0.0]*(len(Li2)+1)
            for k in range(len(Li2)):
                Hi[k] += Li2[k]
            for k in range(len(Li2)):
                Hi[k] += 2*Li_prime*Li2[k]*self.X[i]  
                Hi[k+1] -= 2*Li_prime*Li2[k]           
            termo = [0.0]*max(len(Hi), len(Ki))
            for k in range(len(Hi)):
                termo[k] += self.Y[i]*Hi[k]
            for k in range(len(Ki)):
                termo[k] += self.DY[i]*Ki[k]

            for k in range(len(termo)):
                coef[k] += termo[k]

        while len(coef) > 1 and abs(coef[-1]) < 1e-14:
            coef.pop()

        return Polinomio(coef[::-1])
        
    def evaluate(self, v: float) -> float:
        if len(self.X) != len(self.Y) or len(self.X) < 2:
            raise ValueError(f"x and y must have the same length ({len(self.X)} != {len(self.Y)}) and have atleast 2 points.")
        return self.f.evaluate(v)




def hermite_interp(x: Sequence[float], y: Sequence[float], dy: Sequence[float], domain: Optional[Interval]=None) -> HermiteInterpolation:
    """
    Cria uma função de interpolação polinomial de Hermite a partir de um conjunto de coordenadas X, Y
    e de suas derivadas.

    Args:
        x (Sequence[float]): Coordenadas no eixo X.
        y (Sequence[float]): Valores de Y nas respectivas coordenadas.
        dy (Sequence[float]): Valores das derivadas nas respectivas coordenadas.
        domain (Optional[Interval]): domínio da função (opcional)
        
    Returns:
        HermiteInterpolation: Uma classe chamável que avalia o polinômio interpolador de Hermite.
        
    Raises:
        ValueError: Se x, y e dy tiverem comprimentos diferentes ou contiverem menos de dois pontos.
    """
    if len(x) != len(y) or len(x) != len(dy) or len(x) < 2:
        raise ValueError(
            f"x, y, dy must have the same length and contain at least two points "
        )

    return HermiteInterpolation(x, y, dy, domain)
 


class PolinomialInterpolation(RealFunction):
    def __init__(self, x: Sequence[float], y: Sequence[float], domain: Optional[Interval] = None):
        self.X = x
        self.Y = y
        self.domain = domain
        self.f = self._coeficientes() # O Callable principal para RealFunction

    def _coeficientes(self):
        n = len(self.X)
        coef = [0.0 for _ in range(n)]

        for i in range(n): 
            Li = [1.0]
            denom = 1.0

            for j in range(n): 
                if i != j:
                    novo = [0.0 for _ in range(len(Li) + 1)]
                    for k in range(len(Li)):
                        novo[k]     += Li[k]          
                        novo[k + 1] -= Li[k] * self.X[j]
                    Li = novo
                    denom *= (self.X[i] - self.X[j])

            Li = [a * (self.Y[i] / denom) for a in Li]
            for k in range(len(Li)):
                coef[k] += Li[k]

        return Polinomio(coef) 

    def evaluate(self, v: float) -> float:
        if len(self.X) != len(self.Y) or len(self.X) < 2:
            raise ValueError(f"x and y must have the same length ({len(self.X)} != {len(self.Y)}) and have atleast 2 points.")
        return self.f.evaluate(v)
    
    

 
def poly_interp(x: Sequence[float], y: Sequence[float], domain: Optional[Interval] = None) -> PolinomialInterpolation:
    """
    Cria uma função de interpolação polinomial a partir de um conjunto de coordenadas X e Y,
    utilizando a forma de Lagrange.

    Args:
        x (Sequence[float]): Sequência das coordenadas no eixo X.
        y (Sequence[float]): Sequência dos valores correspondentes no eixo Y.
        domain (Optional[Interval]): domínio da função (opcional)

    Returns:
        PolinomialInterpolation: Uma classe chamável que avalia o polinômio interpolador
        para qualquer valor de entrada do tipo float.

    Raises:
        ValueError: Se x e y tiverem comprimentos diferentes ou contiverem menos de dois pontos.
    """
    if len(x) != len(y) or len(x) < 2:
        raise ValueError(f"x and y must have the same length ({len(x)} != {len(y)}) and have atleast 2 points.")
    
    return PolinomialInterpolation(x, y, domain)




class PiecewiseLinearFunction(RealFunction):
    def __init__(self, x: Sequence[float], y: Sequence[float], domain: Optional[Interval] = None):
        self.X = x
        self.Y = y
        self.domain = domain if domain else Interval(min(x), max(x))
        self.f = self.evaluate # O Callable principal para RealFunction

    def makePolynomialSegment(self, x1, x2, y1, y2) -> Polinomio:
        if x1 == x2:
            raise ValueError("Pontos x1 e x2 são o mesmo. Não é possível criar um segmento.")

        slope = (y2-y1)/(x2-x1)
        c0 = y1 - slope * x1
        segmentDomain = Interval(min(x1, x2), max(x1, x2))

        pol = Polinomio([slope, c0], segmentDomain) 

        return pol

    @property
    def prime(self) -> Callable[[float], float]: #type: ignore
        """
        Retorna a função que calcula a derivada (inclinação constante) 
        da interpolação linear por partes. A derivada é indefinida nos pontos de referência.
        """
        
        # O self.prime da RealFunction é um Callable. Retornamos uma função que implementa a lógica da derivada.
        def piecewisePrimeFunction(v: float) -> float:
            if not (self.X[0] <= v <= self.X[-1]):
                raise ValueError(f"O ponto {v} está fora do domínio de interpolação.")
            
            n = len(self.X)
            
            for x_i in self.X:
                if abs(v - x_i) < 1e-12: 
                    raise ValueError(f"A derivada é descontínua e indefinida no nó x={v}.")

            start, end = 0, n - 1

            while end - start != 1:
                mid = (end + start) // 2
                if self.X[mid] > v:
                    end = mid
                else:
                    start = mid
            
            x1, x2 = self.X[start], self.X[end]
            y1, y2 = self.Y[start], self.Y[end]
            
            slope = (y2 - y1) / (x2 - x1)
            
            return slope

        return piecewisePrimeFunction

    def evaluate(self, v: float) -> float:
        n = len(self.X)
        if v > self.X[-1]:
            start, end = n - 2, n - 1
        elif v < self.X[0]:
            start, end = 0, 1
        elif v == self.X[0]:
            return self.Y[0]
        elif v == self.X[-1]:
            return self.Y[-1]
        else:
            start, end = 0, n - 1 
            while end - start != 1:
                mid = (end + start) // 2
                if self.X[mid] > v:
                    end = mid
                elif self.X[mid] < v:
                    start = mid
                else:
                    return self.Y[mid] 

        x1, x2 = self.X[start], self.X[end]
        y1, y2 = self.Y[start], self.Y[end]

        return y1 + (v - x1) * ((y2 - y1) / (x2 - x1))
    
    def find_root_segments(self) -> List[Tuple[float, float]]:
        """
        Retorna uma lista de intervalos [a, b] onde f(a) * f(b) < 0.
        """

        segments = []
        for i in range(len(self.X) - 1):
            y_i = self.Y[i]
            y_i_plus_1 = self.Y[i+1]
            
            # Se os sinais são opostos (garantia da raiz)
            if y_i * y_i_plus_1 < 0:
                segments.append((self.X[i], self.X[i+1]))
                
            if y_i == 0:
                segments.append((self.X[i], self.X[i]))

        if self.Y[-1] == 0:
            segments.append((self.X[-1], self.X[-1]))
            
        return segments

    def plot(self) -> tuple[plt.Figure, plt.Axes]:
        """
        Plota o gráfico da função linear por partes.
        Returns:
            tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.
        Examples:
            >>> x = [0, 2, 4, 5]
            >>> y = [1, 2, 0, 4]
            >>> p = linear_interp(x, y)
            >>> fig, ax = p.plot()
            >>> plt.show()
        """
        fig, ax = plt.subplots()
        # Plota as linhas que interligam os pontos
        ax.plot(self.X, self.Y, linestyle='-', color='blue', label='Função Linear por Partes')

        # Plota os pontos de dados individuais
        ax.plot(self.X, self.Y, 'o', color='red', label='Pontos de Dados') # 'o' para marcadores de círculo

        ax.set_title("Gráfico da Função Linear por Partes")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)
        ax.legend() # Mostra a legenda dos elementos plotados

        return fig, ax
        
    
def linear_interp(x: Sequence, y: Sequence) -> PiecewiseLinearFunction:
    """Cria uma função de interpolação (e extrapolação)s linear a partir de um par de sequências de coordenadas X,Y
    assumindo que os valores X são estritamente crescentes.

    Args:
        x (Sequence): Lista de coordenadas do eixo X (estritamente crescente)
        y (Sequence): Lista de coordenadas do eixo Y
    
    Returns:
        Interpolator: Uma função que retorna o valor interpolado linearmente baseado nos valores X, Y.
    Raises:
        ValueError: Se a quantidade de elementos de X e Y forem diferentes ou tiverem menos de dois pontos.
    Examples:
        >>> x = [0, 2, 4, 5]
        >>> y = [1, 2, 0, 4]
        >>> p = linear_interp(x, y)
        >>> print(p(1.5))
        1.75
    """
    
    if len(x) != len(y):
        raise ValueError("Lenght of X is different of Y")
    if len(x) < 2:
        raise ValueError("There must be atleast 2 points")
    
    return PiecewiseLinearFunction(x, y)


if __name__ == "__main__":
    x = [0, 1, 2, 3, 4]
    y = [1, 3, 2, 5, 4]
    plf = linear_interp(x, y)
    fig, ax = plf.plot()
    plt.show()

    a = [-1, 0, 1, 2]
    b = [1, -2, 0, 2]
    plf2 = linear_interp(a, b)  
    fig2, ax2 = plf2.plot()
    plt.show()

    x_poly = [0, 1, 2, 3]
    y_poly = [1, 2, 0, 5]

    # Usando a função poly_interp
    P = poly_interp(x_poly, y_poly)
    X_plot = [i / 10 for i in range(0, 31)]  # domínio para visualização
    Y_plot = [P(x) for x in X_plot]


    plt.figure()
    plt.plot(X_plot, Y_plot, label="Interpolador Lagrange (função)")
    plt.scatter(x_poly, y_poly, color="red", zorder=5, label="Pontos originais")
    plt.title("Interpolação Polinomial via Função poly_interp")
    plt.xlabel("x")
    plt.ylabel("P(x)")
    plt.grid(True)
    plt.legend()
    plt.show()


    # --- Dados de exemplo ---
    x = [0.0, 1.0, 2.0]
    y = [1.0, 2.0, 0.0]
    dy = [0.0, 1.0, -1.0]

    # --- Cria interpolador de Hermite ---
    P = hermite_interp(x, y, dy)

    # --- Gera pontos para o gráfico ---
    X_plot = [i / 20 for i in range(-5, 61)]  # de -0.25 até 3.05
    Y_plot = [P.evaluate(X) for X in X_plot]

    # --- Plota ---
    plt.figure()
    plt.plot(X_plot, Y_plot, label="Interpolador Hermite", color="blue")
    plt.scatter(x, y, color="red", zorder=5, label="Pontos originais")

    # Desenha setinhas indicando derivadas (slopes)
    for xi, yi, dyi in zip(x, y, dy):
        plt.arrow(
            xi, yi, 0.3, 0.3 * dyi, 
            head_width=0.05, head_length=0.05,
            fc='green', ec='green', zorder=6
        )

    plt.title("Interpolação de Hermite")
    plt.xlabel("x")
    plt.ylabel("P(x)")
    plt.grid(True)
    plt.legend()
    plt.show()

    import numpy as np

    # --- Dados de entrada baseados em f(x) = sin(x) ---
    x = [0.0, np.pi/2, np.pi]
    y = [np.sin(xi) for xi in x]  # [0.0, 1.0, 0.0]
    dy = [np.cos(xi) for xi in x] # [1.0, 0.0, -1.0]

    # --- Cria interpolador de Hermite ---
    P = HermiteInterpolation(x, y, dy)

    # --- Gera pontos para o gráfico ---
    # Vamos plotar de -0.5 a 4.0
    X_plot = np.linspace(-0.5, 4.0, 100)
    Y_plot = [P.evaluate(X) for X in X_plot]

    # Gera a curva real do sin(x) para comparação
    Y_real = np.sin(X_plot)

    # --- Plota ---
    plt.figure()
    plt.plot(X_plot, Y_plot, label="Interpolador Hermite P(x)", color="blue")
    plt.plot(X_plot, Y_real, label="Função Real (sin(x))", color="green", linestyle="--")
    plt.scatter(x, y, color="red", zorder=5, label="Pontos originais")

    # Desenha setinhas indicando derivadas (slopes)
    for xi, yi, dyi in zip(x, y, dy):
        plt.arrow(
            xi, yi, 0.4, 0.4 * dyi, 
            head_width=0.05, head_length=0.05,
            fc='orange', ec='orange', zorder=6
        )

    plt.title("Interpolação de Hermite (em sin(x))")
    plt.xlabel("x")
    plt.ylabel("P(x)")
    plt.grid(True)
    plt.legend()
    plt.ylim(-1.5, 1.5) # Ajusta o zoom vertical
    plt.show()

    x = [0.0, 1.0, 2.0, 3.0]
    y = [1.0, 2.0, 4.5, 2.5]
    dy = [0.0, 1.0, -0.5, 0.5]

    # --- Cria interpolador de Hermite ---
    P = hermite_interp(x, y, dy)

    # --- Gera pontos para o gráfico ---
    X_plot = [i / 20 for i in range(-5, 81)]  # de -0.25 até 4.05
    Y_plot = [P.evaluate(X) for X in X_plot]

    # --- Plota ---
    plt.figure(figsize=(7, 4))
    plt.plot(X_plot, Y_plot, label="Interpolador de Hermite", color="blue")
    plt.scatter(x, y, color="red", zorder=5, label="Pontos originais")

    # Desenha setinhas indicando derivadas (slopes)
    for xi, yi, dyi in zip(x, y, dy):
        plt.arrow(
            xi, yi, 0.3, 0.3 * dyi,
            head_width=0.05, head_length=0.05,
            fc='green', ec='green', zorder=6
        )

    plt.title("Interpolação de Hermite com 4 pontos")
    plt.xlabel("x")
    plt.ylabel("P(x)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
