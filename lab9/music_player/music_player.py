from pathlib import Path

import pygame


def load_playlist(music_dir):
    music_dir.mkdir(parents=True, exist_ok=True)
    tracks = []
    for pattern in ("*.mp3", "*.wav", "*.ogg"):
        tracks.extend(sorted(music_dir.glob(pattern)))
    return tracks


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((700, 500))
    pygame.display.set_caption("Keyboard Music Player")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 28)
    small_font = pygame.font.SysFont("arial", 22)

    music_dir = Path(__file__).resolve().parent / "music_player" / "music" / "sample_tracks"
    playlist = load_playlist(music_dir)
    current_index = 0
    is_playing = False

    def current_track_name():
        if not playlist:
            return "No tracks found"
        return playlist[current_index].name

    def play_current():
        nonlocal is_playing
        if not playlist:
            return
        pygame.mixer.music.load(str(playlist[current_index]))
        pygame.mixer.music.play()
        is_playing = True

    def stop_music():
        nonlocal is_playing
        pygame.mixer.music.stop()
        is_playing = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_p:
                    play_current()
                elif event.key == pygame.K_s:
                    stop_music()
                elif event.key == pygame.K_n and playlist:
                    current_index = (current_index + 1) % len(playlist)
                    play_current()
                elif event.key == pygame.K_b and playlist:
                    current_index = (current_index - 1) % len(playlist)
                    play_current()

        screen.fill((245, 245, 245))

        title = font.render("Music Player", True, (25, 25, 25))
        screen.blit(title, (40, 40))

        track_text = small_font.render(f"Track: {current_track_name()}", True, (40, 40, 40))
        screen.blit(track_text, (40, 110))

        state_text = small_font.render(
            f"State: {'Playing' if is_playing else 'Stopped'}",
            True,
            (40, 40, 40),
        )
        screen.blit(state_text, (40, 150))

        position_ms = pygame.mixer.music.get_pos()
        position_seconds = 0 if position_ms < 0 else position_ms // 1000
        progress_text = small_font.render(
            f"Position: {position_seconds} sec",
            True,
            (40, 40, 40),
        )
        screen.blit(progress_text, (40, 190))

        controls = ["P = Play", "S = Stop", "N = Next", "B = Previous", "Q = Quit"]
        y = 280
        for line in controls:
            control_text = small_font.render(line, True, (60, 60, 60))
            screen.blit(control_text, (40, y))
            y += 36

        if not playlist:
            hint = small_font.render(
                "Add audio files to music_player/music/sample_tracks/",
                True,
                (140, 40, 40),
            )
            screen.blit(hint, (40, 420))

        pygame.display.flip()
        clock.tick(30)

    pygame.mixer.music.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
