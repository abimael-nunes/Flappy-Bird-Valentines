import pygame
import os
import random
from tkinter import messagebox, simpledialog

DIFICULDADE = simpledialog.askinteger("FlappyBird", "Informe o nível de dificuldade desejado.\n Escolha um número entre 1 (Mais devagar) e 10 (Mais rápido)")             # Define a velocidade de passagem dos canos e do chão
PONTUACAO_DESEJADA = 5          # Define a pontuação mínima para que "coisas aconteçam"
TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGEM_BACKGROUND_FINAL = pygame.image.load(os.path.join('imgs', 'bg_2.png'))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)


class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = DIFICULDADE

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = DIFICULDADE
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def tela_inicial(tela):
    # Desenhar o fundo da tela inicial
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render("Clique para começar!", True, (0, 0, 0), (60, 156, 164))
    font = pygame.font.Font(None, 26)
    text_credito = font.render("Por Abimael Nunes", True, (90, 90, 90))
    text_rect = text.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA // 2))
    text_credito_rect = text_credito.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA - 20))
    tela.blit(text, text_rect)
    tela.blit(text_credito,text_credito_rect)
    pygame.display.update()

    # Loop para aguardar o clique do usuário
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                esperando = False


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()


def tela_pedido(tela):
    font = pygame.font.Font(None, 36)

    # Cria os botões (retângulos)
    button_sim = pygame.Rect(100, TELA_ALTURA // 2 + 100, 100, 50)
    button_nao = pygame.Rect(300, TELA_ALTURA // 2 + 100, 100, 50)

    # Variável para controlar a posição do botão "não"
    nao_moving = False

    rodando = True
    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

            # Verifica se o mouse está sobre o botão "não"
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if button_nao.collidepoint(mouse_pos):
                    nao_moving = True
                else:
                    nao_moving = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_sim.collidepoint(mouse_pos):
                    messagebox.askyesno("FlappyBird", "Você declara que leu e concorda com os termos?", icon='question')
                    pygame.quit()
                    quit()


        # Atualiza a posição do botão "não" se necessário
        if nao_moving:
            button_nao.x = random.randint(0, TELA_LARGURA - button_nao.width)
            button_nao.y = random.randint(0, TELA_ALTURA - button_nao.height)

        # Desenha na tela
        tela.blit(IMAGEM_BACKGROUND, (0, 0))
        tela.blit(IMAGEM_BACKGROUND_FINAL, (TELA_LARGURA // 2 - 145, TELA_ALTURA // 2 - 350))
        pygame.draw.rect(tela, (255, 102, 196), button_sim)
        pygame.draw.rect(tela, (255, 255, 255), button_nao)

        # Texto nos botões
        text_sim = font.render("Sim", True, (0, 0, 0))
        text_nao = font.render("Não", True, (0, 0, 0))
        tela.blit(text_sim, (button_sim.x + 20, button_sim.y + 10))
        tela.blit(text_nao, (button_nao.x + 20, button_nao.y + 10))

        pygame.display.flip()


def tela_fim_de_jogo(tela, pontos):
    # Desenhar o fundo, o texto e os botões
    fonte = pygame.font.SysFont('arial', 50)
    texto = fonte.render(f"Fim de jogo! Pontuação: {pontos}", True, (255, 255, 255))
    texto_rect = texto.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA // 2 - 150))
    fonte = pygame.font.SysFont('arial', 26)
    texto_restart = fonte.render("Você quer jogar novamente?", True, (0, 0, 0))
    texto_restart_rect = texto_restart.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA // 2 - 50))


    botao_sim = pygame.Rect(TELA_LARGURA // 2 - 100, TELA_ALTURA // 2, 200, 50)
    botao_nao = pygame.Rect(TELA_LARGURA // 2 - 100, TELA_ALTURA // 2 + 70, 200, 50)

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if botao_sim.collidepoint(mouse_pos):
                    # Reiniciar o jogo
                    if pontos < 5:
                        main()
                    else:
                        tela_pedido(tela)
                elif botao_nao.collidepoint(mouse_pos):
                    # Sair do jogo
                    pygame.quit()
                    quit()

        tela.blit(IMAGEM_BACKGROUND, (0, 0))
        pygame.draw.rect(tela, (94, 226, 112), botao_sim)
        pygame.draw.rect(tela, (60, 156, 164), botao_nao)
        tela.blit(texto, texto_rect)
        tela.blit(texto_restart, texto_restart_rect)
        fonte_botao = pygame.font.SysFont('arial', 30)
        texto_sim = fonte_botao.render("Sim", True, (255, 255, 255))
        texto_nao = fonte_botao.render("Não", True, (255, 255, 255))
        tela.blit(texto_sim, (botao_sim.x + 50, botao_sim.y + 10))
        tela.blit(texto_nao, (botao_nao.x + 50, botao_nao.y + 10))
        pygame.display.update()


def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()

    # Adicionar a tela inicial
    tela_inicial(tela)

    rodando = True
    while rodando:
        
        relogio.tick(30)

        # interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

        # mover as coisas
        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos)

        # Verificar se o jogo acabou (e.g., se a lista de pássaros está vazia)
        if not passaros:
            tela_fim_de_jogo(tela, pontos)


if __name__ == '__main__':
    main()