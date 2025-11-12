import pygame
import random

def mainloop():
    pygame.init()

    screen = pygame.display.set_mode((800,600))
    background = pygame.image.load("background.png")
    pygame.display.set_caption("Learning pygame")
    icon = pygame.image.load('startup.png')
    pygame.display.set_icon(icon)

    # player: __________________________________
    playerimg = pygame.image.load('player.png') 
    playerX = 400
    playerY = 500
    playermoveX = 0 
    def player(x, y):
        screen.blit(playerimg, (playerX, playerY))
    # =============================================

    # enemy: __________________________________
    enemyimg = pygame.image.load('enemy.png') 
    enemyX = random.randint(0, 800)
    enemyY = 50
    enemymoveX = 0.8
    def enemy(x, y):
        screen.blit(enemyimg, (enemyX, enemyY))
    # =============================================
    
    running = True
    while running:
        screen.fill((10,10,10))
        screen.blit(background, (0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    playermoveX = -0.5
                if event.key == pygame.K_d:
                    playermoveX = 0.5
            if event.type == pygame.KEYUP:
                playermoveX = 0

        playerX += playermoveX
        if playerX >= 736:
            playerX = 736
        elif playerX <= 0:
            playerX = 0

        enemyX += enemymoveX
        if enemyX >= 736:
            enemymoveX = -0.8
            enemyY += 30
        elif enemyX <= 0:
            enemymoveX = 0.8
            enemyY += 30

        player(playerX, playerY)
        enemy(enemyX, enemyY)
        pygame.display.update()
if __name__ == "__main__":
    mainloop()