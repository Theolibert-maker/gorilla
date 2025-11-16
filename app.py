#!/usr/bin/env python3
"""Gorilla 2025 - QBasic Gorillas revisité en pygame."""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pygame
import pygame_gui

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
GRAVITY = 260.0  # px/s^2
DRAG_COEFF = 0.55
EXPLOSION_RADIUS = 38
MAX_WIND = 140.0
SCORES_PATH = Path(__file__).with_name("scores.json")

SKY_TOP = (6, 11, 38)
SKY_BOTTOM = (38, 77, 145)
CITY_LIGHT = (229, 199, 126)


@dataclass
class Gorilla:
    """Représente un gorille posé sur un immeuble."""

    rect: pygame.Rect
    color: Tuple[int, int, int]
    direction: int  # +1 vers la droite, -1 vers la gauche

    def draw(self, surface: pygame.Surface) -> None:
        body_rect = pygame.Rect(self.rect.x, self.rect.y + 10, self.rect.width, self.rect.height - 10)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=8)
        head_center = (self.rect.centerx, self.rect.y + 8)
        pygame.draw.circle(surface, (255, 220, 193), head_center, self.rect.width // 3)
        eye_offset = 6
        eye_radius = 3
        pygame.draw.circle(surface, (0, 0, 0), (head_center[0] - eye_offset, head_center[1] - 2), eye_radius)
        pygame.draw.circle(surface, (0, 0, 0), (head_center[0] + eye_offset, head_center[1] - 2), eye_radius)
        arm_y = self.rect.y + 18
        arm_length = 14
        pygame.draw.line(
            surface,
            (40, 28, 25),
            (self.rect.centerx, arm_y),
            (self.rect.centerx + self.direction * arm_length, arm_y - 4),
            4,
        )

    def throw_position(self) -> pygame.Vector2:
        x = self.rect.centerx + self.direction * (self.rect.width // 2 + 6)
        y = self.rect.y + 12
        return pygame.Vector2(x, y)


class Projectile:
    """Une banane explosive."""

    def __init__(self, start_pos: pygame.Vector2, speed: float, angle_deg: float, wind_speed: float):
        self.pos = start_pos.copy()
        radians = math.radians(angle_deg)
        self.vel = pygame.Vector2(math.cos(radians) * speed, -math.sin(radians) * speed)
        self.wind_speed = wind_speed
        self.trail: List[pygame.Vector2] = []

    def update(self, dt: float) -> None:
        rel_vx = self.vel.x - self.wind_speed
        ax = -DRAG_COEFF * rel_vx
        ay = GRAVITY - DRAG_COEFF * self.vel.y
        self.vel.x += ax * dt
        self.vel.y += ay * dt
        self.pos += self.vel * dt
        self.trail.append(self.pos.copy())
        if len(self.trail) > 120:
            self.trail.pop(0)

    def draw(self, surface: pygame.Surface) -> None:
        for idx, point in enumerate(self.trail):
            alpha = int(255 * (idx / len(self.trail))) if self.trail else 0
            color = (
                255,
                max(0, min(255, 230 - alpha // 2)),
                max(0, min(255, 80 - alpha // 3)),
            )
            pygame.draw.circle(surface, color, (int(point.x), int(point.y)), 3)
        pygame.draw.circle(surface, (255, 248, 150), (int(self.pos.x), int(self.pos.y)), 6)


class Skyline:
    """Ville générée procéduralement, gère les collisions et les explosions."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.buildings: List[pygame.Rect] = []

    def generate(self) -> None:
        self.surface.fill((0, 0, 0, 0))
        self.buildings.clear()
        x = 0
        while x < self.width:
            building_width = random.randint(55, 110)
            if x + building_width > self.width:
                building_width = self.width - x
            height = random.randint(120, 360)
            rect = pygame.Rect(x, self.height - height, building_width, height)
            self.buildings.append(rect)
            base_color = pygame.Color(random.randint(60, 140), random.randint(40, 110), random.randint(90, 160))
            pygame.draw.rect(self.surface, base_color, rect, border_radius=4)
            window_color = pygame.Color(*CITY_LIGHT, 230)
            for win_y in range(rect.y + 10, rect.bottom - 10, 20):
                for win_x in range(rect.x + 8, rect.right - 8, 16):
                    if random.random() < 0.6:
                        pygame.draw.rect(self.surface, window_color, pygame.Rect(win_x, win_y, 8, 12), border_radius=2)
            x += building_width

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, (0, 0))

    def carve_explosion(self, center: Tuple[int, int], radius: int) -> None:
        pygame.draw.circle(self.surface, (0, 0, 0, 0), center, radius)

    def collides(self, point: Tuple[int, int]) -> bool:
        if not (0 <= point[0] < self.width and 0 <= point[1] < self.height):
            return False
        return self.surface.get_at(point).a > 10


class GorillaGame:
    """Gestionnaire de la partie complète."""

    def __init__(self, screen: pygame.Surface, manager: pygame_gui.UIManager):
        self.screen = screen
        self.manager = manager
        self.clock = pygame.time.Clock()
        self.sky_surface = self._build_sky()
        self.skyline = Skyline(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.projectile: Projectile | None = None
        self.current_player = 0
        self.wind_speed = 0.0
        self.round_wins = [0, 0]
        self.current_round = 1
        self.match_over = False
        self.gorillas: List[Gorilla] = []
        self.status_message = ""
        self._build_ui()
        self.start_match()

    # UI -----------------------------------------------------------------
    def _build_ui(self) -> None:
        self.names_panel = pygame_gui.elements.UIPanel(
            pygame.Rect(20, 15, 360, 90),
            manager=self.manager,
        )
        pygame_gui.elements.UILabel(
            pygame.Rect(10, 5, 150, 20),
            text="Pseudo Joueur 1",
            manager=self.manager,
            container=self.names_panel,
        )
        self.name_inputs = [
            pygame_gui.elements.UITextEntryLine(
                pygame.Rect(10, 30, 150, 25),
                manager=self.manager,
                container=self.names_panel,
            ),
            pygame_gui.elements.UITextEntryLine(
                pygame.Rect(190, 30, 150, 25),
                manager=self.manager,
                container=self.names_panel,
            ),
        ]
        self.name_inputs[0].set_text("Gorille A")
        self.name_inputs[1].set_text("Gorille B")
        pygame_gui.elements.UILabel(
            pygame.Rect(190, 5, 150, 20),
            text="Pseudo Joueur 2",
            manager=self.manager,
            container=self.names_panel,
        )

        control_rect = pygame.Rect(20, SCREEN_HEIGHT - 130, SCREEN_WIDTH - 40, 110)
        self.control_panel = pygame_gui.elements.UIPanel(control_rect, manager=self.manager)
        pygame_gui.elements.UILabel(
            pygame.Rect(10, 10, 120, 25),
            text="Angle (°)",
            manager=self.manager,
            container=self.control_panel,
        )
        self.angle_input = pygame_gui.elements.UITextEntryLine(
            pygame.Rect(10, 40, 120, 28), manager=self.manager, container=self.control_panel
        )
        self.angle_input.set_text("45")
        pygame_gui.elements.UILabel(
            pygame.Rect(150, 10, 140, 25),
            text="Vitesse (px/s)",
            manager=self.manager,
            container=self.control_panel,
        )
        self.speed_input = pygame_gui.elements.UITextEntryLine(
            pygame.Rect(150, 40, 140, 28), manager=self.manager, container=self.control_panel
        )
        self.speed_input.set_text("320")
        self.fire_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(310, 30, 120, 40),
            text="Lancer",
            manager=self.manager,
            container=self.control_panel,
        )
        self.status_label = pygame_gui.elements.UILabel(
            pygame.Rect(450, 10, control_rect.width - 470, 60),
            text="",
            manager=self.manager,
            container=self.control_panel,
        )

    # Match / rounds -----------------------------------------------------
    def start_match(self) -> None:
        self.round_wins = [0, 0]
        self.current_round = 1
        self.match_over = False
        self.start_round()

    def start_round(self) -> None:
        self.skyline.generate()
        self.gorillas = self._place_gorillas()
        self.wind_speed = random.uniform(-MAX_WIND, MAX_WIND)
        self.projectile = None
        # alter starting player each round
        self.current_player = 0 if self.current_round % 2 == 1 else 1
        self.update_status(f"Round {self.current_round} - {self.current_player_name()} commence !")

    def update_status(self, text: str) -> None:
        self.status_message = text
        self.status_label.set_text(text)

    def player_name(self, index: int) -> str:
        name = self.name_inputs[index].get_text().strip()
        if name:
            return name
        return "Gorille A" if index == 0 else "Gorille B"

    def current_player_name(self) -> str:
        return self.player_name(self.current_player)

    def _place_gorillas(self) -> List[Gorilla]:
        gorillas: List[Gorilla] = []
        left_candidates = [b for b in self.skyline.buildings if b.centerx < SCREEN_WIDTH * 0.45]
        right_candidates = [b for b in self.skyline.buildings if b.centerx > SCREEN_WIDTH * 0.55]
        if not left_candidates:
            left_candidates = self.skyline.buildings[: len(self.skyline.buildings) // 2]
        if not right_candidates:
            right_candidates = self.skyline.buildings[len(self.skyline.buildings) // 2 :]
        gorilla_size = pygame.Rect(0, 0, 42, 48)
        left_building = random.choice(left_candidates)
        gorilla_size.midbottom = (left_building.centerx, left_building.top + 2)
        gorillas.append(Gorilla(gorilla_size.copy(), (143, 98, 72), 1))
        right_building = random.choice(right_candidates)
        gorilla_size.midbottom = (right_building.centerx, right_building.top + 2)
        gorillas.append(Gorilla(gorilla_size.copy(), (91, 60, 111), -1))
        return gorillas

    # Game loop ---------------------------------------------------------
    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.start_match()
                if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.fire_button:
                        self.handle_fire()
                self.manager.process_events(event)
            self.manager.update(dt)
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_fire(self) -> None:
        if self.projectile or self.match_over:
            return
        try:
            angle = float(self.angle_input.get_text())
            speed = float(self.speed_input.get_text())
        except ValueError:
            self.update_status("Angle ou vitesse invalide.")
            return
        if not (0 < angle < 180) or speed <= 0:
            self.update_status("Entrez un angle entre 0 et 180° et une vitesse positive.")
            return
        speed = max(60.0, min(speed, 600.0))
        if self.current_player == 1:
            angle = 180 - angle
        start_pos = self.gorillas[self.current_player].throw_position()
        self.projectile = Projectile(start_pos, speed, angle, self.wind_speed)
        self.update_status(f"{self.current_player_name()} a lancé une banane !")

    def update(self, dt: float) -> None:
        if self.projectile:
            self.projectile.update(dt)
            px, py = int(self.projectile.pos.x), int(self.projectile.pos.y)
            if px < 0 or px >= SCREEN_WIDTH or py >= SCREEN_HEIGHT:
                self.projectile = None
                self.switch_turn("La banane est tombée...")
                return
            if py < 0:
                # continue en dehors de l'écran haut
                pass
            elif self.skyline.collides((px, py)):
                self.skyline.carve_explosion((px, py), EXPLOSION_RADIUS)
                self.projectile = None
                self.switch_turn(f"{self.current_player_name()} a touché un immeuble !")
                return
            for idx, gorilla in enumerate(self.gorillas):
                if gorilla.rect.collidepoint(px, py):
                    self.projectile = None
                    loser = idx
                    winner = self.current_player if idx != self.current_player else 1 - self.current_player
                    self.resolve_hit(winner, loser)
                    return

    def switch_turn(self, message: str) -> None:
        if self.match_over:
            return
        self.current_player = 1 - self.current_player
        self.update_status(f"{message}\nÀ {self.current_player_name()} de jouer.")

    def resolve_hit(self, winner: int, loser: int) -> None:
        self.round_wins[winner] += 1
        winner_name = self.player_name(winner)
        loser_name = self.player_name(loser)
        self.update_status(f"{winner_name} touche {loser_name} !")
        if self.round_wins[winner] >= 2:
            self.match_over = True
            self.projectile = None
            self.save_score(winner_name, loser_name)
            self.update_status(f"{winner_name} remporte la partie !\nAppuyez sur R pour rejouer.")
        else:
            self.current_round += 1
            self.start_round()

    def save_score(self, winner: str, loser: str) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "winner": winner,
            "loser": loser,
            "rounds": {"player_1": self.round_wins[0], "player_2": self.round_wins[1]},
            "wind": round(self.wind_speed, 2),
        }
        data = []
        if SCORES_PATH.exists():
            try:
                data = json.loads(SCORES_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = []
        data.append(entry)
        SCORES_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def draw(self) -> None:
        self.screen.blit(self.sky_surface, (0, 0))
        self.skyline.draw(self.screen)
        for gorilla in self.gorillas:
            gorilla.draw(self.screen)
        if self.projectile:
            self.projectile.draw(self.screen)
        self._draw_hud()
        self.manager.draw_ui(self.screen)
        pygame.display.flip()

    def _draw_hud(self) -> None:
        font = pygame.font.SysFont("arial", 20)
        big_font = pygame.font.SysFont("arial", 28, bold=True)
        score_text = f"{self.player_name(0)} {self.round_wins[0]} - {self.round_wins[1]} {self.player_name(1)}"
        score_surface = big_font.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (SCREEN_WIDTH // 2 - score_surface.get_width() // 2, 20))
        wind_text = f"Vent: {int(self.wind_speed)} px/s"
        wind_surface = font.render(wind_text, True, (240, 240, 240))
        self.screen.blit(wind_surface, (SCREEN_WIDTH - 220, 25))
        arrow_length = 70
        arrow_center = (SCREEN_WIDTH - 120, 60)
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (arrow_center[0] - arrow_length // 2, arrow_center[1]),
            (arrow_center[0] + arrow_length // 2, arrow_center[1]),
            2,
        )
        direction = 1 if self.wind_speed >= 0 else -1
        arrow_tip = (
            arrow_center[0] + direction * arrow_length // 2,
            arrow_center[1],
        )
        pygame.draw.polygon(
            self.screen,
            (255, 215, 0),
            [
                arrow_tip,
                (arrow_tip[0] - 10 * direction, arrow_tip[1] - 6),
                (arrow_tip[0] - 10 * direction, arrow_tip[1] + 6),
            ],
        )
        hint_text = font.render("Terminez 2 rounds pour gagner. R pour recommencer.", True, (220, 220, 220))
        self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 20, SCREEN_HEIGHT - 160))

    @staticmethod
    def _build_sky() -> pygame.Surface:
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (
                int(SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio),
                int(SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio),
                int(SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio),
            )
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        for star in range(120):
            x = random.randint(0, SCREEN_WIDTH - 1)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 1)
        return surface


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Gorilla 2025")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = GorillaGame(screen, manager)
    game.run()


if __name__ == "__main__":
    main()