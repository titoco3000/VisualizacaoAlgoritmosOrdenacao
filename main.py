'''
Trabalho Prático 4 - Algoritmos e Programação II
Eu,
Tito Ribeiro de Almeida Guidotti
declaro que
todas as respostas são fruto de meu próprio trabalho,
não copiei respostas de colegas externos à equipe,
não disponibilizei nossas respostas para colegas externos ao grupo e
não realizei quaisquer outras atividades desonestas para me beneficiar
ou prejudicar outros.
'''
# imports
import pygame as pg  # para a interface gráfica
import sys  # para simplificar o encerramento
import random  # para montar as listas aleatorias
import math  # para ser usado no Merge Sort
import audio  # para produzir sons

# inicia as variaveis globais.
# Existem maneiras mais elegantes de fazer isso, mas iria complicar
screen = None
screenSize = (800, 600)
reference = 600
mouse = {
    "pos": (0, 0),
    "up": False,
    "down": False
}
dropdown_open = False
som_habilitado = True
sorting_titles = ['Métodos',
                  'Bubble sort',
                  'Selection sort',
                  'Insertion sort',
                  'Quick sort',
                  'Merge sort']
current_sorting_method = 0

listSize = 30
floatList = [0]
delay = 30  # em dezenas de ms
instrumento = 0
old_pointer = []

# cores, na interface
TOP_BAR_COLOR = (50, 168, 151)
DROPDOWN_MARGIN_COLOR = (255, 255, 255)
DROPDOWN_FONT_COLOR = (255, 255, 255)
DROPDOWN_BACKGROUND_COLOR = (100, 100, 100)
DROPDOWN_BACKGROUND_HOVERED_COLOR = (90, 90, 90)
DROPDOWN_BACKGROUND_CLICKED_COLOR = (80, 80, 80)
BAR_COLOR = (255, 255, 255)
BAR_MARGIN_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (0, 0, 30)
POINTER_COLOR = (255, 0, 0)
MUTE_BUTTON_COLOR = (100, 100, 100)
MUTE_BUTTON_HOVERED_COLOR = (90, 90, 90)
MUTE_BUTTON_CLICKED_COLOR = (80, 80, 80)
MUTE_BUTTON_MUTED_COLOR = (255, 0, 0)
BLACK = (0, 0, 0)

'''
Funções ultilitarias
'''


# Retorna n contido entre smallest e largest
def clamp(n, smallest, largest): return max(smallest, min(n, largest))


# Retonna o que está na proporção lerpAmount entre base e top.
def lerp(base, top, lerpAmount):
    return (1.0 - lerpAmount) * base + lerpAmount * top


'''
Funções relacionadas a interface gráfica
'''


# retorna uma superficie contendo o texto
def GetTextSurface(text, size=30, color=(255, 255, 255)):
    # cria a fonte com o tamanho especificado
    font = pg.font.SysFont('Futura', int(size))
    # renderiza o texto usando ela
    return font.render(text, True, color)


# retorna se o mouse está sobre uma área
def mouseOverlaps(rect):
    return rect[0] < mouse['pos'][0] < rect[0] + rect[2] and rect[1] < mouse['pos'][1] < rect[1] + rect[3]


# Desenha um retangulo com a cor dependendo do estado do mouse:
# longe (default), passando por cima (hover), ou clicando (click).
# Se há uma função especificada, chama ela quando o mouse é solto
# sobre ele.
# Retorna se foi acionado nesse frame
def DrawButton(surface, rect, defaultColor, hoverColor, clickColor, *args, **kwargs):
    if mouseOverlaps(rect):
        # click
        if mouse['down']:
            pg.draw.rect(surface, clickColor, rect)
        # hover
        else:
            pg.draw.rect(surface, hoverColor, rect)
            onClickMethod = kwargs.get('onClick')
            onClickArgs = kwargs.get('onClickArgs')
            if onClickMethod and mouse['up']:
                if onClickArgs:
                    onClickMethod(*onClickArgs)
                else:
                    onClickMethod()
                return True
    # default
    else:
        pg.draw.rect(surface, defaultColor, rect)
    return False


# Ativa & desativa dropdown que contém os métodos
def activateDropdownMenu():
    global dropdown_open
    dropdown_open = not dropdown_open


# Habilita & desabilita o som
def InverteEstadoDoSom():
    global som_habilitado
    som_habilitado = not som_habilitado
    audio.HabilitarSom(som_habilitado)


# Chamado pelos itens do dropdown, escolhe o método a ser usado
def setSortingMethod(i):
    global dropdown_open
    global current_sorting_method
    current_sorting_method = i
    dropdown_open = False


# Cria um vetor aleatório de tamanho listSize, com valores de 0.0 a 1.0
def generateFloatList():
    global floatList
    floatList = [0] * listSize
    for i in range(listSize):
        floatList[i] = random.uniform(0.0, 1.0)


# Desenha um botão seletor de numeros com título, modifica o valor
# verificando cliques nas setas, retorna ele
def UpDownValue(Surface, pos, height, text, value):
    # cores definidas localmente
    leftColor = (200, 0, 0)
    rightColor = (0, 200, 0)
    tint = (40, 40, 40)

    # cria os textos
    labelSurface = GetTextSurface(text, height / 2, (255, 255, 255))
    valueSurface = GetTextSurface(str(value), height / 2, (255, 255, 255))

    # detecta mouse nas setas, para mudar o valor e decidir como desenha-las
    if mouseOverlaps((pos[0], pos[1], labelSurface.get_height() * 2, labelSurface.get_height() * 2)):
        leftColor = (clamp(leftColor[0] - tint[0], 0, 255), clamp(leftColor[1] - tint[1], 0, 255),
                     clamp(leftColor[2] - tint[2], 0, 255))
        if mouse['up']:
            value -= 1
    elif mouseOverlaps((pos[0] + labelSurface.get_height() * 2 + labelSurface.get_width(), pos[1],
                        labelSurface.get_height() * 2, labelSurface.get_height() * 2)):
        rightColor = (clamp(rightColor[0] - tint[0], 0, 255), clamp(rightColor[1] - tint[1], 0, 255),
                      clamp(rightColor[2] - tint[2], 0, 255))
        if mouse['up']:
            value += 1

    # desenha os textos criados
    Surface.blit(labelSurface, (pos[0] + 2 * labelSurface.get_height(), pos[1]))
    Surface.blit(valueSurface, (
        pos[0] + labelSurface.get_width() * 0.5 + labelSurface.get_height() * 2 - valueSurface.get_width() * 0.5,
        pos[1] + labelSurface.get_height()))

    # cabeça da seta esquerda
    pg.draw.polygon(Surface, color=leftColor,
                    points=[(pos[0], pos[1] + labelSurface.get_height()),
                            (pos[0] + 2 * labelSurface.get_height(), pos[1] + labelSurface.get_height()),
                            (pos[0] + labelSurface.get_height(), pos[1] + 2 * labelSurface.get_height())])
    # corpo da seta esquerda
    pg.draw.rect(Surface, leftColor, (
        pos[0] + 0.6 * labelSurface.get_height(), pos[1],
        0.99 * labelSurface.get_height(), labelSurface.get_height()))

    # cabeça seta direita
    pg.draw.polygon(Surface, color=rightColor,
                    points=[(pos[0] + labelSurface.get_width() + labelSurface.get_height() * 2,
                             pos[1] + labelSurface.get_height()),
                            (pos[0] + labelSurface.get_width() + labelSurface.get_height() * 3, pos[1]),
                            (pos[0] + labelSurface.get_width() + labelSurface.get_height() * 4,
                             pos[1] + labelSurface.get_height())
                            ])
    # corpo seta direita
    pg.draw.rect(Surface, rightColor, (
        pos[0] + 2.6 * labelSurface.get_height() + labelSurface.get_width(), pos[1] + labelSurface.get_height(),
        0.99 * labelSurface.get_height(), labelSurface.get_height()))

    return value


# Desenha o dropdown. Os valores de posição e escala são fixos, pois é
# chamado uma vez só. Retorna se o valor for modificado
def Dropdown():
    global dropdown_open

    foi_interagido = False

    # se estiver aberto, desenhar todos os botões
    if dropdown_open:
        areaRect = (
            0.01 * reference, 0.01 * reference, 0.3 * reference, 0.051 + (0.041 * len(sorting_titles)) * reference)
        # desenha um fundo
        pg.draw.rect(screen, DROPDOWN_BACKGROUND_COLOR, areaRect)
        dropdown_open = mouseOverlaps(areaRect)
        drawnTitles = 1
        for i in range(len(sorting_titles)):
            if i != current_sorting_method:
                textSurface = GetTextSurface(sorting_titles[i], int(0.04 * reference))
                foi_interagido = foi_interagido or DrawButton(screen,
                                                              (
                                                                  0.01 * reference,
                                                                  (0.02 + drawnTitles * 0.04) * reference,
                                                                  0.3 * reference, 0.04 * reference),
                                                              DROPDOWN_BACKGROUND_COLOR,
                                                              DROPDOWN_BACKGROUND_HOVERED_COLOR,
                                                              DROPDOWN_BACKGROUND_CLICKED_COLOR,
                                                              onClick=setSortingMethod,
                                                              onClickArgs=[i])
                screen.blit(textSurface, (0.02 * reference, (0.03 + drawnTitles * 0.04) * reference))
                drawnTitles += 1
    # Botão principal
    areaRect = (0.01 * reference, 0.01 * reference, 0.3 * reference, 0.05 * reference)
    DrawButton(screen, areaRect, DROPDOWN_BACKGROUND_COLOR, DROPDOWN_BACKGROUND_HOVERED_COLOR,
               DROPDOWN_BACKGROUND_CLICKED_COLOR, onClick=activateDropdownMenu)
    # Margem para o botão principal
    pg.draw.rect(screen, DROPDOWN_MARGIN_COLOR,
                 (int(0.01 * reference), int(0.01 * reference), int(0.3 * reference), int(0.05 * reference)),
                 width=max(int(0.005 * reference), 1))
    # Seta do botão, indicando estado (aberto ou fechado)
    pg.draw.polygon(screen, DROPDOWN_FONT_COLOR,
                    ([(0.28 * reference, 0.025 * reference), (0.265 * reference, 0.041 * reference),
                      (0.295 * reference, 0.041 * reference)] if dropdown_open
                     else [(0.28 * reference, 0.046 * reference), (0.265 * reference, 0.03 * reference),
                           (0.295 * reference, 0.03 * reference)]))
    # texto do botão
    screen.blit(GetTextSurface(sorting_titles[current_sorting_method], int(reference * 0.05)),
                (0.02 * reference, 0.02 * reference))
    return foi_interagido


# Desenha o conteúdo da tela, incluindo as barras que representam a lista
# e os controles da interface.
# Todos os algorítmos de organização (Sorting) chamam esta função para
# trocar de lugar os items, ou a cada etapa que seja necessário, para a
# visualização, um intervalo.
# Também desenha "pointers", que ajudam a indicar o que o algorítmo está
# fazendo.
def drawUI(swap=None, pointer=[], animatedPointerTransition=True):
    global screenSize
    global mouse
    global dropdown_open
    global delay
    global reference
    global old_pointer
    global listSize
    global instrumento

    # usado para calcular o progresso
    startTime = pg.time.get_ticks()
    # usado para desenhar barras no estágio correto da animação e pelo volume
    progress = 0.0

    # para o audio anterior
    audio.parar()

    if swap is not None:
        # Se for haver troca, deve ser tocada um acorde. Ele toca durante
        # todo o período da troca, a frequencia de suas notas dependem dos
        # itens sendo trocados, ficando cada um entre 50 e 440Hz.
        audio.tocarNotas(audio.freq2midi(
            lerp(50, 440, floatList[swap[0]]),
            lerp(50, 440, floatList[swap[1]])
        ))

    # enquanto ainda não acabou a troca
    while progress < 1:
        mouse['up'] = False
        # verifica eventos
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYUP and e.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif e.type == pg.WINDOWRESIZED:
                screenSize = e.x, e.y
            elif e.type == pg.MOUSEMOTION:
                mouse['pos'] = e.pos
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    mouse['down'] = True
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    mouse['down'] = False
                    mouse['up'] = True

        # tamanho da interface depende da altura da tela
        reference = screenSize[1]

        areaRect = (0, 0, screenSize[0], screenSize[1] * 0.1)
        # barra superior
        pg.draw.rect(screen, TOP_BAR_COLOR, areaRect)

        # fundo
        pg.draw.rect(screen, BACKGROUND_COLOR, (0, 0.1 * reference, screenSize[0], screenSize[1] * 0.9))

        bar_width = screenSize[0] / len(floatList)
        pointer_width = max(10, 0.01 * screenSize[0])

        # desenha os pointers
        for i in range(len(pointer)):
            if len(old_pointer) > i and animatedPointerTransition:
                lastPos = old_pointer[i]
            else:
                lastPos = pointer[i]
            pg.draw.rect(screen, POINTER_COLOR, (
                (bar_width * (lastPos + 0.5) - pointer_width * 0.5) * (1 - progress) + (
                        bar_width * (pointer[i] + 0.5) - pointer_width * 0.5) * progress,
                0.1 * reference, pointer_width, 0.9 * reference))

        # Desenha as barras.
        # Cada uma tem a altura especificada por floatList
        for i in range(len(floatList)):
            # se for uma das indicadas em swap, ela é desenhada um pouco
            # para o lado da outra, para dar a ilusão de que elas estão
            # trocando de posição
            if swap is not None and i == swap[0]:
                xPos = (screenSize[0] / len(floatList)) * swap[0] * (1 - progress) + (screenSize[0] / len(floatList)) * \
                       swap[1] * progress
            elif swap is not None and i == swap[1]:
                xPos = (screenSize[0] / len(floatList)) * swap[0] * progress + (screenSize[0] / len(floatList)) * \
                       swap[1] * (1 - progress)
            else:
                xPos = (screenSize[0] / len(floatList)) * i

            rect = (xPos,
                    screenSize[1] - (0.9 * reference * floatList[i]),
                    screenSize[0] / len(floatList),
                    0.9 * reference * floatList[i])

            # desenha o preenchimento da barra
            pg.draw.rect(screen, BAR_COLOR, rect)
            # desenha a margem da barra
            pg.draw.rect(screen, BAR_MARGIN_COLOR, rect, 1)

        # menu dropdown
        if Dropdown():
            # se ele foi modificado, devemos parar o algorítmo sendo rodado
            return False

        # Seletor de delay:
        # indica o quanto devemos esperar entre cada etapa do algorítmo
        delay = max(0.001, round(
            UpDownValue(screen, (0.33 * reference, 0.01 * reference), 0.08 * reference, "delay", delay)
        ))

        # Seletor do tamanho da lista:
        # novo tamanho só será aplicado na próxima lista gerada
        listSize = max(1,
                       UpDownValue(screen, (0.53 * reference, 0.01 * reference), 0.08 * reference, "tamanho", listSize))

        # seletor de instrumento, para o audio
        last_instrumento = instrumento
        instrumento = clamp(UpDownValue(
            screen, (0.77 * reference, 0.01 * reference), 0.08 * reference, "instrumento", instrumento),
            0, 100)
        if instrumento != last_instrumento:
            audio.set_instrumento(instrumento)

        # Botão de volume
        DrawButton(screen, (1.05 * reference, 0.02 * reference, 0.06 * reference, 0.06 * reference), MUTE_BUTTON_COLOR,
                   MUTE_BUTTON_HOVERED_COLOR, MUTE_BUTTON_CLICKED_COLOR, onClick=InverteEstadoDoSom)
        # desenha o ícone
        pg.draw.rect(screen, BLACK,
                     (1.07 * reference, 0.04 * reference, 0.015 * reference, 0.02 * reference))
        pg.draw.polygon(screen, BLACK, [(1.08 * reference, 0.04 * reference), (1.09 * reference, 0.03 * reference),
                                        (1.09 * reference, 0.07 * reference), (1.08 * reference, 0.06 * reference)])
        # linha de "sem volume"
        if not som_habilitado:
            pg.draw.polygon(screen, MUTE_BUTTON_MUTED_COLOR,
                            [(1.05 * reference, 0.02 * reference),
                             (1.06 * reference, 0.02 * reference),
                             (1.109 * reference, 0.07 * reference),
                             (1.109 * reference, 0.079 * reference),
                             (1.102 * reference, 0.079 * reference),
                             (1.05 * reference, 0.025 * reference),
                             ])
        # atualiza o display
        pg.display.flip()

        # verifica o tempo passado para determinar o progresso, em %
        progress = (pg.time.get_ticks() - startTime) / (delay * 10)

    old_pointer = pointer
    if swap is not None:
        # Troca de fato os itens no final da animação, para concluir a
        # ilusão.
        floatList[swap[0]], floatList[swap[1]] = floatList[swap[1]], floatList[swap[0]]

    return True


'''
Funções de ordenamento (sorting)
Em todas elas, a variavel deve_continuar é a saida de drawUI, indicando
se o método de ordenação foi mudado 
'''


def BubbleSort(V):
    i = 0
    deve_continuar = True
    while i < (len(V) - 1) and deve_continuar:
        deve_continuar = drawUI(pointer=[0])
        j = 0
        while j < (len(V) - 1 - i) and deve_continuar:
            swap = None
            if V[j] > V[j + 1]:
                swap = j, j + 1
            deve_continuar = drawUI(swap, pointer=[j + 1])
            j += 1
        i += 1
    if deve_continuar: deve_continuar = drawUI(pointer=[-1])
    return deve_continuar


def SelectionSort(v):
    deve_continuar = True
    i = 0
    while i < (len(v) - 1) and deve_continuar:
        menor = i
        j = i
        while j < len(v) and deve_continuar:
            if v[j] < v[menor]:
                menor = j
            deve_continuar = drawUI(pointer=[j])
            j += 1
        if deve_continuar:
            if i != menor:
                deve_continuar = drawUI(swap=(i, menor), pointer=[i])
            i += 1
    if deve_continuar: deve_continuar = drawUI(pointer=[len(v)])
    return deve_continuar


def InsertionSort(v):
    deve_continuar = drawUI(pointer=[0])
    # ainda não chegou ao final?
    i = 1
    while i < len(v) and deve_continuar:
        j = i - 1
        while j >= 0 and v[j] > v[j + 1] and deve_continuar:
            deve_continuar = drawUI(swap=(j, j + 1), pointer=[i])
            j -= 1
        i += 1
        deve_continuar = drawUI(pointer=[i])
    return deve_continuar


# particiona a lista para o quickSort
def QS_partition(lista, inicio, fim):
    pivo = lista[fim]
    i = inicio  # barra min
    j = inicio
    deve_continuar = True
    while j < fim and deve_continuar:  # barra max
        if lista[j] <= pivo:
            # swap
            deve_continuar = drawUI(swap=(i, j), pointer=[fim, i])
            i += 1
        j += 1

    if deve_continuar:
        deve_continuar = drawUI(swap=(i, fim), pointer=[fim, i])
    return i, deve_continuar


def QuickSort(lista, inicio=0, fim=None):
    if fim is None:
        fim = len(lista) - 1
    deve_continuar = True
    if inicio < fim:
        pivo, deve_continuar = QS_partition(lista, inicio, fim)
        if deve_continuar:
            deve_continuar = QuickSort(lista, inicio, pivo - 1)
            if deve_continuar:
                deve_continuar = QuickSort(lista, pivo + 1, fim)
    return deve_continuar


# retorna uma nova lista, onde cada lista de "listas" é dividida na
# metade se for maior de 1
def MS_dividir_em_2(listas):
    r = []
    for l in listas:
        if len(l) > 1:
            r.append(l[0:int(len(l) / 2)])
            r.append(l[int(len(l) / 2):len(l)])
        else:
            r.append(l)
    return r


# Como MergeSort normalmente não usa SWAP, ela não poderia ser exibida
# neste sistema criado. Por isso, o algoritmo foi bastante modificado,
# dividindo a lista localmente ao invéz de criar novas.
def MergeSort(lista):
    listas = [lista]
    pointers = []
    divisores = []
    deve_continuar = drawUI()

    # Divide a lista em listas de metade do tamanho, mantendo na memória
    # onde foram feitas cada uma das divisões
    i = 0
    while i < math.ceil(math.log(len(lista), 2)) and deve_continuar:
        listas = MS_dividir_em_2(listas)
        total = 0
        for j in range(len(listas) - 1):
            total += len(listas[j])
            if total not in divisores:
                divisores.append(total)
                pointers.append(total - 0.5)
        deve_continuar = drawUI(pointer=pointers)
        i += 1

    # Depois que foi totalmente dividida, organizamos etapa por etapa
    sorted_divisores = divisores.copy()
    sorted_divisores.sort()
    i = len(divisores) - 1
    # para cada divisão, começando da última
    while i > -1 and deve_continuar:
        divisor = divisores[i]

        # retira o divisor da memória
        del pointers[i]
        sorted_divisores.remove(divisor)

        # determina o limite superior da sublista a ser organizada
        upper_limit = list(x for x in sorted_divisores if x > divisor)
        if len(upper_limit) == 0:
            end = len(lista)
        else:
            end = min(upper_limit)
        # determina o limite inferior da sublista a ser organizada
        bottom_limit = list(x for x in sorted_divisores if x < divisor)
        if len(bottom_limit) == 0:
            start = 0
        else:
            start = max(bottom_limit)

        # Realiza um SelectionSort no intervalo determinado, para simular
        # a reconstrução da lista
        h = start
        while h < end - 1 and deve_continuar:
            menor = h
            j = h
            while j < end and deve_continuar:
                if lista[j] < lista[menor]:
                    menor = j
                j += 1
            if h != menor:
                deve_continuar = drawUI(swap=(h, menor), pointer=pointers)
            h += 1
        i -= 1
    return deve_continuar


def main():
    global screen
    global current_sorting_method

    # inicia o pygame
    pg.init()
    pg.font.init()

    # inicia o display
    screen = pg.display.set_mode(screenSize, pg.RESIZABLE)
    pg.display.set_caption("Sort")

    # cria uma lista aleatoria de "tela de início"
    generateFloatList()

    while True:

        # se o metodo selecionado não for idle (0), cria uma lista e depois chama ele
        if current_sorting_method != 0:
            generateFloatList()
            sucesso = [BubbleSort, SelectionSort, InsertionSort, QuickSort, MergeSort][current_sorting_method - 1](
                floatList)
            # se tiver tido sucesso, vai pro idle
            if sucesso:
                current_sorting_method = 0
        else:
            drawUI()


if __name__ == '__main__':
    main()
