import os
import shutil
from pathlib import Path


class FileOrganizer:
    """Organize files in Downloads folder into categorized subdirectories"""

    def __init__(self, downloads_path):
        self.downloads_path = downloads_path
        self.category_folders = {
            "Programs": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".app", ".bat", ".cmd", ".ps1"],
            "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lzma", ".cab", ".iso"],
            "Documents": [
                ".pdf",
                ".doc",
                ".docx",
                ".txt",
                ".rtf",
                ".odt",
                ".pages",
                ".md",
                ".csv",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".odp",
            ],
            "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".aiff", ".alac"],
            "Video": [
                ".mp4",
                ".avi",
                ".mkv",
                ".mov",
                ".wmv",
                ".flv",
                ".webm",
                ".m4v",
                ".3gp",
                ".ogv",
                ".ts",
                ".mts",
                ".m2ts",
            ],
        }

        # Files to exclude from organization
        self.excluded_files = ["results.csv", "desktop.ini"]

    def create_category_folders(self):
        """Create category folders if they don't exist"""
        for folder_name in self.category_folders.keys():
            folder_path = os.path.join(self.downloads_path, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Created folder: {folder_name}")

    def get_file_category(self, filename):
        """Determine which category a file belongs to based on its extension"""
        file_ext = Path(filename).suffix.lower()

        for category, extensions in self.category_folders.items():
            if file_ext in extensions:
                return category

        return None  # No category found

    def organize_files(self):
        """Organize files in Downloads root directory into category folders"""
        print("Starting file organization...")

        # Create category folders
        self.create_category_folders()

        # Get files in root directory
        files_to_organize = []
        for item in os.listdir(self.downloads_path):
            item_path = os.path.join(self.downloads_path, item)

            # Skip if it's a directory or excluded file
            if os.path.isdir(item_path) or item in self.excluded_files:
                continue

            files_to_organize.append(item)

        if not files_to_organize:
            print("No files to organize in root directory")
            return

        print(f"Found {len(files_to_organize)} files to organize")

        # Organize each file
        organized_count = 0
        for filename in files_to_organize:
            category = self.get_file_category(filename)

            if category:
                source_path = os.path.join(self.downloads_path, filename)
                dest_folder = os.path.join(self.downloads_path, category)
                dest_path = os.path.join(dest_folder, filename)

                # Check if destination file already exists
                if os.path.exists(dest_path):
                    # Generate unique filename
                    base_name = Path(filename).stem
                    extension = Path(filename).suffix
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base_name}_{counter}{extension}"
                        dest_path = os.path.join(dest_folder, new_filename)
                        counter += 1

                try:
                    shutil.move(source_path, dest_path)
                    print(f"Moved '{filename}' to '{category}/' folder")
                    organized_count += 1
                except Exception as e:
                    print(f"Error moving '{filename}': {e}")
            else:
                print(f"No category found for '{filename}' - leaving in root directory")

        print(f"File organization completed. {organized_count} files organized.")

    def get_organized_file_paths(self):
        """Get all file paths after organization for monitoring"""
        all_files = []

        # Scan root directory (remaining unorganized files)
        for item in os.listdir(self.downloads_path):
            item_path = os.path.join(self.downloads_path, item)

            if os.path.isfile(item_path) and item not in self.excluded_files:
                all_files.append({"path": item_path, "folder": "~", "filename": item})

        # Scan category folders
        for category in self.category_folders.keys():
            category_path = os.path.join(self.downloads_path, category)
            if os.path.exists(category_path):
                for item in os.listdir(category_path):
                    item_path = os.path.join(category_path, item)

                    if os.path.isfile(item_path):
                        all_files.append({"path": item_path, "folder": category, "filename": item})

        return all_files


def organize_downloads_folder(downloads_path):
    """Convenience function to organize Downloads folder"""
    organizer = FileOrganizer(downloads_path)
    organizer.organize_files()
    return organizer


if __name__ == "__main__":
    # Test the organizer
    from file_monitor import get_downloads_path

    downloads_path = get_downloads_path()
    print(f"Downloads path: {downloads_path}")

    organizer = FileOrganizer(downloads_path)
    organizer.organize_files()
