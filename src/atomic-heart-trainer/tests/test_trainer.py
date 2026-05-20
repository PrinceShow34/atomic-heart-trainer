"""
Unit tests for Trainer module.
Uses mocking to avoid actual process interaction.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trainer import Trainer
from memory import MemoryPatcher


class TestTrainer(unittest.TestCase):
    """Test suite for Trainer class."""

    def setUp(self):
        """Create a mock MemoryPatcher for testing."""
        self.mock_patcher = MagicMock(spec=MemoryPatcher)
        self.mock_patcher.read_memory.return_value = b"\x00\x00\x00\x00"
        self.trainer = Trainer(self.mock_patcher)

    def test_toggle_infinite_health_on(self):
        """Test enabling infinite health saves original and writes new value."""
        self.trainer.toggle_infinite_health()
        self.assertTrue(self.trainer.health_active)
        self.mock_patcher.read_memory.assert_called_once_with(0x00A1B2C0, 4)
        self.mock_patcher.write_memory.assert_called_once()
        args, _ = self.mock_patcher.write_memory.call_args
        self.assertEqual(args[0], 0x00A1B2C0)
        # Should write float 9999.0
        import struct
        expected = struct.pack("f", 9999.0)
        self.assertEqual(args[1], expected)

    def test_toggle_infinite_health_off(self):
        """Test disabling infinite health restores original."""
        self.trainer._original_health = b"\x00\x00\x80\x3f"  # 1.0 float
        self.trainer.health_active = True
        self.trainer.toggle_infinite_health()
        self.assertFalse(self.trainer.health_active)
        self.mock_patcher.write_memory.assert_called_once_with(0x00A1B2C0, b"\x00\x00\x80\x3f")

    def test_toggle_infinite_ammo_on(self):
        """Test enabling infinite ammo."""
        self.trainer.toggle_infinite_ammo()
        self.assertTrue(self.trainer.ammo_active)
        import struct
        expected = struct.pack("I", 999)
        self.mock_patcher.write_memory.assert_called_once_with(0x00A1B2D0, expected)

    def test_toggle_unlimited_energy_on(self):
        """Test enabling unlimited energy."""
        self.trainer.toggle_unlimited_energy()
        self.assertTrue(self.trainer.energy_active)
        import struct
        expected = struct.pack("f", 100.0)
        self.mock_patcher.write_memory.assert_called_once_with(0x00A1B2E0, expected)

    def test_cleanup_restores_all(self):
        """Test cleanup restores all active cheats."""
        self.trainer.health_active = True
        self.trainer.ammo_active = True
        self.trainer.energy_active = True
        self.trainer._original_health = b"a"
        self.trainer._original_ammo = b"b"
        self.trainer._original_energy = b"c"
        self.trainer.cleanup()
        self.assertEqual(self.mock_patcher.write_memory.call_count, 3)
        self.mock_patcher.close.assert_called_once()

    def test_cleanup_no_active(self):
        """Test cleanup with no active cheats does nothing."""
        self.trainer.cleanup()
        self.mock_patcher.write_memory.assert_not_called()
        self.mock_patcher.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
