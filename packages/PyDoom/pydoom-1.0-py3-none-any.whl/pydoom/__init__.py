# pydoom.py
import pygame, os, sys

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# -----------------------------
# РЕГИСТРЫ
# -----------------------------
CUSTOM_WALLS = {}   # символ → текстура стены
CUSTOM_ENEMIES = {} # символ → текстура врага

# -----------------------------
# СТЕНЫ
# -----------------------------
class wall:
    @staticmethod
    def custom(type:str, texture:str):
        CUSTOM_WALLS[type] = texture

# -----------------------------
# ВРАГИ
# -----------------------------
class enemy:
    @staticmethod
    def custom(type:str, texture:str):
        CUSTOM_ENEMIES[type] = texture

# -----------------------------
# СОЗДАНИЕ ОБЪЕКТОВ
# -----------------------------
class create:
    @staticmethod
    def sound(type:str, path:str):
        snd = None
        if os.path.exists(path):
            snd = pygame.mixer.Sound(path)
        return {"type": type, "sound": snd}

    @staticmethod
    def player_gun(texture:str=None, sound=None):
        gun_tex = None
        if texture and os.path.exists(texture):
            gun_tex = pygame.image.load(texture).convert_alpha()
        return {"texture": gun_tex, "sound": sound}

    @staticmethod
    def enemy(x:int, y:int, sound=None):
        return {"x":x, "y":y, "sound":sound}

# -----------------------------
# ЗАГРУЗКА КАРТЫ И ИГРОКА
# -----------------------------
class load:
    @staticmethod
    def map(path:str):
        if not os.path.exists(path):
            print(f"[pydoom] map not found: {path}")
            return []
        with open(path,"r") as f:
            lines = [line.rstrip("\n") for line in f]
        return [list(row) for row in lines]

    @staticmethod
    def player(gun=None, sound=None):
        return {"x":0, "y":0, "gun":gun, "sound":sound}

# -----------------------------
# ИГРОВОЙ ДВИЖОК
# -----------------------------
class doom:
    SCREEN_W = 800
    SCREEN_H = 600
    TILE = 64
    FPS = 60

    @staticmethod
    def run(game_map, player):
        screen = pygame.display.set_mode((doom.SCREEN_W, doom.SCREEN_H))
        clock = pygame.time.Clock()

        # Находим старт игрока
        for j,row in enumerate(game_map):
            for i,cell in enumerate(row):
                if cell=="@":
                    player["x"] = i*doom.TILE + doom.TILE//2
                    player["y"] = j*doom.TILE + doom.TILE//2

        running=True
        while running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False

            keys = pygame.key.get_pressed()
            dx = dy = 0
            speed = 3
            if keys[pygame.K_w]: dy -= speed
            if keys[pygame.K_s]: dy += speed
            if keys[pygame.K_a]: dx -= speed
            if keys[pygame.K_d]: dx += speed

            # Движение (простейшая проверка стен)
            new_x = player["x"] + dx
            new_y = player["y"] + dy
            collide=False
            for j,row in enumerate(game_map):
                for i,cell in enumerate(row):
                    if cell in CUSTOM_WALLS:
                        wall_rect = pygame.Rect(i*doom.TILE,j*doom.TILE,doom.TILE,doom.TILE)
                        player_rect = pygame.Rect(new_x-10,new_y-10,20,20)
                        if wall_rect.colliderect(player_rect):
                            collide=True
            if not collide:
                player["x"] = new_x
                player["y"] = new_y

            # Рендер
            screen.fill((0,0,0))
            for j,row in enumerate(game_map):
                for i,cell in enumerate(row):
                    x=i*doom.TILE
                    y=j*doom.TILE
                    # Стены
                    if cell in CUSTOM_WALLS:
                        tex_path = CUSTOM_WALLS[cell]
                        if os.path.exists(tex_path):
                            img = pygame.image.load(tex_path).convert()
                            img = pygame.transform.scale(img,(doom.TILE,doom.TILE))
                            screen.blit(img,(x,y))
                    # Враги
                    elif cell in CUSTOM_ENEMIES:
                        tex_path = CUSTOM_ENEMIES[cell]
                        if os.path.exists(tex_path):
                            img = pygame.image.load(tex_path).convert_alpha()
                            img = pygame.transform.scale(img,(doom.TILE,doom.TILE))
                            screen.blit(img,(x,y))
                        else:
                            pygame.draw.circle(screen,(255,0,0),(x+doom.TILE//2,y+doom.TILE//2),10)
                    # Игрок
                    elif cell=="@":
                        pygame.draw.circle(screen,(0,255,0),(x+doom.TILE//2,y+doom.TILE//2),10)
                    # Пустота
                    elif cell==".":
                        continue

            # Отображаем оружие
            if player.get("gun") and player["gun"]["texture"]:
                gun_img = pygame.transform.scale(player["gun"]["texture"],(40,20))
                screen.blit(gun_img,(player["x"]-20,player["y"]-10))

            pygame.display.flip()
            clock.tick(doom.FPS)

        pygame.quit()
        sys.exit()
