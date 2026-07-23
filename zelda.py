#!/usr/bin/env python3
"""
AC's Meow Cap Adventure 1.0
================================
A single-file, complete original GBA-style top-down action-adventure for Python 3.14
and pygame-ce. It runs on a 240x160 internal canvas at 60 FPS and scales with
nearest-neighbour filtering.

This is an original tribute, not a copy or ROM of The Legend of Zelda: The
Minish Cap. No Nintendo maps, music, dialogue, code, or graphics are included.

Embedded art: "Tiny Dungeon" by Kenney, CC0 1.0.
Source: https://kenney.nl/assets/tiny-dungeon
The selected PNG sprites are stored inside this file as a tiny ZIP archive and
are loaded directly from memory; no asset folder is created.

Install:
    py -3.14 -m pip install pygame-ce

Run:
    py -3.14 zelda.py

Controls:
    Arrow keys / WASD  Move
    Z / J / Space      Sword
    X / K              Hold shield
    Shift / C          Roll
    E / Enter          Talk, open, use, enter
    Esc                 Pause
    F11                 Fullscreen
"""

from __future__ import annotations

import base64
import io
import math
import os
import random
import sys
import zipfile
from array import array
from dataclasses import dataclass


SMOKE_TEST = "--smoke-test" in sys.argv
if SMOKE_TEST:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame
except ImportError as exc:
    raise SystemExit(
        "pygame-ce is required.\n"
        "Install it with:  py -3.14 -m pip install pygame-ce"
    ) from exc


INTERNAL_W, INTERNAL_H = 240, 160
WINDOW_SCALE = 4
FPS = 60
TILE = 16
TITLE = "AC's Meow Cap Adventure 1.0 — Famicom 60 FPS"
FONT_ENGINE_NAME = "meowfont0.1gba"
SPEED_PROFILE = "FAMICOM"

# Selected 16x16 CC0 sprites from Kenney's Tiny Dungeon pack. Keeping the
# archive in memory is what makes this a true single-file game.


ASSET_ZIP_V2_B64 = (
    "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"
)


COLORS = {
    "ink": (21, 24, 35),
    "cream": (255, 244, 193),
    "gold": (255, 205, 58),
    "red": (224, 62, 57),
    "green": (56, 171, 74),
    "deep_green": (28, 91, 57),
    "grass": (99, 188, 84),
    "grass2": (83, 170, 72),
    "path": (214, 173, 105),
    "water": (48, 135, 196),
    "stone": (83, 91, 121),
    "stone2": (55, 61, 86),
    "purple": (119, 70, 154),
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def sign(value: float) -> int:
    return (value > 0) - (value < 0)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def load_assets() -> dict[int, pygame.Surface]:
    """Decode the embedded CC0 PNG archive without touching the filesystem."""
    packed = base64.b64decode(ASSET_ZIP_V2_B64)
    assets: dict[int, pygame.Surface] = {}
    with zipfile.ZipFile(io.BytesIO(packed)) as archive:
        for name in archive.namelist():
            if not name.endswith(".png"):
                continue
            tile_id = int(name[5:9])
            assets[tile_id] = pygame.image.load(
                io.BytesIO(archive.read(name)), name
            ).convert_alpha()
    return assets


# Hand-authored 5x7 bitmap glyphs. These never pass through a TrueType
# rasterizer, so each source pixel remains a perfect square at every scale.
PIXEL_GLYPHS: dict[str, tuple[int, ...]] = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (15, 16, 16, 16, 16, 16, 15),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (15, 16, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 18, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (30, 1, 1, 14, 1, 1, 30),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 16, 30, 1, 1, 30),
    "6": (14, 16, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 1, 14),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 2, 4, 0, 4),
    ".": (0, 0, 0, 0, 0, 0, 4),
    ",": (0, 0, 0, 0, 0, 4, 8),
    ":": (0, 4, 4, 0, 4, 4, 0),
    ";": (0, 4, 4, 0, 4, 4, 8),
    "'": (4, 4, 2, 0, 0, 0, 0),
    '"': (10, 10, 5, 0, 0, 0, 0),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "_": (0, 0, 0, 0, 0, 0, 31),
    "/": (1, 1, 2, 4, 8, 16, 16),
    "\\": (16, 16, 8, 4, 2, 1, 1),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "[": (14, 8, 8, 8, 8, 8, 14),
    "]": (14, 2, 2, 2, 2, 2, 14),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "$": (4, 15, 20, 14, 5, 30, 4),
    "#": (10, 31, 10, 10, 31, 10, 0),
    "%": (25, 25, 2, 4, 8, 19, 19),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "*": (0, 21, 14, 31, 14, 21, 0),
    "<": (2, 4, 8, 16, 8, 4, 2),
    ">": (8, 4, 2, 1, 2, 4, 8),
    "|": (4, 4, 4, 4, 4, 4, 4),
    "•": (0, 0, 0, 4, 0, 0, 0),
}


class MeowFont01GBA:
    """Minimal pygame Font-compatible bitmap renderer."""

    def __init__(self, scale: int = 1, tracking: int = 1) -> None:
        self.scale = scale
        self.tracking = tracking
        self.height = 7 * scale

    def size(self, text: str) -> tuple[int, int]:
        text = str(text)
        if not text:
            return (0, self.height)
        width = len(text) * (5 * self.scale + self.tracking) - self.tracking
        return (width, self.height)

    def render(
        self,
        text: str,
        antialias: bool,
        color: tuple[int, int, int],
        background: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        del antialias
        text = str(text).upper()
        width, height = self.size(text)
        surface = pygame.Surface((max(1, width), height), pygame.SRCALPHA)
        if background is not None:
            surface.fill(background)
        cursor = 0
        for character in text:
            rows = PIXEL_GLYPHS.get(character, PIXEL_GLYPHS["?"])
            for row_index, bits in enumerate(rows):
                for column in range(5):
                    if bits & (1 << (4 - column)):
                        pygame.draw.rect(
                            surface,
                            color,
                            (
                                cursor + column * self.scale,
                                row_index * self.scale,
                                self.scale,
                                self.scale,
                            ),
                        )
            cursor += 5 * self.scale + self.tracking
        return surface


def make_tone(
    notes: list[tuple[float, float]], volume: float = 0.18, wave: str = "square"
) -> pygame.mixer.Sound | None:
    """Create a tiny original chiptune sound with no audio dependency."""
    if not pygame.mixer.get_init():
        return None
    sample_rate = 22050
    samples = array("h")
    phase = 0.0
    for frequency, duration in notes:
        count = max(1, int(sample_rate * duration))
        for index in range(count):
            if frequency <= 0:
                value = 0.0
            else:
                phase += frequency / sample_rate
                phase %= 1.0
                if wave == "triangle":
                    value = 1.0 - 4.0 * abs(phase - 0.5)
                else:
                    value = 1.0 if phase < 0.5 else -1.0
                fade = min(1.0, (count - index) / max(1, sample_rate * 0.015))
                value *= fade
            sample = int(32767 * volume * value)
            samples.append(sample)
            samples.append(sample)
    return pygame.mixer.Sound(buffer=samples.tobytes())


class Audio:
    def __init__(self) -> None:
        self.enabled = bool(pygame.mixer.get_init())
        self.sounds: dict[str, pygame.mixer.Sound | None] = {}
        self.music: pygame.mixer.Sound | None = None
        if not self.enabled:
            return
        self.sounds = {
            "sword": make_tone([(520, 0.035), (760, 0.045)], 0.12),
            "hit": make_tone([(130, 0.05), (90, 0.06)], 0.16),
            "hurt": make_tone([(260, 0.08), (130, 0.12)], 0.14),
            "item": make_tone([(523, 0.06), (659, 0.06), (784, 0.11)], 0.13),
            "door": make_tone([(180, 0.06), (240, 0.08)], 0.10),
            "shrink": make_tone(
                [(880, 0.05), (660, 0.05), (440, 0.05), (330, 0.12)], 0.12
            ),
            "grow": make_tone(
                [(330, 0.05), (440, 0.05), (660, 0.05), (880, 0.12)], 0.12
            ),
            "roll": make_tone([(220, 0.04), (170, 0.05)], 0.08),
            "block": make_tone([(900, 0.025), (1100, 0.04)], 0.10),
            "win": make_tone(
                [(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.35)], 0.14
            ),
        }
        melody = [
            (392, 0.16), (523, 0.16), (587, 0.16), (659, 0.16),
            (587, 0.16), (523, 0.16), (440, 0.32), (0, 0.08),
            (349, 0.16), (440, 0.16), (523, 0.16), (587, 0.16),
            (523, 0.16), (440, 0.16), (392, 0.32), (0, 0.08),
            (330, 0.16), (392, 0.16), (440, 0.16), (523, 0.16),
            (587, 0.32), (523, 0.16), (440, 0.16),
            (392, 0.16), (349, 0.16), (330, 0.16), (294, 0.16),
            (330, 0.16), (392, 0.16), (440, 0.32), (0, 0.16),
        ]
        self.music = make_tone(melody, 0.035, "triangle")

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def start_music(self) -> None:
        if self.music:
            self.music.play(loops=-1, fade_ms=500)


@dataclass
class Door:
    tile_x: int
    tile_y: int
    target: str
    spawn: tuple[float, float]
    requirement: str = ""
    label: str = "Enter"

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.tile_x * TILE, self.tile_y * TILE, TILE, TILE)


@dataclass
class NPC:
    x: float
    y: float
    sprite: int
    name: str

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x) + 3, round(self.y) + 5, 10, 11)


class Room:
    def __init__(
        self,
        name: str,
        title: str,
        theme: str,
        tilemap: list[str],
        doors: list[Door],
        enemy_specs: list[tuple[str, float, float]] | None = None,
        npcs: list[NPC] | None = None,
    ) -> None:
        if len(tilemap) != 10 or any(len(row) != 15 for row in tilemap):
            raise ValueError(f"{name}: room maps must be exactly 15x10 tiles")
        self.name = name
        self.title = title
        self.theme = theme
        self.tilemap = tilemap
        self.doors = doors
        self.npcs = npcs or []
        self.enemies = [
            Enemy(kind, x, y, name == "forest") for kind, x, y in (enemy_specs or [])
        ]
        self.pickups: list[Pickup] = []
        self.chest_open = False

    def tile_at_pixel(self, x: float, y: float) -> str:
        tx, ty = int(x // TILE), int(y // TILE)
        if tx < 0 or ty < 0 or tx >= 15 or ty >= 10:
            return "#"
        return self.tilemap[ty][tx]

    def collides(self, rect: pygame.Rect) -> bool:
        solid = {"T", "R", "B", "#", "~", "D"}
        left = max(0, rect.left // TILE)
        right = min(14, (rect.right - 1) // TILE)
        top = max(0, rect.top // TILE)
        bottom = min(9, (rect.bottom - 1) // TILE)
        if rect.left < 0 or rect.top < 0 or rect.right > INTERNAL_W or rect.bottom > INTERNAL_H:
            return True
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if self.tilemap[ty][tx] in solid:
                    return True
        return False


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y
        self.direction = "down"
        self.tiny = False
        self.health = 6
        self.max_health = 6
        self.invulnerable = 0.0
        self.attack_timer = 0.0
        self.attack_cooldown = 0.0
        self.roll_timer = 0.0
        self.roll_cooldown = 0.0
        self.shielding = False
        self.walk_time = 0.0
        self.attack_hits: set[int] = set()
        self.roll_vector = pygame.Vector2()

    @property
    def size(self) -> tuple[int, int]:
        return (6, 6) if self.tiny else (10, 11)

    @property
    def rect(self) -> pygame.Rect:
        width, height = self.size
        return pygame.Rect(
            round(self.x - width / 2),
            round(self.y - height / 2),
            width,
            height,
        )

    def start_attack(self, audio: Audio) -> None:
        if self.attack_cooldown <= 0 and self.roll_timer <= 0:
            self.attack_timer = 0.19
            self.attack_cooldown = 0.28
            self.attack_hits.clear()
            audio.play("sword")

    def start_roll(self, keys: pygame.key.ScancodeWrapper, audio: Audio) -> None:
        if self.roll_cooldown > 0 or self.attack_timer > 0 or self.tiny:
            return
        vector = pygame.Vector2(
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - int(keys[pygame.K_LEFT] or keys[pygame.K_a]),
            int(keys[pygame.K_DOWN] or keys[pygame.K_s])
            - int(keys[pygame.K_UP] or keys[pygame.K_w]),
        )
        if vector.length_squared() == 0:
            vector = {
                "up": pygame.Vector2(0, -1),
                "down": pygame.Vector2(0, 1),
                "left": pygame.Vector2(-1, 0),
                "right": pygame.Vector2(1, 0),
            }[self.direction]
        self.roll_vector = vector.normalize()
        self.roll_timer = 0.24
        self.roll_cooldown = 0.48
        audio.play("roll")

    def attack_rect(self) -> pygame.Rect:
        base = self.rect
        reach = 8 if self.tiny else 13
        thickness = 7 if self.tiny else 12
        if self.direction == "up":
            return pygame.Rect(base.centerx - thickness // 2, base.top - reach, thickness, reach + 4)
        if self.direction == "down":
            return pygame.Rect(base.centerx - thickness // 2, base.bottom - 4, thickness, reach + 4)
        if self.direction == "left":
            return pygame.Rect(base.left - reach, base.centery - thickness // 2, reach + 4, thickness)
        return pygame.Rect(base.right - 4, base.centery - thickness // 2, reach + 4, thickness)

    def hurt(self, amount: int, source: tuple[float, float], game: "Game") -> None:
        if self.invulnerable > 0 or self.roll_timer > 0:
            return
        if self.shielding and game.is_in_front(source):
            self.invulnerable = 0.12
            game.audio.play("block")
            game.add_burst(self.x, self.y, COLORS["cream"], 5)
            return
        self.health = max(0, self.health - amount)
        self.invulnerable = 1.05
        game.audio.play("hurt")
        game.shake = 5
        game.flash = 0.12
        game.add_burst(self.x, self.y, COLORS["red"], 8)

    def move_axis(self, room: Room, dx: float, dy: float) -> None:
        if dx:
            self.x += dx
            if room.collides(self.rect):
                self.x -= dx
        if dy:
            self.y += dy
            if room.collides(self.rect):
                self.y -= dy

    def update(self, dt: float, room: Room, keys: pygame.key.ScancodeWrapper) -> None:
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.roll_timer = max(0.0, self.roll_timer - dt)
        self.roll_cooldown = max(0.0, self.roll_cooldown - dt)
        self.shielding = bool(keys[pygame.K_x] or keys[pygame.K_k]) and self.roll_timer <= 0

        if self.roll_timer > 0:
            motion = self.roll_vector * 120 * dt
            self.move_axis(room, motion.x, motion.y)
            self.walk_time += dt * 14
            return
        if self.attack_timer > 0 or self.shielding:
            return

        direction = pygame.Vector2(
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - int(keys[pygame.K_LEFT] or keys[pygame.K_a]),
            int(keys[pygame.K_DOWN] or keys[pygame.K_s])
            - int(keys[pygame.K_UP] or keys[pygame.K_w]),
        )
        if direction.length_squared() == 0:
            return
        if abs(direction.x) > abs(direction.y):
            self.direction = "right" if direction.x > 0 else "left"
        else:
            self.direction = "down" if direction.y > 0 else "up"
        direction = direction.normalize()
        speed = 48 if self.tiny else 66
        motion = direction * speed * dt
        self.move_axis(room, motion.x, 0)
        self.move_axis(room, 0, motion.y)
        self.walk_time += dt * (12 if self.tiny else 9)


class Enemy:
    BOSS_KINDS = {"boss", "moon_boss", "final_boss"}
    SETTINGS = {
        "slime": (108, 2, 25, 1),
        "bat": (120, 1, 38, 1),
        "ghost": (121, 2, 28, 1),
        "knight": (123, 3, 24, 1),
        "boss": (110, 12, 20, 2),
        "moon_boss": (121, 16, 24, 2),
        "final_boss": (123, 24, 29, 2),
    }

    def __init__(self, kind: str, x: float, y: float, shard_drop: bool = False) -> None:
        sprite, health, speed, damage = self.SETTINGS[kind]
        self.kind = kind
        self.x, self.y = x, y
        self.sprite = sprite
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.shard_drop = shard_drop
        self.alive = True
        self.flash = 0.0
        self.stun = 0.0
        self.phase = random.random() * math.tau
        self.wander = pygame.Vector2(1, 0).rotate(random.randrange(360))
        self.wander_timer = random.uniform(0.5, 1.5)

    @property
    def rect(self) -> pygame.Rect:
        size = 18 if self.kind in self.BOSS_KINDS else 11
        return pygame.Rect(round(self.x - size / 2), round(self.y - size / 2), size, size)

    def take_damage(self, amount: int, source: tuple[float, float], game: "Game") -> None:
        if not self.alive or self.stun > 0:
            return
        self.health -= amount
        self.flash = 0.14
        self.stun = 0.20
        away = pygame.Vector2(self.x - source[0], self.y - source[1])
        if away.length_squared():
            away.scale_to_length(5)
            self.x += away.x
            self.y += away.y
        game.audio.play("hit")
        game.shake = 4 if self.kind in self.BOSS_KINDS else 2
        game.add_burst(self.x, self.y, COLORS["gold"], 5)
        if self.health <= 0:
            self.alive = False
            game.on_enemy_defeated(self)

    def update(self, dt: float, game: "Game", room: Room) -> None:
        if not self.alive:
            return
        self.flash = max(0.0, self.flash - dt)
        self.stun = max(0.0, self.stun - dt)
        self.phase += dt * (5 if self.kind == "bat" else 2)
        if self.stun > 0:
            return

        target = pygame.Vector2(game.player.x - self.x, game.player.y - self.y)
        near = target.length_squared() < (
            120 if self.kind in self.BOSS_KINDS else 84
        ) ** 2
        if near and target.length_squared():
            target = target.normalize()
            if self.kind == "bat":
                target.rotate_ip(math.sin(self.phase * 1.7) * 35)
            if self.kind in self.BOSS_KINDS and math.sin(self.phase) > 0.72:
                charge = 3.0 if self.kind == "final_boss" else 2.4
                target *= charge
            motion = target * self.speed * dt
        else:
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                self.wander = pygame.Vector2(1, 0).rotate(random.randrange(360))
                self.wander_timer = random.uniform(0.7, 1.8)
            motion = self.wander * self.speed * 0.45 * dt

        old_x, old_y = self.x, self.y
        self.x += motion.x
        if room.collides(self.rect):
            self.x = old_x
            self.wander.x *= -1
        self.y += motion.y
        if room.collides(self.rect):
            self.y = old_y
            self.wander.y *= -1

        if self.rect.colliderect(game.player.rect):
            game.player.hurt(self.damage, (self.x, self.y), game)


@dataclass
class Pickup:
    x: float
    y: float
    kind: str
    life: float = 12.0
    phase: float = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x) - 5, round(self.y) - 5, 10, 10)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    life: float
    size: int

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 25 * dt
        self.life -= dt


def build_rooms() -> dict[str, Room]:
    village = Room(
        "village",
        "Mossbell Village",
        "outdoor",
        [
            "TTTTTTTTTTTTTTT",
            "T.....===.....T",
            "T.....===.....T",
            "T..BBB===.TT..T",
            "T..B.B===.....T",
            "T..BBB===.....D",
            "T.....===.....T",
            "T..T..===..T..T",
            "T.....===.....T",
            "TTTTTTTTTTTTTTT",
        ],
        [Door(14, 5, "forest", (19, 88), label="Forest")],
        npcs=[NPC(105, 72, 87, "Elder Fern"), NPC(71, 119, 85, "Pip")],
    )
    forest = Room(
        "forest",
        "Whisperleaf Wood",
        "outdoor",
        [
            "TTTTTTTTTTTTTTT",
            "T..TT....TT...T",
            "T......R......T",
            "T.TTT.....TT..T",
            "T....R........T",
            "D............TT",
            "T....TT....S..T",
            "T......TT.....T",
            "T......TT...D.T",
            "TTTTTTTTTTTTTTT",
        ],
        [
            Door(0, 5, "village", (219, 88), label="Village"),
            Door(13, 8, "dungeon_entry", (120, 133), "tiny", "Tiny tunnel"),
        ],
        enemy_specs=[
            ("slime", 83, 46),
            ("bat", 174, 55),
            ("slime", 154, 116),
        ],
    )
    dungeon_entry = Room(
        "dungeon_entry",
        "Rootglass Burrow",
        "dungeon",
        [
            "#######D#######",
            "#.............#",
            "#.###.....###.#",
            "#.#.........#.#",
            "#.#..C......#.#",
            "#.#.........#.#",
            "#.###.....###.#",
            "#.............#",
            "#......D......#",
            "###############",
        ],
        [
            Door(7, 0, "dungeon_hall", (120, 135), label="Deep burrow"),
            Door(7, 8, "forest", (210, 132), label="Forest"),
        ],
        enemy_specs=[("ghost", 176, 72), ("slime", 87, 112)],
    )
    dungeon_hall = Room(
        "dungeon_hall",
        "Hall of Lanterns",
        "dungeon",
        [
            "#######D#######",
            "#.............#",
            "#.##.......##.#",
            "#.............#",
            "#..##.....##..#",
            "#.............#",
            "#.##.......##.#",
            "#.............#",
            "#......D......#",
            "###############",
        ],
        [
            Door(7, 0, "boss", (120, 135), "key", "Sun-lock"),
            Door(7, 8, "dungeon_entry", (120, 24), label="Burrow entrance"),
        ],
        enemy_specs=[
            ("knight", 66, 57),
            ("knight", 177, 59),
            ("bat", 120, 104),
        ],
    )
    boss = Room(
        "boss",
        "Emberheart Sanctum",
        "dungeon",
        [
            "###############",
            "#......A......#",
            "#.............#",
            "#.##.......##.#",
            "#.............#",
            "#.............#",
            "#.##.......##.#",
            "#.............#",
            "#......D......#",
            "###############",
        ],
        [Door(7, 8, "dungeon_hall", (120, 24), label="Hall")],
        enemy_specs=[("boss", 120, 69)],
    )
    highlands = Room(
        "highlands",
        "Copperwind Highlands",
        "outdoor",
        [
            "TTTTTTTTTTTTTTT",
            "T...R....R....T",
            "T..TT...TT....T",
            "T......=......T",
            "T..R...=..R...T",
            "D......=......D",
            "T..TT..=..TT..T",
            "T......=......T",
            "T...R..=..R...T",
            "TTTTTTTTTTTTTTT",
        ],
        [
            Door(0, 5, "forest", (200, 112), label="Forest"),
            Door(14, 5, "lake", (20, 88), "ember", "Moonmere"),
        ],
        enemy_specs=[
            ("knight", 72, 58),
            ("bat", 154, 42),
            ("ghost", 173, 118),
        ],
        npcs=[NPC(113, 55, 85, "Copper Scout")],
    )
    lake = Room(
        "lake",
        "Moonmere Shore",
        "outdoor",
        [
            "TTTTTTTTTTTTTTT",
            "T...~~~~~~~...T",
            "T...~.....~...T",
            "T...~..S..~...T",
            "T...~.....~...T",
            "D...~~~.~~~...T",
            "T.............T",
            "T..TT.....TT..T",
            "T............DT",
            "TTTTTTTTTTTTTTT",
        ],
        [
            Door(0, 5, "highlands", (219, 88), label="Highlands"),
            Door(13, 8, "moon_entry", (120, 133), "ember", "Moon vault"),
        ],
        enemy_specs=[
            ("slime", 61, 110),
            ("ghost", 171, 107),
            ("bat", 120, 82),
        ],
    )
    moon_entry = Room(
        "moon_entry",
        "Moonstone Vault",
        "dungeon",
        [
            "#######D#######",
            "#.....#.#.....#",
            "#.....#.#.....#",
            "#.............#",
            "#..C......##..#",
            "#.........##..#",
            "#.###.........#",
            "#.............#",
            "#......D......#",
            "###############",
        ],
        [
            Door(7, 0, "moon_hall", (120, 135), label="Mirror hall"),
            Door(7, 8, "lake", (216, 132), label="Moonmere"),
        ],
        enemy_specs=[
            ("ghost", 176, 51),
            ("knight", 91, 111),
        ],
    )
    moon_hall = Room(
        "moon_hall",
        "Hall of Reflections",
        "dungeon",
        [
            "#######D#######",
            "#.............#",
            "#..##.....##..#",
            "#..#.......#..#",
            "#.............#",
            "#....##.##....#",
            "#.............#",
            "#..##.....##..#",
            "#......D......#",
            "###############",
        ],
        [
            Door(7, 0, "moon_boss", (120, 135), "key", "Moon-lock"),
            Door(7, 8, "moon_entry", (120, 24), label="Vault entrance"),
        ],
        enemy_specs=[
            ("ghost", 61, 57),
            ("ghost", 179, 57),
            ("knight", 120, 107),
            ("bat", 120, 50),
        ],
    )
    moon_boss = Room(
        "moon_boss",
        "The Silver Deep",
        "dungeon",
        [
            "###############",
            "#......A......#",
            "#.............#",
            "#...##...##...#",
            "#.............#",
            "#.............#",
            "#...##...##...#",
            "#.............#",
            "#......D......#",
            "###############",
        ],
        [Door(7, 8, "moon_hall", (120, 24), label="Mirror hall")],
        enemy_specs=[("moon_boss", 120, 69)],
    )
    skyway = Room(
        "skyway",
        "Suncloud Causeway",
        "outdoor",
        [
            "TTTTTTTTTTTTTTT",
            "T....R...R....T",
            "T..TT.....TT..T",
            "T......=......T",
            "T..R...=...R..T",
            "D......=......D",
            "T..TT..=..TT..T",
            "T......=......T",
            "T...R..=..R...T",
            "TTTTTTTTTTTTTTT",
        ],
        [
            Door(0, 5, "lake", (200, 111), "moon", "Moonmere"),
            Door(14, 5, "final_hall", (120, 133), "moon", "Sky citadel"),
        ],
        enemy_specs=[
            ("bat", 70, 47),
            ("knight", 119, 90),
            ("bat", 178, 116),
            ("ghost", 180, 46),
        ],
        npcs=[NPC(107, 55, 87, "Cloud Sage")],
    )
    final_hall = Room(
        "final_hall",
        "Crownless Citadel",
        "dungeon",
        [
            "#######D#######",
            "#.............#",
            "#.###.......#.#",
            "#.....##......#",
            "#.............#",
            "#......##.....#",
            "#.#.........#.#",
            "#.............#",
            "#......D......#",
            "###############",
        ],
        [
            Door(7, 0, "final_boss", (120, 135), "crests", "Crown seal"),
            Door(7, 8, "skyway", (219, 88), label="Suncloud"),
        ],
        enemy_specs=[
            ("knight", 57, 53),
            ("knight", 181, 52),
            ("ghost", 84, 113),
            ("ghost", 158, 110),
            ("bat", 120, 75),
        ],
    )
    final_boss = Room(
        "final_boss",
        "Starless Throne",
        "dungeon",
        [
            "###############",
            "#......A......#",
            "#.............#",
            "#..##.....##..#",
            "#.............#",
            "#.............#",
            "#..##.....##..#",
            "#.............#",
            "#......D......#",
            "###############",
        ],
        [Door(7, 8, "final_hall", (120, 24), label="Citadel")],
        enemy_specs=[("final_boss", 120, 69)],
    )
    campaign = (
        village,
        forest,
        dungeon_entry,
        dungeon_hall,
        boss,
        highlands,
        lake,
        moon_entry,
        moon_hall,
        moon_boss,
        skyway,
        final_hall,
        final_boss,
    )
    return {room.name: room for room in campaign}


class Game:
    def __init__(self) -> None:
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.init()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 2, 512)
        except pygame.error:
            pass
        pygame.display.set_caption(TITLE)
        self.fullscreen = False
        self.window = pygame.display.set_mode(
            (INTERNAL_W * WINDOW_SCALE, INTERNAL_H * WINDOW_SCALE)
        )
        self.canvas = pygame.Surface((INTERNAL_W, INTERNAL_H)).convert()
        self.clock = pygame.time.Clock()
        self.font = MeowFont01GBA(1, 1)
        self.font_small = MeowFont01GBA(1, 0)
        self.font_big = MeowFont01GBA(2, 2)
        self.assets = load_assets()
        self.audio = Audio()
        self.rooms = build_rooms()
        self.room_name = "village"
        self.player = Player(120, 119)
        self.state = "title"
        self.running = True
        self.dialogue: list[str] = []
        self.dialogue_index = 0
        self.dialogue_speaker = ""
        self.flags: set[str] = set()
        self.rupees = 0
        self.shards = 0
        self.has_key = False
        self.particles: list[Particle] = []
        self.shake = 0.0
        self.flash = 0.0
        self.room_banner = 0.0
        self.title_time = 0.0
        self.total_time = 0.0
        self.prompt = ""
        self.intro_seen = False
        self.audio.start_music()

    @property
    def room(self) -> Room:
        return self.rooms[self.room_name]

    def new_game(self) -> None:
        self.rooms = build_rooms()
        self.room_name = "village"
        self.player = Player(120, 119)
        self.flags.clear()
        self.rupees = 0
        self.shards = 0
        self.has_key = False
        self.particles.clear()
        self.state = "play"
        self.room_banner = 2.2
        self.open_dialogue(
            "Elder Fern",
            [
                "AC! The forest's Sun Motes have gone wild.",
                "Recover three motes. Their light will wake the shrinking stone.",
                "A tiny traveler may enter places a tall hero cannot.",
            ],
        )

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        size = (0, 0) if self.fullscreen else (
            INTERNAL_W * WINDOW_SCALE,
            INTERNAL_H * WINDOW_SCALE,
        )
        self.window = pygame.display.set_mode(size, flags)

    def open_dialogue(self, speaker: str, lines: list[str]) -> None:
        self.dialogue_speaker = speaker
        self.dialogue = lines
        self.dialogue_index = 0

    def advance_dialogue(self) -> None:
        if not self.dialogue:
            return
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue):
            self.dialogue.clear()
            self.dialogue_index = 0

    def add_burst(
        self, x: float, y: float, color: tuple[int, int, int], count: int
    ) -> None:
        for _ in range(count):
            angle = random.random() * math.tau
            speed = random.uniform(20, 55)
            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed - 12,
                    color,
                    random.uniform(0.25, 0.55),
                    random.choice((1, 1, 2)),
                )
            )

    def is_in_front(self, source: tuple[float, float]) -> bool:
        to_source = pygame.Vector2(source[0] - self.player.x, source[1] - self.player.y)
        facing = {
            "up": pygame.Vector2(0, -1),
            "down": pygame.Vector2(0, 1),
            "left": pygame.Vector2(-1, 0),
            "right": pygame.Vector2(1, 0),
        }[self.player.direction]
        return bool(to_source.length_squared() and facing.dot(to_source.normalize()) > 0.25)

    def on_enemy_defeated(self, enemy: Enemy) -> None:
        if enemy.kind in Enemy.BOSS_KINDS:
            boss_results = {
                "boss": (
                    "ember_defeated",
                    "Emberheart Sanctum",
                    [
                        "The Emberheart fades. The first crest wakes.",
                        "Approach the Sunbud altar. A road opens beyond the forest.",
                    ],
                ),
                "moon_boss": (
                    "moon_defeated",
                    "Silver Deep",
                    [
                        "The Mirror Wraith dissolves into quiet moonlight.",
                        "The second crest waits at the altar.",
                    ],
                ),
                "final_boss": (
                    "final_defeated",
                    "Starless Throne",
                    [
                        "The Crownless King falls. Dawn returns to every road.",
                        "Touch the final Sunbud and finish the adventure.",
                    ],
                ),
            }
            flag, speaker, lines = boss_results[enemy.kind]
            self.flags.add(flag)
            self.room.pickups.append(Pickup(enemy.x, enemy.y, "heart"))
            self.add_burst(enemy.x, enemy.y, COLORS["gold"], 28)
            self.audio.play("win")
            self.open_dialogue(speaker, lines)
            return
        kind = "shard" if enemy.shard_drop else random.choice(("rupee", "rupee", "heart"))
        self.room.pickups.append(Pickup(enemy.x, enemy.y, kind))

    def change_room(self, target: str, spawn: tuple[float, float]) -> None:
        self.room_name = target
        self.player.x, self.player.y = spawn
        self.room_banner = 1.8
        self.audio.play("door")
        self.flash = 0.10

    def interact(self) -> None:
        center = self.player.rect.center

        for npc in self.room.npcs:
            if distance(center, npc.rect.center) <= 25:
                if npc.name == "Elder Fern":
                    if "final_defeated" in self.flags:
                        lines = ["You returned with dawn in your wake. Every road remembers."]
                    elif "moon_crest" in self.flags:
                        lines = ["Two crests shine. The Suncloud Causeway awaits."]
                    elif "ember_crest" in self.flags:
                        lines = ["Carry the Ember Crest east, beyond the Copperwind heights."]
                    elif self.shards >= 3:
                        lines = ["The three motes sing together. Seek the stone in Whisperleaf."]
                    else:
                        lines = [f"Sun Motes recovered: {self.shards}/3. Listen for their chime."]
                elif npc.name == "Copper Scout":
                    lines = [
                        "The Moonstone Vault lies beyond the shore.",
                        "Its mirrors hide a key, and its guardian hates bright steel.",
                    ]
                elif npc.name == "Cloud Sage":
                    lines = [
                        "Ember and Moon together can break the Crown Seal.",
                        "The Starless Throne is the final road.",
                    ]
                else:
                    lines = [
                        "Pip: Shift rolls. X raises your shield.",
                        "A sword is useful, but a clever hero knows when to block!",
                    ]
                self.open_dialogue(npc.name, lines)
                return

        if self.room_name == "forest":
            stump = pygame.Rect(12 * TILE, 6 * TILE, TILE, TILE)
            if distance(center, stump.center) <= 25:
                if self.shards < 3:
                    self.open_dialogue(
                        "Shrinking Stone",
                        [f"The stone sleeps. Sun Motes: {self.shards}/3."],
                    )
                else:
                    self.player.tiny = not self.player.tiny
                    self.audio.play("shrink" if self.player.tiny else "grow")
                    self.flash = 0.35
                    self.shake = 3
                    self.add_burst(
                        self.player.x,
                        self.player.y,
                        COLORS["gold"],
                        16,
                    )
                    self.open_dialogue(
                        "Shrinking Stone",
                        [
                            "The world towers above you!" if self.player.tiny
                            else "You return to your usual size."
                        ],
                    )
                return

        if self.room_name == "lake":
            stone = pygame.Rect(7 * TILE, 3 * TILE, TILE, TILE)
            if distance(center, stone.center) <= 25:
                self.player.tiny = not self.player.tiny
                self.audio.play("shrink" if self.player.tiny else "grow")
                self.flash = 0.35
                self.shake = 3
                self.add_burst(self.player.x, self.player.y, (158, 220, 255), 16)
                self.open_dialogue(
                    "Moonstone",
                    [
                        "The shore becomes a giant world." if self.player.tiny
                        else "The moonlit world returns to scale."
                    ],
                )
                return

        if self.room_name in {"dungeon_entry", "moon_entry"}:
            chest_x = 5 if self.room_name == "dungeon_entry" else 3
            chest = pygame.Rect(chest_x * TILE, 4 * TILE, TILE, TILE)
            if distance(center, chest.center) <= 24:
                if not self.room.chest_open:
                    self.room.chest_open = True
                    self.has_key = True
                    self.audio.play("item")
                    self.add_burst(chest.centerx, chest.centery, COLORS["gold"], 14)
                    key_name = "Sun Key" if self.room_name == "dungeon_entry" else "Moon Key"
                    self.open_dialogue(
                        "Treasure Chest",
                        [f"You found the {key_name}! It opens this dungeon's great lock."],
                    )
                else:
                    self.open_dialogue("Treasure Chest", ["The chest is empty."])
                return

        if self.room_name == "boss" and "ember_defeated" in self.flags:
            altar = pygame.Rect(7 * TILE, TILE, TILE, TILE)
            if distance(center, altar.center) <= 28:
                self.flags.add("ember_crest")
                self.player.tiny = False
                self.player.health = self.player.max_health
                self.audio.play("win")
                self.change_room("highlands", (20, 88))
                self.open_dialogue(
                    "Ember Crest",
                    [
                        "The Ember Crest is yours.",
                        "Chapter two: cross Copperwind Highlands to Moonmere.",
                    ],
                )
                return

        if self.room_name == "moon_boss" and "moon_defeated" in self.flags:
            altar = pygame.Rect(7 * TILE, TILE, TILE, TILE)
            if distance(center, altar.center) <= 28:
                self.flags.add("moon_crest")
                self.player.tiny = False
                self.player.health = self.player.max_health
                self.audio.play("win")
                self.change_room("skyway", (20, 88))
                self.open_dialogue(
                    "Moon Crest",
                    [
                        "The Moon Crest joins the Ember Crest.",
                        "Final chapter: climb the Suncloud Causeway.",
                    ],
                )
                return

        if self.room_name == "final_boss" and "final_defeated" in self.flags:
            altar = pygame.Rect(7 * TILE, TILE, TILE, TILE)
            if distance(center, altar.center) <= 28:
                self.state = "victory"
                self.audio.play("win")
                return

        for door in self.room.doors:
            if distance(center, door.rect.center) <= 26:
                if door.requirement == "tiny" and not self.player.tiny:
                    self.open_dialogue(
                        "Root Tunnel",
                        ["The opening is far too small. The forest stone may know a way."],
                    )
                    return
                if door.requirement == "ember" and "ember_crest" not in self.flags:
                    self.open_dialogue(
                        "Copper Seal",
                        ["The road opens only for the bearer of the Ember Crest."],
                    )
                    return
                if door.requirement == "moon" and "moon_crest" not in self.flags:
                    self.open_dialogue(
                        "Cloud Seal",
                        ["Moonlight must join fire before this road appears."],
                    )
                    return
                if door.requirement == "crests" and not {
                    "ember_crest",
                    "moon_crest",
                }.issubset(self.flags):
                    self.open_dialogue(
                        "Crown Seal",
                        ["Two empty crest-shapes wait in the ancient door."],
                    )
                    return
                if door.requirement == "key" and not self.has_key:
                    self.open_dialogue(
                        "Sun-lock", ["A golden key-shaped light flickers in the seal."]
                    )
                    return
                if door.requirement == "key":
                    self.has_key = False
                self.change_room(door.target, door.spawn)
                return

    def find_prompt(self) -> str:
        center = self.player.rect.center
        for npc in self.room.npcs:
            if distance(center, npc.rect.center) <= 25:
                return "E Talk"
        if self.room_name == "forest":
            if distance(center, (12 * TILE + 8, 6 * TILE + 8)) <= 25:
                return "E Use stone"
        if self.room_name == "lake":
            if distance(center, (7 * TILE + 8, 3 * TILE + 8)) <= 25:
                return "E Use moonstone"
        if self.room_name in {"dungeon_entry", "moon_entry"}:
            chest_x = 5 if self.room_name == "dungeon_entry" else 3
            if distance(center, (chest_x * TILE + 8, 4 * TILE + 8)) <= 24:
                return "E Open"
        altar_flags = {
            "boss": "ember_defeated",
            "moon_boss": "moon_defeated",
            "final_boss": "final_defeated",
        }
        if (
            self.room_name in altar_flags
            and altar_flags[self.room_name] in self.flags
        ):
            if distance(center, (7 * TILE + 8, TILE + 8)) <= 28:
                return "E Sunbud"
        for door in self.room.doors:
            if distance(center, door.rect.center) <= 26:
                return f"E {door.label}"
        return ""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_F11:
            self.toggle_fullscreen()
            return

        if self.state == "title":
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.new_game()
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.running = False
            return
        if self.state == "victory":
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.state = "title"
            return
        if self.state == "gameover":
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.new_game()
            return
        if self.dialogue:
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.advance_dialogue()
            return
        if event.key == pygame.K_ESCAPE:
            self.state = "pause" if self.state == "play" else "play"
            return
        if self.state == "pause":
            return
        if event.key in (pygame.K_z, pygame.K_j, pygame.K_SPACE):
            self.player.start_attack(self.audio)
        elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_c):
            self.player.start_roll(pygame.key.get_pressed(), self.audio)
        elif event.key in (pygame.K_e, pygame.K_RETURN):
            self.interact()

    def update(self, dt: float) -> None:
        self.total_time += dt
        self.title_time += dt
        self.room_banner = max(0.0, self.room_banner - dt)
        self.flash = max(0.0, self.flash - dt)
        self.shake = max(0.0, self.shake - dt * 16)

        for particle in self.particles:
            particle.update(dt)
        self.particles = [particle for particle in self.particles if particle.life > 0]

        if self.state != "play" or self.dialogue:
            return
        keys = pygame.key.get_pressed()
        self.player.update(dt, self.room, keys)

        for enemy in self.room.enemies:
            enemy.update(dt, self, self.room)
            if (
                enemy.alive
                and self.player.attack_timer > 0.05
                and id(enemy) not in self.player.attack_hits
                and self.player.attack_rect().colliderect(enemy.rect)
            ):
                enemy.take_damage(1, (self.player.x, self.player.y), self)
                self.player.attack_hits.add(id(enemy))

        for pickup in self.room.pickups:
            pickup.life -= dt
            pickup.phase += dt * 5
            if pickup.rect.colliderect(self.player.rect):
                if pickup.kind == "rupee":
                    self.rupees += 1
                elif pickup.kind == "heart":
                    self.player.health = min(self.player.max_health, self.player.health + 2)
                else:
                    self.shards = min(3, self.shards + 1)
                pickup.life = 0
                self.audio.play("item")
                self.add_burst(pickup.x, pickup.y, COLORS["gold"], 9)
        self.room.pickups = [pickup for pickup in self.room.pickups if pickup.life > 0]

        self.prompt = self.find_prompt()
        if self.player.health <= 0:
            self.state = "gameover"

    def draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        pos: tuple[int, int],
        color: tuple[int, int, int] = COLORS["cream"],
        font: MeowFont01GBA | None = None,
        center: bool = False,
    ) -> pygame.Rect:
        font = font or self.font
        shadow = font.render(text, False, COLORS["ink"])
        image = font.render(text, False, color)
        rect = image.get_rect()
        rect.center = pos if center else rect.center
        if not center:
            rect.topleft = pos
        surface.blit(shadow, rect.move(1, 1))
        surface.blit(image, rect)
        return rect

    def draw_tile(self, surface: pygame.Surface, char: str, tx: int, ty: int) -> None:
        x, y = tx * TILE, ty * TILE
        seed = tx * 79 + ty * 131
        if self.room.theme == "outdoor":
            if self.room_name == "highlands":
                grass_a, grass_b = (151, 178, 79), (132, 159, 68)
            elif self.room_name == "lake":
                grass_a, grass_b = (79, 171, 108), (66, 151, 101)
            elif self.room_name == "skyway":
                grass_a, grass_b = (103, 188, 142), (86, 169, 132)
            else:
                grass_a, grass_b = COLORS["grass"], COLORS["grass2"]
            base = grass_a if seed % 3 else grass_b
            pygame.draw.rect(surface, base, (x, y, TILE, TILE))
            if char not in {"=", "~", "B", "D"} and seed % 4 == 0:
                tuft = (48, 138, 63)
                px, py = x + 4 + seed % 7, y + 9 + seed % 4
                pygame.draw.line(surface, tuft, (px, py + 3), (px - 1, py))
                pygame.draw.line(surface, tuft, (px, py + 3), (px + 2, py + 1))
            if char == "." and seed % 11 == 0:
                pygame.draw.rect(surface, (255, 233, 114), (x + 11, y + 4, 1, 1))
                pygame.draw.rect(surface, (238, 116, 125), (x + 10, y + 5, 3, 1))
            if char == "=":
                pygame.draw.rect(surface, COLORS["path"], (x, y, TILE, TILE))
                pygame.draw.line(surface, (232, 198, 130), (x, y), (x + 15, y))
                for dot in range(2):
                    px = x + 3 + ((seed + dot * 7) % 11)
                    py = y + 3 + ((seed * 3 + dot * 5) % 10)
                    surface.set_at((px, py), (183, 139, 88))
            elif char == "~":
                pygame.draw.rect(surface, COLORS["water"], (x, y, TILE, TILE))
                wave_y = y + 4 + int((math.sin(self.total_time * 3 + tx) + 1) * 3)
                pygame.draw.line(surface, (96, 191, 224), (x + 2, wave_y), (x + 10, wave_y))
            elif char == "T":
                pygame.draw.rect(surface, (101, 70, 46), (x + 6, y + 9, 4, 7))
                pygame.draw.circle(surface, (20, 82, 51), (x + 8, y + 8), 8)
                pygame.draw.circle(surface, (31, 116, 57), (x + 6, y + 5), 6)
                pygame.draw.circle(surface, (57, 151, 70), (x + 4, y + 4), 3)
                pygame.draw.rect(surface, (102, 188, 83), (x + 5, y + 2, 4, 2))
                pygame.draw.rect(surface, (18, 72, 47), (x, y + 11, TILE, 3))
            elif char == "R":
                pygame.draw.polygon(
                    surface,
                    (103, 112, 122),
                    [(x + 3, y + 12), (x + 5, y + 5), (x + 11, y + 3), (x + 14, y + 12)],
                )
                pygame.draw.line(surface, (170, 176, 168), (x + 6, y + 6), (x + 11, y + 5))
            elif char == "B":
                pygame.draw.rect(surface, (172, 105, 66), (x, y, TILE, TILE))
                pygame.draw.rect(surface, (104, 53, 45), (x, y, TILE, 6))
                pygame.draw.line(surface, (226, 153, 79), (x, y + 8), (x + 15, y + 8))
                pygame.draw.line(surface, (126, 70, 52), (x, y + 12), (x + 15, y + 12))
                pygame.draw.rect(surface, (246, 207, 111), (x + 2, y + 9, 2, 2))
            elif char == "S":
                pygame.draw.circle(surface, (82, 66, 92), (x + 8, y + 9), 7)
                glow = 140 + int(math.sin(self.total_time * 5) * 45)
                pygame.draw.circle(surface, (glow, 211, 111), (x + 8, y + 7), 3)
            elif char == "D":
                pygame.draw.rect(surface, (38, 69, 47), (x + 1, y + 1, 14, 14))
                pygame.draw.ellipse(surface, (17, 25, 27), (x + 3, y + 3, 10, 12))
        else:
            floor = (55, 58, 81) if seed % 2 else (59, 63, 88)
            pygame.draw.rect(surface, floor, (x, y, TILE, TILE))
            pygame.draw.line(surface, (70, 74, 99), (x, y + 15), (x + 15, y + 15))
            pygame.draw.line(surface, (67, 71, 96), (x + 8, y), (x + 8, y + 3))
            pygame.draw.rect(surface, (76, 80, 105), (x + 2 + seed % 9, y + 6, 2, 1))
            if char == "#":
                pygame.draw.rect(surface, COLORS["stone2"], (x, y, TILE, TILE))
                pygame.draw.rect(surface, COLORS["stone"], (x, y, TILE, 5))
                pygame.draw.line(surface, (109, 117, 145), (x + 1, y + 1), (x + 14, y + 1))
                pygame.draw.line(surface, (36, 40, 58), (x, y + 12), (x + 15, y + 12))
            elif char == "D":
                surface.blit(self.assets.get(34, self.assets[33]), (x, y))
            elif char == "C":
                image = self.assets[90] if self.room.chest_open else self.assets[89]
                surface.blit(image, (x, y))
            elif char == "A":
                pulse = int((math.sin(self.total_time * 4) + 1) * 2)
                pygame.draw.circle(surface, (245, 183, 60), (x + 8, y + 8), 5 + pulse)
                pygame.draw.circle(surface, (255, 246, 173), (x + 8, y + 8), 2)

    def draw_enemy(self, surface: pygame.Surface, enemy: Enemy) -> None:
        if not enemy.alive:
            return
        image = self.assets[enemy.sprite]
        if enemy.kind in Enemy.BOSS_KINDS:
            image = pygame.transform.scale(image, (24, 24))
        bob = int(math.sin(enemy.phase * 2) * 2) if enemy.kind in ("bat", "ghost") else 0
        rect = image.get_rect(center=(round(enemy.x), round(enemy.y + bob)))
        shadow_size = (14, 5) if enemy.kind != "boss" else (21, 7)
        shadow = pygame.Rect(0, 0, *shadow_size)
        shadow.center = (round(enemy.x), round(enemy.y + 7))
        pygame.draw.ellipse(surface, (27, 29, 40), shadow)
        if enemy.flash > 0:
            flashed = image.copy()
            flashed.fill((180, 180, 180, 0), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(flashed, rect)
        else:
            surface.blit(image, rect)

    def draw_player(self, surface: pygame.Surface) -> None:
        if self.player.invulnerable > 0 and int(self.player.invulnerable * 16) % 2:
            return
        image = self.assets[112]
        if self.player.direction == "left":
            image = pygame.transform.flip(image, True, False)
        if self.player.tiny:
            image = pygame.transform.scale(image, (8, 8))
        bob = int(math.sin(self.player.walk_time) > 0.5) if self.player.roll_timer <= 0 else 1
        shadow = pygame.Rect(0, 0, 8 if self.player.tiny else 12, 3 if self.player.tiny else 5)
        shadow.center = (round(self.player.x), round(self.player.y + 6))
        pygame.draw.ellipse(surface, (26, 40, 37), shadow)
        rect = image.get_rect(center=(round(self.player.x), round(self.player.y - bob)))
        if self.player.roll_timer > 0:
            image = pygame.transform.rotate(image, int(self.player.roll_timer * 720))
            rect = image.get_rect(center=rect.center)
        surface.blit(image, rect)

        if self.player.shielding:
            shield = self.assets.get(118)
            if shield:
                shield_rect = shield.get_rect(center=rect.center)
                offsets = {"up": (0, -5), "down": (0, 6), "left": (-6, 1), "right": (6, 1)}
                shield_rect.move_ip(*offsets[self.player.direction])
                surface.blit(shield, shield_rect)

        if self.player.attack_timer > 0:
            sword_id = {"up": 106, "down": 103, "left": 105, "right": 104}[self.player.direction]
            sword = self.assets[sword_id]
            if self.player.tiny:
                sword = pygame.transform.scale(sword, (8, 8))
            sword_rect = sword.get_rect()
            offsets = {
                "up": (0, -10),
                "down": (0, 10),
                "left": (-10, 0),
                "right": (10, 0),
            }
            sword_rect.center = (
                round(self.player.x + offsets[self.player.direction][0]),
                round(self.player.y + offsets[self.player.direction][1]),
            )
            surface.blit(sword, sword_rect)

    def draw_pickup(self, surface: pygame.Surface, pickup: Pickup) -> None:
        y = round(pickup.y + math.sin(pickup.phase) * 2)
        if pickup.kind == "heart":
            color = COLORS["red"]
            pygame.draw.circle(surface, color, (round(pickup.x) - 2, y), 3)
            pygame.draw.circle(surface, color, (round(pickup.x) + 2, y), 3)
            pygame.draw.polygon(
                surface,
                color,
                [(round(pickup.x) - 5, y), (round(pickup.x) + 5, y), (round(pickup.x), y + 7)],
            )
        elif pickup.kind == "shard":
            pygame.draw.polygon(
                surface,
                COLORS["gold"],
                [
                    (round(pickup.x), y - 6),
                    (round(pickup.x) + 5, y),
                    (round(pickup.x), y + 6),
                    (round(pickup.x) - 5, y),
                ],
            )
            pygame.draw.circle(surface, COLORS["cream"], (round(pickup.x), y), 2)
        else:
            pygame.draw.polygon(
                surface,
                (72, 216, 107),
                [
                    (round(pickup.x), y - 5),
                    (round(pickup.x) + 4, y),
                    (round(pickup.x), y + 5),
                    (round(pickup.x) - 4, y),
                ],
            )

    def draw_hud(self, surface: pygame.Surface) -> None:
        panel = pygame.Surface((INTERNAL_W, 16), pygame.SRCALPHA)
        panel.fill((10, 27, 36, 232))
        surface.blit(panel, (0, 0))
        pygame.draw.line(surface, (236, 190, 68), (0, 15), (INTERNAL_W, 15))
        for heart in range(self.player.max_health // 2):
            x = 6 + heart * 11
            filled = self.player.health - heart * 2
            color = COLORS["red"] if filled > 0 else (76, 63, 68)
            pygame.draw.circle(surface, (73, 34, 43), (x, 6), 4)
            pygame.draw.circle(surface, (73, 34, 43), (x + 4, 6), 4)
            pygame.draw.polygon(surface, (73, 34, 43), [(x - 4, 7), (x + 8, 7), (x + 2, 14)])
            pygame.draw.circle(surface, color, (x, 6), 3)
            pygame.draw.circle(surface, color, (x + 4, 6), 3)
            pygame.draw.polygon(surface, color, [(x - 3, 7), (x + 7, 7), (x + 2, 13)])
            if filled == 1:
                pygame.draw.rect(surface, (76, 63, 68), (x + 2, 3, 6, 8))

        pygame.draw.polygon(surface, (67, 222, 105), [(49, 3), (53, 8), (49, 13), (45, 8)])
        pygame.draw.polygon(surface, (223, 255, 193), [(49, 4), (51, 8), (49, 8)])
        self.draw_text(surface, f"{self.rupees:02}", (56, 4), (109, 242, 137), self.font_small)

        pygame.draw.polygon(surface, COLORS["gold"], [(84, 2), (89, 8), (84, 14), (79, 8)])
        pygame.draw.circle(surface, COLORS["cream"], (84, 8), 1)
        self.draw_text(surface, f"{self.shards}/3", (93, 4), COLORS["gold"], self.font_small)
        for index, crest_flag in enumerate(("ember_crest", "moon_crest")):
            crest_x = 116 + index * 9
            crest_color = (
                (246, 153, 64)
                if crest_flag == "ember_crest"
                else (143, 215, 255)
            )
            if crest_flag not in self.flags:
                crest_color = (67, 76, 84)
            pygame.draw.polygon(
                surface,
                crest_color,
                [(crest_x, 3), (crest_x + 4, 8), (crest_x, 13), (crest_x - 4, 8)],
            )
        if self.has_key:
            self.draw_text(surface, "K", (133, 4), COLORS["cream"], self.font_small)
        mode = "MINI" if self.player.tiny else "HERO"
        self.draw_text(surface, mode, (148, 4), (126, 223, 255), self.font_small)

        for slot_x, label in ((177, "B"), (209, "A")):
            pygame.draw.rect(surface, (31, 49, 61), (slot_x, 1, 28, 13))
            pygame.draw.rect(surface, COLORS["gold"], (slot_x, 1, 28, 13), 1)
            self.draw_text(surface, label, (slot_x + 3, 4), COLORS["gold"], self.font_small)
        sword = pygame.transform.scale(self.assets[103], (9, 9))
        shield = pygame.transform.scale(self.assets[118], (9, 9))
        surface.blit(sword, (192, 3))
        surface.blit(shield, (224, 3))

        if self.prompt and not self.dialogue:
            width = self.font.size(self.prompt)[0] + 8
            prompt_x = INTERNAL_W - width - 4
            pygame.draw.rect(surface, (10, 31, 42), (prompt_x, 19, width, 13))
            pygame.draw.rect(surface, COLORS["gold"], (prompt_x, 19, width, 13), 1)
            self.draw_text(surface, self.prompt, (prompt_x + 4, 22), COLORS["cream"])

    def objective(self) -> str:
        if "final_defeated" in self.flags:
            return "Touch the final Sunbud."
        if self.room_name == "final_boss":
            return "Defeat the Crownless King."
        if self.room_name == "final_hall":
            return "Reach the Starless Throne."
        if "moon_defeated" in self.flags and "moon_crest" not in self.flags:
            return "Claim the Moon Crest."
        if self.room_name == "moon_boss":
            return "Defeat the Mirror Wraith."
        if self.room_name in {"moon_entry", "moon_hall"}:
            return "Conquer the Moonstone Vault."
        if "ember_defeated" in self.flags and "ember_crest" not in self.flags:
            return "Claim the Ember Crest."
        if self.room_name == "boss":
            return "Defeat the Emberheart."
        if self.has_key:
            return "Find this dungeon's great lock."
        if self.room_name in {"dungeon_entry", "dungeon_hall"}:
            return "Search the Rootglass Burrow."
        if "moon_crest" in self.flags:
            return "Climb the Suncloud Causeway."
        if "ember_crest" in self.flags:
            return "Cross the highlands to Moonmere."
        if self.shards < 3:
            return f"Recover Sun Motes ({self.shards}/3)."
        if not self.player.tiny:
            return "Use the shrinking stone."
        return "Enter the tiny root tunnel."

    def draw_dialogue(self, surface: pygame.Surface) -> None:
        box = pygame.Rect(5, 111, 230, 44)
        pygame.draw.rect(surface, (9, 28, 38), box)
        pygame.draw.rect(surface, COLORS["gold"], box, 2)
        pygame.draw.rect(surface, COLORS["cream"], box.inflate(-6, -6), 1)
        pygame.draw.rect(surface, COLORS["gold"], (4, 110, 3, 3))
        pygame.draw.rect(surface, COLORS["gold"], (233, 110, 3, 3))
        pygame.draw.rect(surface, COLORS["gold"], (4, 153, 3, 3))
        pygame.draw.rect(surface, COLORS["gold"], (233, 153, 3, 3))
        name_width = min(112, self.font.size(self.dialogue_speaker)[0] + 12)
        pygame.draw.rect(surface, (53, 128, 72), (10, 106, name_width, 13))
        pygame.draw.rect(surface, COLORS["gold"], (10, 106, name_width, 13), 1)
        self.draw_text(surface, self.dialogue_speaker, (16, 109), COLORS["cream"])
        line = self.dialogue[self.dialogue_index]
        words = line.split()
        lines: list[str] = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if self.font.size(test)[0] > 204 and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        for index, text in enumerate(lines[:3]):
            self.draw_text(surface, text, (14, 123 + index * 9))
        pygame.draw.circle(surface, (45, 107, 63), (220, 144), 7)
        pygame.draw.circle(surface, COLORS["gold"], (220, 144), 7, 1)
        self.draw_text(surface, "E", (218, 141), COLORS["cream"], self.font_small)

    def render_world(self) -> None:
        self.canvas.fill(COLORS["ink"])
        for ty, row in enumerate(self.room.tilemap):
            for tx, char in enumerate(row):
                self.draw_tile(self.canvas, char, tx, ty)

        drawables: list[tuple[float, str, object]] = []
        for npc in self.room.npcs:
            drawables.append((npc.y, "npc", npc))
        for enemy in self.room.enemies:
            if enemy.alive:
                drawables.append((enemy.y, "enemy", enemy))
        for pickup in self.room.pickups:
            drawables.append((pickup.y, "pickup", pickup))
        drawables.append((self.player.y, "player", self.player))
        for _, kind, item in sorted(drawables, key=lambda entry: entry[0]):
            if kind == "npc":
                npc = item
                assert isinstance(npc, NPC)
                image = self.assets[npc.sprite]
                shadow = pygame.Rect(round(npc.x) + 2, round(npc.y) + 11, 12, 4)
                pygame.draw.ellipse(self.canvas, (28, 49, 39), shadow)
                self.canvas.blit(image, (round(npc.x), round(npc.y)))
            elif kind == "enemy":
                assert isinstance(item, Enemy)
                self.draw_enemy(self.canvas, item)
            elif kind == "pickup":
                assert isinstance(item, Pickup)
                self.draw_pickup(self.canvas, item)
            else:
                self.draw_player(self.canvas)

        for particle in self.particles:
            pygame.draw.rect(
                self.canvas,
                particle.color,
                (round(particle.x), round(particle.y), particle.size, particle.size),
            )

        boss = next(
            (
                enemy
                for enemy in self.room.enemies
                if enemy.kind in Enemy.BOSS_KINDS and enemy.alive
            ),
            None,
        )
        if boss:
            boss_names = {
                "boss": "EMBERHEART",
                "moon_boss": "MIRROR WRAITH",
                "final_boss": "CROWNLESS KING",
            }
            pygame.draw.rect(self.canvas, COLORS["ink"], (57, 18, 126, 7))
            pygame.draw.rect(self.canvas, COLORS["red"], (59, 20, int(122 * boss.health / boss.max_health), 3))
            self.draw_text(
                self.canvas,
                boss_names[boss.kind],
                (120, 29),
                COLORS["cream"],
                self.font_small,
                True,
            )

        self.draw_hud(self.canvas)
        if self.room_banner > 0:
            alpha = int(220 * min(1.0, self.room_banner * 2))
            banner = pygame.Surface((150, 20), pygame.SRCALPHA)
            banner.fill((16, 20, 32, alpha))
            self.canvas.blit(banner, (45, 72))
            self.draw_text(self.canvas, self.room.title, (120, 81), COLORS["cream"], center=True)
        if self.dialogue:
            self.draw_dialogue(self.canvas)
        elif self.state == "pause":
            overlay = pygame.Surface((INTERNAL_W, INTERNAL_H), pygame.SRCALPHA)
            overlay.fill((11, 15, 28, 205))
            self.canvas.blit(overlay, (0, 0))
            self.draw_text(self.canvas, "PAUSED", (120, 47), COLORS["gold"], self.font_big, True)
            self.draw_text(self.canvas, self.objective(), (120, 78), COLORS["cream"], center=True)
            self.draw_text(self.canvas, "Esc  Resume", (120, 104), COLORS["cream"], center=True)

    def render_title(self) -> None:
        self.canvas.fill((25, 72, 61))
        for y in range(0, INTERNAL_H, 16):
            for x in range(0, INTERNAL_W, 16):
                color = (38, 104, 72) if (x // 16 + y // 16) % 2 else (32, 91, 67)
                pygame.draw.rect(self.canvas, color, (x, y, 16, 16))
        for index in range(12):
            x = (index * 37 + int(self.title_time * (8 + index % 3))) % (INTERNAL_W + 20) - 10
            y = 22 + (index * 29) % 112
            pygame.draw.circle(self.canvas, (113, 201, 89), (x, y), 2)
        pygame.draw.circle(self.canvas, (18, 55, 49), (120, 77), 40)
        for angle in (0, 120, 240):
            ray = pygame.Vector2(0, -46).rotate(angle + math.sin(self.title_time) * 4)
            tip = (round(120 + ray.x), round(77 + ray.y))
            left = pygame.Vector2(ray).rotate(-17) * 0.74
            right = pygame.Vector2(ray).rotate(17) * 0.74
            pygame.draw.polygon(
                self.canvas,
                (218, 177, 62),
                [
                    tip,
                    (round(120 + left.x), round(77 + left.y)),
                    (round(120 + right.x), round(77 + right.y)),
                ],
            )
        sword = pygame.transform.scale(self.assets[103], (34, 34))
        sword = pygame.transform.rotate(sword, -42)
        self.canvas.blit(sword, sword.get_rect(center=(130, 79)))
        hero = pygame.transform.scale(self.assets[112], (40, 40))
        self.canvas.blit(hero, hero.get_rect(center=(116, 79)))
        pygame.draw.rect(self.canvas, (10, 26, 38), (9, 109, 222, 46))
        pygame.draw.rect(self.canvas, COLORS["gold"], (9, 109, 222, 46), 2)
        pygame.draw.rect(self.canvas, COLORS["cream"], (12, 112, 216, 40), 1)
        self.draw_text(self.canvas, "AC'S", (120, 5), COLORS["gold"], self.font, True)
        self.draw_text(self.canvas, "MEOW CAP", (120, 19), COLORS["cream"], self.font_big, True)
        self.draw_text(self.canvas, "ADVENTURE", (120, 36), COLORS["gold"], center=True)
        blink = COLORS["gold"] if int(self.title_time * 2) % 2 else COLORS["cream"]
        self.draw_text(self.canvas, "ENTER  START", (120, 116), blink, center=True)
        self.draw_text(self.canvas, "Z SWORD  X SHIELD  SHIFT ROLL  E USE", (120, 133), COLORS["cream"], self.font_small, True)
        self.draw_text(
            self.canvas,
            f"{FONT_ENGINE_NAME} | {FPS} FPS | {SPEED_PROFILE}",
            (120, 145),
            (137, 220, 213),
            self.font_small,
            True,
        )

    def render_end_screen(self, victory: bool) -> None:
        self.canvas.fill((18, 24, 38))
        color = COLORS["gold"] if victory else COLORS["red"]
        pygame.draw.circle(self.canvas, (35, 88, 67), (120, 58), 43)
        if victory:
            for angle in range(0, 360, 30):
                vector = pygame.Vector2(0, -48).rotate(angle + self.total_time * 15)
                pygame.draw.line(
                    self.canvas,
                    COLORS["gold"],
                    (120 + vector.x * 0.70, 58 + vector.y * 0.70),
                    (120 + vector.x, 58 + vector.y),
                    2,
                )
            hero = pygame.transform.scale(self.assets[112], (40, 40))
            self.canvas.blit(hero, hero.get_rect(center=(120, 59)))
            heading = "QUEST COMPLETE"
            sub = "Three chapters clear. Tiny hero, giant courage."
        else:
            heading = "THE LIGHT FADES"
            sub = "The forest waits for its hero."
        self.draw_text(self.canvas, heading, (120, 103), color, self.font_big, True)
        self.draw_text(self.canvas, sub, (120, 127), COLORS["cream"], self.font_small, True)
        self.draw_text(self.canvas, "ENTER", (120, 145), color, center=True)

    def present(self) -> None:
        if self.state == "title":
            self.render_title()
        elif self.state == "victory":
            self.render_end_screen(True)
        elif self.state == "gameover":
            self.render_end_screen(False)
        else:
            self.render_world()
        if self.flash > 0:
            overlay = pygame.Surface((INTERNAL_W, INTERNAL_H), pygame.SRCALPHA)
            overlay.fill((255, 245, 196, int(160 * min(1.0, self.flash * 4))))
            self.canvas.blit(overlay, (0, 0))

        target_w, target_h = self.window.get_size()
        scale = max(1, min(target_w // INTERNAL_W, target_h // INTERNAL_H))
        draw_size = (INTERNAL_W * scale, INTERNAL_H * scale)
        scaled = pygame.transform.scale(self.canvas, draw_size)
        x = (target_w - draw_size[0]) // 2
        y = (target_h - draw_size[1]) // 2
        self.window.fill((6, 8, 13))
        if self.shake > 0:
            x += random.randint(-round(self.shake), round(self.shake))
            y += random.randint(-round(self.shake), round(self.shake))
        self.window.blit(scaled, (x, y))
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 30)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.present()
        pygame.quit()


def run_smoke_test() -> None:
    game = Game()
    game.state = "play"
    for room_name in game.rooms:
        game.room_name = room_name
        game.player.x, game.player.y = 120, 80
        for _ in range(3):
            game.update(1 / 60)
            game.present()
        assert game.canvas.get_size() == (240, 160)
    assert len(game.assets) == 17
    assert len(game.rooms) == 13
    assert FONT_ENGINE_NAME == "meowfont0.1gba"
    assert all(len(room.tilemap) == 10 for room in game.rooms.values())
    pygame.quit()
    print("Smoke test passed: 13 rooms, meowfont0.1gba, render/update loop.")


if __name__ == "__main__":
    if SMOKE_TEST:
        run_smoke_test()
    else:
        Game().run()
