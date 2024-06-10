import pygame
from pygame.locals import *
import os
from random import randrange, choice

# Inicialização do Pygame
pygame.init()
pygame.mixer.init()

# Configurações de diretório
diretorio_principal = os.path.dirname(__file__)
diretorio_imagens = os.path.join(diretorio_principal, 'images')
diretorio_sons = os.path.join(diretorio_principal, 'sounds')

# Constantes de tela
LARGURA = 1280
ALTURA = 720
BRANCO = (255, 255, 255)

# Configurações de jogo
velocidade_jogo = 10
colidiu = False
pontos = 0
escolha_obstaculo = choice([0, 1])

# Configuração da tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Dino Game')

# Carregamento de imagens
background_image = pygame.image.load(os.path.join(diretorio_imagens, 'desert.png')).convert()
background_image = pygame.transform.scale(background_image, (LARGURA, ALTURA))

# Carregamento de sons
som_colisao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'death_sound.wav'))
som_colisao.set_volume(1)
som_pontuacao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'score_sound.wav'))
som_pontuacao.set_volume(1)

# Funções auxiliares
def exibe_mensagem(msg, tamanho, cor):
    cor = (255, 255, 255)
    msg = f'{msg}'
    fonte = pygame.font.SysFont('comicsansms', tamanho, True, False)
    texto_formatado = fonte.render(msg, True, cor)
    return texto_formatado

def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obstaculo, grupo_obstaculos, dino
    pontos = 0
    velocidade_jogo = 10
    colidiu = False
    escolha_obstaculo = choice([0, 1])

    # Reiniciar o Dino
    dino.rect.bottom = dino.pos_y_inicial  # Correção para garantir que o dino alinhe com o chão
    dino.pulo = False
    dino.vel_y = 0  # Reiniciar a velocidade vertical

    # Reiniciar os obstáculos
    for obstaculo in grupo_obstaculos:
        obstaculo.reset()

    # Redefinir a posição do cacto inicial
    grupo_obstaculos.empty()
    for _ in range(3):
        cacto = Cacto()
        grupo_obstaculos.add(cacto)
        todas_as_sprites.add(cacto)

def mostrar_menu(tela, fonte):
    overlay = pygame.Surface((LARGURA, ALTURA))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    tela.blit(overlay, (0, 0))
    mensagem_menu = 'Aperte ENTER para iniciar'
    texto_menu = fonte.render(mensagem_menu, True, (255, 255, 255))
    tela.blit(texto_menu, (LARGURA // 2 - texto_menu.get_width() // 2, ALTURA // 2 - texto_menu.get_height() // 2))
    pygame.display.flip()

    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    esperando = False

class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.som_pulo = pygame.mixer.Sound(os.path.join(diretorio_sons, 'jump_sound.wav'))
        self.som_pulo.set_volume(1)
        
        # Carregar cada quadro da animação do dino em uma lista
        self.imagens_dinossauro = [
            pygame.image.load(os.path.join(diretorio_imagens, f'dino_{i}.png')).convert_alpha()
            for i in range(1, 9)  # Assumindo que existem 8 quadros numerados de 1 a 8
        ]
        
        # Se necessário, ajustar os quadros (mudar o fator de escala conforme necessário)
        self.imagens_dinossauro = [pygame.transform.scale(img, (128, 128)) for img in self.imagens_dinossauro]
        
        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        # Ajustar a posição y inicial do dino para alinhar com o chão, não com o cacto
        self.pos_y_inicial = ALTURA - self.image.get_height()
        self.rect.bottom = self.pos_y_inicial
        self.pulo = False

        # Novos atributos para o pulo
        self.vel_pulo = -16  # Velocidade inicial do pulo, negativa para subir (ajustada para pular mais alto)
        self.gravidade = 0.95  # Gravidade puxando para baixo
        self.vel_y = 0  # Velocidade vertical atual

    def pular(self):
        if not self.pulo:
            self.pulo = True
            self.vel_y = self.vel_pulo  # Iniciar o pulo com a velocidade inicial

    def update(self):
        # Adiciona gravidade
        if self.pulo:
            self.vel_y += self.gravidade
            self.rect.y += self.vel_y

            # Verificar se o dino tocou o chão
            if self.rect.bottom >= self.pos_y_inicial:
                self.rect.bottom = self.pos_y_inicial
                self.pulo = False
                self.vel_y = 0

        # Atualizar animação do dino
        self.index_lista += 0.25
        if self.index_lista >= len(self.imagens_dinossauro):
            self.index_lista = 0
        self.image = self.imagens_dinossauro[int(self.index_lista)]

class Nuvens(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        cloud_strip_path = os.path.join(diretorio_imagens, 'spr_nuvens_strip6.png')
        cloud_strip = pygame.image.load(cloud_strip_path).convert_alpha()
        
        cloud_width = cloud_strip.get_width() // 6
        cloud_height = cloud_strip.get_height()
        cloud_position = randrange(6) * cloud_width
        self.image = cloud_strip.subsurface((cloud_position, 0), (cloud_width, cloud_height))
        
        # Aplicar coloração branca
        white_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        white_surface.fill((255, 255, 255, 180))  # Branco com opacidade
        self.image.blit(white_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Tamanho randômico
        scale_factor = randrange(5, 10) / 10.0  # Escala randômica entre 0.5 e 1.0
        self.image = pygame.transform.scale(self.image, (int(cloud_width * scale_factor), int(cloud_height * scale_factor)))
        
        self.rect = self.image.get_rect()
        self.rect.y = randrange(50, 200, 50)  # Variação na altura das nuvens
        self.rect.x = LARGURA + randrange(0, 300)  # Começam fora da tela à direita

        self.velocidade = randrange(1, 3)  # Velocidade mais uniforme para as nuvens

    def update(self):
        self.rect.x -= self.velocidade
        if self.rect.right < 0:  # Resetar a posição da nuvem quando sair da tela
            self.kill()  # Remover a nuvem antiga e criar uma nova abaixo

class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(diretorio_imagens, 'floor_2.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.y = ALTURA - self.rect.height
        self.rect.x = pos_x * self.rect.width  # Posição x é baseada na largura da imagem e na posição passada como argumento

    def update(self):
        self.rect.x -= velocidade_jogo
        if self.rect.right < 0:
            last_chao = chao_sprites.sprites()[-1]
            self.rect.left = last_chao.rect.right - velocidade_jogo  # Ajuste para garantir que não haja espaços entre as peças do chão

class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Carregar a imagem original do cacto
        self.original_image = pygame.image.load(os.path.join(diretorio_imagens, 'cactus.png')).convert_alpha()
        self.reset()

    def reset(self):
        # Define um fator de escala aleatório entre 1.0 e 1.15
        scale_factor = 1 + randrange(0, 16) / 100.0
        
        # Obter as novas dimensões
        new_width = int(self.original_image.get_width() * scale_factor)
        new_height = int(self.original_image.get_height() * scale_factor)
        
        # Redimensionar a imagem
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        
        # Configurar o rect do sprite
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (LARGURA + randrange(100, 300), ALTURA - 128)

    def update(self):
        self.rect.x -= velocidade_jogo  # Move the cactus left
        if self.rect.right < 0:  # Reset position if it goes off-screen
            self.reset()

class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(diretorio_imagens, 'background_image.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def update(self):
        # If you want a moving background, you can slowly shift it
        self.rect.x -= velocidade_jogo / 10  # Slower speed for parallax
        if self.rect.right < LARGURA:  # Reset position if it goes off-screen
            self.rect.left = 0

# Grupos de sprites
todas_as_sprites = pygame.sprite.Group()
chao_sprites = pygame.sprite.Group()
nuvens_sprites = pygame.sprite.Group()
grupo_obstaculos = pygame.sprite.Group()

# Criação de instâncias
dino = Dino()
todas_as_sprites.add(dino)
chao_sprites.add(Chao(0))

# Adicionar múltiplas nuvens conforme necessário
quantidade_nuvens = randrange(2, 8)  # Número aleatório de nuvens
for _ in range(quantidade_nuvens):
    nuvem = Nuvens()
    nuvens_sprites.add(nuvem)

# Adicionar cactos
for _ in range(3):
    cacto = Cacto()
    grupo_obstaculos.add(cacto)
    todas_as_sprites.add(cacto)

# Adicionar múltiplas peças de chão conforme necessário
numero_pecas = (LARGURA // background_image.get_width()) + 2
for i in range(numero_pecas):
    chao = Chao(i)
    chao_sprites.add(chao)

# Configuração do relógio
relogio = pygame.time.Clock()
mostrar_menu(tela, pygame.font.SysFont('comicsansms', 40))

# Laço principal do jogo
while True:
    relogio.tick(30)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE and not colidiu:
                if dino.rect.bottom >= dino.pos_y_inicial:
                    dino.pular()
            if event.key == K_r and colidiu:
                reiniciar_jogo()

    # Renderizar o fundo
    tela.blit(background_image, (0, 0))

    # Atualizar e desenhar todos os sprites
    if not colidiu:
        todas_as_sprites.update()
        chao_sprites.update()
        nuvens_sprites.update()

        # Verificar se a pontuação deve ser aumentada e aumentar a velocidade do jogo
        pontos += 1
        if pontos % 100 == 0 and pontos != 0:
            som_pontuacao.play()
        velocidade_jogo = 10 + (pontos // 200)  # Aumenta a velocidade continuamente com base nos pontos

    # Adicionar novo chão se necessário
    last_chao = max(chao_sprites, key=lambda c: c.rect.right)
    if last_chao.rect.right <= LARGURA:
        new_chao = Chao(last_chao.rect.right // last_chao.rect.width)
        chao_sprites.add(new_chao)

    # Verificar colisões
    colisoes = pygame.sprite.spritecollide(dino, grupo_obstaculos, False, pygame.sprite.collide_mask)
    if colisoes and not colidiu:
        som_colisao.play()
        colidiu = True
    
    # Atualizar as nuvens
    nuvens_sprites.update()

    # Checar se as nuvens saíram da tela e criar novas se necessário
    for nuvem in list(nuvens_sprites):
        if nuvem.rect.right < 0:
            nuvens_sprites.remove(nuvem)
            if len(nuvens_sprites) < quantidade_nuvens:
                new_nuvem = Nuvens()
                nuvens_sprites.add(new_nuvem)

    # Desenhar o chão e os sprites na tela
    chao_sprites.draw(tela)
    nuvens_sprites.draw(tela)
    todas_as_sprites.draw(tela)

    # Exibir a pontuação
    texto_pontos = exibe_mensagem(str(pontos), 40, BRANCO)
    tela.blit(texto_pontos, (LARGURA - texto_pontos.get_width() - 20, 20))

    # Exibir mensagem de game over se colidiu
    if colidiu:
        game_over = exibe_mensagem('GAME OVER', 40, BRANCO)
        tela.blit(game_over, (LARGURA // 2 - game_over.get_width() // 2, ALTURA // 2))
        restart = exibe_mensagem('Pressione R para reiniciar', 20, BRANCO)
        tela.blit(restart, (LARGURA // 2 - restart.get_width() // 2, ALTURA // 2 + 60))

    # Atualizar a tela
    pygame.display.flip()
