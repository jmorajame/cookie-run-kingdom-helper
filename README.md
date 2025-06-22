# Kaidum - Cookie Run Kingdom Bot

A standalone bot for automating various tasks in Cookie Run Kingdom using image recognition and ADB.

## What's Included

The executable includes:
- ✅ Python runtime (no Python installation needed)
- ✅ All Python dependencies (opencv-python, numpy, customtkinter)
- ✅ ADB (Android Debug Bridge) - bundled inside
- ✅ Button images for recognition
- ✅ Custom fonts

## What You Need to Install

### Android Device Setup Only
1. Enable Developer Options:
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings > Developer Options

2. Enable USB Debugging:
   - In Developer Options, turn on "USB Debugging"
   - Connect your device via USB
   - Allow USB debugging when prompted on your device

## Usage

1. **Connect your Android device** via USB with USB debugging enabled
2. **Run the executable:** `kaidum.exe`
3. **Use the bot:**
   - **Auto Explore Stage:** Enter a stage and it will auto-battle through it
   - **Auto Battle Giant POLY-ROLY:** Automates the POLY-ROLY event battles
   - **Auto Garden Event:** Two modes: "Repeat at lv8" or "Endless loop"

## Troubleshooting

### "Could not find ADB executable"
- The executable should include ADB, but if it's missing, set: `COOKIE_RUN_ADB_PATH=C:\path\to\your\adb.exe`

### Device not detected
- Make sure USB debugging is enabled
- Try a different USB cable
- Check if device appears in `adb devices` command

## Notes

- The bot uses image recognition to find and click buttons
- Make sure your game is in the correct screen before starting any automation
- The bot will automatically handle popups and rewards
- Keep your device screen on while the bot is running

## Download

[Download the latest .exe here](https://github.com/jmorajame/cookie-run-kingdom-helper/releases/latest) 