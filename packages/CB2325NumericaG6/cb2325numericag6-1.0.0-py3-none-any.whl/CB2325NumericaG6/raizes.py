# Alunos Responsáveis: Marcelo Alves, Vinícios Flesh

from typing import Callable, List
# Tentar executar localmente a partir da pasta geral do repositório vai dar erro, mas é assim mesmo que o import deve estar para o deploy.
# Se quiser testar localmente use o comando 'python -m CB2325NumericaG6.raizes' sem as aspas.
from .polinomios import Polinomio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


def secante(f: Callable, a: float, b: float, tol: float = 1e-6) -> float:
    """
    Método da secante:
        Consiste em pegar dois pontos próximos a e b e então realiza a apro-
        ximação da raiz a partir do ponto onde a reta que intercepta ambos os
        pontos encontra o eixo X (m), repetindo o processo até que abs(f(m)) 
        seja menor que a tolerância exigida.

    Parametros:
        f: Função a ser analizada
        a: Ponto inicial da função f
        b: Ponto final da função f
        tol: Tolerância para o erro da aproximação final

    Saida:
        Aproximação da raiz da função encontrada.
    """

    a, b = (a, b) if a < b else (b, a)

    interacao = 0
    aproximacao = (f(b) * a - f(a) * b) / (f(b) - f(a))
    while abs(f(aproximacao)) >  tol:
        interacao += 1
        if interacao > 100:
            raise RuntimeError('Método não convergiu')
        a = b
        b = aproximacao
        aproximacao = (f(b) * a - f(a) * b) / (f(b) - f(a))
    return aproximacao
    

def plot_secante(f: Callable, intervalo:tuple[float, float], a: float, b: float, tol: float=1e-6) -> Figure:
    def func_plot() -> None:
        """
        Função auxiliar para visualização gráfica da secante
        """
        aux.scatter([a, b], [f(a), f(b)], s=10, color='orange', zorder=2)
        aux.plot([a, b, aproximacao], [f(a), f(b), 0], color='r', zorder=1)
        aux.scatter(aproximacao, 0, s=7, color='k', zorder=1)
        aux.plot([aproximacao, aproximacao], [f(aproximacao), 0])

    """
    Plotagem do método da secante:
        Consiste em pegar dois pontos próximos a e b e então realiza a apro-
        ximação da raiz a partir do ponto onde a reta que intercepta ambos os
        pontos encontra o eixo X (m), repetindo o processo até que abs(f(m)) 
        seja menor que a tolerância exigida.

    Parametros:
        f: Função a ser analizada
        intervalo: Intervalo da plotagem da função
        a: Ponto inicial da função f
        b: Ponto final da função f
        tol: Tolerância para o erro da aproximação final

    Saida:
        fig: Imagem da plotagem gerada
        Plotagem da representação do processo
    """

    fig, aux = plt.subplots()
    aux.set_xlabel('x')
    aux.set_ylabel('y')
    aux.set_title('Método da secante')
    aux.axhline(0, color='k', lw=1)

    x = np.linspace(intervalo[0], intervalo[1], 100)
    aux.plot(x, f(x), color='#07d')

    a, b = (a, b) if a < b else (b, a)

    interacao = 0
    aproximacao = (f(b) * a - f(a) * b) / (f(b) - f(a))
    func_plot()
    while abs(f(aproximacao)) >  tol:
        interacao += 1
        if interacao > 100:
            raise RuntimeError('Método não convergiu')
        a = b
        b = aproximacao
        aproximacao = (f(b) * a - f(a) * b) / (f(b) - f(a))
        if aproximacao < min(intervalo) or aproximacao > max(intervalo):
            raise ValueError(f'Aproximação fora do intervalo [{min(intervalo)}, {max(intervalo)}]')
        func_plot()


    plt.show()
    return fig


def bisseccao(f: Callable, a: float, b: float, tol: float=1e-6) -> float:
    """
    Método da bissecção:
        Consiste em pegar um intervalo a e b na qual f(a) tem sinal oposto a f(b),
        então realiza a aproximação da raiz a partir de média do intervalo (m), 
        repetindo o processo até que abs(f(m)) seja menor que a tolerância exigida.

    Parametros:
        f: Função a ser analizada
        a: Intervalo inicial da função f
        b: Intervalo final da função f
        tol: Tolerancia para o erro da aproximação final

    Saida:
        Aproximação da raiz da função no intervalo [a, b]
    """

    if f(a) * f(b) > 0:
        raise ValueError('f(a) tem o mesmo sinal que f(b), não há garantia da existencia de uma raiz')
    
    a, b = (a, b) if f(a) < f(b) else (b, a)

    aproximacao = (a + b) / 2
    while abs(f(aproximacao)) > tol:
        if f(aproximacao) > 0:
            b = aproximacao
        else:
            a = aproximacao
        
        aproximacao = (a + b) / 2

    return aproximacao


def plot_bisseccao(f: Callable, intervalo:tuple[float, float], a:float, b:float, tol: float = 1e-6) -> Figure:
    def func_plot():
        """Função auxiliar para o método da bissecção"""
        aux.scatter(a, f(a), s=10, color='#00D', zorder=2)
        aux.scatter(b, f(b), s=10, color='#D00', zorder=2)
        aux.plot([a, b], [f(a), f(a)], color='r')
        aux.plot([aproximacao, aproximacao], [f(a), f(aproximacao)])

    """
    Plotagem método da bissecção:
        Consiste em pegar um intervalo a e b na qual f(a) tem sinal oposto a f(b),
        então realiza a aproximação da raiz a partir de média do intervalo (m), 
        repetindo o processo até que abs(f(m)) seja menor que a tolerância exigida.

    Parametros:
        f: Função a ser analizada
        intervalo: Intervalor de plotagem
        a: Ponto inicial da função f
        b: Ponto final da função f
        tol: Tolerancia para o erro da aproximação final

    Saida:
        fig: Imagem do processo de bissecção
        Plotagem do processo de bissecção
    """

    if f(a) * f(b) > 0:
        raise ValueError('f(a) tem o mesmo sinal que f(b), não há garantia da existencia de uma raiz')

    fig, aux = plt.subplots()
    aux.set_xlabel('x')
    aux.set_ylabel('y')
    aux.set_title('Método da bissecção')
    aux.axhline(0, color='k', lw=1)

    x = np.linspace(intervalo[0], intervalo[1], 100)
    aux.plot(x, f(x), color='#07d')

    a, b = (a, b) if f(a) < f(b) else (b, a)

    aproximacao = (a + b) / 2
    func_plot()
    while abs(f(aproximacao)) > tol:
        if f(aproximacao) > 0:
            b = aproximacao
        else:
            a = aproximacao
        
        aproximacao = (a + b) / 2
        func_plot()

    plt.show()
    return fig


def newton_raphson(f: Callable, df: Callable, a:float, tol: float= 1e-6) -> float:
    """
    Método de Newton Raphson:
        Consiste em pegar um ponto a e então realiza a aproximação da raiz a
        partir do ponto onde a reta tangente o ponto a encontra o eixo X (m),
        repetindo o processo até que abs(f(m)) seja menor que a tolerância 
        exigida.

    Parametros:
        f: Função a ser analizada
        df: Derivada de f
        a: Ponto inicial da função f
        tol: Tolerancia para o erro da aproximação final

    Saida:
        Aproximação da raiz da função encontrada.
    """
    
    interacao = 0
    aproximacao = a - f(a)/df(a)
    while abs(f(aproximacao)) > tol:
        interacao += 1
        if interacao > 100:
            raise RuntimeError('Método não convergiu')
        a = aproximacao
        aproximacao = a - f(a)/df(a)
    
    return aproximacao


def plot_newton_raphson(f: Callable, intervalo:tuple[float, float], df: Callable, a:float, tol: float = 1e-6) -> Figure:
    def func_plot():
        """
        Função auxiliar para plotagem do método de newton-raphson
        """
        aux.scatter(a, f(a), s=10, color='orange', zorder=2)
        aux.plot([a, aproximacao], [f(a), 0], color='r', zorder=1)
        aux.scatter(aproximacao, 0, s=7, color='k', zorder=1)
        aux.plot([aproximacao, aproximacao], [f(aproximacao), 0])

    """
    Plotagem do método de Newton Raphson:
        Consiste em pegar um ponto a e então realiza a aproximação da raiz a
        partir do ponto onde a reta tangente o ponto a encontra o eixo X (m),
        repetindo o processo até que abs(f(m)) seja menor que a tolerância 
        exigida.

    Parametros:
        f: Função a ser analizada
        intervalo: Intervalo da plotagem
        df: Derivada de f
        a: Ponto inicial da função f
        tol: Tolerancia para o erro da aproximação final

    Saida:
        fig: Imagem gerada pelo método de newton-raphson
        plotagem do método de newton-raphson 
    """

    fig, aux = plt.subplots()
    aux.set_xlabel('x')
    aux.set_ylabel('y')
    aux.set_title('Método da bissecção')
    aux.axhline(0, color='k', lw=1)

    x = np.linspace(intervalo[0], intervalo[1], 100)
    aux.plot(x, f(x), color='#07d')

    interacao = 0
    aproximacao = a - f(a)/df(a)
    func_plot()
    while abs(f(aproximacao)) > tol:
        interacao += 1
        if interacao > 100:
            raise RuntimeError('Método não convergiu')
        a = aproximacao
        aproximacao = a - f(a)/df(a)

        if aproximacao < min(intervalo) or aproximacao > max(intervalo):
            raise ValueError(f'Aproximação fora do intervalo [{min(intervalo)}, {max(intervalo)}]')
        func_plot()

    plt.show()
    return fig


def _sturmSequence(P: Polinomio) -> List[Polinomio]:
    sequence = [P, P.diff()]
    remainder = sequence[1]
    index = 1
    while True:
        _, remainder = sequence[index-1].divideBy(sequence[index])
        if remainder.isZero:
            break

        sequence.append(-remainder)
        index += 1

    return sequence


def _countSignVariations(sequence: List[Polinomio], x):
    # TODO: Talvez substituir tolerância por algum calculo de erro no futuro quando .erros.py for implementado
    tolerance = 1e-15

    changes = 0
    signs = []
    for p in sequence:
        value = p.evaluate(x)
        if abs(value) < tolerance:
            continue

        if value > 0:
            signs.append(True)
        else:
            signs.append(False)

    if len(signs) < 2:
        return 0
    
    last = signs[0]
    for i in range(1, len(signs)):
        if signs[i] != last:
            last = signs[i]
            changes += 1

    return changes


def sturm(P: Polinomio, a: float, b: float) -> int:
    """
        Calcula o número de raízes reais de um polinomio no intervalo (a,b].

        Args:
            P (Polinomio): Polinomio a ser avaliado.
            a (float): Extremo inferior do intervalo.
            b (flaot): Extremo superior do intervalo.
        
        Returns:
            int: Número de raízes reais no intervalo (a,b]
        
        Raises:
            ValueError: Limite inferior a é maior ou igual que limite superior b
        
        Examples:
            >>> P = Polinomio([1.0,-2.0,-2.0,2.0, 0])
            >>> raizes = sturm(P, -2, 3)
            >>> print(raizes)

    """
    if a >= b:
        raise ValueError("O limite inferior 'a' deve ser menor que o limite superior 'b'.")

    sequence = _sturmSequence(P)

    signsA = _countSignVariations(sequence, a)
    signsB = _countSignVariations(sequence, b)

    return signsA - signsB


if __name__ == '__main__':
    f = lambda x: x**2 - 2
    df = lambda x: 2*x

    print(secante(f, 1, 1.5, 1e-6))
    plot_secante(f, (-2, 2), 1, 1.5, 1e-6)

    print(bisseccao(f, 0, 2, 1e-6))
    plot_bisseccao(f, (-2, 2), 0, 2, 1e-6)

    print(newton_raphson(f, df, 5, 10 **-6))
    plot_newton_raphson(f, (-2, 2), df, 1, 1e-6)


    P = Polinomio([1.0,-2.0,-2.0,2.0, 0])
    bounds = P.getRealRootBounds()
    print(bounds)
    raizes = sturm(P, bounds[0], bounds[1])
    print(raizes)