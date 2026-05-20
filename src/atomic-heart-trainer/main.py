#!/usr/bin/env python3
"""
Atomic Heart Trainer - Main entry point.
Provides a CLI interface to activate in-game cheats for Atomic Heart.
"""

import sys
import time
from memory import MemoryPatcher
from trainer import Trainer


def main():
    print("Atomic Heart Trainer v1.0")
    print("=========================")
    print("Connecting to game process...")
    try:
        patcher = MemoryPatcher("AtomicHeart.exe")
        trainer = Trainer(patcher)
    except Exception as e:
        print(f"Failed to attach: {e}")
        sys.exit(1)

    print("Attached successfully. Available cheats:")
    print("1) Infinite Health")
    print("2) Infinite Ammo")
    print("3) Unlimited Energy")
    print("4) Exit")

    while True:
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            trainer.toggle_infinite_health()
        elif choice == "2":
            trainer.toggle_infinite_ammo()
        elif choice == "3":
            trainer.toggle_unlimited_energy()
        elif choice == "4":
            print("Exiting. Cleaning up...")
            trainer.cleanup()
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
