# ascii-seas

```text
                                                               .-.
                                                              (   ).
                                                               `-'
                 |~                                \v/
                /|        |~
               /_|___    /|
                 |      /_|___
               ) | ()     |
              )__|__()  ) | ()  __
             )___|___() )_|__() \ \
        ______|____|___)__|___() \ \
       \==================o==o==o==/
   ~~~~~\=========================/~~~~~~~~~~~~~~~~~^~~~~~~~~
 ~~~~~~~≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈~~~~~~~~~~~≈≈≈≈≈~~~~~~
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
```

Because life is basically a series of waves—sometimes you ride the crest, sometimes you crash into the trough, and sometimes you just need to close your IDE and watch a tiny ASCII galleon sail across your terminal for twenty minutes instead of fixing that bug.

No frameworks. No dependencies. No telemetry. Just pure ANSI saltwater therapy.

---

## Why does this exist?

- Your build failed for the fifth time in a row.
- You've been staring at a stack trace so long the letters are starting to dance.
- You realized that life has plenty of ups and downs, but at least this ship handles turbulence gracefully without throwing a NullPointerException.
- Sometimes you just want to see a ship sail through the terminal because it's oddly peaceful.

---

## Features

- **Physics-Based Waves:** Multi-frequency sine curves mimicking real ocean swell, complete with whitecap crests and deep ocean gradients.
- **Dynamic Ship Tilt:** The ship actually rides the wave slope. The bow lifts when climbing a swell, levels out at the peak, and dips down as it surfs the backside.
- **Living Sky:** Twinkling stars, a crescent moon, drifting clouds, seagulls flapping by, and spray splashing off the prow.
- **Zero Dependencies:** Pure Python 3 standard library. No pip installs, no node_modules weighing down your drive like an anchor.
- **Truecolor & Fallback Support:** Rich 24-bit ANSI colors with smooth, flicker-free buffer rendering.

---

## Quick Start

Run it straight from your terminal:

```bash
git clone https://github.com/<your-username>/ascii-seas.git
cd ascii-seas
python ship_animation.py
```

On Windows, you can also just double-click `run_ship.bat`.

---

## Controls

| Key | Action |
|:---|:---|
| Space | Pause / Resume (when your boss walks past your desk) |
| + / W | Summon a storm (increase wave height) |
| - / S | Calm the seas |
| Q or Ctrl+C | Return to harsh reality (quit) |

---

## Global Command Setup (Windows)

To launch your personal ocean getaway anytime simply by typing `ship`:

1. Put `ship.cmd` in any folder that's in your `PATH` (e.g. `%LOCALAPPDATA%\agy\bin` or Python's `Scripts` directory):
   ```cmd
   @python "D:\code\ship_animation.py" %*
   ```
2. Open any console window and type:
   ```powershell
   ship
   ```

### Daily Motivation Mode
If you want the ship to greet you every time you open PowerShell to remind you to stay afloat:
```powershell
Add-Content $PROFILE "`npython D:\code\ship_animation.py"
```

---

## License

MIT License. Do whatever you want with it—sail the seven digital seas.
