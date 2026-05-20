"""
Trainer: High-level cheat toggles for Atomic Heart.
Uses MemoryPatcher to modify specific memory addresses.
"""

from memory import MemoryPatcher


class Trainer:
    """Manages cheat states and applies memory patches."""

    # Example addresses (would be game-version specific)
    HEALTH_ADDR = 0x00A1B2C0
    AMMO_ADDR = 0x00A1B2D0
    ENERGY_ADDR = 0x00A1B2E0

    def __init__(self, patcher: MemoryPatcher):
        self.patcher = patcher
        self.health_active = False
        self.ammo_active = False
        self.energy_active = False
        self._original_health = None
        self._original_ammo = None
        self._original_energy = None

    def toggle_infinite_health(self) -> None:
        """Toggle infinite health (freeze health value)."""
        if not self.health_active:
            # Save original value and set to high value
            self._original_health = self.patcher.read_memory(self.HEALTH_ADDR, 4)
            # Write a large float (9999.0)
            import struct
            new_val = struct.pack("f", 9999.0)
            self.patcher.write_memory(self.HEALTH_ADDR, new_val)
            self.health_active = True
            print("Infinite Health: ON")
        else:
            # Restore original value
            if self._original_health:
                self.patcher.write_memory(self.HEALTH_ADDR, self._original_health)
            self.health_active = False
            print("Infinite Health: OFF")

    def toggle_infinite_ammo(self) -> None:
        """Toggle infinite ammo (freeze ammo count)."""
        if not self.ammo_active:
            self._original_ammo = self.patcher.read_memory(self.AMMO_ADDR, 4)
            import struct
            new_val = struct.pack("I", 999)
            self.patcher.write_memory(self.AMMO_ADDR, new_val)
            self.ammo_active = True
            print("Infinite Ammo: ON")
        else:
            if self._original_ammo:
                self.patcher.write_memory(self.AMMO_ADDR, self._original_ammo)
            self.ammo_active = False
            print("Infinite Ammo: OFF")

    def toggle_unlimited_energy(self) -> None:
        """Toggle unlimited energy (freeze energy value)."""
        if not self.energy_active:
            self._original_energy = self.patcher.read_memory(self.ENERGY_ADDR, 4)
            import struct
            new_val = struct.pack("f", 100.0)
            self.patcher.write_memory(self.ENERGY_ADDR, new_val)
            self.energy_active = True
            print("Unlimited Energy: ON")
        else:
            if self._original_energy:
                self.patcher.write_memory(self.ENERGY_ADDR, self._original_energy)
            self.energy_active = False
            print("Unlimited Energy: OFF")

    def cleanup(self) -> None:
        """Restore all original values and close patcher."""
        if self.health_active and self._original_health:
            self.patcher.write_memory(self.HEALTH_ADDR, self._original_health)
        if self.ammo_active and self._original_ammo:
            self.patcher.write_memory(self.AMMO_ADDR, self._original_ammo)
        if self.energy_active and self._original_energy:
            self.patcher.write_memory(self.ENERGY_ADDR, self._original_energy)
        self.patcher.close()
