import pygame
from pygame.locals import *
from sys import exit
import os
from random import randrange, choice

pygame.init()
pygame.mixer.init()

diretorio_principal = os.path.dirname(__file__)
diretorio_imagens = os.path.join(diretorio_principal, 'images')
diretorio_sons = os.path.join(diretorio_principal, 'sounds')

LARGURA = 1280
ALTURA = 720
BRANCO = (255,255,255)
velocidade_jogo = 10

tela = pygame.display.set_mode((LARGURA, ALTURA))

pygame.display.set_caption('Dino Game')

background = pygame.image.load(os.path.join(diretorio_imagens, 'floor.png')).convert_alpha()
bg_size = background.get_size()

# Carregar a imagem de fundo
background_image = pygame.image.load(os.path.join(diretorio_imagens, 'desert.png')).convert()

# Ajustar o tamanho da imagem para cobrir toda a tela, se necessário
background_image = pygame.transform.scale(background_image, (LARGURA, ALTURA))

som_colisao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'death_sound.wav'))
som_colisao.set_volume(1)

som_pontuacao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'score_sound.wav'))
som_pontuacao.set_volume(1)

colidiu = False

escolha_obstaculo = choice([0, 1])

pontos = 0

fonte = pygame.font.SysFont('comicsansms', 40)

def exibe_mensagem(msg, tamanho, cor):
    cor = (255, 255, 255)
    fonte = pygame.font.SysFont('comicsansms', tamanho, True, False)
    mensagem = f'{msg}' 
    texto_formatado = fonte.render(mensagem, True, cor)
    return texto_formatado

def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obstaculo
    pontos = 0
    velocidade_jogo = 10
    colidiu = False
    dino.rect.y = ALTURA - 96 - dino.image.get_height()  # Ajuste para que o dino volte à altura correta
    dino.pulo = False
    cacto.rect.x = LARGURA
    escolha_obstaculo = choice([0, 1])
    
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
        self.imagens_dinossauro = [pygame.transform.scale(img, (96, 96)) for img in self.imagens_dinossauro]
        
        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        # Ajustar a posição y inicial do dino para alinhar com o chão, não com o cacto
        self.pos_y_inicial = ALTURA - self.image.get_height()
        self.rect.bottom = self.pos_y_inicial
        self.pulo = False

        # Novos atributos para o pulo
        self.vel_pulo = -15  # Velocidade inicial do pulo, negativa para subir
        self.gravidade = 1  # Gravidade puxando para baixo
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
        
        self.image = pygame.transform.scale(self.image, (cloud_width * 2, cloud_height * 2))  # Ajuste opcional de escala
        self.rect = self.image.get_rect()
        self.rect.y = randrange(50, 200, 50)  # Variação na altura das nuvens
        self.rect.x = LARGURA + randrange(0, 300)  # Começam fora da tela à direita

        self.velocidade = randrange(1, 5)  # Velocidade variável para cada nuvem

    def update(self):
        self.rect.x -= self.velocidade
        if self.rect.right < 0:  # Resetar a posição da nuvem quando sair da tela
            self.rect.left = LARGURA
            self.rect.y = randrange(50, 200, 50)
            self.velocidade = randrange(1, 5)  # Nova velocidade quando reciclada

class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(diretorio_imagens, 'floor_2.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.y = ALTURA - self.rect.height
        self.rect.x = pos_x * self.rect.width  # Posição x é baseada na largura da imagem e na posição passada como argumento

    def update(self):
        self.rect.x -= velocidade_jogo
        if self.rect.right < 0:  # Se a parte direita do chão sair da tela, move para a direita da última peça
            self.rect.left = LARGURA

    
class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        # Carregar a imagem original do cacto
        original_image = pygame.image.load(os.path.join(diretorio_imagens, 'cactus.png')).convert_alpha()
        
        # Definir um fator de escala
        scale_factor = 1.5  # Ajuste este valor conforme necessário para aumentar ou diminuir o tamanho do cacto
        
        # Obter as novas dimensões
        new_width = int(original_image.get_width() * scale_factor)
        new_height = int(original_image.get_height() * scale_factor)
        
        # Redimensionar a imagem
        self.image = pygame.transform.scale(original_image, (new_width, new_height))
        
        # Configurar o rect do sprite
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (LARGURA, ALTURA - 96)  # Adjust 64 if necessary to match ground height

    def update(self):
        self.rect.x -= velocidade_jogo  # Move the cactus left
        if self.rect.right < 0:  # Reset position if it goes off-screen
            self.rect.left = LARGURA


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

# class DinoVoador(pygame.sprite.Sprite):
#     def __init__(self):
#         pygame.sprite.Sprite.__init__(self)
#         self.imagens_dinossauro = []
#         for i in range(3,5):
#             img = sprite_sheet.subsurface((i*32, 0), (32,32))
#             img = pygame.transform.scale(img, (32*3, 32*3))
#             self.imagens_dinossauro.append(img)

#         self.index_lista = 0
#         self.image = self.imagens_dinossauro[self.index_lista]
#         self.mask = pygame.mask.from_surface(self.image)
#         self.escolha = escolha_obstaculo
#         self.rect = self.image.get_rect()
#         self.rect.center = (LARGURA, 300)
#         self.rect.x = LARGURA
    
#     def update(self):
#         if self.escolha == 1:
#             if self.rect.topright[0] < 0:
#                 self.rect.x = LARGURA
#             self.rect.x -= velocidade_jogo

#             if self.index_lista > 1:
#                 self.index_lista = 0
#             self.index_lista += 0.25
#             self.image = self.imagens_dinossauro[int(self.index_lista)]

todas_as_sprites = pygame.sprite.Group()
dino = Dino()
todas_as_sprites.add(dino)

for i in range(4):
    nuvem = Nuvens()
    todas_as_sprites.add(nuvem)

chao_sprites = pygame.sprite.Group()
floor_length = bg_size[0]
for i in range(0, LARGURA + floor_length, floor_length):
    chao = Chao(i // floor_length)
    chao.rect.y = dino.rect.bottom - 8
    chao_sprites.add(chao)
    
nuvens_sprites = pygame.sprite.Group()
for _ in range(10):  # Criar 10 nuvens
    nuvem = Nuvens()
    nuvens_sprites.add(nuvem)

todas_as_sprites.add(*nuvens_sprites)  # Adicionar todas as nuvens ao grupo de sprites principal


cacto = Cacto()
todas_as_sprites.add(cacto)

# dino_voador = DinoVoador()
# todas_as_sprites.add(dino_voador)

grupo_obstaculos = pygame.sprite.Group()
grupo_obstaculos.add(cacto)
# grupo_obstaculos.add(dino_voador)

relogio = pygame.time.Clock()
mostrar_menu(tela, fonte)
# Loop principal do jogo
# Loop principal do jogo
while True:
    relogio.tick(30)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE and not colidiu:
                if dino.rect.bottom == dino.pos_y_inicial:
                    dino.pular()
            if event.key == K_r and colidiu:
                reiniciar_jogo()

    # Desenhar o fundo primeiro
    tela.blit(background_image, (0, 0))

    # Atualiza e desenha o chão apenas se não houve colisão
    if not colidiu:
        chao_sprites.update()

    chao_sprites.draw(tela)

    # Atualiza todas as outras sprites apenas se não houve colisão
    if not colidiu:
        todas_as_sprites.update()
        if pontos % 100 == 0 and pontos != 0:
            som_pontuacao.play()
            if velocidade_jogo < 20:
                velocidade_jogo += 1
        pontos += 1

    todas_as_sprites.draw(tela)  # Desenhar todas as sprites na tela depois do fundo e do chão

    # Exibir a pontuação sempre, independente do estado de colisão
    texto_pontos = exibe_mensagem(str(pontos), 40, (0,0,0))
    tela.blit(texto_pontos, (520, 30))

    # Detecção de colisão
    colisoes = pygame.sprite.spritecollide(dino, grupo_obstaculos, False, pygame.sprite.collide_mask)
    if colisoes and not colidiu:
        som_colisao.play()
        colidiu = True

    # Exibe as mensagens de game over, se necessário
    if colidiu:
        game_over = exibe_mensagem('GAME OVER', 40, (0,0,0))
        tela.blit(game_over, (LARGURA // 2 - game_over.get_width() // 2, ALTURA // 2))
        restart = exibe_mensagem('Pressione R para reiniciar', 20, (0,0,0))
        tela.blit(restart, (LARGURA // 2 - restart.get_width() // 2, ALTURA // 2 + 60))

    pygame.display.flip()