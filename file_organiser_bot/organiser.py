import logging
import shutil
from datetime import datetime
from pathlib import Path

# ── Setup logging ──────────────────────────────────────────────────
log_filename = f'organiser_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)

log = logging.getLogger('FileOrganiser')
log.info('FileOrganiser bot started')

# ── Extension → Folder Map ─────────────────────────────────────────
EXT_MAP = {
    # Documents
    '.pdf': 'documents',
    '.docx': 'documents',
    '.doc': 'documents',
    '.pptx': 'documents',
    '.ppt': 'documents',
    '.odt': 'documents',
    '.brf': 'documents',

    # Data
    '.csv': 'data',
    '.xlsx': 'data',
    '.xls': 'data',
    '.json': 'data',
    '.xml': 'data',
    '.sql': 'data',

    # Images
    '.jpg': 'images',
    '.jpeg': 'images',
    '.png': 'images',
    '.gif': 'images',
    '.bmp': 'images',
    '.tiff': 'images',
    '.svg': 'images',
    '.webp': 'images',
    '.ico': 'images',

    # Text
    '.txt': 'text',
    '.md': 'text',
    '.rtf': 'text',
    '.log': 'text',

    # Scripts
    '.py': 'scripts',
    '.js': 'scripts',
    '.jsx': 'scripts',
    '.ts': 'scripts',
    '.tsx': 'scripts',
    '.sh': 'scripts',
    '.html': 'scripts',
    '.css': 'scripts',
    '.java': 'scripts',
    '.cpp': 'scripts',
    '.c': 'scripts',
    '.php': 'scripts',
    '.ipynb': 'scripts',

    # Videos
    '.mp4': 'videos',
    '.mov': 'videos',
    '.avi': 'videos',
    '.mkv': 'videos',
    '.wmv': 'videos',
    '.flv': 'videos',
    '.webm': 'videos',

    # Audio
    '.mp3': 'audio',
    '.wav': 'audio',
    '.aac': 'audio',
    '.flac': 'audio',
    '.ogg': 'audio',
    '.m4a': 'audio',
    '.wma': 'audio',

    # Archives
    '.zip': 'archives',
    '.rar': 'archives',
    '.7z': 'archives',
    '.tar': 'archives',
    '.gz': 'archives',

    # Applications
    '.exe': 'applications',
    '.msi': 'applications',
    '.msix': 'applications',
    '.winmd': 'applications',
    '.apk': 'applications',

    # Ebooks
    '.epub': 'ebooks',
    '.mobi': 'ebooks',

    # Fonts
    '.ttf': 'fonts',
    '.otf': 'fonts',

    # Designs
    '.psd': 'designs',
    '.ai': 'designs',
    '.fig': 'designs'
}


def organise(source_folder):
    source = Path(source_folder)

    if not source.exists():
        log.error(f'Source folder not found: {source}')
        return {}

    log.info(f'Scanning folder: {source.resolve()}')

    summary = {}
    skipped = []

    for file in source.iterdir():

        if not file.is_file():
            continue

        # Skip organiser.py
        if file.name == Path(__file__).name:
            continue

        # Skip current log file
        if file.name == log_filename:
            continue

        # Skip old organiser log files
        if file.name.startswith("organiser_") and file.suffix.lower() == ".log":
            continue

        # Skip backup zip files
        if file.name.startswith("Downloads_backup_") and file.suffix.lower() == ".zip":
            continue

        # Skip desktop.ini
        if file.name.lower() == "desktop.ini":
            continue

        ext = file.suffix.lower()

        if ext not in EXT_MAP:
            log.warning(f'Unknown extension — skipping: {file.name}')
            skipped.append(file.name)
            continue

        category = EXT_MAP[ext]
        dest_folder = source / category
        dest_folder.mkdir(exist_ok=True)

        dest_path = dest_folder / file.name

        try:
            shutil.move(str(file), str(dest_path))
            log.info(f'Moved [{category}] {file.name}')
            summary[category] = summary.get(category, 0) + 1

        except Exception as e:
            log.error(f'Could not move {file.name}: {e}')

    if skipped:
        log.warning(
            f'Skipped {len(skipped)} unknown file(s): {skipped}'
        )

    return summary


def print_summary(summary):

    if not summary:
        print("\nNo files were organised.\n")
        return

    total = sum(summary.values())

    print("\n" + "=" * 40)
    print(f"Summary - {total} files organised")
    print("=" * 40)

    for category, count in sorted(summary.items()):
        print(f"{category:<15} {count}")

    print("=" * 40 + "\n")


if __name__ == '__main__':

    SOURCE = Path.home() / "Downloads"

    log.info('=== Starting File Organiser ===')

    summary = organise(SOURCE)

    print_summary(summary)

    log.info('=== Done ===')