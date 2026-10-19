# Alien Invasion 👾

A classic arcade-style game built with Python and Pygame. Pilot your ship, shoot down waves of aliens, and try to beat your high score. Each new level gets faster and more challenging.

## Features

- Move the ship and fire bullets
- Fight increasingly faster alien fleets
- Track your score, level, remaining ships, and high score
- Play on desktop with a keyboard and mouse
- Use touch controls in a mobile browser: tap to fire and drag horizontally to move
- Package the game for a web browser with Pygbag

## Run on your computer

You need Python and Pygame installed. From the project folder, install Pygame and start the game:

```bash
python -m pip install pygame
python main.py
```

## Controls

| Action | Desktop | Phone / tablet |
| --- | --- | --- |
| Move left or right | Left and right arrow keys | Drag your finger horizontally |
| Fire | Spacebar or click | Tap the screen |
| Start after game over | Click **Play** or press `P` | Tap **Play** |
| Quit | Press `Q` | Close the browser tab |

## Run in a browser with Pygbag

Pygbag packages the Pygame project to run in a browser using WebAssembly. It does not convert the game into JavaScript.

1. Install Pygbag:

   ```bash
   python -m pip install pygbag
   ```

2. In a terminal, go to this project folder and build/run the browser version:

   ```bash
   python -m pygbag .
   ```

3. Open [http://localhost:8000](http://localhost:8000) to try it locally.

Keep the game's image and other asset files inside the project folder so Pygbag can package them.

## Deploy the browser build to Netlify

After generating the Pygbag build, Netlify can publish the static browser files from `build/web`:

- **Base directory:** leave blank
- **Build command:** leave blank when you have already built the game locally
- **Publish directory:** `build/web`

The `build/web` folder must be included in the GitHub repository for this setup. If your `.gitignore` excludes `build/`, remove that ignore rule or otherwise make the generated web files available to Netlify.

## Project files

The game is organized into Python modules. For example:

- `main.py` starts the game
- `settings.py` stores screen, ship, bullet, and alien settings
- `game_functions.py` handles input, game updates, collisions, and drawing
- `ship.py`, `alien.py`, and `bullet.py` define the game sprites
- `game_stats.py` and `scoreboard.py` track and display game progress
- `button.py` defines the Play button
- `images/` contains game images

## Notes

- The browser build can run more slowly than the desktop version, especially on older phones.
- The game loop in `main.py` must be asynchronous for Pygbag and yield with `await asyncio.sleep(0)` each frame.
- Pygbag browser compatibility may require small code changes depending on the libraries and features used.

## License

No license has been specified yet. Add a `LICENSE` file if you want to define how others may use, modify, or distribute this project.
