import numpy as np
import pytest
from erros import erro_absoluto, erro_relativo

# 1. Teste com o exemplo exato do PDF
def test_exemplo_pdf():
    valor_real = 3.141592
    valor_aprox = 3.14
    
    ea = erro_absoluto(valor_real, valor_aprox)
    er = erro_relativo(valor_real, valor_aprox)
    
    # pytest.approx() é usado para comparar números de ponto flutuante (floats)
    # com uma pequena tolerância, o que é essencial em cálculo numérico.
    assert ea == pytest.approx(0.001592)
    assert er == pytest.approx(0.0005067, abs=1e-8) # Tolerância absoluta de 10^-8

# 2. Testes com valores escalares (simples)
def test_escalares():
    assert erro_absoluto(10, 8) == 2
    assert erro_relativo(10, 8) == 0.2
    
    # Testa se o valor absoluto está correto (ordem não importa)
    assert erro_absoluto(8, 10) == 2
    assert erro_relativo(8, 10) == 0.25 # (Note que o relativo muda!)

# 3. Testes com arrays NumPy (vectorização)
def test_numpy_arrays():
    valor_real = np.array([10, 100, 5])
    valor_aprox = np.array([9, 95, 5])
    
    ea_esperado = np.array([1, 5, 0])
    er_esperado = np.array([0.1, 0.05, 0.0])
    
    # np.testing.assert_allclose é a forma correta de comparar arrays
    np.testing.assert_allclose(erro_absoluto(valor_real, valor_aprox), ea_esperado)
    np.testing.assert_allclose(erro_relativo(valor_real, valor_aprox), er_esperado)

# 4. Testes de casos especiais (divisão por zero) para erro_relativo
def test_casos_especiais_relativo():
    # Caso 1: valor_real é 0, mas valor_aprox não é. Erro deve ser infinito.
    assert erro_relativo(0, 5) == np.inf
    
    # Caso 2: Ambos são 0. Erro é 0.
    assert erro_relativo(0, 0) == 0.0
    
    # Caso 3: Array com casos mistos
    valor_real = np.array([10, 0, 0])
    valor_aprox = np.array([8, 5, 0])
    
    er_esperado = np.array([0.2, np.inf, 0.0])
    
    np.testing.assert_allclose(erro_relativo(valor_real, valor_aprox), er_esperado)