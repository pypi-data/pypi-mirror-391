import argparse
import pathlib
from typing import Any

import whisper
from devicer import get_device

ALLOWED_SUFFIXES = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


def trainscribe(
    folder: pathlib.Path = pathlib.Path("dataset/wavs"),
    lang: str = "en",
    model: str = "medium",
    speaker: str = "speaker",
    device: Any = None,
    output: pathlib.Path | None = None,
) -> pathlib.Path:
    try:
        device = get_device() if device is None else device
    except Exception:
        device = "cpu"

    whisper_model = whisper.load_model(model, device=device)

    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    audio_files = [
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES
    ]
    audio_files = sorted(audio_files, key=lambda p: p.name)

    if not audio_files:
        print("No audio files found in the folder.")
        raise FileNotFoundError

    metadata_lines: list[str] = []
    for audio_path in audio_files:
        result: dict[str, Any] = whisper_model.transcribe(
            str(audio_path), language=lang
        )
        text: str = result.get("text", "").strip()
        file_id = audio_path.stem
        metastr = (
            f"{file_id}|{text}" if speaker is None else f"{file_id}|{text}|{speaker}"
        )
        metadata_lines.append(metastr)

    if output is None:
        metadata_path = folder / "metadata.csv"
    else:
        out_path = output
        if out_path.suffix:
            metadata_path = out_path
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            out_path.mkdir(parents=True, exist_ok=True)
            metadata_path = out_path / "metadata.csv"

    metadata_path.write_text("\n".join(metadata_lines), encoding="utf-8")
    print(f"Transcription complete. Metadata saved to {metadata_path}")

    return metadata_path


def build_parser():
    parser = argparse.ArgumentParser(
        description="Transcribe a folder of audio files to metadata.csv using Whisper."
    )
    parser.add_argument(
        "--folder",
        "-f",
        type=pathlib.Path,
        help="Folder with audio files",
        required=True,
    )
    parser.add_argument(
        "--lang", "-l", default="en", help="Language code for transcription (e.g. 'en')"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="medium",
        help="Whisper model name (tiny, base, small, medium, large, turbo)",
    )
    parser.add_argument(
        "--speaker",
        "-s",
        help="Speaker label to add to metadata lines",
    )
    parser.add_argument("--device", "-d", help="Device for whisper model (cuda/cpu)")
    parser.add_argument(
        "--output",
        "-o",
        type=pathlib.Path,
        default=None,
    )

    return parser.parse_args()


def main():
    args = build_parser()
    trainscribe(
        folder=args.folder,
        lang=args.lang,
        model=args.model,
        speaker=args.speaker,
        device=args.device,
        output=args.output,
    )


if __name__ == "__main__":
    main()
