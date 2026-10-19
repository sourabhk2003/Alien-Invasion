import sys
import json

import pygame
from alien import Alien
from bullet import Bullet


# Mouse controls for PC
_mouse_pointer_down = False
_last_mouse_x = 0

# Touch controls for phones
_touch_positions = {}


def move_ship_by(ship, screen, delta_x):
    """Move the ship horizontally and keep it inside the screen."""
    if hasattr(ship, "center"):
        half_width = ship.rect.width / 2
        ship.center += delta_x
        ship.center = max(
            half_width,
            min(ship.center, screen.get_width() - half_width),
        )
        ship.rect.centerx = round(ship.center)

    elif hasattr(ship, "x"):
        ship.x += delta_x
        ship.x = max(
            0,
            min(ship.x, screen.get_width() - ship.rect.width),
        )
        ship.rect.x = round(ship.x)

    else:
        ship.rect.centerx += delta_x
        ship.rect.clamp_ip(screen.get_rect())


def handle_mouse_controls(event, ai_settings, screen, ship, bullets):
    """On PC, click to fire and drag horizontally to move the ship."""
    global _mouse_pointer_down, _last_mouse_x

    # Ignore mouse events generated from a touchscreen.
    # The phone controls are handled by FINGER events below.
    if getattr(event, "touch", False):
        return

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        _mouse_pointer_down = True
        _last_mouse_x = event.pos[0]
        fire_bullet(ai_settings, screen, ship, bullets)

    elif event.type == pygame.MOUSEMOTION and _mouse_pointer_down:
        current_x = event.pos[0]
        move_ship_by(ship, screen, current_x - _last_mouse_x)
        _last_mouse_x = current_x

    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        _mouse_pointer_down = False


def handle_finger(event, ai_settings, screen, ship, bullets):
    """On phones, tap to fire and drag horizontally to move the ship."""
    finger_id = event.finger_id
    current_x = int(event.x * screen.get_width())

    if event.type == pygame.FINGERDOWN:
        _touch_positions[finger_id] = current_x
        fire_bullet(ai_settings, screen, ship, bullets)

    elif event.type == pygame.FINGERMOTION:
        if finger_id in _touch_positions:
            previous_x = _touch_positions[finger_id]
            move_ship_by(ship, screen, current_x - previous_x)
            _touch_positions[finger_id] = current_x

    elif event.type == pygame.FINGERUP:
        _touch_positions.pop(finger_id, None)


def check_keydown_events(event, ai_settings, screen, stats, ship, aliens, bullets):
    """Respond to keyboard presses."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True

    elif event.key == pygame.K_LEFT:
        ship.moving_left = True

    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)

    elif event.key == pygame.K_q:
        with open("high_score.json", "w") as f:
            json.dump(stats.high_score, f)
        sys.exit()

    elif event.key == pygame.K_p and not stats.game_active:
        start_game(ai_settings, screen, stats, ship, aliens, bullets)


def check_keyup_events(event, ship):
    """Respond to keyboard releases."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False

    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet if the bullet limit has not been reached."""
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    """Respond to keyboard, mouse, touch, and quit events."""
    global _mouse_pointer_down

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open("high_score.json", "w") as f:
                json.dump(stats.high_score, f)
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(
                event, ai_settings, screen, stats, ship, aliens, bullets
            )

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            was_playing = stats.game_active

            if not getattr(event, "touch", False):
                mouse_x, mouse_y = event.pos

                check_play_button(
                    ai_settings,
                    screen,
                    stats,
                    sb,
                    play_button,
                    ship,
                    aliens,
                    bullets,
                    mouse_x,
                    mouse_y,
                )

                # Clicking Play starts the game without firing.
                if was_playing:
                    handle_mouse_controls(
                        event, ai_settings, screen, ship, bullets
                    )
            else:
                # Touch-generated mouse event; finger input is handled below.
                _mouse_pointer_down = False

        elif event.type == pygame.MOUSEMOTION:
            handle_mouse_controls(
                event, ai_settings, screen, ship, bullets
            )

        elif event.type == pygame.MOUSEBUTTONUP:
            handle_mouse_controls(
                event, ai_settings, screen, ship, bullets
            )

        elif event.type == pygame.FINGERDOWN:
            x = int(event.x * screen.get_width())
            y = int(event.y * screen.get_height())

            if not stats.game_active:
                check_play_button(
                    ai_settings,
                    screen,
                    stats,
                    sb,
                    play_button,
                    ship,
                    aliens,
                    bullets,
                    x,
                    y,
                )
            else:
                handle_finger(
                    event, ai_settings, screen, ship, bullets
                )

        elif event.type in (pygame.FINGERMOTION, pygame.FINGERUP):
            handle_finger(
                event, ai_settings, screen, ship, bullets
            )


def check_play_button(
    ai_settings,
    screen,
    stats,
    sb,
    play_button,
    ship,
    aliens,
    bullets,
    mouse_x,
    mouse_y,
):
    """Start a new game when the Play button is clicked or tapped."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)

    if button_clicked and not stats.game_active:
        pygame.mouse.set_visible(False)
        ai_settings.initialize_dynamic_settings()
        stats.reset_stats()
        stats.game_active = True

        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        aliens.empty()
        bullets.empty()

        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def start_game(ai_settings, screen, stats, ship, aliens, bullets):
    """Start a new game from the keyboard."""
    pygame.mouse.set_visible(False)
    stats.reset_stats()
    stats.game_active = True

    aliens.empty()
    bullets.empty()

    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()


def update_screen(
    ai_settings,
    screen,
    stats,
    sb,
    ship,
    aliens,
    bullets,
    play_button,
):
    """Update the display."""
    screen.fill(ai_settings.bg_color)

    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme()
    aliens.draw(screen)

    sb.show_score()

    if not stats.game_active:
        play_button.draw_button()

    pygame.display.flip()


def get_number_alien_x(ai_settings, alien_width):
    """Determine the number of aliens that fit in one row."""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    return available_space_x // (2 * alien_width)


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create and position one alien."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width

    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number

    aliens.add(alien)


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Update bullet positions and remove off-screen bullets."""
    bullets.update()

    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(
        ai_settings, screen, stats, sb, ship, aliens, bullets
    )


def check_bullet_alien_collisions(
    ai_settings, screen, stats, sb, ship, aliens, bullets
):
    """Remove bullets and aliens that collide."""
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for hit_aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(hit_aliens)
            sb.prep_score()

        check_high_score(stats, sb)

        if len(aliens) == 0:
            bullets.empty()
            ai_settings.increase_speed()

            stats.level += 1
            sb.prep_level()

            create_fleet(ai_settings, screen, ship, aliens)


def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens."""
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_alien_x(
        ai_settings, alien.rect.width
    )
    number_rows = get_number_rows(
        ai_settings, ship.rect.height, alien.rect.height
    )

    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(
                ai_settings,
                screen,
                aliens,
                alien_number,
                row_number,
            )


def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of alien rows that fit on the screen."""
    available_space_y = (
        ai_settings.screen_height - (3 * alien_height) - ship_height
    )
    return available_space_y // (2 * alien_height)


def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Respond when an alien hits the ship."""
    if stats.ships_left > 1:
        stats.ships_left -= 1
        sb.prep_ships()

        aliens.empty()
        bullets.empty()

        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Update alien positions and check collisions."""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)

    check_aliens_bottom(
        ai_settings, screen, stats, sb, ship, aliens, bullets
    )


def check_fleet_edges(ai_settings, aliens):
    """Change direction if an alien reaches a screen edge."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Drop the fleet and reverse its direction."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed

    ai_settings.fleet_direction *= -1


def check_aliens_bottom(
    ai_settings, screen, stats, sb, ship, aliens, bullets
):
    """Treat an alien reaching the bottom as a ship hit."""
    screen_rect = screen.get_rect()

    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(
                ai_settings, screen, stats, sb, ship, aliens, bullets
            )
            break


def check_high_score(stats, sb):
    """Check to see if there's a new high score."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()