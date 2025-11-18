import math
from functools import reduce
import warnings
from typing import Sequence, Union

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

ArrayLike = Union[Sequence[float], np.ndarray]

def ajuste(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        tipo: str, 
        **kwargs
) -> np.ndarray:
    """
    Realiza ajustes de curvas pelo Método dos Mínimos Quadrados (MMQ)
    para diversos modelos.

    As funções de ajuste também podem ser chamadas separadamente.

    Parâmetros
    ----------
    valores_x : ArrayLike
        Variável independente (ou matriz de variáveis para 'mul').
    valores_y : ArrayLike
        Variável dependente.
    tipo : str 
        Modelo de ajuste:
        - 'lin': Linear (y = ax + b)
        - 'pol': Polinomial (requer 'grau_pol')
        - 'sen': Senoidal (y = A*sin(Bx + C) + D, recomenda-se
            declarar 'T_aprox', já que estimativa pode falhar)
        - 'exp': Exponencial (y = b*e^(ax), linearizado via ln(y))
        - 'log': Logarítmico(y = a + b*ln(x), linearizado via ln(x))
        - 'mul': Regressão Múltipla (usa 'incluir_intercepto')
    **kwargs :
        Parâmetros opcionais e específicos do modelo, como:
        - grau_pol (int): Grau do polinômio (tipo='pol').
        - T_aprox (float): Período aproximado inicial (tipo='sen').
        - incluir_intercepto (bool): Inclui termo independente (tipo='mul').
        - plt_grafico (bool): Se True, exibe o gráfico do ajuste (opcional). 
            Padrão: False.
        - expr (bool): Se True, imprime a expressão matemática encontrada (opcional).
            Padrão: False.
    Retorna
    -------
    np.ndarray
        Coeficientes do modelo ajustado. A ordem depende do modelo escolhido.
    """

    funcoes = {
        'lin': ajuste_linear,
        'pol': ajuste_polinomial,
        'sen': ajuste_senoidal,
        'exp': ajuste_exponencial,
        'log': ajuste_logaritmo,
        'mul': ajuste_multiplo,
    }

    if tipo not in funcoes:
        raise ValueError(f"Tipo de ajuste desconhecido: {tipo}")

    func = funcoes[tipo]
    if 'mostrar_parametros' in kwargs and kwargs['mostrar_parametros']:
        import inspect
        print(f"Parâmetros disponíveis para '{tipo}':")
        print(inspect.signature(func))
        return None

    return func(valores_x, valores_y, **kwargs)


def _plotar_grafico(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        func_sym: sp.Expr, 
        titulo: str, 
        qtd_pontos: int = 200
):
    """
    Função auxiliar para plotagem dos ajustes.
    """

    # Tratar a função simbólica

    x_sym = sp.Symbol("x")
    f = sp.lambdify(x_sym, func_sym, "numpy")

    # Gerar os pontos

    x_func = np.linspace(min(valores_x), max(valores_x), qtd_pontos)
    y_func = np.array(f(x_func))    
    y_func = np.broadcast_to(y_func, x_func.shape)

    # Plotar os gráficos

    plt.scatter(
        valores_x, valores_y, 
        color="blue", marker="o", 
        label="Dados Fornecidos"
    )

    plt.plot(
        x_func, y_func, 
        color="black", linewidth=2, 
        label="Função Aproximadora"
    )

    plt.title(titulo)
    plt.xlabel("Eixo x")
    plt.ylabel("Eixo y")
    plt.margins(x=0.1, y=0.1)
    plt.grid(True)
    plt.legend()
    plt.show()


def ajuste_linear(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        plt_grafico: bool = False, 
        expr: bool = False
):
    """
    Modelo: y = ax + b
    Usa regressão linear simples (polinômio de grau 1) via MMQ.
    """
    
    if len(valores_x) != len(valores_y):
        raise ValueError("As listas 'valores_x' e 'valores_y' devem ter o mesmo tamanho.")

    x_medio = reduce(lambda x, y: x + y, valores_x) / len(valores_x)
    y_medio = reduce(lambda x, y: x + y, valores_y) / len(valores_y)

    # Cálculo da covariância de x e y e da variância

    cov_xy = 0
    var_x = 0

    for i in range(len(valores_x)):
        cov_xy += (valores_x[i] - x_medio) * (valores_y[i] - y_medio)
        var_x += (valores_x[i] - x_medio) ** 2

    if var_x == 0:
        raise ValueError(
            f"A variância de valores_x é zero. "
            "Não é possível calcular o ajuste."
            )

    # Cálculo do coeficientes

    a = cov_xy / var_x           
    b = y_medio - a * x_medio 

    # Print da expressão

    if expr:
        print(f"Função linear aproximadora: y = {a:.4f}x + {b:.4f}") 

    # Plot do gráfico

    if plt_grafico:
        x_sym = sp.Symbol("x")
        y_func = a * x_sym + b

        _plotar_grafico(
            valores_x, 
            valores_y,
            y_func,
            "Gráfico do Ajuste Linear"
        )

    return np.array([a, b])


def ajuste_polinomial(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        grau_pol: int, 
        plt_grafico: bool = False, 
        expr: bool = False
):
    """
    Modelo: y = c0 + c1*x + c2*x^2 + ... + cn*x^n

    Requer 'grau_pol'. Usa MMQ para encontrar os coeficientes do
    polinômio.

    Retorna
    -------
    np.ndarray
        Array contendo os coeficientes em ordem crescente do grau da variável associada.
    """

    # Condições de início
    
    if grau_pol is None:
        raise ValueError(
            "Para o ajuste polinomial ('pol'), o parâmetro " \
            "'grau_pol' deve ser fornecido."
        )

    if len(valores_x) != len(valores_y):
        raise ValueError(
            "As listas 'valores_x' e 'valores_y' devem ter o mesmo tamanho."
        )
    
    if grau_pol < 0:
        raise ValueError("grau_pol deve ser não negativo.")

    # Construir matriz de Vandermonde (x_matriz)

    x_matriz = np.array(
        [[valor ** i for i in range(grau_pol + 1)] for valor in valores_x]
    )
    
    # Construir a matriz dos valores de y (y_matriz)

    y_matriz = np.array(valores_y)

    # Obter os coeficientes (array_coeficientes)

    array_coeficientes, *_ = np.linalg.lstsq(x_matriz, y_matriz, rcond=None)

    # Gerar função polinomial aproximadora simbólica (func_aprox)

    x_sym = sp.Symbol("x")
    func_aprox = 0

    for i in range(len(array_coeficientes)):
        func_aprox += array_coeficientes[i] * x_sym ** i

    if expr:
        print(f"Função Polinomial Aproximadora: {func_aprox}")

    # Plotar o gráfico

    if plt_grafico:
        _plotar_grafico(
            valores_x, 
            valores_y,
            func_aprox, 
            f"Gráfico dos Dados Fornecidos e da Função "
            f"Polinomial Aproximadora de Grau {grau_pol}"
        )
    
    # Retornar os coeficientes (array_coeficientes)

    return array_coeficientes


def ajuste_exponencial(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        plt_grafico: bool = False, 
        expr: bool = False
):
    """
    Modelo: y = b * e^(ax)
    Linearizado via logaritmo natural em y: ln(y) = ln(b) + ax.
    Requer que todos os valores de y sejam positivos.
    """

    if len(valores_x) != len(valores_y):
        raise ValueError("As listas 'valores_x' e 'valores_y' devem ter o mesmo tamanho.")

    for y in valores_y:
        if y <= 0:
            raise ValueError("A lista de valores de y possui valores não postivos.")

    ln_Y = [math.log(y) for y in valores_y]
    a, b_aux = ajuste_linear(valores_x, ln_Y)
    b = math.exp(b_aux)

    # Print da expressão

    if expr:
        print(f"Função exponencial aproximadora: y = {b:.4f} * e^({a:.4f}x)")

    # Plot do gráfico

    if plt_grafico:
        x_sym = sp.Symbol("x")
        y_func = b * sp.exp(a * x_sym)

        _plotar_grafico(
            valores_x, 
            valores_y,
            y_func,
            "Gráfico do Ajuste Exponencial"
        )
    
    return np.array([a, b])


def ajuste_logaritmo(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        plt_grafico: bool = False, 
        expr: bool = False
):
    """
    Modelo: y = a + b * ln(x)
    Linearizado usando ln(x) como nova variável independente.
    Requer que todos os valores de x sejam positivos.
    """
    
    if len(valores_x) != len(valores_y):
        raise ValueError("As listas 'valores_x' e 'valores_y' devem ter o mesmo tamanho.")

    if any(x <= 0 for x in valores_x):
        raise ValueError("A lista de valores de x possui valores não positivos.")

    ln_X = [math.log(x) for x in valores_x]
    b, a = ajuste_linear(ln_X, valores_y)


    # Print da expressão

    if expr:
        print(f"Função logaritmo aproximadora: y = {a:.4f} + {b:.4f} * ln(x)")

    # Plot do gráfico

    if plt_grafico:
        x_sym = sp.Symbol("x")
        y_func = a + b * sp.ln(x_sym)

        _plotar_grafico(
            valores_x, 
            valores_y,
            y_func,
            "Gráfico do Ajuste Logaritmo"
        )

    return np.array([a, b])


def ajuste_senoidal(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        T_aprox: float, 
        plt_grafico: bool = False, 
        expr: bool = False
):
    """
    Modelo: y = A * sin(B * x + C) + D

    Lineariza o modelo para diferentes frequências B em torno da
    frequência inicial B_0 = 2pi/(T_aprox).
    Encontra A, C, D para cada B testado e escolhe o melhor ajuste.
    """
    
    if len(valores_x) != len(valores_y):
        raise ValueError(
            "As listas 'valores_x' e 'valores_y' devem ter o mesmo tamanho."
        )

    # Calcular a frequência aproximada 

    freq_aprox = (2 * np.pi) / T_aprox

    valores_x = np.array(valores_x)

    freq_list = np.linspace(freq_aprox * 0.5, freq_aprox * 1.5, 400)
    y_matriz = np.array(valores_y)
    erros_vals = []
    parametros = []

    for freq in freq_list:
        x_matriz = np.array([
            [np.sin(freq * v), np.cos(freq * v), 1] for v in valores_x
        ])

        try:
            coeff, *_ = np.linalg.lstsq(x_matriz, y_matriz, rcond=None)
        except np.linalg.LinAlgError:
            erros_vals.append(np.inf)
            parametros.append((0, 0, 0))
            continue

        a, b, d = coeff
        erro = np.linalg.norm(
            y_matriz - (a * np.sin(freq * valores_x) 
                        + b*np.cos(freq * valores_x) + d)) ** 2
        erros_vals.append(erro)
        parametros.append((a, b, d))

    idx_min = int(np.argmin(erros_vals))
    freq_final = freq_list[idx_min]
    a, b, d = parametros[idx_min]

    # Gerar array de coeficientes (array_coeficientes)
    # Contém A, B, C, D tal que a função aproximadora é definida como 
    # y = A * sin( B* x + C) + D.

    A = float(np.hypot(a, b))
    B = freq_final
    C = float(np.arctan2(b, a))
    D = d

    array_coeficientes = np.array([A, B, C, D])

    # Gerar função senoidal aproximadora simbólica (func_aprox)

    x_sym = sp.Symbol("x")
    func_aprox = A * sp.sin(B * x_sym + C) + D

    def _clean_zero(x, tol=1e-12):
        return 0.0 if abs(x) < tol else x

    C_vis = _clean_zero(C)
    D_vis = _clean_zero(D)

    sign1 = "+" if C >= 0 else "-"
    sign2 = "+" if D >= 0 else "-"

    C_vis = abs(C_vis)
    D_vis = abs(D_vis)

    if expr:
        print(f"Função Senoidal Aproximadora: "
              f"{A:.4f} * sin({B:.4f}x {sign1} {C_vis:.4f}) {sign2} {D_vis:.4f}")

    # Plotar o Gráfico

    if plt_grafico:
        _plotar_grafico(
            valores_x, 
            valores_y,
            func_aprox, 
            "Gráfico dos Dados Fornecidos e da Função Senoidal Aproximadora",
            qtd_pontos=600
        )
    
    # Retornar o array de coeficientes (array_coeficientes)

    return array_coeficientes


def ajuste_multiplo(
        valores_var: ArrayLike, 
        valores_y: ArrayLike, 
        incluir_intercepto: bool = False, 
        expr: bool = False):
    """
    Modelo: y = c0 + c1*x1 + c2*x2 + ... + cn*xn (Regressão Múltipla)

    Cada linha de 'valores_var' representa uma variável independente.
    Cada coluna (ou índice dentro de cada vetor) representa uma amostra.

    Aplica MMQ diretamente na matriz de variáveis independentes.
    """

    # Construir a matriz de valores das variáveis ind. (x_matriz)

    x_matriz = np.array(valores_var, dtype=float)

    # Construir a matriz de valores da variável dependente (y_matriz)

    y_matriz = np.array(valores_y, dtype=float).reshape(-1, 1)

    # Transpor para o formato exigido pelo MMQ: (n_amostras, n_variáveis)

    x_matriz = x_matriz.T

    # Validar dimensões

    if x_matriz.shape[0] != y_matriz.shape[0]:
        raise ValueError(
                "Formato inconsistente em 'valores_var'. "
                "Forneça uma matriz "
                "(n_variaveis, n_amostras)."
            )

    # Tratar o caso com intercepto

    if incluir_intercepto:
        x_matriz = np.column_stack([np.ones(len(valores_y)), x_matriz])

    # Verificar colinearidade

    tol = 1e-10
    rank = np.linalg.matrix_rank(x_matriz, tol=tol)
    cond = np.linalg.cond(x_matriz)

    if rank < x_matriz.shape[1] or cond > 1e14:
        warnings.warn(
            f"Aviso: matriz quase singular (cond = {cond:.2e}). "
            "Os resultados podem ser instáveis devido à colinearidade.",
            RuntimeWarning
        )

    # Construir a matriz de parâmetros (array_coeficientes)

    array_coeficientes, *_ = np.linalg.lstsq(x_matriz, y_matriz, rcond=None)
    array_coeficientes = array_coeficientes.ravel()

    # Gerar função aproximadora simbólica para regressão múltipla

    if expr:
        if incluir_intercepto:
            qtd_var = x_matriz.shape[1] - 1
            ind_fin = qtd_var + 1
        
            x_sym = sp.symbols(f"x1:{ind_fin}")
            func_aprox = array_coeficientes[0]

            for i in range(qtd_var):
                func_aprox += array_coeficientes[i + 1] * x_sym[i]
        else:
            qtd_var = x_matriz.shape[1]
            ind_fin = qtd_var + 1
        
            x_sym = sp.symbols(f"x1:{ind_fin}")
            func_aprox = 0

            for i in range(qtd_var):
                func_aprox += array_coeficientes[i] * x_sym[i]
        
        print(f"Função Aproximadora para Regressão Múltipla: {func_aprox}")

    # Retornar o array de coeficientes

    return array_coeficientes


def avaliar_ajuste(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        criterio: str, 
        modelo: str, 
        coeficientes: tuple | np.ndarray
    ) -> float | tuple:
    """
    Avalie um modelo de ajuste por meio de um ou mais critérios

    Argumentos:
        valores_x (list): Lista de valores da variável independente.
        valores_y (list): Lista de valores da variável dependente.
        criterio (str): Critério de avaliação ("R2", "R2A", "AIC", 
            "AICc", "BIC", "all").
        modelo (str): Modelo utilizado ("linear", "polinomial", 
            "exponencial", "logaritmo", "senoidal").
        coeficientes (tuple | np.ndarray): Coeficientes do modelo.

    Retorna:
        float | tuple: Valor do critério (float) ou uma tupla com 
            todos os critérios (caso criterio="all").
    
    Raises:
        ValueError: Se as listas de valores x e y tiverem tamanho
            diferente ou os o criterio ou modelo forem desconhecidos.
        ZeroDivisionError: Se for impossível calcular R2A ou AICc.
    """


    if len(valores_x) != len(valores_y):
        raise ValueError("As listas 'valores_x' e 'valores_y' devem ter o mesmo tamanho.")

    if criterio not in ("R2", "R2A", "AIC", "AICc", "BIC", "all"):
        raise ValueError("Critério desconhecido. Use R2, R2A , AIC, AICc, BIC, all")

    if modelo not in ("linear", "polinomial", "exponencial", "logaritmo", "senoidal"):
        raise ValueError("Modelo desconhecido. Use linear, polinomial, exponencial, logaritmo, senoidal")

    valores_x = np.array(valores_x)
    valores_y = np.array(valores_y)
    n = len(valores_x)

    # Adquire os valores de y que a aproximação forneceu

    if modelo == "linear":
        qtd_coeficientes = 2
        y_modelo = coeficientes[0] * valores_x + coeficientes[1]

    elif modelo == "polinomial":
        qtd_coeficientes = len(coeficientes)
        y_modelo = np.polynomial.polynomial.polyval(valores_x, coeficientes)

    elif modelo == "exponencial":
        qtd_coeficientes = 2
        y_modelo = coeficientes[1] * np.exp(coeficientes[0] * valores_x)

    elif modelo == "logaritmo":
        qtd_coeficientes = 2
        y_modelo = coeficientes[0] + coeficientes[1] * np.log(valores_x)

    elif modelo == "senoidal":
        qtd_coeficientes = 4
        y_modelo = coeficientes[0] * np.sin(coeficientes[1] * valores_x + coeficientes[3]) + coeficientes[2]

    # Calcula o resíduo quadrático e o resíduo total (tratando o caso igual a 0)

    media_y = np.mean(valores_y)
    RST = 1e-12 if np.sum((valores_y - media_y) ** 2) == 0 else np.sum((valores_y - media_y) ** 2)
    RSS = max(np.sum((valores_y - y_modelo) ** 2), 1e-12) # Evita problemas no log

    R2 = 1 - (RSS / RST)

    # Calcula os critérios

    if (n - qtd_coeficientes - 1) <= 0 and criterio in ("R2A", "AICc", "all"):
        raise ZeroDivisionError("Não é possível calcular o critério solicitado.")

    if criterio == "R2":
        return R2
    
    elif criterio == "R2A":
        return 1 - ((1- R2) * (n - 1) / (n - qtd_coeficientes - 1))
            
    elif criterio == "AIC":
        return n * np.log(RSS / n) + 2 * qtd_coeficientes
    
    elif criterio == "AICc":
        AIC = n * np.log(RSS / n) + 2 * qtd_coeficientes
        return AIC + (2 * qtd_coeficientes * (qtd_coeficientes + 1)) / (n - qtd_coeficientes - 1)

    elif criterio == "BIC":
        return n * np.log(RSS / n) + qtd_coeficientes * np.log(n)
    
    elif criterio == "all":
        AIC = n * np.log(RSS / n) + 2 * qtd_coeficientes
        BIC = n * np.log(RSS / n) + qtd_coeficientes * np.log(n)
        R2A = 1 - ((1 - R2) * (n - 1) / (n - qtd_coeficientes - 1))
        AICc = AIC + (2 * qtd_coeficientes * (qtd_coeficientes + 1)) / (n - qtd_coeficientes - 1)

        return (R2, R2A, AIC, AICc, BIC)


def melhor_ajuste(
        valores_x: ArrayLike, 
        valores_y: ArrayLike, 
        criterio: str, 
        exibir_todos: bool = False, 
        plt_grafico: bool = False, 
        expr: bool = False
):
    """
    Fornece o melhor ajuste (linear ou polinomial) para a variável Y.

    A função encontra os ajustes linear e polinomial (grau 2 a 10) 
    a partir das funções ajuste_linear e ajuste_polinomial. 
    Além disso, calcula seus respectivos valores 
    de Soma dos Quadrados dos Erros (SSE).

    Após esses processos, a função calcula o R^2, R^2 ajustado, 
    AIC, AICc e BIC através da função avaliar_ajuste,
    considerando que os resíduos do modelo seguem uma distribuição normal 
    com variância constante.

    Por fim, ela retorna o ajuste mais apropriado quanto ao critério escolhido 
    e o valor deste para essa aproximação.
    Nesse sentido, se o critério é R^2 ou R^2 ajustado, 
    é retornado o ajuste cujo valor para o critério é o maior.
    Já se o critério é AIC, AICc ou BIC, 
    é retornado o ajuste cujo valor para o critério é o menor.

    Opcionalmente, a função também exibe:
        - Um gráfico de dispersão dos pontos com a função de ajuste;
        - A forma simbólica da reta/polinômio de ajuste (func_aprox);
        - Os valores dos outros critérios para o ajuste sugerido.

    Parâmetros
    ----------
    valores_x : list | np.ndarray
        Valores da variável independente.
    valores_y : list | np.ndarray
        Valores da variável dependente.
    criterio : str
        Critério escolhido dentre as opções: "R2", "R2A" (R^2 ajustado), 
        "AIC", "AICc" e "BIC" para sugestão do modelo.
    exibir_todos : bool, opcional 
        Se True, exibe os valores dos outros critérios; 
        Padrão: False.
    plt_grafico : bool, opcional
        Se True, exibe o gráfico de ajuste; 
        Padrão: False.
    expr : bool, opcional
        Se True, exibe a função simbólica aproximadora sugerida; 
        Padrão: False.

    Retorna:
    -------
        str: 
            aprox_escolhida, representando o nome do modelo escolhido.
        dict: 
            funcs[aprox_escolhida], contendo as principais informações 
            do modelo sugerido.
    """

    # Condições de Início da Função

    if len(valores_x) != len(valores_y):
        raise ValueError(
            "As listas 'valores_x' e 'valores_y' devem ter o mesmo tamanho."
        )
    
    if criterio not in ("R2", "R2A", "AIC", "AICc", "BIC"):
        raise ValueError(
            "Critério deve ser escolhido dentre as seguintes opções: "
            "R2, R2A, AIC, AICc, BIC"
        )

    # Obter os parâmetros dos ajustes linear e polinomial (grau 2 a 10)

    funcs = {}

    funcs["linear"] = {"params": ajuste(valores_x, valores_y, 
        tipo='lin', plt_grafico=False)
    }

    for grau in range(2, 11):
        funcs[f"polinomial grau {grau}"] = {"params": ajuste(
            valores_x, valores_y, tipo='pol', grau_pol=grau, 
            plt_grafico=False, expr=False
        )}

    # Encontrar os valores dos critérios

    valores_x = np.array(valores_x)
    valores_y = np.array(valores_y)

    # Ajuste Linear

    # Ajuste Linear - Calcular SSE

    y_lin = np.array(funcs["linear"]["params"][0] * valores_x 
                     + funcs["linear"]["params"][1])

    SSE_lin = np.sum((valores_y - y_lin)**2)
    SSE_lin = max(SSE_lin, 1e-12) # Evita problemas no cálculo do log(SSE_lin / n).

    funcs["linear"]["SSE"] = SSE_lin

    # Ajustes Polinomiais

    for i in range(2, 11):

        # Ajustes Polinomiais - Calcular SSE

        y_pol = np.polynomial.polynomial.polyval(
            valores_x, funcs[f"polinomial grau {i}"]["params"])

        SSE_pol = np.sum((valores_y - y_pol) ** 2)
        SSE_pol = max(SSE_pol, 1e-12) # Evita problemas no cálculo do log(SSE_pol / n).

        funcs[f"polinomial grau {i}"]["SSE"] = SSE_pol

    # Obter R^2, R^2 ajustado, AIC, AICc e BIC para Ajustes Linear e Polinomiais

    lista_ajustes = ["linear"] + [f"polinomial grau {i}" for i in range(2, 11)]

    for nome_ajuste in lista_ajustes:
        mod = "linear" if nome_ajuste == "linear" else "polinomial"
        
        try:
            # Tenta calcular todas as métricas
            R2, R2A, AIC, AICc, BIC = avaliar_ajuste(
                valores_x, valores_y, "all", mod, funcs[nome_ajuste]["params"]
            )
            funcs[nome_ajuste]["R2"] = R2
            funcs[nome_ajuste]["R2A"] = R2A
            funcs[nome_ajuste]["AIC"] = AIC
            funcs[nome_ajuste]["AICc"] = AICc
            funcs[nome_ajuste]["BIC"] = BIC
        except ZeroDivisionError:
            # Se não há pontos suficientes para as métricas ajustadas, 
            # penalizamos o modelo para que ele não seja escolhido.
            funcs[nome_ajuste]["R2"] = -np.inf   # Valor muito ruim
            funcs[nome_ajuste]["R2A"] = -np.inf  # Valor muito ruim
            funcs[nome_ajuste]["AIC"] = np.inf   # Valor muito ruim (queremos o menor)
            funcs[nome_ajuste]["AICc"] = np.inf  # Valor muito ruim
            funcs[nome_ajuste]["BIC"] = np.inf   # Valor muito ruim
    
    # Encontrar a aproximação mais adequada com base no critério escolhido
    
    if criterio == "R2" or criterio == "R2A":
        funcs_ordenadas = dict(sorted(funcs.items(), 
                    key=lambda item: item[1][criterio], reverse=True))
    elif criterio == "AIC" or criterio == "AICc" or criterio == "BIC":
        funcs_ordenadas = dict(sorted(funcs.items(), 
                    key=lambda item: item[1][criterio]))
    
    aprox_escolhida = next(iter(funcs_ordenadas))
    
    print(f"Modelo sugerido: Aproximação {aprox_escolhida}")
    print(
        f"{criterio}: {funcs[aprox_escolhida][criterio]:.6f}\n"
    )

    # Exibir todos o valores de todos os critérios da aproximação escolhida

    if exibir_todos:
        lista_criterios = [c for c in ["R2", "R2A", "AIC", "AICc", "BIC"] if c != criterio]
        for crit in lista_criterios:
            if crit == "R2A":
                print(f"R2 Ajustado: {funcs[aprox_escolhida][crit]}")
            else:
                print(f"{crit}: {funcs[aprox_escolhida][crit]}")

    # Plotar o gráfico e exibir a expressão simbólica da aproximação escolhida

    graf = True if plt_grafico else False
    ff = True if expr else False

    if aprox_escolhida == "linear":
        ajuste(valores_x, valores_y, tipo='lin', plt_grafico=graf, expr=ff)
    else:
        grau = int(aprox_escolhida.split()[-1])
        ajuste(valores_x, valores_y, tipo='pol', grau_pol=grau, plt_grafico=graf, expr=ff)

    return aprox_escolhida, funcs[aprox_escolhida]


__all__ = ["ajuste", "ajuste_linear", "ajuste_polinomial", "ajuste_exponencial", "ajuste_logaritmo", "ajuste_senoidal", "ajuste_multiplo", "avaliar_ajuste", "melhor_ajuste"]

if __name__ == '__main__':
    ajuste([0, 1, 2, 3, 4, 5], [1.1, 1.7, 2.9, 5.1, 8.5, 14.2], 'exp', plt_grafico=True)
