# Trainscribe

Trainscribe is a command-line tool that transcribes audio files in a specified folder using [OpenAI's Whisper](https://github.com/openai/whisper) and generates a `metadata.csv` file. The produced metadata file is intended to use in training/finetune of text to speech (TTS) models, and may use one of the following formats: 
- `file_id|transcribed_text`, or 
- `file_id|transcribed_text|speaker`, if a speaker label is provided. 

This is similar to LJ Speech format, but lacks an additional field with normalized transcribed text for pronuciation. Particularly, `file_id|transcribed_text` may be used in projects like [piper-train](https://github.com/veralvx/piper-train), and `file_id|transcribed_text|speaker` in [xtts-finetune](https://github.com/veralvx/xtts-finetune).

## Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/)
- `ffmpeg` (install with `sudo apt install ffmpeg`)


## Usage

Run the tool with:

```console
uvx trainscribe --folder /path/to/audio/folder [options]
```

```console
Transcribe a folder of audio files to metadata.csv using Whisper.

options:
  -h, --help            show this help message and exit
  --folder, -f FOLDER   Folder with audio files
  --lang, -l LANG       Language code for transcription (e.g. 'en')
  --model, -m MODEL     Whisper model name (tiny, base, small, medium, large, turbo)
  --speaker, -s SPEAKER
                        Speaker label to add to metadata lines
  --device, -d DEVICE   Device for whisper model (cuda/cpu)
  --output, -o OUTPUT
```

### Example
Transcribe English audio in dataset/wavs using the medium model:

```console
uvx trainscribe --folder dataset/wavs --lang en --model medium 
```

This generates `dataset/wavs/metadata.csv` 
