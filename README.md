# AI-Game-1
THE DREAM MARKET - README
=====================

Overview
--------
Dreams are commodities. You play a rookie Dream Broker on your first night shift
in the surreal Dream Market. The game is a text-based roleplaying game that
implements character creation, a multi-stage world, turn-based combat, inventory,
branching choices with multiple endings, and save/load functionality.

How to run
----------
Requires Python 3.8+ (no external packages). Save the file 'dream_market.py' and run:
    python3 dream_market.py

Basic commands (in combat or menus)
----------------------------------
- attack: perform a basic attack
- defend: brace to reduce incoming damage next enemy turn
- use <item name>: use an item from inventory (e.g., use Dream Elixir)
- inventory: list your items
- special: use your class special ability
- stats: show player stats
- run: attempt to flee combat
- In menus, type the number for options, or text commands when prompted

Features implemented
--------------------
- Character classes: Night Surgeon, Lucid Magician, Insomniac, Broker (Novice), Night Watch, Somnomancer
- Stats: Strength, Agility, Magic, Health, Sanity
- Multi-stage world: Neon Arcade, Moonlit Bazaar, Hollow Atrium
- Turn-based combat with dice-roll randomness and special moves
- Inventory with use and discard (remove by using)
- Branching decisions and at least three distinct endings:
    * merchant_resell (wealthy but cursed)
    * burned_contract (free market, no fortune)
    * bound_contract (powerful but indebted)
    * plus neutral/helping/exploit/death endings
- Error handling for unexpected inputs and save/load functionality
- AI-only generated code, story text, items, and README (per assignment)

Design notes & limitations
--------------------------
- Combat uses simple mechanics but includes randomness and class-specific special moves.
- Economy is minimal (merchant is a straightforward vendor). This keeps the game focused on narrative and branching.
- Future expansions: add equipment, persistent gold, more endings, and deeper merchant logic.

Enjoy the Dream Market!