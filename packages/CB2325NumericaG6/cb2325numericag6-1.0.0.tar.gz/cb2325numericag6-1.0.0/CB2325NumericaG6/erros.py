import numpy as np

def erro_absoluto(valor_real, valor_aprox):
    """
    Calcula o erro absoluto entre um ou mais valores reais e aproximados.
    
    Esta função é 'vectorizada': ela aceita tanto números únicos
    quanto arrays NumPy.

    Fórmula: ea = |valor_real - valor_aprox|
    
    Args:
        valor_real (float ou np.ndarray): O valor exato ou de referência.
        valor_aprox (float ou np.ndarray): O valor obtido ou medido.

    Returns:
        float ou np.ndarray: O erro absoluto.
    """
    # np.abs lida automaticamente com escalares e arrays
    return np.abs(valor_real - valor_aprox)

def erro_relativo(valor_real, valor_aprox):
    """
    Calcula o erro relativo entre um ou mais valores reais e aproximados.
    
    Esta função é 'vectorizada' e trata corretamente a divisão por zero.

    Fórmula: er = |valor_real - valor_aprox| / |valor_real|
    
    Args:
        valor_real (float ou np.ndarray): O valor exato ou de referência.
        valor_aprox (float ou np.ndarray): O valor obtido ou medido.

    Returns:
        float ou np.ndarray: O erro relativo. 
                          Retorna np.inf se valor_real for 0 e valor_aprox não.
                          Retorna 0.0 se ambos forem 0.
    """
    # Garante que a entrada seja um array NumPy para operações vectorizadas
    # Se já for escalar, np.asarray() lida com isso sem problemas
    valor_real = np.asarray(valor_real)
    valor_aprox = np.asarray(valor_aprox)
    
    ea = erro_absoluto(valor_real, valor_aprox)
    
    # Prepara um array de saída com o mesmo formato da entrada,
    # preenchido com np.inf (para o caso de divisão por zero)
    # dtype=float garante que tenhamos um float mesmo se a entrada for int
    er = np.full_like(ea, np.inf, dtype=float)
    
    # Encontra os índices onde valor_real NÃO é zero
    indices_nao_zero = np.where(valor_real != 0)
    
    # Calcula o erro relativo apenas para esses índices
    # np.abs(valor_real[indices_nao_zero]) garante que o denominador seja positivo
    er[indices_nao_zero] = ea[indices_nao_zero] / np.abs(valor_real[indices_nao_zero])

    # Caso especial: onde valor_real e valor_aprox são 0, o erro é 0
    indices_ambos_zero = np.where((valor_real == 0) & (valor_aprox == 0))
    er[indices_ambos_zero] = 0.0

    # Se a entrada foi um único número (escalar), retorna um escalar
    if er.ndim == 0: # ndim é num de dimensões
        return float(er)
        
    return er
