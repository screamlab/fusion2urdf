#!/usr/bin/env python3
"""URDF_Exporter cross-platform installer.

Copies the URDF_Exporter folder into Fusion 360's API Scripts directory.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def get_default_target_base() -> Path:
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is not set")
        return Path(appdata) / "Autodesk" / "Autodesk Fusion 360" / "API" / "Scripts"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Autodesk" / "Autodesk Fusion 360" / "API" / "Scripts"
    # Linux is not officially supported by Fusion 360, but keep a fallback
    return Path.home() / ".local" / "share" / "Autodesk" / "Autodesk Fusion 360" / "API" / "Scripts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install URDF_Exporter into Fusion 360 Scripts directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing installation without prompting.")
    parser.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Custom target Scripts directory (defaults to Fusion 360 API Scripts path).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    source_dir = script_dir / "URDF_Exporter"

    if not source_dir.exists():
        print("Error: URDF_Exporter directory not found.")
        print("Make sure install.py is in the fusion2urdf project root.")
        return 1

    target_base = args.target or get_default_target_base()
    target_dir = target_base / "URDF_Exporter"

    if not target_base.exists():
        print("Error: Fusion 360 API Scripts directory not found.")
        print(f"Path: {target_base}")
        return 1

    if target_dir.exists():
        if not args.force:
            resp = input("Detected an existing URDF_Exporter. Remove and reinstall? (y/N): ").strip().lower()
            if resp != "y":
                print("Installation canceled.")
                return 0
        try:
            shutil.rmtree(target_dir)
            print("Previous version removed.")
        except Exception as exc:  # noqa: BLE001
            print(f"Warning: could not fully remove old version: {exc}")
            print("Will attempt to overwrite.")

    try:
        print("Installing URDF_Exporter...")
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        print("✓ URDF_Exporter installation complete!")
        print(f"Source: {source_dir}")
        print(f"Target: {target_dir}")
        print("\nUsage:")
        print("1. Open Fusion 360")
        print("2. Go to Scripts and Add-Ins (Shift+S)")
        print("3. Select URDF_Exporter and run")
        print("4. Choose automatic cleanup to keep files tidy")
    except Exception as exc:  # noqa: BLE001
        print(f"✗ Installation failed: {exc}")
        return 1

    print("\nInstallation complete! Restart Fusion 360 to load the new version.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
