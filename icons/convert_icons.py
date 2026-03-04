#!/usr/bin/env python3
"""
Icon Converter for Boop Python

Converts Boop icons to all required formats for macOS, Linux, and Windows.
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


class IconConverter:
    """Convert icons to various formats."""

    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        # Source images are in icon.iconset/ subdirectory
        self.iconset_dir = source_dir / "icon.iconset"
        self.output_dir = source_dir
        
        # Create output directory if needed
        self.output_dir.mkdir(exist_ok=True)

    def get_source_image(self, size: str) -> Path:
        """Get path to source image for given size."""
        sizes = {
            "16": "icon_16x16.png",
            "32": "icon_32x32.png",
            "64": "icon_32x32@2x.png",
            "128": "icon_128x128.png",
            "256": "icon_256x256.png",
            "512": "icon_512x512.png",
            "1024": "icon_512x512@2x.png",
        }
        # First try iconset directory, then source directory
        filename = sizes.get(size, sizes["256"])
        iconset_path = self.iconset_dir / filename
        if iconset_path.exists():
            return iconset_path
        return self.source_dir / filename
    
    def load_image(self, size: str) -> Image.Image:
        """Load and resize image to specified size."""
        source = self.get_source_image(size)
        if source.exists():
            img = Image.open(source)
        else:
            # Fallback to largest available in iconset
            largest = self.iconset_dir / "icon_512x512@2x.png"
            if largest.exists():
                img = Image.open(largest)
            else:
                raise FileNotFoundError(f"No source image found for {size}")

        # Convert to RGBA if necessary
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Resize to target size
        target_size = int(size)
        if img.size != (target_size, target_size):
            img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

        return img
    
    def create_windows_ico(self) -> Path:
        """
        Create Windows .ico file.
        
        Uses 256x256 PNG-based icon which works for modern Windows and PyInstaller.
        Output: icon.ico in same directory
        """
        print("Creating Windows .ico file...")

        # Use 256x256 size for modern Windows compatibility
        size = 256
        try:
            img = self.load_image(str(size))
            output_path = self.output_dir / "icon.ico"
            
            # Save as PNG-based ICO (modern format)
            img.save(output_path, format="ICO", sizes=[(size, size)])
            
            print(f"  Created: {output_path} ({size}x{size})")
            return output_path
        except Exception as e:
            print(f"  Warning: Could not create ICO: {e}")
            return None
    
    def create_linux_icons(self) -> list:
        """
        Create Linux icon files for various contexts.

        Standard sizes:
        - 16x16: Panel icons
        - 32x32: Panel icons
        - 48x48: Application icons
        - 128x128: Application icons
        - 256x256: Application icons (used by PyInstaller)
        - 512x512: Application icons / AppStream
        Output: icons/icon_*.png (same directory as source)
        """
        print("Creating Linux icon files...")

        sizes = ["16", "32", "48", "128", "256", "512"]
        output_paths = []

        for size in sizes:
            try:
                img = self.load_image(size)
                output_path = self.output_dir / f"icon_{size}x{size}.png"
                img.save(output_path, "PNG", optimize=True)
                output_paths.append(output_path)
                print(f"  Created: {size}x{size} -> {output_path.name}")
            except Exception as e:
                print(f"  Warning: Could not create {size}x{size}: {e}")

        return output_paths
    
    def create_macos_icns(self) -> Path:
        """
        Create macOS .icns file from iconset.
        
        Note: This requires iconutil on macOS.
        For cross-platform, we use the existing iconset.
        """
        print("Preparing macOS iconset...")
        
        iconset_dir = self.output_dir / "icon.iconset"
        iconset_dir.mkdir(exist_ok=True)
        
        # Standard macOS icon sizes
        sizes = {
            "icon_16x16.png": "16",
            "icon_16x16@2x.png": "32",
            "icon_32x32.png": "32",
            "icon_32x32@2x.png": "64",
            "icon_128x128.png": "128",
            "icon_128x128@2x.png": "256",
            "icon_256x256.png": "256",
            "icon_256x256@2x.png": "512",
            "icon_512x512.png": "512",
            "icon_512x512@2x.png": "1024",
        }
        
        for filename, size in sizes.items():
            try:
                img = self.load_image(size)
                output_path = iconset_dir / filename
                img.save(output_path, "PNG", optimize=True)
                print(f"  Created iconset: {filename}")
            except Exception as e:
                print(f"  Warning: Could not create {filename}: {e}")

        # Try to create .icns using iconutil (macOS only)
        # Save to icons/ directory
        icns_path = self.output_dir / "icon.icns"

        if sys.platform == "darwin":
            import subprocess
            try:
                subprocess.run(
                    ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)],
                    check=True,
                    capture_output=True
                )
                print(f"  Created: {icns_path.name}")
            except subprocess.CalledProcessError as e:
                print(f"  Warning: iconutil failed: {e.stderr.decode()}")

        return icns_path if icns_path.exists() else None
    
    def create_all(self):
        """Create all icon formats."""
        print("=" * 50)
        print("Boop Python Icon Converter")
        print("=" * 50)
        print()
        
        results = {
            "windows": None,
            "linux": [],
            "macos": None,
        }
        
        try:
            results["windows"] = self.create_windows_ico()
        except Exception as e:
            print(f"Failed to create Windows icon: {e}")
        
        print()
        
        try:
            results["linux"] = self.create_linux_icons()
        except Exception as e:
            print(f"Failed to create Linux icons: {e}")
        
        print()
        
        try:
            results["macos"] = self.create_macos_icns()
        except Exception as e:
            print(f"Failed to create macOS icon: {e}")
        
        print()
        print("=" * 50)
        print("Icon conversion complete!")
        print("=" * 50)
        
        return results


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    source_dir = script_dir  # Source icons are in icon.iconset/

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        sys.exit(1)

    converter = IconConverter(source_dir)
    results = converter.create_all()

    print("\nIcons ready for building:")
    print(f"  macOS:   icon.icns")
    print(f"  Windows: icon.ico")
    print(f"  Linux:   icon_256x256.png")


if __name__ == "__main__":
    main()
