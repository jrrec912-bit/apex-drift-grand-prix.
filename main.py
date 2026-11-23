import math
import random
import sys
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
WIDTH, HEIGHT = 1100, 700
FPS = 60

ROAD_WIDTH = 2200          # Half-width in world units (-2200 to +2200)
SEGMENT_LENGTH = 200       # Length of each road slice along Z
RUMBLE_LENGTH = 3          # Alternating rumble strip frequency
DRAW_DISTANCE = 180        # Number of segments rendered ahead of the camera
CAMERA_HEIGHT = 1150
CAMERA_DEPTH = 0.84        # Field-of-view / perspective factor

# Controls
KEY_ACCEL = pygame.K_UP
KEY_BRAKE = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_BOOST = pygame.K_SPACE
KEY_DRIFT = pygame.K_LSHIFT
KEY_PAUSE = pygame.K_p
KEY_RESTART = pygame.K_r

# Color Palette
HUD_BG = (12, 16, 28)
HUD_ACCENT = (0, 229, 255)
HUD_WARN = (255, 72, 96)
HUD_GOLD = (255, 204, 51)
WHITE = (245, 248, 255)

# ==============================================================================
# ROSTER: CHARACTERS & CAR CLASSES
# ==============================================================================
CHARACTERS = [
    {
        "name": "KAI",
        "title": "Apex Prodigy",
        "bonus": "+12% Drift Charge",
        "helmet_col": (0, 229, 255),
        "visor_col": (15, 25, 45),
        "suit_col": (240, 245, 255),
        "drift_mult": 1.12,
        "boost_mult": 1.0,
        "grip_mult": 1.0,
        "speed_mult": 1.0,
    },
    {
        "name": "NOVA",
        "title": "Nitro Queen",
        "bonus": "+15% Nitro Power",
        "helmet_col": (255, 72, 130),
        "visor_col": (35, 15, 45),
        "suit_col": (45, 22, 60),
        "drift_mult": 1.0,
        "boost_mult": 1.15,
        "grip_mult": 1.0,
        "speed_mult": 1.0,
    },
    {
        "name": "REX",
        "title": "Iron Grip",
        "bonus": "+15% Corner Grip",
        "helmet_col": (255, 190, 40),
        "visor_col": (25, 25, 25),
        "suit_col": (35, 45, 38),
        "drift_mult": 1.0,
        "boost_mult": 1.0,
        "grip_mult": 1.15,
        "speed_mult": 1.0,
    },
    {
        "name": "VEX",
        "title": "Shadow Velocity",
        "bonus": "+6% Top Speed",
        "helmet_col": (165, 95, 255),
        "visor_col": (10, 10, 20),
        "suit_col": (22, 24, 34),
        "drift_mult": 1.0,
        "boost_mult": 1.0,
        "grip_mult": 1.0,
        "speed_mult": 1.06,
    },
]

CAR_TYPES = [
    {
        "name": "INTERCEPTOR GT",
        "class": "Balanced All-Rounder",
        "body_col": (0, 195, 255),
        "shade_col": (0, 105, 175),
        "accent_col": (255, 255, 255),
        "max_speed": 13400.0,
        "accel": 8000.0,
        "grip": 7.6,
        "drift_grip": 4.3,
        "stats": (8, 8, 8),  # Speed, Accel, Handling out of 10
    },
    {
        "name": "VULCAN V12",
        "class": "Hyper Top-Speed",
        "body_col": (255, 62, 68),
        "shade_col": (165, 24, 32),
        "accent_col": (255, 210, 60),
        "max_speed": 14600.0,
        "accel": 7200.0,
        "grip": 6.6,
        "drift_grip": 3.8,
        "stats": (10, 7, 6),
    },
    {
        "name": "SHOGUN RS",
        "class": "Drift & Corner Master",
        "body_col": (255, 185, 30),
        "shade_col": (180, 110, 12),
        "accent_col": (25, 28, 38),
        "max_speed": 12700.0,
        "accel": 8900.0,
        "grip": 9.0,
        "drift_grip": 5.2,
        "stats": (7, 9, 10),
    },
    {
        "name": "SPECTRE EV-X",
        "class": "Instant Torque",
        "body_col": (145, 75, 255),
        "shade_col": (82, 32, 165),
        "accent_col": (0, 245, 210),
        "max_speed": 13100.0,
        "accel": 9600.0,
        "grip": 8.1,
        "drift_grip": 4.6,
        "stats": (8, 10, 8),
    },
]

# ==============================================================================
# 5 CHAMPIONSHIP TRACKS
# ==============================================================================
TRACK_CONFIGS = [
    {
        "name": "1. EMERALD COAST",
        "subtitle": "Fast Sweeping Ocean Highway",
        "laps": 2,
        "sky_top": (14, 28, 64),
        "sky_horizon": (72, 125, 188),
        "mtn_far": (34, 58, 98),
        "mtn_near": (24, 44, 76),
        "road_a": (52, 56, 68),
        "road_b": (44, 48, 58),
        "grass_a": (28, 108, 62),
        "grass_b": (22, 88, 50),
        "rumble_a": (225, 50, 62),
        "rumble_b": (240, 242, 248),
        "prop_style": "coastal",
        "sections": [
            (55, 0.0, 0.0, 0.0, 1.0),
            (65, 0.0, 2.1, 320.0, 0.5),
            (55, 2.1, 2.1, 0.0, 1.0),
            (70, 2.1, -2.3, 450.0, 1.0),
            (60, -2.3, 0.0, 0.0, 1.0),
            (65, 0.0, 2.5, 380.0, 1.0),
            (55, 2.5, 0.0, 0.0, 1.0),
        ],
    },
    {
        "name": "2. SUNSET CANYON",
        "subtitle": "Red Rock Hairpins & Cliff Crests",
        "laps": 2,
        "sky_top": (48, 18, 42),
        "sky_horizon": (215, 102, 58),
        "mtn_far": (118, 48, 46),
        "mtn_near": (84, 32, 36),
        "road_a": (58, 52, 56),
        "road_b": (48, 43, 47),
        "grass_a": (156, 78, 42),
        "grass_b": (132, 64, 34),
        "rumble_a": (245, 195, 45),
        "rumble_b": (40, 36, 42),
        "prop_style": "desert",
        "sections": [
            (45, 0.0, 0.0, 0.0, 1.0),
            (65, 0.0, -3.1, 620.0, 1.0),
            (50, -3.1, -3.1, 0.0, 1.0),
            (75, -3.1, 3.3, 720.0, 1.5),
            (55, 3.3, 0.0, 280.0, 0.5),
            (65, 0.0, -2.9, 540.0, 1.0),
            (55, -2.9, 0.0, 0.0, 1.0),
        ],
    },
    {
        "name": "3. NEON TOKYO EXPRESS",
        "subtitle": "Midnight Technical S-Bends",
        "laps": 2,
        "sky_top": (8, 10, 26),
        "sky_horizon": (32, 24, 78),
        "mtn_far": (20, 18, 52),
        "mtn_near": (14, 14, 36),
        "road_a": (36, 40, 54),
        "road_b": (28, 32, 44),
        "grass_a": (22, 26, 48),
        "grass_b": (16, 20, 38),
        "rumble_a": (0, 229, 255),
        "rumble_b": (255, 55, 130),
        "prop_style": "cyber",
        "sections": [
            (50, 0.0, 0.0, 0.0, 1.0),
            (60, 0.0, 3.2, 260.0, 0.5),
            (65, 3.2, -3.4, 380.0, 1.0),
            (65, -3.4, 3.4, 380.0, 1.0),
            (55, 3.4, -2.6, 220.0, 0.5),
            (60, -2.6, 2.2, 300.0, 1.0),
            (50, 2.2, 0.0, 0.0, 1.0),
        ],
    },
    {
        "name": "4. GLACIER PEAK",
        "subtitle": "High-Altitude Alpine Switchbacks",
        "laps": 2,
        "sky_top": (18, 38, 68),
        "sky_horizon": (145, 185, 225),
        "mtn_far": (95, 125, 165),
        "mtn_near": (68, 96, 136),
        "road_a": (62, 70, 84),
        "road_b": (52, 60, 74),
        "grass_a": (210, 226, 242),
        "grass_b": (185, 205, 226),
        "rumble_a": (255, 85, 45),
        "rumble_b": (245, 248, 255),
        "prop_style": "alpine",
        "sections": [
            (45, 0.0, 0.0, 0.0, 1.0),
            (70, 0.0, -3.5, 780.0, 1.0),
            (55, -3.5, 3.5, 840.0, 1.5),
            (60, 3.5, 3.5, 0.0, 1.0),
            (70, 3.5, -3.2, 680.0, 1.0),
            (55, -3.2, 0.0, 320.0, 0.5),
        ],
    },
    {
        "name": "5. APEX GRAND FINALE",
        "subtitle": "Championship Pro Circuit",
        "laps": 3,
        "sky_top": (16, 14, 34),
        "sky_horizon": (92, 68, 138),
        "mtn_far": (44, 34, 76),
        "mtn_near": (30, 24, 54),
        "road_a": (48, 50, 62),
        "road_b": (38, 40, 52),
        "grass_a": (26, 86, 58),
        "grass_b": (20, 70, 46),
        "rumble_a": (255, 204, 51),
        "rumble_b": (220, 42, 58),
        "prop_style": "grand",
        "sections": [
            (55, 0.0, 0.0, 0.0, 1.0),
            (65, 0.0, 3.4, 650.0, 1.0),
            (75, 3.4, -3.8, 820.0, 1.5),
            (55, -3.8, -3.8, 0.0, 1.0),
            (75, -3.8, 3.8, 850.0, 1.5),
            (65, 3.8, -2.8, 520.0, 1.0),
            (60, -2.8, 2.4, 420.0, 1.0),
            (55, 2.4, 0.0, 0.0, 1.0),
        ],
    },
]

RIVAL_PROFILES = [
    {"name": "MAX", "body": (255, 76, 76), "shade": (170, 32, 32), "pace": 0.96},
    {"name": "SORA", "body": (255, 178, 36), "shade": (185, 115, 10), "pace": 0.93},
    {"name": "ZED", "body": (155, 89, 255), "shade": (95, 42, 185), "pace": 0.90},
    {"name": "LUNA", "body": (52, 211, 153), "shade": (20, 135, 95), "pace": 0.87},
    {"name": "BLAZE", "body": (255, 115, 45), "shade": (175, 65, 18), "pace": 0.84},
    {"name": "ECHO", "body": (96, 165, 250), "shade": (37, 99, 185), "pace": 0.81},
    {"name": "ACE", "body": (244, 114, 182), "shade": (165, 48, 110), "pace": 0.78},
]

CHAMPIONSHIP_POINTS = [15, 12, 10, 8, 6, 4, 2, 1]


def clamp(val, low, high):
    return max(low, min(high, val))


def lerp(a, b, t):
    return a + (b - a) * t


def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# ==============================================================================
# TOUCH CONTROLS MANAGER (MULTI-TOUCH & MOUSE SUPPORT)
# ==============================================================================
class TouchControls:
    def __init__(self):
        self.enabled = True
        self.active_fingers = {}  # finger_id -> (x, y)
        self.mouse_down = False
        self.mouse_pos = (0, 0)

        # Virtual control pads (rects)
        btn_y = HEIGHT - 150
        self.left_rect = pygame.Rect(24, btn_y, 112, 108)
        self.right_rect = pygame.Rect(150, btn_y, 112, 108)

        self.nitro_rect = pygame.Rect(WIDTH - 365, btn_y + 18, 96, 90)
        self.drift_rect = pygame.Rect(WIDTH - 255, btn_y + 18, 96, 90)
        self.accel_rect = pygame.Rect(WIDTH - 142, btn_y - 18, 118, 126)
        self.brake_rect = pygame.Rect(WIDTH - 142, btn_y - 112, 118, 82)
        self.pause_rect = pygame.Rect(WIDTH - 86, 86, 68, 38)

        self.state = {
            "left": False,
            "right": False,
            "accel": False,
            "brake": False,
            "drift": False,
            "boost": False,
        }

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
            fx = event.x * WIDTH
            fy = event.y * HEIGHT
            self.active_fingers[event.finger_id] = (fx, fy)
        elif event.type == pygame.FINGERUP:
            self.active_fingers.pop(event.finger_id, None)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_down = True
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEMOTION and self.mouse_down:
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_down = False

    def get_pointers(self):
        pts = list(self.active_fingers.values())
        if self.mouse_down:
            pts.append(self.mouse_pos)
        return pts

    def update(self):
        for k in self.state:
            self.state[k] = False

        if not self.enabled:
            return

        for px, py in self.get_pointers():
            if self.left_rect.inflate(16, 16).collidepoint(px, py):
                self.state["left"] = True
            if self.right_rect.inflate(16, 16).collidepoint(px, py):
                self.state["right"] = True
            if self.accel_rect.inflate(14, 14).collidepoint(px, py):
                self.state["accel"] = True
            if self.brake_rect.inflate(14, 14).collidepoint(px, py):
                self.state["brake"] = True
            if self.drift_rect.inflate(14, 14).collidepoint(px, py):
                self.state["drift"] = True
            if self.nitro_rect.inflate(14, 14).collidepoint(px, py):
                self.state["boost"] = True

    def draw(self, surface, font_md, font_sm):
        if not self.enabled:
            return

        buttons = [
            (self.left_rect, "<", self.state["left"], HUD_ACCENT),
            (self.right_rect, ">", self.state["right"], HUD_ACCENT),
            (self.brake_rect, "BRAKE", self.state["brake"], HUD_WARN),
            (self.accel_rect, "GAS", self.state["accel"], (52, 211, 153)),
            (self.drift_rect, "DRIFT", self.state["drift"], HUD_GOLD),
            (self.nitro_rect, "NITRO", self.state["boost"], HUD_ACCENT),
        ]

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for rect, label, active, col in buttons:
            alpha = 145 if active else 70
            border_alpha = 235 if active else 150
            pygame.draw.rect(overlay, (*col, alpha), rect, border_radius=14)
            pygame.draw.rect(overlay, (*col, border_alpha), rect, width=3, border_radius=14)

        surface.blit(overlay, (0, 0))

        for rect, label, active, col in buttons:
            fnt = font_md if len(label) <= 2 else font_sm
            txt = fnt.render(label, True, WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Pause touch button
        pygame.draw.rect(surface, HUD_BG, self.pause_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 78, 115), self.pause_rect, width=2, border_radius=8)
        p_txt = font_sm.render("PAUSE", True, WHITE)
        surface.blit(p_txt, (self.pause_rect.centerx - p_txt.get_width() // 2, self.pause_rect.centery - p_txt.get_height() // 2))


# ==============================================================================
# ROAD SEGMENT & TRACK GENERATOR
# ==============================================================================
class RoadSegment:
    def __init__(self, index, curve=0.0, y=0.0, road_color=None, grass_color=None, rumble_color=None):
        self.index = index
        self.z = index * SEGMENT_LENGTH
        self.curve = curve
        self.y = y
        self.road_color = road_color
        self.grass_color = grass_color
        self.rumble_color = rumble_color
        self.cars = []
        self.scenery = []

        self.screen_x = 0.0
        self.screen_y = 0.0
        self.screen_w = 0.0
        self.scale = 0.0
        self.clip = HEIGHT


class Track:
    def __init__(self, config):
        self.config = config
        self.segments = []
        self._build_circuit()

    def _add_section(self, num_segments, curve_start=0.0, curve_end=0.0, hill_amp=0.0, hill_cycles=1.0):
        start_idx = len(self.segments)
        cfg = self.config
        for i in range(num_segments):
            t = i / max(1, num_segments - 1)
            smooth_t = t * t * (3 - 2 * t)
            curve = lerp(curve_start, curve_end, smooth_t)
            y = math.sin(t * math.pi * 2 * hill_cycles) * hill_amp

            idx = start_idx + i
            is_rumble = (idx // RUMBLE_LENGTH) % 2 == 0

            road_col = cfg["road_a"] if is_rumble else cfg["road_b"]
            grass_col = cfg["grass_a"] if is_rumble else cfg["grass_b"]
            rumble_col = cfg["rumble_a"] if is_rumble else cfg["rumble_b"]

            seg = RoadSegment(idx, curve=curve, y=y, road_color=road_col, grass_color=grass_col, rumble_color=rumble_col)

            if idx % 6 == 0:
                kind = "sign" if abs(curve) > 1.6 else ("pylon" if idx % 18 == 0 else "tree")
                seg.scenery.append((-1, kind))
            if idx % 7 == 3:
                kind = "sign" if abs(curve) > 1.6 else ("pylon" if idx % 21 == 3 else "tree")
                seg.scenery.append((1, kind))

            self.segments.append(seg)

    def _build_circuit(self):
        for num_seg, c_start, c_end, h_amp, h_cyc in self.config["sections"]:
            self._add_section(num_seg, c_start, c_end, hill_amp=h_amp, hill_cycles=h_cyc)

    @property
    def length(self):
        return len(self.segments) * SEGMENT_LENGTH

    def get_segment(self, z):
        idx = int(z // SEGMENT_LENGTH) % len(self.segments)
        return self.segments[idx]


# ==============================================================================
# PARTICLES & ENTITIES
# ==============================================================================
class Particle:
    def __init__(self, x, y, vx, vy, size, color, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.life = life
        self.max_life = life

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha_ratio = clamp(self.life / self.max_life, 0.0, 1.0)
        radius = max(1, int(self.size * alpha_ratio))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class RivalCar:
    def __init__(self, profile, lane_offset, start_z, base_speed):
        self.name = profile["name"]
        self.x = lane_offset * ROAD_WIDTH * 0.65
        self.z = start_z
        self.total_distance = start_z
        self.base_speed = base_speed * profile["pace"]
        self.speed = self.base_speed
        self.width = 430
        self.body_col = profile["body"]
        self.shade_col = profile["shade"]
        self.accent_col = WHITE
        self.wobble_phase = random.uniform(0, math.tau)
        self.lane_timer = random.uniform(1.5, 4.0)
        self.target_x = self.x
        self.finished = False
        self.finish_time = 0.0

    def update(self, dt, track_length, player_total_dist, race_target_dist, race_time):
        if self.finished:
            self.z = (self.z + self.speed * 0.6 * dt) % track_length
            return

        self.wobble_phase += dt * 2.8
        self.lane_timer -= dt
        if self.lane_timer <= 0:
            self.lane_timer = random.uniform(2.2, 5.0)
            self.target_x = random.choice([-0.68, -0.25, 0.25, 0.68]) * ROAD_WIDTH

        self.x = lerp(self.x, self.target_x, clamp(2.0 * dt, 0.0, 1.0))

        # Competitive rubber-banding based on total race distance
        rel_dist = self.total_distance - player_total_dist
        rubber = 0.0
        if rel_dist > 15000:
            rubber = -1400.0
        elif rel_dist < -15000:
            rubber = 1350.0

        self.speed = clamp(self.base_speed + math.sin(self.wobble_phase) * 420 + rubber, 4500, 13400)
        dz = self.speed * dt
        self.total_distance += dz
        self.z = self.total_distance % track_length

        if self.total_distance >= race_target_dist:
            self.finished = True
            self.finish_time = race_time


class PlayerCar:
    def __init__(self, char_cfg, car_cfg, total_laps):
        self.char_cfg = char_cfg
        self.car_cfg = car_cfg
        self.total_laps = total_laps
        self.reset()

    def reset(self):
        self.x = 0.0
        self.z = 0.0
        self.total_distance = 0.0
        self.speed = 0.0

        self.max_speed = self.car_cfg["max_speed"] * self.char_cfg["speed_mult"]
        self.boost_max_speed = self.max_speed * 1.22
        self.accel = self.car_cfg["accel"]
        self.brake_force = 11800.0
        self.drag = 2100.0
        self.offroad_drag = 5600.0

        self.base_grip = self.car_cfg["grip"] * self.char_cfg["grip_mult"]
        self.drift_grip = self.car_cfg["drift_grip"] * self.char_cfg["grip_mult"]

        self.lateral_vel = 0.0
        self.steer_angle = 0.0
        self.drifting = False
        self.drift_charge = 0.0
        self.boost_fuel = 100.0
        self.boosting = False
        self.width = 440

        self.lap = 1
        self.halfway_passed = False
        self.lap_times = []
        self.current_lap_time = 0.0
        self.total_race_time = 0.0
        self.score = 0
        self.combo = 1.0
        self.near_miss_cooldown = 0.0

    def update(self, dt, controls, track, particles):
        self.current_lap_time += dt
        self.total_race_time += dt
        self.near_miss_cooldown = max(0.0, self.near_miss_cooldown - dt)

        accel_input = 1.0 if controls["accel"] else 0.0
        brake_input = 1.0 if controls["brake"] else 0.0
        steer_input = (1.0 if controls["right"] else 0.0) - (1.0 if controls["left"] else 0.0)

        # Boost logic
        want_boost = controls["boost"] and self.boost_fuel > 2.0 and self.speed > 1500
        if want_boost:
            self.boosting = True
            self.boost_fuel = max(0.0, self.boost_fuel - 32.0 * dt)
        else:
            self.boosting = False
            self.boost_fuel = min(100.0, self.boost_fuel + 8.5 * dt)

        # Speed integration
        top_spd = self.boost_max_speed if self.boosting else self.max_speed
        if accel_input > 0:
            boost_mult = (1.42 * self.char_cfg["boost_mult"]) if self.boosting else 1.0
            self.speed += self.accel * boost_mult * accel_input * dt
        if brake_input > 0:
            self.speed -= self.brake_force * brake_input * dt

        if accel_input == 0 and brake_input == 0:
            if self.speed > 0:
                self.speed = max(0.0, self.speed - self.drag * dt)
            elif self.speed < 0:
                self.speed = min(0.0, self.speed + self.drag * dt)

        offroad = abs(self.x) > ROAD_WIDTH
        if offroad and self.speed > 5500:
            self.speed = max(5500.0, self.speed - self.offroad_drag * dt)

        self.speed = clamp(self.speed, -1500.0, top_spd)

        current_seg = track.get_segment(self.z)
        speed_factor = clamp(abs(self.speed) / self.max_speed, 0.0, 1.0)

        # Drift mechanics
        self.drifting = controls["drift"] and abs(steer_input) > 0 and self.speed > 4500 and not offroad
        steer_authority = 1.35 if self.drifting else 1.0
        target_lat_vel = steer_input * 5500.0 * steer_authority * max(0.28, speed_factor)

        centrifugal = -current_seg.curve * (self.speed / self.max_speed) ** 2 * 2400.0
        if self.drifting:
            centrifugal *= 0.65

        grip = self.drift_grip if self.drifting else self.base_grip
        self.lateral_vel = lerp(self.lateral_vel, target_lat_vel + centrifugal, clamp(grip * dt, 0.0, 1.0))
        self.x += self.lateral_vel * dt

        target_lean = clamp(steer_input + (0.35 * steer_input if self.drifting else 0.0), -1.0, 1.0)
        self.steer_angle = lerp(self.steer_angle, target_lean, clamp(12.0 * dt, 0.0, 1.0))

        # Drift charge
        if self.drifting:
            self.drift_charge += dt * 0.78 * self.char_cfg["drift_mult"]
            self.boost_fuel = min(100.0, self.boost_fuel + 19.0 * self.char_cfg["drift_mult"] * dt)
            self.score += int(250 * dt * self.combo)
        elif self.drift_charge > 0.25:
            bonus = int(self.drift_charge * 800 * self.combo)
            self.score += bonus
            self.combo = min(5.0, self.combo + 0.15)
            self.drift_charge = 0.0
        else:
            self.drift_charge = 0.0
            self.combo = max(1.0, self.combo - 0.12 * dt)

        # Boundary clamp
        max_x = ROAD_WIDTH * 1.45
        if self.x > max_x:
            self.x = max_x
            self.lateral_vel = -abs(self.lateral_vel) * 0.35
            self.speed *= 0.94
        elif self.x < -max_x:
            self.x = -max_x
            self.lateral_vel = abs(self.lateral_vel) * 0.35
            self.speed *= 0.94

        # Advance Z & track total distance
        dz = self.speed * dt
        self.z += dz
        if dz > 0:
            self.total_distance += dz
            self.score += int(dz * 0.02 * self.combo)

        if self.z >= track.length:
            self.z -= track.length
            if self.halfway_passed:
                self.lap_times.append(self.current_lap_time)
                self.current_lap_time = 0.0
                self.score += int(2500 * self.combo)
                self.lap += 1
                self.halfway_passed = False
        elif self.z < 0:
            self.z += track.length

        if track.length * 0.45 < self.z < track.length * 0.65:
            self.halfway_passed = True

        # Particles
        if self.drifting and random.random() < 0.75:
            for side in (-34, 34):
                particles.append(
                    Particle(
                        WIDTH * 0.5 + side + random.uniform(-6, 6),
                        HEIGHT - 68 + random.uniform(-4, 4),
                        random.uniform(-45, 45) - self.lateral_vel * 0.02,
                        random.uniform(-60, -15),
                        random.uniform(5, 10),
                        (220, 225, 235) if not offroad else (130, 95, 55),
                        random.uniform(0.25, 0.5),
                    )
                )
        if self.boosting and random.random() < 0.85:
            for side in (-16, 16):
                particles.append(
                    Particle(
                        WIDTH * 0.5 + side + random.uniform(-4, 4),
                        HEIGHT - 64,
                        random.uniform(-25, 25),
                        random.uniform(25, 85),
                        random.uniform(4, 8),
                        random.choice([(0, 229, 255), (255, 180, 40), (255, 255, 255)]),
                        random.uniform(0.15, 0.3),
                    )
                )


# ==============================================================================
# MAIN GAME & CHAMPIONSHIP MANAGER
# ==============================================================================
class RacingGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("APEX DRIFT GRAND PRIX — 5-Track Championship")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_xl = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_lg = pygame.font.SysFont("consolas", 26, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 19, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 14, bold=True)

        self.touch = TouchControls()

        # Selection & Championship State
        self.selected_char_idx = 0
        self.selected_car_idx = 0
        self.selected_track_idx = 0
        self.championship_mode = True
        self.standings = {}  # racer_name -> points
        self.last_race_results = []

        self.state = "SELECT"  # SELECT | RACING | PAUSED | RACE_RESULTS | CHAMPIONSHIP_PODIUM
        self.ui_buttons = []   # List of (rect, action_callback)

        self.track = None
        self.player = None
        self.rivals = []
        self.particles = []
        self.horizon_scroll = 0.0
        self.countdown_timer = 0.0

        self._reset_standings()
        self._load_track(0)

    def _reset_standings(self):
        player_name = f"{CHARACTERS[self.selected_char_idx]['name']} (YOU)"
        self.standings = {player_name: 0}
        for rp in RIVAL_PROFILES:
            self.standings[rp["name"]] = 0

    def _load_track(self, track_idx):
        self.selected_track_idx = track_idx % len(TRACK_CONFIGS)
        cfg = TRACK_CONFIGS[self.selected_track_idx]
        self.track = Track(cfg)
        self.player = PlayerCar(
            CHARACTERS[self.selected_char_idx],
            CAR_TYPES[self.selected_car_idx],
            cfg["laps"],
        )
        self.particles.clear()
        self._spawn_rivals()
        self.countdown_timer = 2.4

    def _spawn_rivals(self):
        self.rivals.clear()
        lanes = [-0.65, 0.0, 0.65]
        # Scale AI difficulty slightly across the 5 tracks
        base_speed = 11400.0 + self.selected_track_idx * 420.0
        for i, profile in enumerate(RIVAL_PROFILES):
            start_z = (i + 1) * 650.0
            lane = lanes[i % len(lanes)]
            self.rivals.append(RivalCar(profile, lane, start_z, base_speed))

    def start_championship(self):
        self._reset_standings()
        self._load_track(0)
        self.state = "RACING"

    def start_single_race(self):
        self._load_track(self.selected_track_idx)
        self.state = "RACING"

    def _finalize_race(self):
        player_name = f"{CHARACTERS[self.selected_char_idx]['name']} (YOU)"
        racers = [
            {
                "name": player_name,
                "dist": self.player.total_distance,
                "time": self.player.total_race_time,
                "is_player": True,
            }
        ]
        for r in self.rivals:
            racers.append(
                {
                    "name": r.name,
                    "dist": r.total_distance,
                    "time": r.finish_time if r.finished else self.player.total_race_time + 2.0,
                    "is_player": False,
                }
            )

        racers.sort(key=lambda x: x["dist"], reverse=True)
        self.last_race_results = []
        for rank, entry in enumerate(racers):
            pts = CHAMPIONSHIP_POINTS[rank] if rank < len(CHAMPIONSHIP_POINTS) else 0
            if entry["name"] not in self.standings:
                self.standings[entry["name"]] = 0
            self.standings[entry["name"]] += pts
            self.last_race_results.append(
                {
                    "rank": rank + 1,
                    "name": entry["name"],
                    "pts": pts,
                    "total_pts": self.standings[entry["name"]],
                    "is_player": entry["is_player"],
                }
            )

        self.state = "RACE_RESULTS"

    def _get_player_rank(self):
        rank = 1
        for r in self.rivals:
            if r.total_distance > self.player.total_distance:
                rank += 1
        return rank

    # ==========================================================================
    # RENDERING: TRACK & CARS
    # ==========================================================================
    def _project_and_render_track(self):
        cfg = self.track.config
        sky_top = cfg["sky_top"]
        sky_hor = cfg["sky_horizon"]

        for y in range(0, HEIGHT // 2 + 40, 4):
            t = y / (HEIGHT // 2 + 40)
            col = (
                int(lerp(sky_top[0], sky_hor[0], t)),
                int(lerp(sky_top[1], sky_hor[1], t)),
                int(lerp(sky_top[2], sky_hor[2], t)),
            )
            pygame.draw.rect(self.screen, col, (0, y, WIDTH, 4))

        base_seg = self.track.get_segment(self.player.z)
        self.horizon_scroll = (self.horizon_scroll + base_seg.curve * (self.player.speed / 12000.0) * 18) % WIDTH

        for layer, (col, height_scale, scroll_mult, step) in enumerate([
            (cfg["mtn_far"], 65, 0.45, 110),
            (cfg["mtn_near"], 42, 0.85, 80),
        ]):
            pts = [(0, HEIGHT // 2)]
            offset = -(self.horizon_scroll * scroll_mult) % step
            x = offset - step
            while x <= WIDTH + step * 2:
                peak = abs(math.sin((x + offset) * 0.008 + layer * 2.1)) * height_scale + 12
                pts.append((x, HEIGHT // 2 - peak))
                x += step * 0.5
            pts.append((WIDTH, HEIGHT // 2))
            pygame.draw.polygon(self.screen, col, pts)

        for seg in self.track.segments:
            seg.cars.clear()
        for rival in self.rivals:
            seg = self.track.get_segment(rival.z)
            seg.cars.append(rival)

        n_segs = len(self.track.segments)
        start_idx = int(self.player.z // SEGMENT_LENGTH)
        cam_x = self.player.x
        cam_y = self.track.segments[start_idx % n_segs].y + CAMERA_HEIGHT

        x_pos = 0.0
        dx = 0.0
        max_y = HEIGHT
        projected = []

        for n in range(1, DRAW_DISTANCE):
            seg_idx = (start_idx + n) % n_segs
            seg = self.track.segments[seg_idx]
            wrapped = seg_idx < start_idx
            seg_z = seg.z + (self.track.length if wrapped else 0.0)
            rel_z = seg_z - self.player.z
            if rel_z <= 0:
                continue

            x_pos += dx
            dx += seg.curve * 0.42

            scale = CAMERA_DEPTH * (HEIGHT * 0.5) / rel_z
            screen_x = WIDTH * 0.5 + scale * (x_pos - cam_x)
            screen_y = HEIGHT * 0.5 - scale * (seg.y - cam_y)
            screen_w = scale * ROAD_WIDTH

            seg.screen_x = screen_x
            seg.screen_y = screen_y
            seg.screen_w = screen_w
            seg.scale = scale
            seg.clip = max_y

            if screen_y < max_y:
                projected.append(seg)
                max_y = screen_y

        for i in range(len(projected) - 1, 0, -1):
            far = projected[i]
            near = projected[i - 1]
            if near.screen_y <= far.screen_y:
                continue

            y1, y2 = int(far.screen_y), int(near.screen_y)
            x1, w1 = far.screen_x, far.screen_w
            x2, w2 = near.screen_x, near.screen_w

            pygame.draw.rect(self.screen, near.grass_color, (0, y1, WIDTH, max(1, y2 - y1)))

            r1, r2 = w1 * 1.14, w2 * 1.14
            pygame.draw.polygon(self.screen, near.rumble_color, [(x1 - r1, y1), (x1 + r1, y1), (x2 + r2, y2), (x2 - r2, y2)])
            pygame.draw.polygon(self.screen, near.road_color, [(x1 - w1, y1), (x1 + w1, y1), (x2 + w2, y2), (x2 - w2, y2)])

            # Start/Finish checkered line near index 0
            if near.index < 3:
                pygame.draw.polygon(self.screen, WHITE, [(x1 - w1, y1), (x1 + w1, y1), (x2 + w2, y2), (x2 - w2, y2)])
            elif (near.index // 2) % 2 == 0:
                for lane_ratio in (-0.33, 0.0, 0.33):
                    lx1 = x1 + w1 * lane_ratio
                    lx2 = x2 + w2 * lane_ratio
                    lw1 = max(1.0, w1 * 0.022)
                    lw2 = max(1.0, w2 * 0.022)
                    line_col = HUD_GOLD if lane_ratio == 0.0 else (215, 222, 235)
                    pygame.draw.polygon(
                        self.screen,
                        line_col,
                        [(lx1 - lw1, y1), (lx1 + lw1, y1), (lx2 + lw2, y2), (lx2 - lw2, y2)],
                    )

        prop_style = cfg["prop_style"]
        for i in range(len(projected) - 1, -1, -1):
            seg = projected[i]
            if seg.scale <= 0:
                continue

            for side, kind in seg.scenery:
                prop_x = seg.screen_x + side * seg.screen_w * 1.38
                prop_y = seg.screen_y
                if prop_y > seg.clip:
                    continue
                h = seg.scale * 950
                w = seg.scale * 260
                if h < 3 or h > 420:
                    continue

                if kind == "tree":
                    if prop_style == "desert":
                        # Cactus
                        pygame.draw.rect(self.screen, (42, 138, 68), (prop_x - w * 0.14, prop_y - h * 0.72, w * 0.28, h * 0.72), border_radius=4)
                        pygame.draw.rect(self.screen, (42, 138, 68), (prop_x - w * 0.36, prop_y - h * 0.52, w * 0.72, h * 0.14), border_radius=3)
                    elif prop_style == "cyber":
                        # Neon light tower
                        pygame.draw.rect(self.screen, (28, 34, 58), (prop_x - w * 0.12, prop_y - h * 0.85, w * 0.24, h * 0.85))
                        neon_c = HUD_ACCENT if side < 0 else (255, 55, 130)
                        pygame.draw.rect(self.screen, neon_c, (prop_x - w * 0.16, prop_y - h * 0.82, w * 0.32, h * 0.25))
                    elif prop_style == "alpine":
                        # Snow pine
                        pygame.draw.polygon(self.screen, (28, 86, 66), [(prop_x - w * 0.5, prop_y - h * 0.15), (prop_x + w * 0.5, prop_y - h * 0.15), (prop_x, prop_y - h * 0.85)])
                        pygame.draw.polygon(self.screen, WHITE, [(prop_x - w * 0.26, prop_y - h * 0.48), (prop_x + w * 0.26, prop_y - h * 0.48), (prop_x, prop_y - h * 0.85)])
                    else:
                        pygame.draw.rect(self.screen, (82, 52, 32), (prop_x - w * 0.14, prop_y - h * 0.35, w * 0.28, h * 0.35))
                        pygame.draw.circle(self.screen, (34, 130, 62), (int(prop_x), int(prop_y - h * 0.55)), max(2, int(w * 0.55)))
                elif kind == "sign":
                    pygame.draw.rect(self.screen, (180, 185, 195), (prop_x - w * 0.06, prop_y - h * 0.65, w * 0.12, h * 0.65))
                    pygame.draw.rect(self.screen, HUD_WARN, (prop_x - w * 0.4, prop_y - h * 0.85, w * 0.8, h * 0.32))
                else:
                    pygame.draw.polygon(
                        self.screen,
                        (255, 120, 35),
                        [(prop_x - w * 0.22, prop_y), (prop_x + w * 0.22, prop_y), (prop_x, prop_y - h * 0.55)],
                    )

            for rival in seg.cars:
                car_screen_x = seg.screen_x + seg.scale * rival.x
                car_screen_y = seg.screen_y
                if car_screen_y > seg.clip:
                    continue
                cw = seg.scale * rival.width
                ch = cw * 0.58
                if cw < 5 or cw > 380:
                    continue
                self._draw_car_sprite(
                    car_screen_x,
                    car_screen_y,
                    cw,
                    ch,
                    rival.body_col,
                    rival.shade_col,
                    rival.accent_col,
                    lean=0.0,
                    is_player=False,
                )

    def _draw_car_sprite(self, cx, bottom_y, w, h, body_col, shade_col, accent_col=WHITE, lean=0.0, is_player=False, char_cfg=None):
        top_y = bottom_y - h
        shift_x = lean * w * 0.14

        pygame.draw.ellipse(self.screen, (12, 14, 20), (cx - w * 0.54, bottom_y - h * 0.14, w * 1.08, h * 0.22))

        tw = w * 0.22
        th = h * 0.34
        for tx in (cx - w * 0.52, cx + w * 0.30):
            pygame.draw.rect(self.screen, (20, 22, 28), (tx, bottom_y - th * 0.9, tw, th), border_radius=3)

        body_rect = pygame.Rect(cx - w * 0.46 + shift_x * 0.5, top_y + h * 0.22, w * 0.92, h * 0.62)
        pygame.draw.rect(self.screen, body_col, body_rect, border_radius=max(3, int(w * 0.08)))

        # Racing stripe
        stripe_rect = pygame.Rect(cx - w * 0.12 + shift_x * 0.5, top_y + h * 0.24, w * 0.24, h * 0.58)
        pygame.draw.rect(self.screen, accent_col, stripe_rect, border_radius=2)

        cabin_rect = pygame.Rect(cx - w * 0.34 + shift_x, top_y + h * 0.04, w * 0.68, h * 0.34)
        pygame.draw.rect(self.screen, shade_col, cabin_rect, border_radius=max(2, int(w * 0.06)))
        glass_rect = pygame.Rect(cx - w * 0.28 + shift_x, top_y + h * 0.09, w * 0.56, h * 0.18)
        pygame.draw.rect(self.screen, (35, 50, 75), glass_rect, border_radius=2)

        # Visible driver helmet silhouette inside rear window
        if char_cfg is not None:
            hx = int(cx + shift_x * 1.1)
            hy = int(top_y + h * 0.18)
            hr = max(3, int(w * 0.085))
            pygame.draw.circle(self.screen, char_cfg["helmet_col"], (hx, hy), hr)

        wing_y = top_y + h * 0.16 if is_player else top_y + h * 0.25
        pygame.draw.rect(self.screen, shade_col, (cx - w * 0.48 + shift_x * 0.4, wing_y, w * 0.96, h * 0.1))

        light_col = (255, 45, 70) if is_player else (210, 35, 50)
        for lx in (cx - w * 0.38 + shift_x * 0.5, cx + w * 0.22 + shift_x * 0.5):
            pygame.draw.rect(self.screen, light_col, (lx, top_y + h * 0.52, w * 0.16, h * 0.11), border_radius=2)

        if is_player and self.player and self.player.boosting:
            flame_h = h * (0.28 + 0.12 * math.sin(pygame.time.get_ticks() * 0.05))
            for fx in (cx - w * 0.22, cx + w * 0.22):
                pygame.draw.polygon(
                    self.screen,
                    HUD_ACCENT,
                    [(fx - w * 0.08, bottom_y - h * 0.15), (fx + w * 0.08, bottom_y - h * 0.15), (fx, bottom_y - h * 0.15 + flame_h)],
                )

    def _draw_driver_portrait(self, surface, cx, cy, radius, char_cfg):
        pygame.draw.circle(surface, (24, 32, 54), (cx, cy), radius + 4)
        pygame.draw.circle(surface, char_cfg["helmet_col"], (cx, cy), radius)
        # Visor
        visor_rect = pygame.Rect(cx - radius * 0.72, cy - radius * 0.22, radius * 1.44, radius * 0.48)
        pygame.draw.rect(surface, char_cfg["visor_col"], visor_rect, border_radius=6)
        # Visor shine
        pygame.draw.line(surface, WHITE, (visor_rect.x + 6, visor_rect.y + 5), (visor_rect.right - 10, visor_rect.y + 5), 2)

    # ==========================================================================
    # RENDERING: HUD & SCREENS
    # ==========================================================================
    def _draw_speed_lines(self):
        ratio = clamp((self.player.speed - 9500) / 6700, 0.0, 1.0)
        if ratio <= 0:
            return
        count = int(12 + ratio * 24)
        for i in range(count):
            angle = (i * 2.39996 + pygame.time.get_ticks() * 0.004) % math.tau
            r_inner = 190 + (i * 37) % 140
            r_outer = r_inner + 45 + ratio * 95
            x1 = WIDTH * 0.5 + math.cos(angle) * r_inner
            y1 = HEIGHT * 0.5 + math.sin(angle) * r_inner * 0.75
            x2 = WIDTH * 0.5 + math.cos(angle) * r_outer
            y2 = HEIGHT * 0.5 + math.sin(angle) * r_outer * 0.75
            pygame.draw.line(self.screen, (200, 235, 255), (x1, y1), (x2, y2), 1)

    def _draw_hud(self):
        pygame.draw.rect(self.screen, HUD_BG, (18, 14, WIDTH - 36, 62), border_radius=8)
        pygame.draw.rect(self.screen, (36, 48, 76), (18, 14, WIDTH - 36, 62), width=2, border_radius=8)

        rank = self._get_player_rank()
        rank_col = HUD_GOLD if rank == 1 else (HUD_ACCENT if rank <= 3 else WHITE)
        rank_txt = self.font_lg.render(f"POS {ordinal(rank)}/8", True, rank_col)

        lap_display = min(self.player.lap, self.player.total_laps)
        lap_txt = self.font_md.render(f"LAP {lap_display}/{self.player.total_laps}", True, WHITE)
        track_lbl = self.font_sm.render(f"ROUND {self.selected_track_idx + 1}/5: {self.track.config['name'][3:]}", True, HUD_ACCENT)
        kmh = int(abs(self.player.speed) / 48.0)
        spd_txt = self.font_md.render(f"{kmh:03d} KM/H", True, HUD_GOLD if self.player.boosting else WHITE)

        self.screen.blit(rank_txt, (32, 30))
        self.screen.blit(lap_txt, (215, 34))
        self.screen.blit(track_lbl, (345, 22))
        self.screen.blit(spd_txt, (345, 45))

        # Nitro bar
        boost_label = self.font_sm.render("NITRO", True, HUD_ACCENT)
        self.screen.blit(boost_label, (790, 22))
        pygame.draw.rect(self.screen, (26, 34, 54), (790, 42, 268, 20), border_radius=4)
        fill_w = int(268 * clamp(self.player.boost_fuel / 100.0, 0.0, 1.0))
        bar_col = HUD_ACCENT if not self.player.boosting else WHITE
        if fill_w > 0:
            pygame.draw.rect(self.screen, bar_col, (790, 42, fill_w, 20), border_radius=4)

        if self.player.drifting:
            drift_lbl = self.font_md.render("DRIFTING!", True, HUD_GOLD)
            self.screen.blit(drift_lbl, (WIDTH // 2 - drift_lbl.get_width() // 2, 88))

        if self.countdown_timer > 0:
            cd_num = math.ceil(self.countdown_timer)
            cd_txt = self.font_xl.render(str(cd_num), True, HUD_GOLD)
            self.screen.blit(cd_txt, (WIDTH // 2 - cd_txt.get_width() // 2, HEIGHT // 2 - 80))

    def _draw_selection_screen(self):
        self.ui_buttons.clear()
        self.screen.fill((10, 14, 26))

        title = self.font_xl.render("APEX DRIFT GRAND PRIX", True, WHITE)
        sub = self.font_sm.render("TAP OR CLICK TO CHOOSE DRIVER, CAR & TRACK  •  TOUCH CONTROLS ENABLED", True, HUD_ACCENT)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 18))
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 66))

        # 1. CHARACTER SELECTION ROW
        lbl1 = self.font_md.render("1. SELECT DRIVER", True, HUD_GOLD)
        self.screen.blit(lbl1, (36, 98))
        for i, ch in enumerate(CHARACTERS):
            card = pygame.Rect(36 + i * 260, 126, 246, 118)
            selected = i == self.selected_char_idx
            pygame.draw.rect(self.screen, (20, 28, 48) if selected else HUD_BG, card, border_radius=10)
            pygame.draw.rect(self.screen, HUD_ACCENT if selected else (40, 52, 82), card, width=3 if selected else 2, border_radius=10)
            self._draw_driver_portrait(self.screen, card.x + 42, card.centery, 26, ch)

            n_surf = self.font_md.render(ch["name"], True, WHITE)
            t_surf = self.font_sm.render(ch["title"], True, (175, 190, 215))
            b_surf = self.font_sm.render(ch["bonus"], True, HUD_GOLD)
            self.screen.blit(n_surf, (card.x + 82, card.y + 18))
            self.screen.blit(t_surf, (card.x + 82, card.y + 46))
            self.screen.blit(b_surf, (card.x + 82, card.y + 74))

            self.ui_buttons.append((card, lambda idx=i: setattr(self, "selected_char_idx", idx)))

        # 2. CAR CLASS SELECTION ROW
        lbl2 = self.font_md.render("2. SELECT CAR CLASS", True, HUD_GOLD)
        self.screen.blit(lbl2, (36, 260))
        for i, car in enumerate(CAR_TYPES):
            card = pygame.Rect(36 + i * 260, 288, 246, 175)
            selected = i == self.selected_car_idx
            pygame.draw.rect(self.screen, (20, 28, 48) if selected else HUD_BG, card, border_radius=10)
            pygame.draw.rect(self.screen, HUD_ACCENT if selected else (40, 52, 82), card, width=3 if selected else 2, border_radius=10)

            self._draw_car_sprite(card.centerx, card.y + 66, 92, 52, car["body_col"], car["shade_col"], car["accent_col"])
            cn = self.font_md.render(car["name"], True, WHITE)
            cc = self.font_sm.render(car["class"], True, HUD_ACCENT)
            self.screen.blit(cn, (card.centerx - cn.get_width() // 2, card.y + 74))
            self.screen.blit(cc, (card.centerx - cc.get_width() // 2, card.y + 98))

            # Mini stat bars
            for s_idx, (s_name, s_val) in enumerate(zip(("SPD", "ACC", "HND"), car["stats"])):
                sy = card.y + 122 + s_idx * 15
                st = self.font_sm.render(s_name, True, (180, 195, 220))
                self.screen.blit(st, (card.x + 16, sy - 2))
                pygame.draw.rect(self.screen, (30, 38, 60), (card.x + 54, sy + 2, 172, 8), border_radius=3)
                pygame.draw.rect(self.screen, HUD_GOLD, (card.x + 54, sy + 2, int(172 * (s_val / 10.0)), 8), border_radius=3)

            self.ui_buttons.append((card, lambda idx=i: setattr(self, "selected_car_idx", idx)))

        # 3. TRACK SELECTION ROW (5 TRACKS)
        lbl3 = self.font_md.render("3. SELECT STARTING TRACK (5 CIRCUITS)", True, HUD_GOLD)
        self.screen.blit(lbl3, (36, 480))
        for i, trk in enumerate(TRACK_CONFIGS):
            card = pygame.Rect(36 + i * 208, 508, 196, 86)
            selected = i == self.selected_track_idx
            pygame.draw.rect(self.screen, (20, 28, 48) if selected else HUD_BG, card, border_radius=10)
            pygame.draw.rect(self.screen, HUD_GOLD if selected else (40, 52, 82), card, width=3 if selected else 2, border_radius=10)

            tn = self.font_sm.render(trk["name"], True, WHITE)
            ts = self.font_sm.render(f"{trk['laps']} Laps", True, HUD_ACCENT)
            self.screen.blit(tn, (card.x + 12, card.y + 18))
            self.screen.blit(ts, (card.x + 12, card.y + 48))

            self.ui_buttons.append((card, lambda idx=i: setattr(self, "selected_track_idx", idx)))

        # START BUTTONS
        gp_btn = pygame.Rect(WIDTH // 2 - 330, 614, 310, 62)
        sr_btn = pygame.Rect(WIDTH // 2 + 20, 614, 310, 62)

        pygame.draw.rect(self.screen, HUD_GOLD, gp_btn, border_radius=12)
        gp_txt = self.font_lg.render("5-TRACK GRAND PRIX", True, (12, 16, 28))
        self.screen.blit(gp_txt, (gp_btn.centerx - gp_txt.get_width() // 2, gp_btn.centery - gp_txt.get_height() // 2))
        self.ui_buttons.append((gp_btn, self._btn_start_gp))

        pygame.draw.rect(self.screen, HUD_ACCENT, sr_btn, border_radius=12)
        sr_txt = self.font_lg.render("SINGLE RACE", True, (12, 16, 28))
        self.screen.blit(sr_txt, (sr_btn.centerx - sr_txt.get_width() // 2, sr_btn.centery - sr_txt.get_height() // 2))
        self.ui_buttons.append((sr_btn, self._btn_start_single))

    def _btn_start_gp(self):
        self.championship_mode = True
        self.start_championship()

    def _btn_start_single(self):
        self.championship_mode = False
        self.start_single_race()

    def _draw_results_overlay(self):
        self.ui_buttons.clear()
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((8, 12, 22, 210))
        self.screen.blit(dim, (0, 0))

        panel = pygame.Rect(WIDTH // 2 - 380, 46, 760, 608)
        pygame.draw.rect(self.screen, HUD_BG, panel, border_radius=14)
        pygame.draw.rect(self.screen, HUD_ACCENT, panel, width=2, border_radius=14)

        is_final_gp = self.championship_mode and self.selected_track_idx >= len(TRACK_CONFIGS) - 1
        header = "CHAMPIONSHIP FINAL STANDINGS!" if is_final_gp else f"{self.track.config['name']} — RESULTS"
        h_surf = self.font_lg.render(header, True, HUD_GOLD)
        self.screen.blit(h_surf, (panel.centerx - h_surf.get_width() // 2, panel.y + 22))

        # Table headers
        y0 = panel.y + 72
        self.screen.blit(self.font_sm.render("POS", True, HUD_ACCENT), (panel.x + 40, y0))
        self.screen.blit(self.font_sm.render("RACER", True, HUD_ACCENT), (panel.x + 130, y0))
        self.screen.blit(self.font_sm.render("RACE PTS", True, HUD_ACCENT), (panel.x + 430, y0))
        self.screen.blit(self.font_sm.render("CUP TOTAL", True, HUD_ACCENT), (panel.x + 580, y0))

        # Sort by championship total if final GP, else race finish order
        rows = list(self.last_race_results)
        if is_final_gp:
            rows.sort(key=lambda r: r["total_pts"], reverse=True)

        for idx, row in enumerate(rows):
            ry = y0 + 34 + idx * 46
            row_rect = pygame.Rect(panel.x + 28, ry - 6, panel.width - 56, 38)
            if row["is_player"]:
                pygame.draw.rect(self.screen, (24, 44, 72), row_rect, border_radius=6)
                pygame.draw.rect(self.screen, HUD_ACCENT, row_rect, width=1, border_radius=6)

            col = HUD_GOLD if idx == 0 else (HUD_ACCENT if row["is_player"] else WHITE)
            self.screen.blit(self.font_md.render(ordinal(idx + 1), True, col), (panel.x + 40, ry))
            self.screen.blit(self.font_md.render(row["name"], True, col), (panel.x + 130, ry))
            self.screen.blit(self.font_md.render(f"+{row['pts']}", True, col), (panel.x + 455, ry))
            self.screen.blit(self.font_md.render(f"{row['total_pts']} PTS", True, col), (panel.x + 585, ry))

        # Action buttons
        next_btn = pygame.Rect(panel.centerx - 310, panel.bottom - 82, 290, 56)
        menu_btn = pygame.Rect(panel.centerx + 20, panel.bottom - 82, 290, 56)

        if self.championship_mode and not is_final_gp:
            pygame.draw.rect(self.screen, HUD_GOLD, next_btn, border_radius=10)
            nt = self.font_md.render("NEXT TRACK ->", True, (12, 16, 28))
            self.screen.blit(nt, (next_btn.centerx - nt.get_width() // 2, next_btn.centery - nt.get_height() // 2))
            self.ui_buttons.append((next_btn, self._advance_next_track))
        else:
            pygame.draw.rect(self.screen, HUD_GOLD, next_btn, border_radius=10)
            nt = self.font_md.render("RACE AGAIN", True, (12, 16, 28))
            self.screen.blit(nt, (next_btn.centerx - nt.get_width() // 2, next_btn.centery - nt.get_height() // 2))
            self.ui_buttons.append((next_btn, self._replay_mode))

        pygame.draw.rect(self.screen, HUD_ACCENT, menu_btn, border_radius=10)
        mt = self.font_md.render("GARAGE / MENU", True, (12, 16, 28))
        self.screen.blit(mt, (menu_btn.centerx - mt.get_width() // 2, menu_btn.centery - mt.get_height() // 2))
        self.ui_buttons.append((menu_btn, lambda: setattr(self, "state", "SELECT")))

    def _advance_next_track(self):
        self._load_track(self.selected_track_idx + 1)
        self.state = "RACING"

    def _replay_mode(self):
        if self.championship_mode:
            self.start_championship()
        else:
            self.start_single_race()

    def _draw_pause_overlay(self):
        self.ui_buttons.clear()
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((8, 12, 22, 195))
        self.screen.blit(dim, (0, 0))

        panel = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 140, 520, 280)
        pygame.draw.rect(self.screen, HUD_BG, panel, border_radius=12)
        pygame.draw.rect(self.screen, HUD_ACCENT, panel, width=2, border_radius=12)

        t = self.font_xl.render("PAUSED", True, WHITE)
        self.screen.blit(t, (panel.centerx - t.get_width() // 2, panel.y + 30))

        res_btn = pygame.Rect(panel.centerx - 180, panel.y + 105, 360, 54)
        menu_btn = pygame.Rect(panel.centerx - 180, panel.y + 178, 360, 54)

        pygame.draw.rect(self.screen, HUD_GOLD, res_btn, border_radius=10)
        rt = self.font_lg.render("RESUME RACE", True, (12, 16, 28))
        self.screen.blit(rt, (res_btn.centerx - rt.get_width() // 2, res_btn.centery - rt.get_height() // 2))
        self.ui_buttons.append((res_btn, lambda: setattr(self, "state", "RACING")))

        pygame.draw.rect(self.screen, HUD_ACCENT, menu_btn, border_radius=10)
        mt = self.font_lg.render("EXIT TO GARAGE", True, (12, 16, 28))
        self.screen.blit(mt, (menu_btn.centerx - mt.get_width() // 2, menu_btn.centery - mt.get_height() // 2))
        self.ui_buttons.append((menu_btn, lambda: setattr(self, "state", "SELECT")))

    # ==========================================================================
    # COLLISIONS, UPDATE & MAIN LOOP
    # ==========================================================================
    def _handle_collisions(self):
        for rival in self.rivals:
            dz = abs(rival.z - self.player.z)
            if dz > self.track.length * 0.5:
                dz = self.track.length - dz

            dx = rival.x - self.player.x
            if dz < 260:
                if abs(dx) < 390:
                    push = 420.0 if dx < 0 else -420.0
                    self.player.lateral_vel += push * 4.5
                    self.player.speed *= 0.88
                    self.player.combo = 1.0
                    self.player.drift_charge = 0.0
                    rival.x -= push * 0.25
                elif abs(dx) < 620 and self.player.near_miss_cooldown <= 0 and abs(self.player.speed) > 6500:
                    self.player.near_miss_cooldown = 1.1
                    self.player.boost_fuel = min(100.0, self.player.boost_fuel + 12.0)
                    self.player.combo = min(5.0, self.player.combo + 0.35)
                    self.player.score += int(500 * self.player.combo)

    def _gather_controls(self):
        keys = pygame.key.get_pressed()
        self.touch.update()
        t = self.touch.state
        return {
            "left": keys[KEY_LEFT] or t["left"],
            "right": keys[KEY_RIGHT] or t["right"],
            "accel": keys[KEY_ACCEL] or t["accel"],
            "brake": keys[KEY_BRAKE] or t["brake"],
            "drift": keys[KEY_DRIFT] or t["drift"],
            "boost": keys[KEY_BOOST] or t["boost"],
        }

    def update(self, dt):
        if self.state != "RACING":
            return

        if self.countdown_timer > 0:
            self.countdown_timer = max(0.0, self.countdown_timer - dt)
            return

        controls = self._gather_controls()
        self.player.update(dt, controls, self.track, self.particles)

        race_target_dist = self.track.length * self.player.total_laps
        for rival in self.rivals:
            rival.update(dt, self.track.length, self.player.total_distance, race_target_dist, self.player.total_race_time)

        self._handle_collisions()
        self.particles = [p for p in self.particles if p.update(dt)]

        if self.player.lap > self.player.total_laps:
            self._finalize_race()

    def render(self):
        if self.state == "SELECT":
            self._draw_selection_screen()
            pygame.display.flip()
            return

        self._project_and_render_track()
        self._draw_speed_lines()

        car_cfg = self.player.car_cfg
        char_cfg = self.player.char_cfg
        player_screen_x = WIDTH * 0.5 + self.player.steer_angle * 22
        player_screen_y = HEIGHT - 58
        self._draw_car_sprite(
            player_screen_x,
            player_screen_y,
            132,
            76,
            car_cfg["body_col"],
            car_cfg["shade_col"],
            car_cfg["accent_col"],
            lean=self.player.steer_angle,
            is_player=True,
            char_cfg=char_cfg,
        )

        for p in self.particles:
            p.draw(self.screen)

        self._draw_hud()

        if self.state == "RACING":
            self.touch.draw(self.screen, self.font_md, self.font_sm)
        elif self.state == "PAUSED":
            self._draw_pause_overlay()
        elif self.state == "RACE_RESULTS":
            self._draw_results_overlay()

        pygame.display.flip()

    def _handle_tap(self, pos):
        if self.state == "RACING" and self.touch.pause_rect.collidepoint(pos):
            self.state = "PAUSED"
            return

        if self.state in ("SELECT", "PAUSED", "RACE_RESULTS"):
            for rect, callback in self.ui_buttons:
                if rect.collidepoint(pos):
                    callback()
                    return

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.touch.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_tap(event.pos)
                elif event.type == pygame.FINGERDOWN:
                    self._handle_tap((event.x * WIDTH, event.y * HEIGHT))
                elif event.type == pygame.KEYDOWN:
                    if event.key == KEY_PAUSE and self.state in ("RACING", "PAUSED"):
                        self.state = "PAUSED" if self.state == "RACING" else "RACING"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.state == "SELECT":
                        self._btn_start_gp()

            self.update(dt)
            self.render()


if __name__ == "__main__":
    RacingGame().run()
