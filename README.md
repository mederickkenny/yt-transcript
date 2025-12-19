# ytt - YouTube Transcript Tool

Quick YouTube transcript fetcher that copies to clipboard. Because who has time for clicking?

## Installation

Navigate to your script directory:
```bash
cd ~/code/src/github/kuebic/personal/04-RESOURCES/scripts/yt-transcript/
```

Replace the old files with the new ones (ytt.py and pyproject.toml), then install with pipx:

```bash
pipx install .
```

Done! Now `ytt` works from anywhere on your system.

## Usage

**Default: Clipboard only**
```bash
ytt https://youtube.com/watch?v=dQw4w9WgXcQ
```
→ Transcript copied to clipboard, no file saved

**Save with default name**
```bash
ytt -o https://youtube.com/watch?v=dQw4w9WgXcQ
```
→ Copies to clipboard + saves as `{video-title}-[video_id]-transcript.txt`

**Save with custom name**
```bash
ytt -o my_cool_video.txt https://youtube.com/watch?v=dQw4w9WgXcQ
```
→ Copies to clipboard + saves as `my_cool_video.txt`

## Updating

If you make changes to ytt.py:
```bash
cd ~/code/src/github/kuebic/personal/04-RESOURCES/scripts/yt-transcript/
pipx reinstall ytt
```

## Uninstalling

```bash
pipx uninstall ytt
```

## Requirements

- pipx (install with: `pacman -S python-pipx` on CachyOS)
- xclip (for clipboard: `pacman -S xclip`)
