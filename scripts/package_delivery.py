"""Pacote local limpo de entrega."""
import argparse
import os
import zipfile
from pathlib import Path

DEFAULT_EXCLUDES = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', 'dist', 'build', '.next', 'coverage', 'deliveries', 'graphify-out', '.agents', '.codex', '.aws'}
DEFAULT_EXCLUDE_FILES = {'.env', '.env.local', '.DS_Store', 'Thumbs.db'}

def should_exclude(relative_path):
    return bool(set(relative_path.parts) & DEFAULT_EXCLUDES or relative_path.name in DEFAULT_EXCLUDE_FILES or (relative_path.name.startswith('.env') and relative_path.name != '.env.example') or relative_path.suffix.lower() in {'.zip', '.log', '.pyc', '.pem', '.key'})

def build_package(project_root, output_path):
    project_root, output_path = project_root.resolve(), output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for directory, folders, files in os.walk(project_root, followlinks=False):
            folders[:] = sorted(folder for folder in folders if not should_exclude((Path(directory) / folder).relative_to(project_root)) and not (Path(directory) / folder).is_symlink())
            for name in sorted(files):
                p = Path(directory) / name
                relative = p.relative_to(project_root)
                if p.is_symlink() or p.resolve() == output_path or should_exclude(relative):
                    continue
                archive.write(p, arcname=relative.as_posix())
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Gera ZIP limpo de entrega local.')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--output', type=Path, default=Path('deliveries/projeto-sgp-entrega.zip'))
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    print('Pacote gerado em:', build_package(root, output))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
