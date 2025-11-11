import unittest
from unittest.mock import patch
import io
import json
from pathlib import Path

# Import the main game classes and functions
from dream_market import Player, CLASSES, CLASS_KEY_MAP, ITEMS, Inventory, Enemy, Combat, save_game, load_game

class TestDreamMarket(unittest.TestCase):

    def setUp(self):
        # Create a default player (Night Surgeon)
        self.cls = CLASS_KEY_MAP['night_surgeon']
        self.player = Player("Tester", self.cls)

    def test_player_creation(self):
        self.assertEqual(self.player.name, "Tester")
        self.assertEqual(self.player.class_name, "Night Surgeon")
        self.assertEqual(self.player.health, self.cls['health'])
        self.assertEqual(self.player.strength, self.cls['strength'])

    def test_inventory_add_remove(self):
        inv = Inventory()
        item = ITEMS['Dream Elixir']
        inv.add(item)
        self.assertIn(item, inv.items)
        removed = inv.remove('Dream Elixir')
        self.assertEqual(removed, item)
        self.assertEqual(inv.items, [])

    def test_inventory_list_empty(self):
        inv = Inventory()
        self.assertEqual(inv.list(), "Your inventory is empty.")

    def test_enemy_take_damage_and_alive(self):
        enemy = Enemy("Test Enemy", 50, 5, 5, 5, "Desc")
        enemy.take_damage(20)
        self.assertEqual(enemy.hp, 30)
        self.assertTrue(enemy.alive)
        enemy.take_damage(30)
        self.assertEqual(enemy.hp, 0)
        self.assertFalse(enemy.alive)

    @patch('builtins.input', side_effect=['attack', 'run'])
    def test_combat_player_attack_and_run(self, mock_input):
        enemy = Enemy("Dummy", 10, 1, 1, 1, "Desc")
        combat = Combat(self.player, enemy)
        result = combat.player_turn()
        self.assertIn(result, [None, 'escaped', 'player_dead', 'enemy_dead'])

    def test_save_and_load(self):
        # Add an item and save
        self.player.inventory.add(ITEMS['Dream Elixir'])
        save_game(self.player)
        self.assertTrue(Path("dream_market_save.json").exists())
        # Load game
        loaded_player = load_game()
        self.assertEqual(loaded_player.name, self.player.name)
        self.assertTrue(any(it.name == 'Dream Elixir' for it in loaded_player.inventory.items))
        # Cleanup
        Path("dream_market_save.json").unlink()

    def test_player_gain_xp_and_level(self):
        old_level = self.player.level
        self.player.gain_xp(200)  # enough for at least one level
        self.assertGreaterEqual(self.player.level, old_level + 1)

    def test_modify_health_and_sanity(self):
        old_health = self.player.health
        self.player.modify_health(-10)
        self.assertEqual(self.player.health, old_health - 10)
        old_sanity = self.player.sanity
        self.player.modify_sanity(-20)
        self.assertEqual(self.player.sanity, old_sanity - 20)

    def test_special_items_use_function(self):
        item = ITEMS['Dream Elixir']
        result = item.use(self.player)
        self.assertIn("recover", result)

if __name__ == '__main__':
    unittest.main()