import math
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np
from numpy.polynomial import Polynomial
#simplificações:
pi, sin, cos = sp.pi, sp.sin, sp.cos

def integral_trapezio(function, a, b, n : int, plotar = False) -> float:
    '''
    Calcula a integral definida de uma função usando o método do trapézio.
    Compatível com funções do sympy e funções normais do python.

    Parâmetros:
    function: A função a ser integrada.
    a: Limite inferior da integração.
    b: Limite superior da integração.
    n: Número de subintervalos.

    Retorna:
    A aproximação da integral definida.

    Formula:
        ∫[a,b] f(x) dx ≈ (h/2) * [f(x0) + 2*f(x1) + 2*f(x2) + ... + 2*f(x(n-1)) + f(xn]]
        onde h = (b - a) / n e xi = a + i*h para i = 0, 1, ..., n
    '''
    #Tratamento de erros
    if n < 1:
        raise ValueError("O número de subintervalos (n) deve ser pelo menos 1.")
    
    #Conversão feita por IA.
    #converter SymPy -> callable quando necessário
    if not callable(function):
        if isinstance(function, sp.Lambda):
            # extrai variável e expressão de Lambda
            vars_ = function.variables
            if len(vars_) != 1:
                raise TypeError("sp.Lambda com mais de uma variável não é suportado.")
            sym = vars_[0]
            expr = function.expr
        elif isinstance(function, sp.Expr):
            syms = list(function.free_symbols)
            if len(syms) == 0:
                sym = sp.Symbol('x')  # constante — cria símbolo dummy
                expr = function
            elif len(syms) == 1:
                sym = syms[0]
                expr = function
            else:
                raise TypeError("Expressão SymPy com múltiplas variáveis não é suportada.")
        else:
            raise TypeError("function deve ser callable ou uma expressão/lambda do SymPy.")
        function = sp.lambdify(sym, expr, modules=["math"])

    a = float(a)
    b = float(b)
    h = (b - a) / n
    
    # Cálculo da integral (movido para fora do if/else para calcular sempre)
    def x(i):
        return a + i * h
    
    soma_interna = 0
    for i in range(1, n):
        soma_interna += function(x(i))

    integral = (h/2) * (function(a) + 2 * soma_interna + function(b))

    if plotar:
        # Função interna para plotar
        def plot(f):
            # 1. Pontos para a curva suave
            num_pontos_smooth = 300 # Mais pontos para suavidade
            x_smooth = []
            y_smooth = []
            delta_x_smooth = (b - a) / (num_pontos_smooth - 1)
            for i in range(num_pontos_smooth):
                x_val = a + i * delta_x_smooth
                x_smooth.append(x_val)
                y_smooth.append(f(x_val))

            # 2. Pontos para os vértices dos trapézios
            x_trap = []
            y_trap = []
            for i in range(n + 1):
                x_val = a + i * h
                x_trap.append(x_val)
                y_trap.append(f(x_val))

            # --- Criação do Gráfico ---
            _, ax = plt.subplots(figsize=(10, 6))

            #plot da função
            func_label = 'f(x)'
            ax.plot(x_smooth, y_smooth, label=func_label, color='blue', linewidth=2)

            #plot dos trapézios
            for i in range(n):
                ax.plot([x_trap[i], x_trap[i+1]], [y_trap[i], y_trap[i+1]], color='red', linestyle='-', marker='o', markersize=4)

            #sombreia a área sob os trapézios
            ax.fill_between(x_trap, 0, y_trap, color='red', alpha=0.3, label=f'Área Aproximada ({n} trapézios)')

            ax.set_title('Visualização da Regra do Trapézio')
            ax.set_xlabel('x')
            ax.set_ylabel('f(x)')
            ax.legend()
            ax.grid(True)
            ax.axhline(0, color='black', linewidth=0.5)
            plt.show()

        plot(function)

        #valor calculado da integral para print
        return integral
        
    else:
        return integral

def integral_simpson38(function, a, b, n : int, plotar = False) -> float:
    """
    Calcula a integral de f no intervalo [a, b] usando a regra de Simpson 3/8.
    Parâmetros:
        f (function): Função a ser integrada
        a (float): Limite inferior da integração
        b (float): Limite superior da integração
        n (int): Número de subintervalos (deve ser múltiplo de 3)
    Retorna:
        float: Aproximação da integral definida de f de a até b.
    """
    if n % 3 != 0:
        raise ValueError("n deve ser múltiplo de 3")

    a = float(a)
    b = float(b)
    h = (b - a) / n
    soma = function(a) + function(b)
    
    for i in range(1, n):
        x = a + i * h
        if i % 3 == 0:
            soma += 2 * function(x)
        else:
            soma += 3 * function(x)
    
    integral = (3 * h / 8) * soma

    if plotar:
        # Função para plotagem
        def plot(f):
            x_plot = np.linspace(a, b, 300)
            y_plot = f(x_plot)
            xi = np.linspace(a, b, n + 1)
            yi = f(xi)
            
            # Aproximação Simpson 3/8 por blocos de 3 subintervalos
            simpson_y = np.zeros_like(x_plot)
            for k in range(0, n, 3):
                x_block = xi[k:k+4]
                y_block = yi[k:k+4]
                # Interpolação cúbica
                p = Polynomial.fit(x_block, y_block, 3) 
                mask = (x_plot >= x_block[0]) & (x_plot <= x_block[-1])
                simpson_y[mask] = p(x_plot[mask])

            plt.figure(figsize=(8,5))
            plt.plot(x_plot, y_plot, 'b', label='f(x) escolhida')
            plt.plot(x_plot, simpson_y, 'orange', label='Aproximação Simpson 3/8', linewidth=2)
            plt.fill_between(x_plot, simpson_y, color='skyblue', alpha=0.3)
            plt.vlines(xi, 0, yi, colors='gray', linestyles='dashed', alpha=0.7)
            plt.scatter(xi, yi, color='red', zorder=5)
            plt.title("Integração Numérica - Simpson 3/8 com polinômios cúbicos")
            plt.xlabel("x")
            plt.ylabel("f(x)")
            plt.legend()
            plt.grid(True)
            plt.show()

        plot(function)
        return integral
        
    else:
        return integral
    
def integral_boole(function, a, b, n: int, plotar=False) -> float:
    """
    Calcula a integral de f no intervalo [a, b] usando a Regra de Boole (Newton–Cotes de 4ª ordem).

    Parâmetros
    ----------
    function : callable
        Função a ser integrada.
    a, b : float
        Limites de integração.
    n : int
        Número de subintervalos (deve ser múltiplo de 4).
    plotar : bool, opcional
        Se True, exibe um gráfico da função e das subdivisões.

    Retorna
    -------
    float
        Valor aproximado da integral.

    Fórmula:
        ∫[a,b] f(x) dx ≈ (2h/45) * [7f(x0) + 32f(x1) + 12f(x2) + 32f(x3) + 7f(x4)]
        onde h = (b - a) / 4
    """
    if n % 4 != 0:
        raise ValueError("n deve ser múltiplo de 4 para a Regra de Boole.")

    a = float(a)
    b = float(b)
    h = (b - a) / n
    soma = 0

    for k in range(0, n, 4):
        x0 = a + k * h
        x1 = x0 + h
        x2 = x0 + 2 * h
        x3 = x0 + 3 * h
        x4 = x0 + 4 * h

        soma += (2 * h / 45) * (7 * function(x0) + 32 * function(x1) +
                                12 * function(x2) + 32 * function(x3) +
                                7 * function(x4))

    if plotar:
        import numpy as np
        import matplotlib.pyplot as plt
        x = np.linspace(a, b, 400)
        y = function(x)
        xi = np.linspace(a, b, n + 1)
        yi = function(xi)

        plt.figure(figsize=(8, 5))
        plt.plot(x, y, label="f(x)", color="blue")
        plt.vlines(xi, 0, yi, colors='gray', linestyles='dashed', alpha=0.7)
        plt.fill_between(x, y, color='lightgreen', alpha=0.3, label='Área Boole')
        plt.scatter(xi, yi, color='red', zorder=5)
        plt.title("Integração Numérica - Regra de Boole (Newton–Cotes 4ª ordem)")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.grid(True)
        plt.show()

    return soma

def integral_gauss_legendre(function, a, b, n: int = 3, plotar=False) -> float:
    """
    Calcula a integral de f(x) no intervalo [a, b] usando a Quadratura de Gauss-Legendre.

    Parâmetros
    ----------
    function : callable
        Função a ser integrada.
    a, b : float
        Limites de integração.
    n : int, opcional
        Número de pontos da quadratura (grau do polinômio de Legendre). Padrão: 3.
    plotar : bool, opcional
        Se True, exibe o gráfico da função e os pontos de amostragem da quadratura.

    Retorna
    -------
    float
        Valor aproximado da integral.

    Fórmula:
        ∫[a,b] f(x) dx ≈ (b - a)/2 * Σ [ w_i * f( (b - a)/2 * x_i + (a + b)/2 ) ]

    Observação:
        Este método é exato para polinômios de grau até (2n - 1).
    """

    # Nós e pesos da quadratura de Legendre
    xi, wi = np.polynomial.legendre.leggauss(n)

    # Mapeamento dos pontos de [-1, 1] → [a, b]
    x_mapped = 0.5 * (b - a) * xi + 0.5 * (b + a)
    f_vals = function(x_mapped)

    # Soma ponderada
    integral = 0.5 * (b - a) * np.sum(wi * f_vals)

    # Gráfico opcional
    if plotar:
        x = np.linspace(a, b, 400)
        y = function(x)
        plt.figure(figsize=(8, 5))
        plt.plot(x, y, label="f(x)", color="blue")
        plt.fill_between(x, y, color="lightcoral", alpha=0.3)
        plt.scatter(x_mapped, function(x_mapped), color="red", zorder=5, label="Nós de Gauss-Legendre")
        plt.title(f"Quadratura de Gauss–Legendre (n={n})")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.grid(True)
        plt.show()

    return integral


def integral_de_montecarlo(func,a:float,b:float, c:int = None,d:int=None,qte = 100,plot = False):
    '''
        Parâmetros:
           func : função que será integrada
           a: inicio do intervalo de integração
           b: fim do intervalo de integraço
           c: limite superior do quadrado em que os pontos serão gerados
           d: limite inferior do quadrado em que os pontos serão gerados
           qte: quantidade de pontos que serão gerados para calcular a integral, quanto mais pontos mais precisa mas mais tempo gasto.
           plot: plota a integração

           obs: a função no intervalo de integração deve estar contida no quadrado formado por a,b,c,d. 
        
        Retorna:
            Float: retorna o valor calculado da integral.
            
    '''

    if qte == 0:
        raise RuntimeWarning('qte não pode ser igual a 0') 


    x_list =np.random.uniform(a,b,qte)

    #calculando o intervalo em y
    test = np.linspace(a,b,100)
    nums = func(test)
    c = np.max(nums)
    d = np.min(nums)
    k = c-d
    c += k*0.2
    d -= k*0.2
    c,d = np.int64(c), np.int64(d)

    y_list = np.random.uniform(d,c,qte)

    dots = zip(x_list,y_list)


    I = 0
    for x,y in dots:
        if func(x) > y:
            I += 1
    

    if plot:
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.scatter(x_list,y_list,alpha = 0.5,color = 'yellow')
        ax.plot(test,nums)
        
        ax.text(-0.2,d-k*0.3,f'Pontos a baixo da função:{I} , Pontos totais : {qte}')

    return (c-d)*(b-a)*(I/qte) + d*(b-a)




if __name__ == "__main__":

    print("=== Documentação dos Métodos ===\n")
    print(integral_trapezio.__doc__)
    print(integral_simpson38.__doc__)
    print(integral_de_montecarlo.__doc__)
    print(integral_boole.__doc__)
    print(integral_gauss_legendre.__doc__)

    print("\n=== Exemplos de Uso ===\n")

    f = lambda x: np.sin(x)

    print("→ Regra dos Trapézios:")
    area_t = integral_trapezio(f, 0, math.pi, n=100, plotar=True)
    print(f"Resultado: {area_t:.6f}\n")

    print("→ Regra de Simpson 3/8:")
    area_s = integral_simpson38(f, 0, math.pi, n=99, plotar=True)
    print(f"Resultado: {area_s:.6f}\n")

    print("→ Regra de Boole:")
    area_b = integral_boole(f, 0, math.pi, n=8, plotar=True)
    print(f"Resultado: {area_b:.6f}\n")

    print("→ Integração de Monte Carlo:")
    area_m = integral_de_montecarlo(f, 0, math.pi, qte=5000, plot=True)
    print(f"Resultado: {area_m:.6f}")

    print("→ Quadratura de Gauss–Legendre:")
    area_g = integral_gauss_legendre(f, 0, np.pi, n=3, plotar=True)
    print(f"Resultado: {area_g:.6f}")