import random
import math

class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.alive = True
        self.direction = "down"
        self.speed = 5
        self.shoot_timer = 0
        self.shoot_delay = 10
        self.is_moving = False

    def move(self, input_state, walls):
        self.is_moving = False
        old_x, old_y = self.x, self.y

        if input_state["up"]:
            self.y -= self.speed
            self.direction = "up"
            self.is_moving = True
        if input_state["down"]:
            self.y += self.speed
            self.direction = "down"
            self.is_moving = True
        if input_state["left"]:
            self.x -= self.speed
            self.direction = "left"
            self.is_moving = True
        if input_state["right"]:
            self.x += self.speed
            self.direction = "right"
            self.is_moving = True

        # Проверка коллизий со стенами
        if self.check_collision_walls(walls):
            self.x, self.y = old_x, old_y

    def check_collision_walls(self, walls):
        hero_rect = (self.x, self.y, 50, 50) 
        for w in walls:
            wall_rect = (w.x, w.y, w.width, w.height)
            if self.rects_collide(hero_rect, wall_rect):
                return True
        return False

    def rects_collide(self, r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

    def can_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            return True
        return False

    def update_timer(self):
        if self.shoot_timer > 0:
            self.shoot_timer -= 1


class Enemy:
    def __init__(self, x, y, speed=2, health=50, distant=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.health = health
        self.alive = True
        self.attack_cooldown = 0
        self.distant = distant
        self.shoot_range = 300 if distant else 0
        self.shoot_delay = 90

    def attack(self, hero):
        if self.attack_cooldown == 0:
            hero.health -= 10
            if hero.health <= 0:
                hero.alive = False
            self.attack_cooldown = 60

    def update(self, hero_x, hero_y):
        if not self.alive:
            return
        # Теперь и дальний враг тоже ходит:
        if abs(hero_x - self.x) > 5:
            self.x += self.speed if hero_x > self.x else -self.speed
        if abs(hero_y - self.y) > 5:
            self.y += self.speed if hero_y > self.y else -self.speed

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def distance_to_hero(self, hero_x, hero_y):
        dx = hero_x - self.x
        dy = hero_y - self.y
        return math.sqrt(dx*dx + dy*dy)


class Bullet:
    def __init__(self, x, y, direction, speed=10, owner='hero'):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.owner = owner

    def update(self):
        if self.direction == "up":
            self.y -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "right":
            self.x += self.speed

    def rect(self):
        return (self.x, self.y, 10, 10)


class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50

    def rect(self):
        return (self.x, self.y, self.width, self.height)


class GameLogic:
    def __init__(self):
        self.hero = Hero(100, 100)
        self.enemies = []
        self.bullets = []
        self.walls = []
        self.portals = []
        self.shoot_timer = 0
        self.screen_width = 1200
        self.screen_height = 684
        self.generate_room()

    def generate_room(self):
        self.enemies = []
        self.bullets = []
        self.walls = []
        self.portals = []

        self.add_wall(0, 0, 1200, 50)  
        self.add_wall(0, 0, 50, 684)  
        self.add_wall(1150, 0, 50, 684)
        self.add_wall(0, 634, 1200, 50)

        self.spawn_enemy(300, 300, distant=False)
        self.spawn_enemy(500, 300, distant=True)
        self.spawn_random_portals()

        self.hero.x = 100
        self.hero.y = 100
        self.hero.health = 100
        self.hero.alive = True

    def spawn_random_portals(self):
        if len(self.walls) < 4:
            return
        wall_indices = random.sample(range(len(self.walls)), 2)
        for wi in wall_indices:
            w = self.walls[wi]
            if w.width > w.height:
                px = random.randint(w.x + 50, w.x + w.width - 100)
                py = w.y + (w.height // 2) - 25
            else:
                px = w.x + (w.width // 2) - 25
                py = random.randint(w.y + 50, w.y + w.height - 100)
            self.spawn_portal(px, py)

    def add_wall(self, x, y, width, height):
        self.walls.append(Wall(x, y, width, height))

    def spawn_enemy(self, x, y, distant=False):
        self.enemies.append(Enemy(x, y, distant=distant))

    def spawn_portal(self, x, y):
        self.portals.append(Portal(x, y))

    def hero_shoot(self):
        if self.hero.can_shoot():
            self.bullets.append(Bullet(self.hero.x, self.hero.y, self.hero.direction, owner='hero'))

    def enemy_shoot(self, enemy):
        dx = self.hero.x - enemy.x
        dy = self.hero.y - enemy.y
        if abs(dx) > abs(dy):
            direction = 'right' if dx > 0 else 'left'
        else:
            direction = 'down' if dy > 0 else 'up'
        self.bullets.append(Bullet(enemy.x, enemy.y, direction, owner='enemy'))

    def update(self, input_state):
        if not self.hero.alive:
            return

        self.hero.move(input_state, self.walls)
        self.hero.update_timer()

        for bullet in self.bullets:
            bullet.update()

        self.bullets = [b for b in self.bullets if 0 <= b.x <= self.screen_width and 0 <= b.y <= self.screen_height]

        for enemy in self.enemies:
            enemy.update(self.hero.x, self.hero.y)
            # Ближний бой
            if not enemy.distant and abs(enemy.x - self.hero.x) < 50 and abs(enemy.y - self.hero.y) < 50:
                enemy.attack(self.hero)
            # Дальний бой
            if enemy.distant and enemy.distance_to_hero(self.hero.x, self.hero.y) < enemy.shoot_range:
                if enemy.attack_cooldown == 0:
                    self.enemy_shoot(enemy)
                    enemy.attack_cooldown = enemy.shoot_delay

        self.check_bullet_collisions()
        self.enemies = [e for e in self.enemies if e.alive]
        self.check_portal_collision()

    def check_portal_collision(self):
        # Предположим герой 64x64
        hero_rect = (self.hero.x, self.hero.y, 64, 64)

        for p in self.portals:
            p_rect = (p.x, p.y, p.width, p.height)
            if self.rects_collide(hero_rect, p_rect):
                self.generate_room()
                break



    def check_bullet_collisions(self):
        def collide(r1, r2):
            x1, y1, w1, h1 = r1
            x2, y2, w2, h2 = r2
            return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

        new_bullets = []
        for b in self.bullets:
            b_rect = b.rect()
            if b.owner == 'hero':
                hit_enemy = False
                for e in self.enemies:
                    e_rect = (e.x, e.y, 50, 50)
                    if collide(b_rect, e_rect):
                        e.health -= 25
                        if e.health <= 0:
                            e.alive = False
                        hit_enemy = True
                        break
                if not hit_enemy:
                    new_bullets.append(b)
            else:
                hero_rect = (self.hero.x, self.hero.y, 50, 50)
                if collide(b_rect, hero_rect):
                    self.hero.health -= 20
                    if self.hero.health <= 0:
                        self.hero.alive = False
                else:
                    new_bullets.append(b)

        self.bullets = new_bullets

    def rects_collide(self, r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

    def get_game_state(self):
        return {
            "hero": {
                "x": self.hero.x,
                "y": self.hero.y,
                "direction": self.hero.direction,
                "health": self.hero.health,
                "alive": self.hero.alive,
                "moving": self.hero.is_moving
            },
            "bullets": [{"x": b.x, "y": b.y} for b in self.bullets],
            "enemies": [{"x": e.x, "y": e.y, "health": e.health, "type": "demon" if e.distant else "goblin"} for e in self.enemies],
            "walls": [{"x": w.x, "y": w.y, "width": w.width, "height": w.height} for w in self.walls],
            "portals": [{"x": p.x, "y": p.y, "width": p.width, "height": p.height} for p in self.portals]
        }
