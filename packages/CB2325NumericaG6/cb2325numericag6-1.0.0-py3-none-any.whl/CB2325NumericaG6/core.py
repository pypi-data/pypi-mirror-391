from typing import Callable, Optional, Sequence
import matplotlib.pyplot as plt

# Gostei muito da implementação dessas classes da lista 7 do professor então decidi implementar com pequenas modificações
class Domain:
    """
    Define o domínio no qual uma função real existe.
    """
    min = None
    max = None

    def __contains__(self, x):
        raise NotImplementedError
    
    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        return self.__repr__()
    
    def copy(self):
        raise NotImplementedError 


class Interval(Domain):
    """
    Define um intervalo de números reais.
    """
    def __init__(self, p1, p2):
        self.inff, self.supp = min(p1, p2), max(p1, p2)
    
    @property
    def min(self):
        return self.inff

    @property
    def max(self):
        return self.supp
    
    @property
    def size(self):
        return (self.max - self.min)
    
    @property
    def half(self):
        return (self.max + self.min)/2.0
    
    def __contains__(self, other):
        if isinstance(other, Interval):
            return other.min >= self.min and other.max <= self.max
        elif isinstance(other, (float, int)):
            return self.min <= other <= self.max
        elif isinstance(other, Sequence):
            for i in other:
                if not (self.min <= i <= self.max):
                    return False
            return True
        else:
            return False


    def __str__(self):
        return f'[{self.min:2.4f}, {self.max:2.4f}]' 

    def __repr__(self):
        return f'[{self.min!r:2.4f}, {self.max!r:2.4f}]'
    
    def copy(self):
        return Interval(self.min, self.max)

    def intersect(self, other: 'Interval') -> Optional['Interval']:
        if not isinstance(other, Interval):
            return None
        
        newMin = max(self.min, other.min)
        newMax = min(self.max, other.max)
        return Interval(newMin,newMax) if newMin <= newMax else None

class RealFunction:
    """
    Classe abstrata que deve ser utilizada para implementação de funções reais, e.g. Polinomios
    """

    f: Callable[[float], float]
    prime: Optional[Callable[[float], float]]
    domain: Optional[Interval]
    
    def eval_safe(self, x):
        if self.domain is None or x in self.domain:
            return self.f(x)
        else:
            raise Exception("The number is out of the domain")

    def prime_safe(self, x):
        if self.prime is None:
            raise NotImplementedError("Derivative function (prime) is not defined for this function.")
        if self.domain is None or x in self.domain:
            return self.prime(x)
        else:
            raise Exception("The number is out of the domain")
        
    def __call__(self, x) -> float:
        return self.eval_safe(x)
    
    def plot(self, intervalo: Optional[Interval] = None, pontos: int = 100) -> tuple[plt.Figure, plt.Axes]:
        """
        Plota o gráfico da função real no intervalo especificado. Caso nenhum intervalo seja fornecido,
        será utilizado o domínio da função. Se o domínio da função também for None,uma exceção será 
        levantada. O número de pontos no gráfico poder ser ajustado, sendo 100 o padrão.

        Args:
            intervalo (Optional[Interval], optional): Intervalo para plotagem. Default é None.
            pontos (int, optional): Número de pontos no gráfico. Default é 100.
        Returns:
            tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.
        Examples:
            >>> f = Polinomio([1, -3, 2], Interval(0, 5))  # Representa P(x) = x^2 - 3x + 2
            >>> fig, ax = f.plot(Interval(0, 5), pontos=200)
            >>> plt.show()
        """
        dominio = self.domain
        if intervalo is not None:
            dominio = intervalo
        if dominio is None:
            raise Exception("Domínio da função não está definido.")
        fig, ax = plt.subplots()
        X = linspace(dominio.min, dominio.max, pontos)
        Y = [self(val) for val in X]
        ax.plot(X,Y)
        return fig, ax
    
def linspace(min: float, max: float, points: int) -> list[float]:
    """
    Retorna uma lista de pontos igualmente distribuídos em um intervalo

    Args:
        min (float): Valor mínimo do intervalo de pontos
        max (float): Vamor máximo do intervalo de pontos
        points (int): Quantidade de pontos

    Returns:
        list[float]: Lista de pontos igualmente distribuídos no intervalo

    Examples:
        >>> valores = linspace(0, 5, 6)
        >>> print(valores)
        [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    """
    if points < 2:
        return [min]
    step = (max - min) / (points - 1)
    return [(step * i + min) for i in range(points)]

def safe_intersect(d1: Optional['Interval'], d2: Optional['Interval']) -> Optional['Interval']:
    """
    Calcula a intersecção de dois intervalos, lidando com valores None.
    """
    if d1 is None or d2 is None:
        return None

    return d1.intersect(d2)