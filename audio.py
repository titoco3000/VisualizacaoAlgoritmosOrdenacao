'''
Modulo de som
'''
import pygame.midi

notas_atuais = []
pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)

som_habilitado = True


# Transforma de frequencia (Hz) para notas musicais
def freq2midi(*args):
    L = []
    for frequencia in args:
        L.append(pygame.midi.frequency_to_midi(frequencia))
    return L


# Toca o acorde formado pelas notas
def tocarNotas(notas):
    global notas_atuais
    volume = 64 if som_habilitado else 0
    # desativa as notas que não vão ser usadas
    for nota in notas_atuais:
        if nota not in notas:
            player.note_off(nota, volume)

    # ativa as que vão ser usadas
    for nota in notas:
        if nota not in notas_atuais:
            player.note_on(nota, volume)

    notas_atuais = notas


# Para o acorde atual
def parar():
    tocarNotas([])


# habilita ou desabilita o som
def HabilitarSom(valor):
    global som_habilitado
    # muda o estado de cada uma das notas ativas
    volume_inicial = 64 if som_habilitado else 0
    volume_final = 0 if som_habilitado else 64
    for nota in notas_atuais:
        player.note_off(nota, volume_inicial)
        player.note_on(nota, volume_final)

    som_habilitado = valor


# muda o instrumento
def set_instrumento(instrumento):
    player.set_instrument(instrumento)
