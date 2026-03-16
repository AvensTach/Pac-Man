import sys
import pygame as pg
import settings as s

def draw_shadowed_round_rect(surface, rect: pg.Rect, fill, border, radius=18, border_w=2, shadow_offset=(0, 6)):
    shadow_rect = rect.move(shadow_offset)
    pg.draw.rect(surface, s.SHADOW, shadow_rect, border_radius=radius)
    pg.draw.rect(surface, fill, rect, border_radius=radius)
    pg.draw.rect(surface, border, rect, width=border_w, border_radius=radius)


def draw_text_center(surface, font, text, center, color=s.TEXT):
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(center=center))


class Button:
    def __init__(self, rect: pg.Rect, text: str, font: pg.font.Font, on_click):
        self.rect = rect
        self.text = text
        self.font = font
        self.on_click = on_click
        self.hovered = False
        self.pressed = False

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.on_click()
            self.pressed = False

    def draw(self, surface):
        fill = s.BTN_FILL_HOVER if self.hovered else s.BTN_FILL
        border = s.ACCENT if self.hovered else s.ACCENT_SOFT
        draw_shadowed_round_rect(surface, self.rect, fill=fill, border=border, radius=22, border_w=3)
        draw_text_center(surface, self.font, self.text, self.rect.center, color=s.TEXT)


class IconButton:
    def __init__(self, rect: pg.Rect, on_click):
        self.rect = rect
        self.on_click = on_click
        self.hovered = False
        self.pressed = False

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.on_click()
            self.pressed = False

    def draw_gear(self, surface):
        cx, cy = self.rect.center
        r = min(self.rect.w, self.rect.h) // 3
        color = s.TEXT if self.hovered else s.TEXT_MUTED

        pg.draw.circle(surface, color, (cx, cy), r, width=2)
        pg.draw.circle(surface, color, (cx, cy), max(3, r // 2), width=2)

        # teeth
        for i in range(8):
            ang = i * (3.14159265 / 4)
            v = pg.Vector2(1, 0).rotate_rad(ang)
            x1, y1 = cx + int((r + 2) * v.x), cy + int((r + 2) * v.y)
            x2, y2 = cx + int((r + 8) * v.x), cy + int((r + 8) * v.y)
            pg.draw.line(surface, color, (x1, y1), (x2, y2), width=2)

    def draw(self, surface):
        fill = s.BTN_FILL_HOVER if self.hovered else s.BTN_FILL
        border = s.ACCENT if self.hovered else s.ACCENT_SOFT
        draw_shadowed_round_rect(surface, self.rect, fill=fill, border=border, radius=16, border_w=2, shadow_offset=(0, 4))
        self.draw_gear(surface)


# ---------- Screens ----------
class MainMenuScreen:
    def __init__(self, on_play, on_exit, on_settings):
        self.on_play = on_play
        self.on_exit = on_exit
        self.on_settings = on_settings

        self.title_font = pg.font.SysFont(None, 84)
        self.btn_font = pg.font.SysFont(None, 48)
        self.small_font = pg.font.SysFont(None, 24)

        cx = s.SCREEN_WIDTH // 2
        btn_w, btn_h = 260, 72
        gap = 18
        top_y = s.SCREEN_HEIGHT // 2 - btn_h - gap // 2

        self.play_btn = Button(pg.Rect(cx - btn_w // 2, top_y, btn_w, btn_h), "PLAY", self.btn_font, self.on_play)
        self.exit_btn = Button(pg.Rect(cx - btn_w // 2, top_y + btn_h + gap, btn_w, btn_h), "EXIT", self.btn_font, self.on_exit)

        gear_size = 52
        padding = 18
        self.gear_btn = IconButton(
            pg.Rect(s.SCREEN_WIDTH - gear_size - padding, s.SCREEN_HEIGHT - gear_size - padding, gear_size, gear_size),
            self.on_settings
        )

    def handle_event(self, event):
        self.play_btn.handle_event(event)
        self.exit_btn.handle_event(event)
        self.gear_btn.handle_event(event)

    def draw(self, screen):
        screen.fill(s.WALL_COLOR)

        # subtle grid
        grid_color = (10, 10, 30)
        step = 38
        for x in range(0, s.SCREEN_WIDTH, step):
            pg.draw.line(screen, grid_color, (x, 0), (x, s.SCREEN_HEIGHT), 1)
        for y in range(0, s.SCREEN_HEIGHT, step):
            pg.draw.line(screen, grid_color, (0, y), (s.SCREEN_WIDTH, y), 1)

        panel = pg.Rect(0, 0, 520, 360)
        panel.center = (s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2)
        draw_shadowed_round_rect(screen, panel, fill=s.PANEL_COLOR, border=s.ACCENT_SOFT, radius=28, border_w=2, shadow_offset=(0, 10))

        draw_text_center(screen, self.title_font, "PAC-MAN", (s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 150))
        draw_text_center(screen, self.small_font, "Press PLAY to start", (s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 110), color=s.TEXT_MUTED)

        self.play_btn.draw(screen)
        self.exit_btn.draw(screen)
        self.gear_btn.draw(screen)

def create_color_gradient(width, height):
    """Creates a surface with a full spectrum of colors"""
    gradient = pg.Surface((width, height))
    for x in range(width):
        # Converting the X position to a color using the HSV model
        hue = x / width
        # pygame.Color.from_hsv(hue, saturation, value)
        color = pg.Color(0)
        color.hsva = (hue * 360, 100, 100, 100)
        pg.draw.line(gradient, color, (x, 0), (x, height))
    return gradient


class SettingsScreen:
    def __init__(self, on_back):
        self.on_back = on_back

        self.title_font = pg.font.SysFont(None, 64)
        self.text_font = pg.font.SysFont(None, 28)
        self.btn_font = pg.font.SysFont(None, 40)

        self.back_btn = Button(pg.Rect(24, 24, 220, 60), "BACK", self.btn_font, self.on_back)

        self.palette_width = 400
        self.palette_height = 40
        self.palette_rect = pg.Rect(
            s.SCREEN_WIDTH // 2 - self.palette_width // 2,
            s.SCREEN_HEIGHT // 2 + 100,
            self.palette_width,
            self.palette_height
        )

        self.indicator_x = self.palette_rect.centerx

        self.palette_image = create_color_gradient(self.palette_width, self.palette_height)
        self.selected_color = pg.Color(s.WALL_COLOR)

        music_text = "MUSIC: ON" if s.CONFIG["MUSIC_ON"] else "MUSIC: OFF"
        self.toggle_music = Button(pg.Rect(s.SCREEN_WIDTH // 2 - 200, s.SCREEN_HEIGHT // 2 - 60, 400, 64),
                                   music_text, self.btn_font, self._toggle_music)

        sfx_text = "SOUNDS: ON" if s.CONFIG["SFX_ON"] else "SOUNDS: OFF"
        self.toggle_sfx = Button(pg.Rect(s.SCREEN_WIDTH // 2 - 200, s.SCREEN_HEIGHT // 2 + 20, 400, 64),
                                 sfx_text, self.btn_font, self._toggle_sfx)

    def _toggle_music(self):
        s.CONFIG["MUSIC_ON"] = not s.CONFIG["MUSIC_ON"]
        self.toggle_music.text = f"MUSIC: {'ON' if s.CONFIG['MUSIC_ON'] else 'OFF'}"

        if not s.CONFIG["MUSIC_ON"]:
            pg.mixer.stop()

    def _toggle_sfx(self):
        s.CONFIG["SFX_ON"] = not s.CONFIG["SFX_ON"]
        self.toggle_sfx.text = f"SOUNDS: {'ON' if s.CONFIG['SFX_ON'] else 'OFF'}"

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.toggle_music.handle_event(event)
        self.toggle_sfx.handle_event(event)

        if pg.mouse.get_pressed()[0]:
            m_pos = pg.mouse.get_pos()
            if self.palette_rect.collidepoint(m_pos):
                self.indicator_x = m_pos[0]

                rel_x = m_pos[0] - self.palette_rect.x
                picked_color = self.palette_image.get_at((rel_x, self.palette_height // 2))

                dark_color = pg.Color(picked_color)
                h, s_val, v, a = dark_color.hsva
                dark_color.hsva = (h, s_val, 20, a)

                s.WALL_COLOR = (dark_color.r, dark_color.g, dark_color.b)

    def draw(self, screen):
        screen.fill(s.WALL_COLOR)

        panel = pg.Rect(0, 0, 620, 460)
        panel.center = (s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2)
        draw_shadowed_round_rect(screen, panel, fill=s.PANEL_COLOR, border=s.ACCENT_SOFT, radius=28, border_w=2,
                                 shadow_offset=(0, 10))

        draw_text_center(screen, self.title_font, "SETTINGS", (s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 160))
        draw_text_center(screen, self.text_font, "Click to toggle", (s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 120),
                         color=s.TEXT_MUTED)

        screen.blit(self.palette_image, self.palette_rect)
        pg.draw.rect(screen, s.TEXT, self.palette_rect, width=2, border_radius=2)

        pg.draw.line(screen, s.TEXT, (self.indicator_x, self.palette_rect.y - 5),
                     (self.indicator_x, self.palette_rect.bottom + 5), width=3)

        self.toggle_music.draw(screen)
        self.toggle_sfx.draw(screen)
        self.back_btn.draw(screen)