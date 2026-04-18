# File Organizer CLI

A smart command-line tool that automatically organizes files into category-based subdirectories.

## Features

- **Smart Categorization**: Automatically detects file types and organizes them into logical categories (Documents, Images, Videos, Audio, Code, Archives, Executables, Other)
- **Dry-Run Mode**: Preview changes before applying them
- **Safety First**: No files are moved unless you explicitly use `--apply`
- **Detailed Reporting**: See exactly what will happen before it happens

## Installation

```bash
chmod +x file_organizer.py
```

## Usage

### Preview organization (dry-run)
```bash
python3 file_organizer.py /path/to/directory
python3 file_organizer.py  # Current directory
```

### Actually organize files
```bash
python3 file_organizer.py /path/to/directory --apply
```

### Show recognized categories
```bash
python3 file_organizer.py --show-categories
```

## Example

```bash
$ python3 file_organizer.py ~/Downloads

📊 File Organization Analysis
==================================================
Total files: 12

📁 Code: 2 file(s)
   - script.py
   - config.js

📁 Documents: 3 file(s)
   - resume.pdf
   - invoice.docx
   - notes.txt

📁 Images: 4 file(s)
   - photo1.jpg
   - photo2.png
   - icon.svg
   ... and 1 more

📁 Videos: 2 file(s)
   - tutorial.mp4
   - demo.mkv

💡 Run with --apply to actually move files
```

## Categories

The tool recognizes the following file categories:

- **Documents**: PDF, Word, Excel, PowerPoint, Text files
- **Images**: JPEG, PNG, GIF, BMP, SVG, WebP, ICO
- **Videos**: MP4, MKV, AVI, MOV, FLV, WMV, WebM
- **Audio**: MP3, WAV, FLAC, AAC, OGG, M4A, WMA
- **Code**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, Ruby, PHP, Swift
- **Archives**: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ
- **Executables**: EXE, MSI, APP, DEB, RPM, APK
- **Other**: Any file type not in the above categories

## Safety

- **Dry-run by default**: Changes are previewed, never applied without `--apply`
- **Error handling**: Failed moves are reported with error messages
- **Directory creation**: Target category directories are created automatically
