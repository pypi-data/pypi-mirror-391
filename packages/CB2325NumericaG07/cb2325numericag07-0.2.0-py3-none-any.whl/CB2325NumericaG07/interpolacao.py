import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def diff_numerica(x,y) -> list:
    '''
    Recebe duas listas de numeros que representam os pontos x e y, e retorna a derivada numerica em cada ponto,usando diferença central nos pontos centrais,
    e diferença progressiva/regressiva nas pontas.

    Parâmetros:
        x (list): lista com os valores dos pontos na coordenada x
        y (list): lista com os valores dos pontos na coordenada y

    Retorna:
        list: lista com as 'derivadas' em cada ponto 
        

    '''
    
    if len(x) != len(y):
        raise ValueError('As listas x e y devem ter o mesmo tamanho')

    lista = zip(x,y)

    lista = list(lista)

    diff_list = lista.copy()

    for index,num in enumerate(lista):
        x,y = num
        if index in [0,len(lista)-1]: #se for um dos pontos das pontas
            if index == 0:
                next_x , next_y = lista[index + 1]
                diff_list[index] = (next_y - y)/(next_x - x)  
            
            else:
                prev_x,prev_y = lista[index - 1]
                diff_list[index] = (y - prev_y)/(x - prev_x)

        else:
            next_x , next_y = lista[index + 1]
            prev_x,prev_y = lista[index - 1]
            diff_list[index] = (next_y - prev_y)/(next_x - prev_x)
    
    return diff_list


def _function_definer(lista_x,lista_y,exception=None):
    '''
    Essa função recebe duas listas e as vincula, retornando uma função vinculo que ao receber um ponto da lista_x retorna um ponto da lista_x
    '''

    if len(lista_x) != len(lista_y):
        raise ValueError('As listas x e y devem ter o mesmo tamanho')


    func_dicio = dict()
    for x,y in zip(lista_x,lista_y):
        func_dicio[x] = y 
    
    def func(pont):
        if pont in func_dicio.keys():
            return func_dicio[pont]
        else:
            if exception == None:
                raise Exception('Esse ponto não foi definido na função')
            else:
                return exception

    return func

def _duplicate(lista) -> list:
        '''
        Duplica cada elemento da lista e mantem a ordem, necessaria para o calculo por exemplo da interpolação de hermite,
        recebe: [1,2,3,4] e retorna: [1,1,2,2,3,3,4,4]
        '''
        l = []
        for i in lista:
            l.append(i)
            l.append(i)
        return l


def _hermite_ddfunc(Point_list:list,derivada,func)-> list:
    '''
    Recebe a lista de pontos, uma função que retorna as derivadas em cada ponto, e a função que queremos usar na interpolação,
    e retorna as f[] necessarias para o calculo da intepolação de hermite em ordem,
    por exemplo [f[x_0],f[x_0,x_0],f[x_0,x_0,x_1],...] .

    Parâmetros:
        Point_list (list): lista com os valores dos pontos na coordenada x
        derivada (função): função que retorna a derivada de cada ponto da Point_list
        func (função): função que retorna os valores dos pontos na coordenada y para cada ponto da coordenada y, func(x) = y

    Retorna:
        list: Lista com os valores de cada f[] necessária para calcular o polinomio de hermite na ordem que o f[x] aparece


    '''
    subslist1,subslist2 = list(Point_list.copy()),list(Point_list.copy())#sublist1 e sublist2 são listas que usarei para guardar quais valores serão subtraidos nos denomidaores
    Point_list = [func(p) for p in Point_list] #aplica na lista de pontos a função e retorna cada valor
    
    def der(P_list): #funciona com uma redução de lista, seja x_i o elemento da nova lista e x1_i o elemento da lista antiga de posição i, x_i = (x1_(i+1) - x1_i)/(sublist[i]-sublist2[i]), da mesma forma que seria calcular a interpolação por tabela,  
        '''
        Reduz uma lista usando o metodo de calcular os valores de f[], pelo método de tabela
        '''


        new_list = [] #salva nessa lista
        subslist1.pop(0)
        subslist2.pop()
        for i in range(len(P_list)-1):
            if subslist1[i] == subslist2[i]:
                new_list.append(derivada(subslist1[i]))
            else:
                new_list.append((P_list[i+1] - P_list[i])/(subslist1[i] - subslist2[i]))

        return new_list

    result_list = []
    while len(Point_list) != 1: #vai reduzindo a lista até sobrar apenas um elemento, e guarda apenas o topo na tabela, no caso o primeiro da lista
        result_list.append(Point_list[0]) 
        Point_list = der(Point_list)
    result_list.append(Point_list[0])
    return result_list



def interpolacao_de_hermite(x,y,plot=False, grid=True):
    '''
    Essa função retorna, recebendo uma lista de valores de x e outra lista dos respectivos valores de f(x), uma função que interpola valores conforme f(x)
    
    Parâmetros:
        x (float): Lista de valores de x.
        y (float): Lista de valores conhecidos de f(x).
        (Ambos devem estar em ordem)
        plot (bool): Determina se a função deve plotar as informações ou não
        grid (bool): Determina se a função for plotar se a plotagem deve ter grid ou não
        
    Retorna:
        Função: Essa nova função recebe valores de x e retorna os valores de f(x) interpolados.
    '''
    
    #Cálculo final

    f = _function_definer(x,y) #define a função que f(x) = y
    d = diff_numerica(x,y) #gera a lista de derivadas de cada ponto de x
    f_linha = _function_definer(x,d,exception=0) # define a função 'derivada' f'(x) = y'
    x_duplicated = _duplicate(x)#prepara a lista para obter os coeficientes da função
    coeficientes_hermite = _hermite_ddfunc(x_duplicated,f_linha,f)#calcula os resultados dos f[x_0],f[x_0,x_0] ... necessários
    

    def interpolation(ponto,plt = plot): #função que será retornada
        '''
        Essa função esta diretamente ligada a função original interpolação_de_hermite que a gerou, e seu resultado depende diretamente da função original


        Parâmetros:
            ponto (float): ponto x que será calculado o f(x)
            plt: Determina se a função deve ou não plotar o ponto x (só funciona se na função interpolação de hermite o parametro: plot = True)
        
        Retorna:
            float: Valor f(x)
        '''
        
        
        soma = 0 #para os (x - x_i), que crecem assim como os pontos da lista x_duplicate
        hermite = 0 
        for i in coeficientes_hermite:# para cadaf[x_i]
            mult = 1
            for j in x_duplicated[:soma]:#calcula os (x - x_i)
                mult = mult*(ponto - j)


            hermite += mult*i # + f[x_0,...,x_i]*(x-x_0)^2 * ... (x - x_i)
            soma += 1
        
        return hermite

    if plot: #plotagem
            fig = plt.figure()
            ax = fig.add_subplot()
            ax.scatter(x,y,color = 'red',label = 'Pontos Originais',zorder = 3) #plota os pontos originais
            
            ax.set_title('Interpolação de Newton')

            inicio = min(x)
            fim = max(x)
            arranjo = 1
            pontos_unidades = 100
            interval = fim-inicio

            if interval < 1: #se o intervalo for menor que 1 o linspace precisa ser modificado
                print('A distância entre os pontos está bem pequena')
                arranjo =10
                pontos_unidades = 5
                while (fim-inicio)*arranjo<10: #calcula o arranjo para que o pseudo intervalo possa ser gerado no linpace
                    arranjo = arranjo*10
            
            cred =lambda x: x/arranjo #serve apenas para consertar o intervalo
            xval = np.linspace(int(inicio*arranjo),int(fim*arranjo),int((interval)*arranjo)*pontos_unidades) #gera uma sequencia de x pontos entre a e b
            xval = np.array(list(map(cred,xval))) # calcula os valores de x para plotar

            yval = np.array(list(map(lambda x: interpolation(x,plt=False),xval))) #calcula os valores de y para plotar
            ax.plot(xval,yval,label = 'Curva de Interpolação') #plota a curva
            
            #configuações da plotagem
            ax.grid(grid)
            ax.legend()


    return interpolation


def _newton_ddfunc(Point_list:list,func)-> list:
    '''Recebe a lista de pontos e a função que queremos usar na interpolação,
    e retorna as f[] necessarias para o calculo da intepolação de newton em ordem,
    por exemplo [f[x_0],f[x_0,x_1],f[x_0,x_1,x_2],...] .
    '''
    subslist1,subslist2 = list(Point_list.copy()),list(Point_list.copy())#sublist1 e sublist2 são listas que usarei para guardar quais valores serão subtraidos nos denomidaores
    Point_list = [func(p) for p in Point_list] #aplica na lista de pontos a função e retorna cada valor
    
    def der(P_list): #funciona com uma redução de lista, seja x_i o elemento da nova lista e x1_i o elemento da lista antiga de posição i, x_i = (x1_(i+1) - x1_i)/(sublist[i]-sublist2[i]), da mesma forma que seria calcular a interpolação por tabela,  
        '''
        Reduz uma lista usando o metodo de calcular os valores de f[], pelo método de tabela
        '''
        

        new_list = [] #salva nessa lista
        subslist1.pop(0)
        subslist2.pop()
        for i in range(len(P_list)-1):
            new_list.append((P_list[i+1] - P_list[i])/(subslist1[i] - subslist2[i]))

        return new_list

    result_list = []
    while len(Point_list) != 1: #vai reduzindo a lista até sobrar apenas um elemento, e guarda apenas o topo na tabela, no caso o primeiro da lista
        result_list.append(Point_list[0]) 
        Point_list = der(Point_list)
    result_list.append(Point_list[0])
    return result_list



def interpolacao_de_newton(x,y,plot:bool = False,grid:bool = True):
    '''Essa função retorna, recebendo uma lista de valores de x e outra lista dos respectivos valores de f(x), uma função que interpola valores conforme f(x)
    
    Parâmetros:
        x (float): Lista de valores de x.
        y (float): Lista de valores conhecidos de f(x).
        Ambos devem estar em ordem
        
    Retorna:
        Função: Essa nova função recebe valores de x e retorna os valores de f(x) interpolados.
    
    
    '''

    f = _function_definer(x,y) #define a função que f(x) = y
    coeficientes_newton = _newton_ddfunc(x,f)#calcula os resultados dos f[x_0],f[x_0,x_0] ... necessários

    
    def interpolation(ponto,plt = plot): #função que será retornada
        '''
        Parâmetros:
            x (float): Lista de valores de x.
            y (float): Lista de valores conhecidos de f(x).
            Ambos devem estar em ordem
        
        Retorna:
            Função: Essa nova função recebe valores de x e retorna os valores de f(x) interpolados.'''
        
        soma = 0 #para os (x - x_i), que crecem assim como os pontos da lista x_duplicate
        newton = 0 
        for i in coeficientes_newton:# para cadaf[x_i]
            mult = 1
            for j in x[:soma]:#calcula os (x - x_i)
                mult = mult*(ponto - j)


            newton += mult*i # + f[x_0,...,x_i]*(x-x_0)^2 * ... (x - x_i)
            soma += 1
        

        return newton

    
    if plot: #plotagem
            fig = plt.figure()
            ax = fig.add_subplot()
            ax.scatter(x,y,color = 'red',label = 'Pontos Originais',zorder = 3) #plota os pontos originais
            
            fig.set_title('Interpolação de Newton')

            inicio = min(x)
            fim = max(x)
            arranjo = 1
            pontos_unidades = 100
            interval = fim-inicio

            if interval < 1: #se o intervalo for menor que 1 o linspace precisa ser modificado
                print('A distância entre os pontos está bem pequena')
                arranjo =10
                pontos_unidades = 5
                while (fim-inicio)*arranjo<10: #calcula o arranjo para que o pseudo intervalo possa ser gerado no linpace
                    arranjo = arranjo*10
            
            cred =lambda x: x/arranjo #serve apenas para consertar o intervalo
            xval = np.linspace(int(inicio*arranjo),int(fim*arranjo),int((interval)*arranjo)*pontos_unidades) #gera uma sequencia de x pontos entre a e b
            xval = np.array(list(map(cred,xval))) # calcula os valores de x para plotar
            yval = np.array(list(map(lambda x: interpolation(x,plt=False),xval))) #calcula os valores de y para plotar
            ax.plot(xval,yval,label = 'Curva de Interpolação') #plota a curva
            
            #configuações da plotagem
            ax.grid(grid)
            ax.legend()


    return interpolation



def interpolacao_polinomial(tupla_de_pontos, plotar = False) -> sp.Expr:
    """
    Calcula o Polinômio Interpolador de Lagrange para um conjunto de
    pontos (x_i, f(x_i)) dados.

    Retorna a expressão polinomial simplificada e simbólica usando a
    biblioteca SymPy.

    Parâmetros:
        tupla_de_pontos (list of tuple): Lista contendo os pontos de
            interpolação na forma [(x0, f(x0)), (x1, f(x1)), ...].
        plotar (bool, opcional): Se True, gera e exibe um gráfico
            do polinômio interpolador e dos pontos originais usando
            Matplotlib. Padrão é False.

    Retorna:
        sympy.Expr or str: A expressão simbólica do polinômio de
            Lagrange simplificado (e.g., a_n*x^n + ... + a_0) ou uma
            mensagem de erro se a lista de pontos estiver vazia.
    """

    # Aplicamos um teste de entrada, mais precisamente verificamos se a
    # lista de entrada está vazia. Se estiver, retorna uma mensagem de
    # erro.
    if not tupla_de_pontos:
        return "Lista de pontos vazia"
    

    # Quebramos a lista de tuplas [(x_0, f(x_0)), (x_1, f(x_1)), ...]
    # em dois arrays separados.
    # O dtype=float converte os elementos do array para float.
    X = np.array([p[0] for p in tupla_de_pontos], dtype=float)
    Y = np.array([p[1] for p in tupla_de_pontos], dtype=float)
    n = len(X)

    # Definimos aqui 'x' como uma variável simbólica usando SymPy
    # para que consigamos manipular os resultados obtidos na cons-
    # trução do polinômio de forma algébrica.
    x = sp.Symbol('x')


    # Inicializamos o Polinômio Interpolador de Lagrange P(x)
    P_x = 0
    
    # Inicializamos a lista L (Polinômios Construtores L_k(x)),
    # com n 1's, onde n é o grau máximo posível para esse 
    # polinômio. Ademais, inicializamos com n 1's pois L acumulará 
    # um produto de termos.
    L = [1]*n
    
   
    # O loop externo (k) itera sobre cada ponto (x_k, f(x_k)) para
    # construir L_k(x), isto é, gerará os n Polinômios Construtores
    # Lagrangianos que apendaremos em L.
    for k in range(n):
        # O loop interno (i) constrói o k-ésimo Polinômio 
        # Construtor L_k(x) via produtório, isto é:
        # L_k(x) = Prod_{i != k} [ (x - x_i) / (x_k - x_i) ]
        for i in range(n):
            # Aqui aplicamos a condição i != k da fórmula de Lagrange,
            # visando evitar a divisão por zero, ou seja, 
            # evitamos que o denominador (X[k] - X[i]) se anule.
            if i != k:
                # Multiplimos cumulativamente: 
                # L[k] = L[k] * proximo_termo
                # O proximo_termo é (x - X_i) / (X_k - X_i).
                L[k] *= (x - X[i])/(X[k] - X[i])
                
    
    # O loop final (j) soma os termos para obter o Polinômio 
    # Interpolador de Lagrange P(x): 
    # P(x) = Sum_{j=0}^{n-1} [ Y_j * L_j(x) ]
    for j in range(n):
        P_x += Y[j] * L[j]
    
    polinomio_simplificado = sp.simplify(P_x)





    if plotar:
        # Definimos uma função interna que plotará os pontos e o 
        # Polinômio Interpolador
        def plotar_interpolacao(pontos, polinomio_simplificado):
            """
            Esta função gera o gráfico do polinômio interpolador e dos
            pontos originais.
            
            Argumentos:
                pontos (lista de tupla): Lista de pontos 
                originais (x_i, f(x_i)).
                polinomio_simplificado (sympy.Expr): 
                    O polinômio P(x) retornado pela função.
            """
            
            # Preparamos dos Dados Originais 
            # (para plotagem dos marcadores)
            X_pontos = np.array([p[0] for p in pontos])
            Y_pontos = np.array([p[1] for p in pontos])
            
            # Convertemos a expressão simbólica para função numérica
            # sp.lambdify converte a expressão SymPy (em 'x') 
            # para um função NumPy rápida.
            x_simbolico = sp.Symbol('x')
            P_x_numerico = sp.lambdify(x_simbolico, polinomio_simplificado, 
                                       'numpy')
            
            # Geração do Espaço Amostral para a Curva
            # Define o intervalo de plotagem ligeiramente maior que 
            # os pontos dados.
            x_min = np.min(X_pontos) - 0.5
            x_max = np.max(X_pontos) + 0.5
            
            # Gera 1000 pontos uniformemente espaçados para a curva
            X_curva = np.linspace(x_min, x_max, 1000)
            
            # Avaliamos do Polinômio
            Y_curva = P_x_numerico(X_curva)
            
            # Plotagem via Matplotlib
            plt.figure(figsize=(10, 6))
            
            # Plota a curva do Polinômio (linha contínua)
            plt.plot(X_curva, Y_curva, 
                     label=f'$P(x) = {polinomio_simplificado}$', 
                     color='blue')
            
            # Plota os Pontos Originais (marcadores vermelhos)
            plt.scatter(X_pontos, Y_pontos, label='Pontos de Interpolação', 
                        color='red', marker='o', zorder=5)
            
            # Adicionando rótulos e título
            plt.title('Interpolação Polinomial de Lagrange')
            plt.xlabel('Eixo X')
            plt.ylabel('Eixo Y')
            plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
            plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
            plt.legend()
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.show()

        plotar_interpolacao(tupla_de_pontos, polinomio_simplificado)

        # Retorna a expressão final simplificada, expandindo e 
        # combinando os termos para a forma padrão de um polinômio 
        # (e.g., a_n*x^n + a_{n-1}*x^{n-1} + . . . + a_1*x + a_0).
        return polinomio_simplificado
    else:
        # Retorna a expressão final simplificada, expandindo e 
        # combinando o termos para a forma padrão de um polinômio 
        # (e.g., a_n*x^n + a_{n-1}*x^{n-1} + . . . + a_1*x + a_0).
        return polinomio_simplificado
    


def interp_vand(tupla_de_pontos, plotar=False):
    """
    Calcula o Polinômio Interpolador via solução do Sistema Linear
    V * a = Y, onde V é a Matriz de Vandermonde.

    Retorna a expressão polinomial simplificada e simbólica usando a
    biblioteca SymPy.

    Parâmetros:
        tupla_de_pontos (list of tuple): Lista contendo os pontos de
            interpolação na forma [(x0, f(x0)), (x1, f(x1)), ...].
        plotar (bool, opcional): Se True, gera e exibe um gráfico
            do polinômio interpolador e dos pontos originais usando
            Matplotlib. Padrão é False.

    Retorna:
        sympy.Expr or str: A expressão simbólica do polinômio na forma
            padrão (e.g., a_n*x^n + ... + a_0) ou uma mensagem de erro
            se a lista de pontos estiver vazia ou a matriz for singular
    """

    # Aplicamos um teste de entrada, mais precisamente verificamos se a
    # lista de entrada está vazia. Se estiver, retorna uma mensagem de
    # erro.
    if not tupla_de_pontos:
        return "Lista de pontos vazia"
    
    # Quebramos a lista de tuplas [(x_0, f(x_0)), (x_1, f(x_1)), ...]
    # em dois arrays separados.
    # O dtype=float converte os elementos do array para float.
    X = np.array([p[0] for p in tupla_de_pontos], dtype=float)
    Y = np.array([p[1] for p in tupla_de_pontos], dtype=float)
    n = len(X) # número de pontos

    # Construímos a Matriz de Vandermonde (V)
    # A matriz V tem a forma:
    # | 1  x_0  x_0^2 ... x_0^(n-1) |
    # | 1  x_1  x_1^2 ... x_1^(n-1) |
    # | ...                        |
    # | 1 x_(n-1) ... x_(n-1)^(n-1)|


    # A função np.vander() constrói esta matriz. Por padrão, ele coloca 
    # a maior potência na primeira coluna.O argumento 'increasing=True'
    # garante a ordem crescente de potência (da 0-ésima à (n-1)-ésima),
    # que é a convenção padrão para a equação do polinômio P(x) = a_0 + 
    # a_1*x + ...
    V = np.vander(X, n, increasing=True)

    # Agora precisamos resolver o Sistema Linear V * a = Y
    # Para isso utilizamos a função np.linalg.solve(A, b) que 
    # resolve o sistema A * x = b para x.
    # Nessa situação V é A, Y é b e os coeficientes 
    # 'a' são a solução 'x'.
    try:
        coeficientes = np.linalg.solve(V, Y)
    except np.linalg.LinAlgError:
        # Temos um erro caso a matriz seja singular (determinante 
        # próximo de zero), o que geralmente ocorre caso haja 
        # valores de X duplicados.
        return ("A matriz de Vandermonde é singular (pontos x duplicados "
                "ou erro de precisão). Não é possível resolver tal sistema")

    # Vamos construir o polinômio simbólico

    # Definimos 'x' como variável simbólica via SymPy
    x = sp.Symbol('x')

    # Inicializamos o Polinômio P(x)
    P_x = 0

    # P(x) = a_0 + a_1 * x^1 + a_2 * x^2 + ... + a_(n-1) * x^(n-1)
    for i in range(n):
        # O coeficiente[i] corresponde a a_i, e o termo é x^i
        P_x += coeficientes[i] * (x**i)
        
    polinomio_simplificado = sp.simplify(P_x)


    # A parte de plotagem e retorno é idêntica à sua, garantindo a 
    # mesma funcionalidade.
    if plotar:
        # Definimos uma função interna que plotará os pontos e o 
        # Polinômio Interpolador
        def plotar_interpolacao(pontos, polinomio_simplificado):
            """
            Esta função gera o gráfico do polinômio interpolador e dos
            pontos originais.
            
            Argumentos:
                pontos (lista de tupla): Lista de pontos originais 
                (x_i, f(x_i)).
                polinomio_simplificado (sympy.Expr): O polinômio P(x) 
                retornado pela função.
            """
            
            # Preparação dos Dados Originais (plotagem dos marcadores)
            X_pontos = np.array([p[0] for p in pontos])
            Y_pontos = np.array([p[1] for p in pontos])
            
            # Convertemos a expressão simbólica para função numérica
            # sp.lambdify converte a expressão SymPy (em 'x') para uma 
            # função NumPy rápida.
            x_simbolico = sp.Symbol('x')
            P_x_numerico = sp.lambdify(x_simbolico, polinomio_simplificado, 
                                       'numpy')
            
            # Geração do Espaço Amostral para a Curva
            # Define o intervalo de plotagem ligeiramente maior 
            # que os pontos dados.
            x_min = np.min(X_pontos) - 0.5
            x_max = np.max(X_pontos) + 0.5
            
            # Gera 1000 pontos uniformemente espaçados para a curva
            X_curva = np.linspace(x_min, x_max, 1000)
            
            # Avaliamos do Polinômio
            Y_curva = P_x_numerico(X_curva)
            
            # Plotagem via Matplotlib
            plt.figure(figsize=(10, 6))
            
            # Plota a curva do Polinômio (linha contínua)
            plt.plot(X_curva, Y_curva, 
                     label=f'$P(x) = {polinomio_simplificado}$', 
                     color='blue')
            
            # Plota os Pontos Originais (marcadores vermelhos)
            plt.scatter(X_pontos, Y_pontos, label='Pontos de Interpolação', 
                        color='red', marker='o', zorder=5)
            
            # Adicionando rótulos e título
            plt.title('Interpolação Polinomial via Matriz de Vandermonde')
            plt.xlabel('Eixo X')
            plt.ylabel('Eixo Y')
            plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
            plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
            plt.legend()
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.show()

        plotar_interpolacao(tupla_de_pontos, polinomio_simplificado)

        # Retorna a expressão final simplificada
        return polinomio_simplificado
    else:
        # Retorna a expressão final simplificada
        return polinomio_simplificado
    


def interpolacao_linear_por_partes(x_vals:list, y_vals:list, plotar = False, x_test= None):
    """
    Função que recebe uma lista x de abscissas, uma lista y de ordenadas, um
    possível True para plotar um gráfico com os pontos recebidos e a interpolação 
    linear por partes e um possível valor x_test para descobrir o valor de f(x_test)
    a partir da interpolação. E retorna uma lista com os polinômios lineares,
    podendo também plotar o gráfico e retornar o valor de f(x_text) junto aos
    polinômios se receber True para plotar e algum valor para x_text.
    """

    n = len(x_vals)
    tuplas = [(x_vals[i], y_vals[i]) for i in range(n)] 
    tuplas_ord = sorted(tuplas, key=lambda x: x[0]) 
    # É feita a ordenação das coordenadas recebidas em ordem crescente considerando
    # as abscissas, pois não se sabe se o usuário indicará nesta ordem. 
    x_vals = [tuplas_ord[i][0] for i in range(n)]
    y_vals = [tuplas_ord[i][1] for i in range(n)]
    lista_poli = []

    x_sym = sp.Symbol('x')
    for i in range(n - 1):
        poli = y_vals[i] + ((y_vals[i+1] - y_vals[i])/(x_vals[i+1] - x_vals[i])) * (x_sym - x_vals[i]) #Calcula o polinômio linear entre dois pontos consecutivos.
        lista_poli.append(poli)

    def p(x):
        '''
        Função que recebe um valor x e retorna o valor de f(x) a partir da interpolação se 
        ele não for nem menor do que o primeiro e nem maior do que o último porque não é
        possível calcular nestes casos.
        '''
        if x < x_vals[0] or x > x_vals[n-1]:
            return "Fora do intervalo. Tente outro valor!"
        else:
            for i in range(n - 1):
                if x >= x_vals[i] and x <= x_vals[i+1]:
                    return y_vals[i] + ((y_vals[i+1] - y_vals[i])/(x_vals[i+1] - x_vals[i])) * (x - x_vals[i])

    if plotar: #Plota o gráfico com os pontos recebidos e a interpolação linear por partes se plotar = True. 
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, 'o', label='Pontos Originais')

        x_sym = sp.Symbol('x')
        for i in range(n - 1):
            poli = lista_poli[i]
            poli_func = sp.lambdify(x_sym, poli, 'numpy')
            x_values = np.linspace(x_vals[i], x_vals[i+1], 100)
            y_values = poli_func(x_values)
            plt.plot(x_values, y_values, label=f'Polinômio linear {i+1}')

        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Interpolação Linear por Partes')
        plt.legend()
        plt.grid(True)
        plt.show()

    if x_test: # Calcula f(x_test) e o retorna junto com os polinômios se receber algum valor para x_test.
        return lista_poli, p(x_test)
    
    return lista_poli #Caso não receba um valor para x_test, retorna apenas a lista de polinômios.

if __name__ == '__main__':
    print(interpolacao_de_hermite.__doc__ + '\n')
    print(interpolacao_polinomial.__doc__ + '\n')
    print(interpolacao_linear_por_partes.__doc__)









            