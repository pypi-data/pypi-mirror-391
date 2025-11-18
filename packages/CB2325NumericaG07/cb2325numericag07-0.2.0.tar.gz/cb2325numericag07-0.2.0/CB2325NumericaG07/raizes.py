import matplotlib.pyplot as plt
import numpy as np

def metodo_newton_raphson(função, tol=1e-6, max_iter=100, plotar = False, estimativa_inicial=None):
    '''
    Encontra a raíz de uma função pelo método Newton-Raphson.
    O método localiza uma raiz da função usando a reta tangente
    à função numa estimativa f(x). Tal estimativa pode ser um argumento
    ou o padrão, que é uma função que faz uma estimativa inicial grosseira.
    A busca é interrompida quando o erro, f(x) - 0, é menor que 'tol' ou
    'max_inter' é atingido.

    Args:
        função (callable): A função para a qual a raiz está sendo procurada
            (deve receber um float e retornar um float).
        tol (float): A tolerância (critério de parada). O loop para
            quando f(x) < tol. Default é 1e-6. Além disso, tol é usado
            para calcular a derivada numérica.
        max_iter (int): O número máximo de iterações da função 'metodo_nr',
            acima dos quais a função retorna 'O método não convergiu.'.
            Default é 100.
        plotar (bool, optional): Se True, exibe um gráfico das
            iterações ao final. Default é False.
        estimativa_inicial (float): Primeiro número que será aplicado
            na função para obter a reta tangente à f(x). Default é uma
            estimativa de baixa precisão automática. 
    
        
    Returns:
        float: A aproximação da raiz da função.
        None: Se o método atingir 'max_inter' antes de convergir.

    Raises:
        ValueError: Se 'função' não for callable ou se max_iter/tol tiverem
            valores inválidos.

    '''

    #Estimativa inicial grosseira. 
    #Pode ser substituída por uma manual para aumentar a precisão.

    def estimar_raiz(função):
        estimativa0 = 1
        iterações = 0
        iterações2 = 0
        max_iterações = 10
        while abs(função(estimativa0)) > 1000:
            estimativa0 *= 2
            iterações += 1
            if iterações >= max_iterações:
                estimativa0 = -1
                while abs(função(estimativa0)) > 1000:
                    estimativa0 *= 2
                    iterações2 += 1
                    if iterações2 >= max_iterações:
                        estimativa0 = 1
                        break

        estimativa_raiz = estimativa0

        return estimativa_raiz
    
    #Por tol ser muito baixo, podemos usá-lo para fazer a derivada numérica

    def derivar(função, tol):
        return lambda x: (função(x + tol) - função(x)) / (tol)

    def metodo_nr(função, estimativa, tol):
        derivada = derivar(função, tol)
        proxima_estimativa = estimativa - função(estimativa)/derivada(estimativa)
        try:
            return proxima_estimativa
        except ZeroDivisionError:
            print(f"Derivada nula em x = {estimativa}")
            return estimativa  
    
    if estimativa_inicial is not None:
        estimativa = float(estimativa_inicial)
    else:
        estimativa = estimar_raiz(função)
    erros = [tol+1]
    estimativas_tentadas = [estimativa]
    iterações = 0
    while erros.pop() > tol and iterações < max_iter:
        nova_estimativa = metodo_nr(função, estimativa, tol)
        erro = abs(nova_estimativa - estimativa)
        erros.append(erro)
        estimativa = nova_estimativa
        estimativas_tentadas.append(estimativa)
        iterações += 1
    if iterações == max_iter:
        print("O método não convergiu")

    #Plotagem

    x0 = estimativas_tentadas[0]
    xf = estimativas_tentadas[-1]
    raiz = xf
        
    if plotar:
        f = função
        df = derivar(f, tol)

        # Ponto inicial e final
        y0 = f(x0)
        yf = f(xf)

        # Tangentes
        m0 = df(x0)
        mf = df(xf)

        # Intervalo de plotagem
        amplitude = max(abs(xf), abs(x0), 1)
        x = np.linspace(-2*amplitude, 2*amplitude, 400)
        y = f(x)

        # Reta tangente inicial
        y_t0 = m0 * (x - x0) + y0

        # Reta tangente final
        x_tf = np.linspace(xf - 2, xf + 2, 20)
        y_tf = mf * (x - xf) + yf

        plt.plot(x, y, label='f(x)')
        plt.plot(x, y_t0, '--', color='orange', label='Tangente inicial')
        plt.plot(x, y_tf, '--', color='green', label='Tangente final')

        # Pontos
        plt.scatter(x0, y0, color='orange', label=f'Estimativa inicial ({x0:.3f})', zorder=5)
        plt.scatter(xf, yf, color='green', label=f'Estimativa final ({xf:.3f})', zorder=5)

        # Eixo X
        plt.axhline(0, color='black', linewidth=1)
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title('Método de Newton-Raphson — Função e Tangentes')
        plt.legend()
        plt.grid(True)
        plt.show()

    return raiz
    

def metodo_bissecao(f, a, b, tol=1e-6, max_inter = 100, plotar = False):
    """Encontra a raiz de uma função pelo Método da Bisseção.

    O método localiza uma raiz da função 'f' dentro do intervalo [a, b],
    desde que f(a) e f(b) tenham sinais opostos. A busca é
    interrompida quando a largura do intervalo é menor que 'tol' ou
    'max_inter' é atingido.

    Args:
        f (callable): A função para a qual a raiz está sendo procurada
            (deve receber um float e retornar um float).
        a (float): O início do intervalo.
        b (float): O fim do intervalo.
        tol (float, optional): A tolerância (critério de parada). O loop para
            quando abs(a - b) < tol. Default é 1e-6.
        max_inter (int, optional): O número máximo de iterações.
            Default é 100.
        plotar (bool, optional): Se True, exibe um gráfico das
            iterações ao final. Default é False.

    Returns:
        float: A aproximação da raiz da função.
        None: Se o método atingir 'max_inter' antes de convergir.

    Raises:
        ValueError: Se f(a) e f(b) tiverem o mesmo sinal.
    """
    inter = 0
    if f(a) * f(b) >= 0:
        raise ValueError("f(a) e f(b) devem ter sinais opostos.")
    pontos_c = []
    pontos_f = []
    while abs(a-b)>tol and inter<max_inter:
        c = (a + b)/2
        inter += 1
        pontos_c.append(c)
        pontos_f.append(f(c))
        if inter == max_inter:
            print('Não foram encontradas raizes')
            return None
        if f(c)*f(a)<0:
            b = c
        elif f(c)*f(b)<0:
            a = c
        else:
            break
    
    c_final = (a+b)/2
        
    if plotar:
        x = np.linspace(a, b, 400)
        y = [f(xi) for xi in x]

        plt.figure(figsize=(8, 5))
        plt.axhline(0, color='black', linewidth=1)
        plt.plot(x, y, label='f(x)', color='blue')
        plt.scatter(pontos_c, pontos_f, color='red', s=40, label='Iterações')
        plt.scatter(c_final, f(c_final), color='green', s=80, label=f'Raiz ≈ {c_final:.6f}')
        plt.title('Método da Bisseção')
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.legend()
        plt.grid(True)
        plt.show()

    return c_final



def metodo_secante(f, x0, x1, tol = 1e-6, max_inter = 100, plotar= False):
    """Encontra a raiz de uma função pelo Método da Secante.

    O método localiza uma raiz da função 'f' usando aproximações
    sucessivas baseadas na reta secante definida pelos dois pontos
    anteriores. Começa com x0 e x1.

    Args:
        f (callable): A função para a qual a raiz está sendo procurada
            (deve receber um float e retornar um float).
        x0 (float): O primeiro ponto inicial.
        x1 (float): O segundo ponto inicial.
        tol (float, optional): A tolerância (critério de parada). O loop para
            quando abs(x1 - x0) < tol. Default é 1e-6.
        max_inter (int, optional): O número máximo de iterações.
            Default é 100.
        plotar (bool, optional): Se True, exibe um gráfico das
            iterações ao final. Default é False.

    Returns:
        float: A aproximação da raiz da função.
        None: Se o método atingir 'max_inter' antes de convergir.

    Raises:
        ValueError: Se f(x1) e f(x0) forem iguais em alguma iteração,
            o que causaria uma divisão por zero.
    """
    inter = 0
    historico = [x0, x1]
    while abs(x0-x1)>=tol and inter<max_inter:
        if f(x1) == f(x0):
            if f(x1) == 0:
                return x1
            else:
                raise ValueError('f(x1) e f(x0) não podem ser iguais (divisão por zero)') 
        else:
            x2 = x1 - (f(x1)*(x1-x0))/(f(x1)-f(x0))
            historico.append(x2)
            x0 = x1
            x1 = x2
            inter += 1
        if inter == max_inter:
            print('Não foram encontradas raizes')
            return None

    if plotar:
        x_min = min(historico) - 0.5
        x_max = max(historico) + 0.5
        x_curva = np.linspace(x_min , x_max , 100)
        y_curva = f(x_curva)
        plt.plot(x_curva, y_curva, label="f(x)")

        plt.axhline(0, color='black', linewidth=1)

        y_historico = f(np.array(historico))
        plt.scatter(historico, y_historico, color='red', zorder=5, label="Iterações")

        plt.title("Método da Secante")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.grid(True)
        plt.show()
    return x1

def grid_search(func,a,b,n= 1000):
    '''
    Função para procurar os intervalos para calculo da raiz 
    
    Parâmetros:
    func (function) : função que queremos as raizes
    a (float) : inicio do intervalo
    b (float) : fim do intervalo
    n (int) : numero de partições que serão checadas 
    
    '''


    intervals = []
    vals = np.linspace(a,b,n)
    for idx in range(1,len(vals)):
        if func(vals[idx-1])*func(vals[idx]) < 0:
            intervals.append((vals[idx-1],vals[idx]))

    return intervals




if __name__ == '_main_':
    print(metodo_newton_raphson._doc_)
    print(metodo_bissecao._doc_)
    print(metodo_secante._doc_)
