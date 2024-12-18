import pygame
import sys
import os

class Frontend:
    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Legends of EVI")
        self.clock = pygame.time.Clock()
        self.background_image = pygame.image.load("resources/texture/1.png").convert()

        # Коэффициент увеличения спрайтов
        self.scale_factor = 2

        def load_and_scale_images_from_dir(directory, num):
            images = []
            for i in range(1, num):
                path = os.path.join(directory, f"{i}.png")
                img = pygame.image.load(path).convert_alpha()
                # Масштабируем в 2 раза
                w, h = img.get_size()
                img = pygame.transform.scale(img, (w * self.scale_factor, h * self.scale_factor))
                images.append(img)
            return images

        self.hero_images = {
            "up": load_and_scale_images_from_dir("resources/walk_up_surf", 10),
            "down": load_and_scale_images_from_dir("resources/walk_down_prosto", 10),
            "right": load_and_scale_images_from_dir("resources/walk_left_prosto", 10),
        }
        # Отражаем вправо - масштабирование уже произошло при загрузке
        self.hero_images["left"] = [pygame.transform.flip(img, True, False) for img in self.hero_images["right"]]

        self.enemy_images = {
            "goblin": load_and_scale_images_from_dir("resources/goblin", 9),
            "demon": load_and_scale_images_from_dir("resources/demon", 9)
        }

        bullet_img = pygame.image.load("resources/bullet.png").convert_alpha()
        bw, bh = bullet_img.get_size()
        self.bullet_image = pygame.transform.scale(bullet_img, (bw * self.scale_factor, bh * self.scale_factor))

        # Шрифт
        self.font = pygame.font.SysFont(None, 25)

        self.hero_frame = 0
        self.animation_timer = 0
        self.animation_delay = 4

    def get_user_input(self):
        quit_game = False
        input_state = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "shoot": False
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = True

        keys = pygame.key.get_pressed()
        input_state["up"] = keys[pygame.K_w]
        input_state["down"] = keys[pygame.K_s]
        input_state["left"] = keys[pygame.K_a]
        input_state["right"] = keys[pygame.K_d]
        input_state["shoot"] = keys[pygame.K_SPACE]

        return input_state, quit_game

    def draw(self, hero_state, enemies_state, bullets_state, walls_state, portals_state=None):
        
        if portals_state is None:
            portals_state = []
        self.screen.blit(self.background_image, (0, 0))

        # Отрисовка стен
        for w in walls_state:
            pygame.draw.rect(self.screen, (100, 100, 100), (w["x"], w["y"], w["width"], w["height"]))

        # Отрисовка героя
        if hero_state["alive"]:
            direction = hero_state["direction"]
            images = self.hero_images[direction]

            if hero_state["moving"]:
                self.animation_timer += 1
                if self.animation_timer >= self.animation_delay:
                    self.animation_timer = 0
                    self.hero_frame = (self.hero_frame + 1) % len(images)
            else:
                self.hero_frame = 0

            hero_img = images[self.hero_frame]
            self.screen.blit(hero_img, (hero_state["x"], hero_state["y"]))
        else:
            dead_text = self.font.render("You are dead!", True, (255, 0, 0))
            self.screen.blit(dead_text, (hero_state["x"], hero_state["y"]))

        # Отрисовка врагов
        for e in enemies_state:
            etype = e["type"]
            eimgs = self.enemy_images.get(etype, None)
            if eimgs:
                # Тут можно сделать примитивную анимацию. Пока возьмём первый кадр.
                enemy_img = eimgs[0]
            else:
                enemy_img = pygame.Surface((50 * self.scale_factor, 50 * self.scale_factor))
                enemy_img.fill((255, 0, 0))
            self.screen.blit(enemy_img, (e["x"], e["y"]))

            # Полоска здоровья врага
            max_hp = 100
            hp_ratio = e["health"] / max_hp
            hp_width = 50 * hp_ratio * self.scale_factor
            pygame.draw.rect(self.screen, (255, 0, 0), (e["x"], e["y"] - 10, hp_width, 5))

        # Отрисовка пуль
        for b in bullets_state:
            self.screen.blit(self.bullet_image, (b["x"], b["y"]))

        # Отрисовка порталов
        for p in portals_state:
            # Нарисуем просто яркий фиолетовый квадрат
            pygame.draw.rect(self.screen, (255, 0, 255), (p["x"], p["y"], p["width"], p["height"]))

        # Полоска здоровья героя
        

        health_text = self.font.render(f"Health: {hero_state['health']}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 10))

        pygame.display.flip()
        self.clock.tick(60)
