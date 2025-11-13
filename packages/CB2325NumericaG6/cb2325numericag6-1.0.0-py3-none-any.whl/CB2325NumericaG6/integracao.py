from typing import Callable


def integral(f:Callable, start: float, end: float, divisions: int) -> float:
    """Esse método calcula a integral de uma função por aproximação trapezoidal
    Args:
        f (Callable): Função a ser integrada
        start (float): Ponto inicial do intervalo
        end (float): Ponto final do intervalo
        divisions (int): Número de subdivisões do intervalo: números maiores implicam uma aproximação mais precisa, mas também consome mais CPU.
    Returns:
        float: Valor da integral.
    Examples:
        >>> import math
        >>> f = lambda x: math.sin(x)**2+math.cos(x)**2
        >>> i = integracao.integral(f, 0, 2, 1000)
        >>> print(i)
        2.0
    """
    
    sumVal: float = 0
    Xincrement: float = abs(start-end)/divisions
    
    i: float = start
    while i < end:
        area: float = ( f(i) + f(min(end, i+Xincrement)) )
        area *= Xincrement/2.0 if i+Xincrement < end else (end-i)/2.0
        
        sumVal += area
        i += Xincrement
    
    return sumVal
