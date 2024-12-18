import sys
from logic import GameLogic
from frontend import Frontend
import pygame

def main():
    screen_width = 1200
    screen_height = 684

    front = Frontend(screen_width, screen_height)
    game = GameLogic()

    running = True
    while running:
        input_state, quit_game = front.get_user_input()
        if quit_game:
            running = False
            break

        if input_state.get("shoot", False):
            game.shoot_timer += 1
            if game.shoot_timer >= 5:
                game.shoot_timer = 0
                game.hero_shoot()
        else:
            game.shoot_timer = 5

        game.update(input_state)

        gs = game.get_game_state()

        front.draw(gs["hero"], gs["enemies"], gs["bullets"], gs["walls"], gs["portals"])

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
