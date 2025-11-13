import math
import statistics
from polinomios import Polinomio
import numpy as np

def ajuste_linear(x: list[float], y: list[float]) -> Polinomio:
    """
    Ajusta y = a*x + b aos pontos (x, y) por mínimos quadrados (erro vertical).

    Args:
        x: Valores da variável independente.
        y: Valores da variável dependente (mesmo tamanho de x).

    Returns:
        Polinomio: Classe Polinomio contendo os coeficientes

    Raises:
        ValueError: Tamanhos diferentes ou menos de dois pontos.
        ZeroDivisionError: Variância de x igual a zero.
    """
    n = len(x)
    if n != len(y):
        raise ValueError("Ambas as listas devem ter o mesmo tamanho.")
    if n < 2:
        raise ValueError("Precisa de pelo menos dois pontos.")

    mx = statistics.mean(x)
    my = statistics.mean(y)

    cov_xy = math.fsum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x  = math.fsum((xi - mx) ** 2 for xi in x)

    if var_x == 0.0:
        raise ZeroDivisionError("A variância de x é zero.")

    a = cov_xy / var_x
    b = my - a * mx
    return Polinomio([a,b])

def ajuste_polinomial(x: list[float], y: list[float], n = 2, precisao = 5) -> Polinomio:
    """
    Ajusta y = a_0*x^n + a_1*x^(n-1) + ... + a_n aos pontos (x,y) por mínimos quadrados (erro vertical)

    Args:
        x: Valores da variável independente.
        y: Valores da variável dependente (mesmo tamanho de x).

    Returns:
        Polinomio: Classe Polinomio contendo os coeficientes

    Raises:
        ValueError: Tamanhos diferentes, menos de dois pontos ou grau inadequado.
        ZeroDivisionError: Variância de x igual a zero.
    """

    if len(x) != len(y):
        raise ValueError("Ambas as listas devem ter o mesmo tamanho.")
    if len(x) < 2:
        raise ValueError("Precisa de pelo menos dois pontos.")
    if n > len(x) - 1:
        raise ValueError("O grau do polinomio deve ser menor que o numero de pontos.")
    X = np.array(x)
    Y = np.array(y)
    Coeficientes = np.polyfit(X,Y,n)
    Poly = Polinomio([round(Coeficientes[i],precisao) for i in range(len(Coeficientes))])
    return Poly

if __name__ == "__main__":
    x = [0, 1, 2, 3, 4]
    y = [1.1, 1.9, 3.0, 3.9, 5.2]

    Px = ajuste_linear(x,y)
    print("Ajuste Linear: ", f"y = {Px[0]:.2f}x + {Px[1]:.2f}")
    Px_2 = ajuste_polinomial(x,y,2)
    Px_3 = ajuste_polinomial(x,y,3)
    print("Ajuste quadrático:",f"y = {Px_2[0]:.2f}x^2 + {Px_2[1]:.2f}x + {Px_2[2]:.2f}")
    print("Ajuste cúbico:",f"y = {Px_3[0]:.2f}x^3 + {Px_3[1]:.2f}x^2 + {Px_3[2]:.2f}x + {Px_3[3]:.2f}")