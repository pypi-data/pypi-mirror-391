# EverydayAI CLI

A powerful command-line toolkit for AI-powered multimedia processing

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/everydayai-cli.svg)](https://pypi.org/project/everydayai-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform images, audio, and video using AI - designed for content creators,
educators, marketers, and anyone who needs powerful AI tools without writing
code.

## Installation

```bash
pip install everydayai-cli
```

Or with pipx (recommended for CLI tools):

```bash
pipx install everydayai-cli
```

## Quick Start

```bash
# Analyze an image
eai vision photo.jpg --prompt "What's in this image?"

# Generate an image
eai image "a futuristic city at sunset" -o city.png

# Transcribe audio
eai transcribe podcast.mp3

# Download and transcribe YouTube video
eai transcribe_video "https://youtube.com/watch?v=..." -o transcript.txt
```

## Commands

| Command | Description |
|---------|-------------|
| `eai image` | Generate images with gpt-image-1 |
| `eai vision` | Analyze single images with GPT-5 |
| `eai multi_vision` | Analyze multiple images simultaneously |
| `eai speak` | Text-to-speech with OpenAI voices |
| `eai transcribe` | Audio-to-text with Whisper |
| `eai search` | Web search with AI-powered answers |
| `eai youtube` | Manage YouTube authentication |
| `eai transcribe_video` | Download and transcribe videos |
| `eai translate_audio` | Translate audio to English |
| `eai elevenlabs` | Premium TTS with ElevenLabs |

For detailed documentation on each command, see below.

## Tool Details

### Image Generation

`eai image` - Create images from text descriptions using gpt-image-1

📖 **[Complete gpt-image-1 Guide](docs/GPT_IMAGE_1_GUIDE.md)** - Sizes, quality levels, transparent backgrounds, costs, and advanced features

```bash
eai image "a serene mountain landscape" -o landscape.png
eai image "corporate logo" --size 1024x1024 --quality hd -o logo.png
```

### Vision Analysis

`eai vision` - Analyze images with GPT-5 Vision

```bash
eai vision photo.jpg --prompt "What's in this image?"
eai vision receipt.jpg --prompt "What is the total amount?"
eai vision document.jpg --prompt "Extract all text"
```

### Multi-Image Analysis

`eai multi_vision` - Analyze 2-3 images simultaneously

```bash
eai multi_vision before.jpg after.jpg --prompt "What changed?"
eai multi_vision img1.jpg img2.jpg img3.jpg --compare
```

### Text-to-Speech

`eai speak` - Convert text to speech with OpenAI TTS

```bash
eai speak "Hello world" -o hello.mp3
eai speak "Welcome" -o welcome.mp3 --voice nova --model tts-1-hd
eai speak --input script.txt -o audiobook.mp3 --stream
```

Voices: alloy, echo, fable, onyx, nova, shimmer

### Audio Transcription

`eai transcribe` - Transcribe audio with Whisper (90+ languages)

```bash
eai transcribe podcast.mp3 -o transcript.txt
eai transcribe video.mp3 --format srt -o subtitles.srt
eai transcribe meeting.mp3 --parallel --language es
```

### YouTube Video Processing

`eai transcribe_video` - Download and transcribe YouTube videos

```bash
eai transcribe_video "https://youtube.com/watch?v=abc123"
eai transcribe_video "VIDEO_URL" --format srt -o subtitles.srt
eai transcribe_video "VIDEO_URL" --keep-audio --parallel
```

### Audio Translation

`eai translate_audio` - Translate audio to English

```bash
eai translate_audio spanish_audio.mp3 -o english.txt
eai translate_audio foreign.mp3 --format srt -o english_subs.srt
```

### Web Search

`eai search` - AI-powered web search with citations

```bash
eai search "latest AI developments 2024"
eai search "Python tutorials" --domains "edu,github.io"
eai search "restaurants" --city "New York" --country "US"
```

### Premium Text-to-Speech

`eai elevenlabs` - High-quality TTS with ElevenLabs

```bash
eai elevenlabs list-voices
eai elevenlabs speak "Welcome" -o intro.mp3 --voice adam
```

### YouTube Authentication

`eai youtube` - Manage YouTube authentication

```bash
eai youtube check
eai youtube setup
eai youtube clear
```

## Configuration

Set your API keys:

```bash
export OPENAI_API_KEY="your-key-here"
export ELEVENLABS_API_KEY="your-key-here"  # Optional
```

Or use config file (`~/.ei_cli/config.yaml`):

```yaml
openai:
  api_key: ${OPENAI_API_KEY}
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
```

## Plugin Architecture

Create custom commands as plugins:

```python
from ei_cli.plugins import BaseCommandPlugin
import click

class MyPlugin(BaseCommandPlugin):
    name = "my-command"
    category = "custom"
    help_text = "My custom command"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help_text)
        def my_command():
            click.echo("Hello!")
        return my_command

plugin = MyPlugin()
```

Register in `pyproject.toml`:

```toml
[project.entry-points."eai.plugins"]
my-plugin = "my_package.plugin:plugin"
```

## Development

```bash
git clone https://github.com/kaw393939/eai.git
cd eai
poetry install
poetry run pytest
```

## License

MIT License

## Links

- GitHub: <https://github.com/kaw393939/eai>
- PyPI: <https://pypi.org/project/everydayai-cli/>
- Issues: <https://github.com/kaw393939/eai/issues>

## Author

Keith Williams - Director of Enterprise AI @ NJIT

---

**Version:** 0.2.0 | **Status:** Alpha - Core features stable
