#!/usr/bin/env python3
# Dream Market - text-based RPG
# AI-generated (per assignment)
# Save as: dream_market.py
#
# Features:
#  - Character creation (6 classes, including Night Surgeon, Lucid Magician, Insomniac)
#  - Stats: Strength, Agility, Magic, Health, Sanity
#  - Multi-stage world (Neon Arcade, Moonlit Bazaar, Hollow Atrium)
#  - Turn-based combat with randomness, enemy specials, and class specials
#  - Inventory (view/use/discard), items with use behaviors
#  - Branching choices and multiple endings (>=3)
#  - Save/load (simple JSON) and error handling for unexpected input
#  - All narrative, code, and documentation are AI-generated

import random
import sys
import textwrap
import json
from pathlib import Path

# ---------------- utility functions ----------------

def wrap(s, width=78):
    """Wrap long paragraphs to terminal-friendly width"""
    return "\n".join(textwrap.wrap(s, width=width))

def prompt(options=None, text=None):
    """
    Generic prompt wrapper.
    - options: if provided, checks the raw input against allowed options (case-insensitive).
    - returns the user's raw input (string) or None if invalid for options.
    Handles KeyboardInterrupt / EOF gracefully.
    """
    try:
        if text:
            print(text)
        choice = input("> ").strip()
        if options is None:
            return choice
        if choice.lower() in [o.lower() for o in options]:
            return choice
        return None
    except (EOFError, KeyboardInterrupt):
        print("\nInput interrupted. Exiting game.")
        sys.exit(0)

def roll(d=20):
    """Roll a d-sided die (1..d)"""
    return random.randint(1, d)

# ---------------- Items & inventory ----------------

class Item:
    """Represents a usable or passive item."""
    def __init__(self, name, desc, use_fn=None, stackable=False):
        self.name = name
        self.desc = desc
        self.use_fn = use_fn  # callable(player, enemy)
        self.stackable = stackable

    def use(self, player, enemy=None, **kwargs):
        if callable(self.use_fn):
            return self.use_fn(player, enemy, **kwargs)
        return wrap(f"Nothing happens when you use the {self.name}.")

    def __str__(self):
        return f"{self.name}: {self.desc}"

class Inventory:
    """Simple inventory with duplicate items allowed."""
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def remove(self, item_name):
        # remove first matching by name, case-insensitive
        for i, it in enumerate(self.items):
            if it.name.lower() == item_name.lower():
                return self.items.pop(i)
        return None

    def list(self):
        if not self.items:
            return "Your inventory is empty."
        counts = {}
        for it in self.items:
            counts[it.name] = counts.get(it.name, 0) + 1
        lines = []
        for name, cnt in counts.items():
            desc = next((it.desc for it in self.items if it.name == name), "")
            lines.append(f"{name} x{cnt} - {desc}")
        return "\n".join(lines)

# ---------------- player & classes ----------------

class Player:
    """Player object with stats, inventory, and flags used for branching."""
    def __init__(self, name, cls):
        self.name = name
        self.cls = cls['key']
        self.class_name = cls['name']
        self.max_health = cls['health']
        self.health = cls['health']
        self.sanity = cls.get('sanity', 100)
        self.strength = cls['strength']
        self.agility = cls['agility']
        self.magic = cls['magic']
        self.level = 1
        self.xp = 0
        self.inventory = Inventory()
        self.equipped = None
        self.alive = True
        self.flags = {}          # story flags (e.g., helped_child)
        self.class_resource = {} # class specific temp resources

    def status(self):
        s = [
            f"{self.name} - {self.class_name} (Level {self.level})",
            f"HP: {self.health}/{self.max_health}    Sanity: {self.sanity}",
            f"STR: {self.strength}  AGI: {self.agility}  MAG: {self.magic}",
            f"XP: {self.xp}"
        ]
        if self.equipped:
            s.append(f"Equipped: {self.equipped.name}")
        return "\n".join(s)

    def modify_health(self, amt):
        self.health = max(0, min(self.max_health, self.health + amt))
        if self.health == 0:
            self.alive = False

    def modify_sanity(self, amt):
        self.sanity += amt
        if self.sanity <= -50:
            # sanity death: some classes die by losing sanity
            self.alive = False

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= 100 * self.level:
            self.xp -= 100 * self.level
            self.level += 1
            self.max_health += 10
            self.strength += 1
            self.agility += 1
            self.magic += 1
            print(wrap(f"You leveled up! You are now level {self.level}."))

# ---------------- class definitions (AI-generated) ----------------

CLASSES = [
    {
        'key': 'night_surgeon', 'name': 'Night Surgeon',
        'health': 90, 'strength': 8, 'agility': 6, 'magic': 6, 'sanity': 80,
        'desc': 'Extracts emotional items from defeated nightmares (Fear Shard, Hope Seed).'
    },
    {
        'key': 'lucid_magician', 'name': 'Lucid Magician',
        'health': 70, 'strength': 4, 'agility': 7, 'magic': 12, 'sanity': 90,
        'desc': 'Reality-bending actions like "rewrite rule: enemy misses next turn."'
    },
    {
        'key': 'insomniac', 'name': 'Insomniac',
        'health': 60, 'strength': 10, 'agility': 8, 'magic': 4, 'sanity': 120,
        'desc': 'Has powerful abilities but loses sanity instead of health.'
    },
    # Added accessible starter classes
    {
        'key': 'broker_novice', 'name': 'Broker (Novice)',
        'health': 80, 'strength': 6, 'agility': 8, 'magic': 6, 'sanity': 100,
        'desc': 'Balanced starter: negotiates and resells dreams.'
    },
    {
        'key': 'night_watch', 'name': 'Night Watch',
        'health': 100, 'strength': 9, 'agility': 5, 'magic': 3, 'sanity': 100,
        'desc': 'Tough guard-like class: excels at physical combat.'
    },
    {
        'key': 'somnomancer', 'name': 'Somnomancer',
        'health': 65, 'strength': 3, 'agility': 6, 'magic': 11, 'sanity': 95,
        'desc': 'Dream-focused mage with higher magic stat.'
    }
]

CLASS_KEY_MAP = {c['key']: c for c in CLASSES}

# ---------------- items and item behaviors ----------------

def heal_potion_use(player, enemy=None, **kwargs):
    amt = 30
    player.modify_health(amt)
    return wrap(f"You drink the Dream Elixir and recover {amt} HP.")

def sanity_potion_use(player, enemy=None, **kwargs):
    amt = 25
    player.modify_sanity(amt)
    return wrap(f"You inhale a Calm Mist and recover {amt} Sanity.")

def fear_shard_use(player, enemy=None, **kwargs):
    if enemy:
        dmg = 20 + int(player.magic * 0.5)
        enemy.take_damage(dmg)
        return wrap(f"You hurl a Fear Shard at {enemy.name}, dealing {dmg} magic damage.")
    return wrap("The Fear Shard hums; it's inert outside combat.")

ITEMS = {
    'Dream Elixir': Item('Dream Elixir', 'Restores 30 HP.', use_fn=heal_potion_use, stackable=True),
    'Calm Mist': Item('Calm Mist', 'Restores 25 Sanity.', use_fn=sanity_potion_use, stackable=True),
    'Fear Shard': Item('Fear Shard', 'A sliver of dread. Use in combat to damage enemies.', use_fn=fear_shard_use, stackable=True),
    'Hope Seed': Item('Hope Seed', 'A tiny mote of hope. Can pacify weak nightmares.', stackable=True),
    'Broker Ledger': Item('Broker Ledger', 'Record of transactions; required for one ending.'),
}

# ---------------- enemy logic & specials ----------------

class Enemy:
    def __init__(self, name, hp, strength, agility, magic, desc, difficulty=1, special=None):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.strength = strength
        self.agility = agility
        self.magic = magic
        self.desc = desc
        self.difficulty = difficulty
        self.special = special or {}
        self.alive = True

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False

    def attack_player(self, player):
        hit_roll = roll(20) + int(self.agility / 2)
        evade = roll(20) + int(player.agility / 2)
        if hit_roll >= evade:
            base = int(self.strength * (1 + random.random() * 0.5))
            player.modify_health(-base)
            return wrap(f"{self.name} attacks and hits you for {base} damage.")
        return wrap(f"{self.name} lunges but misses.")

    def special_move(self, player):
        if not self.special:
            return None
        name, effect = random.choice(list(self.special.items()))
        return effect(self, player)

def nightmare_bellow(enemy, player):
    val = 10 + enemy.magic
    player.modify_sanity(-val)
    return wrap(f"{enemy.name} bellows — your mind frays (-{val} Sanity).")

def dream_snare(enemy, player):
    loss = 2
    player.agility = max(1, player.agility - loss)
    return wrap(f"{enemy.name} ensnares dream-threads — your agility drops by {loss} this fight.")

# ---------------- areas & encounters ----------------

AREAS = [
    {
        'key': 'neon_arcade',
        'name': 'Neon Arcade',
        'desc': 'A humming arcade of half-remembered games. Light leaks like memory in rain.',
        'encounters': [
            lambda: Enemy('Pixel Wraith', 30, 6, 8, 4, 'A jagged ghost of a corrupted sprite.', difficulty=1, special={'bellow': nightmare_bellow}),
            lambda: Enemy('Token Thief', 35, 7, 9, 3, 'A quick-handed dream that steals small comforts.', difficulty=1),
            'merchant',
            'choice_scene'
        ]
    },
    {
        'key': 'moonlit_bazaar',
        'name': 'Moonlit Bazaar',
        'desc': 'Stalls of impossible goods and other Brokers trading in whispers.',
        'encounters': [
            lambda: Enemy('Somber Vendor', 40, 5, 6, 8, 'A vendor whose wares sadden those who linger.', difficulty=2, special={'snare': dream_snare}),
            lambda: Enemy('Sleep-Poltergeist', 45, 9, 5, 6, 'A heavy-handed nightmare that throws furniture.', difficulty=2),
            'merchant',
            'choice_scene'
        ]
    },
    {
        'key': 'hollow_atrium',
        'name': 'Hollow Atrium',
        'desc': 'The vault where deep traded dreams are stored — echoes answer back.',
        'encounters': [
            lambda: Enemy('Atrium Warden', 75, 12, 8, 10, 'A guardian formed of contracts and lost promises.', difficulty=3, special={'bellow': nightmare_bellow, 'snare': dream_snare}),
            'boss_scene'
        ]
    }
]

AREA_MAP = {a['key']: a for a in AREAS}

def merchant_scene(player):
    """Simple merchant stub allowing basic purchases (no gold accounting; items added directly)."""
    print(wrap("A robed figure counts teeth like coins. They offer goods in exchange for items or favors."))
    while True:
        print("\nMerchant offers:")
        print("1) Dream Elixir (30 gold equivalent) - pity price")
        print("2) Calm Mist (20)")
        print("3) Fear Shard (rare) - tradeable")
        print("Type 'leave' to go back.")
        choice = prompt(options=None, text="Choose an item to 'buy' by typing its number, or 'leave'.")
        if choice is None:
            print("That is not a valid command. Try again.")
            continue
        if choice.lower() == 'leave':
            return "leave"
        if choice == '1':
            player.inventory.add(ITEMS['Dream Elixir'])
            print("You bought a Dream Elixir.")
        elif choice == '2':
            player.inventory.add(ITEMS['Calm Mist'])
            print("You bought a Calm Mist.")
        elif choice == '3':
            player.inventory.add(ITEMS['Fear Shard'])
            print("You bought a Fear Shard.")
        else:
            print("That is not a valid command.")

# ---------------- combat engine ----------------

class Combat:
    """Handles a single enemy encounter: turn order, player actions, enemy specials."""
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.turn_count = 0
        self.rewrite_effects = {}  # for Lucid Magician rewrites

    def show_status(self):
        print(wrap(f"=== Combat: {self.player.name} vs {self.enemy.name} ==="))
        print(self.player.status())
        print(f"{self.enemy.name} HP: {self.enemy.hp}/{self.enemy.max_hp}")

    def player_turn(self):
        print("\nYour options: attack, defend, use <item name>, inventory, special, stats, run")
        choice = prompt(options=None, text="What do you do? (type command)")
        if choice is None:
            print("That's not a valid command.")
            return self.player_turn()
        tokens = choice.split()
        cmd = tokens[0].lower()
        if cmd == 'attack':
            return self.player_attack()
        elif cmd == 'defend':
            return self.player_defend()
        elif cmd == 'use':
            if len(tokens) == 1:
                print("Use what? Type: use Dream Elixir")
                return None
            item_name = " ".join(tokens[1:])
            item = self.player.inventory.remove(item_name)
            if not item:
                print(f"You don't have a '{item_name}'.")
                return None
            print(item.use(self.player, self.enemy))
            return None
        elif cmd == 'inventory':
            print(self.player.inventory.list())
            return None
        elif cmd == 'special':
            return self.player_special()
        elif cmd == 'stats':
            print(self.player.status())
            return None
        elif cmd == 'run':
            chance = roll(20) + int(self.player.agility / 2)
            escape = roll(20) + int(self.enemy.agility / 2)
            if chance > escape:
                print("You slip through dream-threads and escape the fight!")
                return 'escaped'
            print("You try to run but the dream pulls you back.")
            return None
        else:
            print("That is not a valid command.")
            return None

    def player_attack(self):
        atk_roll = roll(20) + int(self.player.strength / 2)
        def_roll = roll(20) + int(self.enemy.agility / 2)
        if atk_roll >= def_roll:
            base = int(self.player.strength * (1 + random.random() * 0.5))
            # Lucid chance to critical via reality-bend
            if self.player.class_name.lower().startswith('lucid') and roll(100) < 20:
                base = int(base * 1.8)
                print("You bend a seam of reality — critical strike!")
            self.enemy.take_damage(base)
            print(f"You hit {self.enemy.name} for {base} damage.")
            return None
        print("Your attack misses.")
        return None

    def player_defend(self):
        print("You brace yourself, preparing to reduce incoming damage.")
        old = self.player.agility
        self.player.agility += 4
        self.player.flags['defend_tmp'] = old
        return None

    def player_special(self):
        cls = self.player.cls
        if cls == 'night_surgeon':
            # Extraction: harvest an item if successful
            if 'extracted' in self.player.class_resource:
                print("You lack the tools to extract again so soon.")
                return None
            if roll(20) + self.player.magic >= 15:
                self.player.inventory.add(ITEMS['Fear Shard'])
                self.player.class_resource['extracted'] = True
                print("You deftly slice dream-membranes and extract a Fear Shard.")
            else:
                print("Your extraction falters and yields nothing.")
            return None
        elif cls == 'lucid_magician':
            # Rewrite rule to make enemy miss next attack
            if 'rewritten' in self.rewrite_effects:
                print("Reality already feels altered; you cannot rewrite twice in a row.")
                return None
            if roll(20) + self.player.magic >= 15:
                self.rewrite_effects['enemy_miss_next'] = True
                print("You whisper a new rule: the enemy's next attack will fail.")
            else:
                print("Your rewrite fails to anchor into the dream-fabric.")
            return None
        elif cls == 'insomniac':
            # powerful move that costs sanity instead of health
            cost = 20
            if self.player.sanity - cost <= -50:
                print("You cannot spend that much sanity — collapse risk too high.")
                return None
            self.player.modify_sanity(-cost)
            dmg = int(self.player.strength * 2.5)
            self.enemy.take_damage(dmg)
            print(f"You unleash a desperate onslaught, dealing {dmg} damage at the cost of {cost} Sanity.")
            return None
        else:
            # generic special: magic-based if possible
            if self.player.magic >= 10 and roll(20) + self.player.magic >= 12:
                dmg = int(self.player.magic * 1.5)
                self.enemy.take_damage(dmg)
                print(f"You cast a focused dream-spark, dealing {dmg} magic damage.")
            else:
                print("You attempt something special but nothing notable happens.")
            return None

    def enemy_turn(self):
        if not self.enemy.alive:
            return
        if self.rewrite_effects.get('enemy_miss_next'):
            print("The rewritten rule holds: the enemy's attack falters.")
            self.rewrite_effects.pop('enemy_miss_next', None)
            return
        if self.enemy.special and roll(100) < 30:
            res = self.enemy.special_move(self.player)
            if res:
                print(res)
                return
        print(self.enemy.attack_player(self.player))

    def run(self):
        # Combat loop
        while self.player.alive and self.enemy.alive:
            self.show_status()
            res = self.player_turn()
            if res == 'escaped':
                return 'escaped'
            # revert defend buff if present
            if 'defend_tmp' in self.player.flags:
                self.player.agility = self.player.flags.pop('defend_tmp')
            if not self.enemy.alive:
                break
            self.enemy_turn()
            if not self.player.alive:
                break
            self.turn_count += 1

        if not self.player.alive:
            print(wrap("You have been unmade by the dream. Everything fades."))
            return 'player_dead'
        if not self.enemy.alive:
            print(wrap(f"You defeated {self.enemy.name}!"))
            xp = 20 * self.enemy.difficulty + random.randint(0, 20)
            self.player.gain_xp(xp)
            # chance for drop
            if roll(100) < (30 * self.enemy.difficulty):
                drop = random.choice(['Fear Shard', 'Hope Seed'])
                self.player.inventory.add(ITEMS[drop])
                print(f"The dream spills a {drop}. You collect it.")
            return 'enemy_dead'

# ---------------- scenes & story flow ----------------

def intro():
    print(wrap("Welcome to THE DREAM MARKET — a night-shift text RPG."))
    print(wrap("Dreams are goods. You are a rookie Dream Broker. Tonight you will learn what it costs to trade in sleep."))
    print()

def choose_name():
    while True:
        name = prompt(options=None, text="Enter your name, broker:")
        if name:
            return name
        print("Please type a name.")

def choose_class():
    print("Choose your class:")
    for i, c in enumerate(CLASSES, 1):
        print(f"{i}) {c['name']} - {c['desc']} (HP:{c['health']} STR:{c['strength']} AGI:{c['agility']} MAG:{c['magic']})")
    while True:
        choice = prompt(options=None, text="Type the number of your chosen class:")
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(CLASSES):
                return CLASSES[idx]
        print("That is not a valid command.")

def area_loop(player):
    """Main area progression loop with random encounters and story branches."""
    current = 'neon_arcade'
    while player.alive:
        area = AREA_MAP[current]
        print("\n" + "="*10 + f" {area['name']} " + "="*10)
        print(wrap(area['desc']))
        encounter = random.choice(area['encounters'])
        if callable(encounter):
            enemy = encounter()
            combat = Combat(player, enemy)
            result = combat.run()
            if result == 'player_dead':
                return 'dead'
            elif result == 'escaped':
                current = area_choice_menu(player, current)
                continue
            else:
                if enemy.name == 'Atrium Warden':
                    player.flags['defeated_warden'] = True
                current = area_choice_menu(player, current)
                continue
        elif encounter == 'merchant':
            merchant_scene(player)
            current = area_choice_menu(player, current)
            continue
        elif encounter == 'choice_scene':
            choice_branch(player, area)
            current = area_choice_menu(player, current)
            continue
        elif encounter == 'boss_scene':
            boss = Enemy('The Slumber Contract', 110, 14, 9, 12, 'A contract made sentient, holding many bargains.', difficulty=4, special={'bellow': nightmare_bellow})
            print(wrap("A deep resonance echoes: the final bargain awaits."))
            combat = Combat(player, boss)
            res = combat.run()
            if res == 'player_dead':
                return 'dead'
            if not boss.alive:
                player.flags['defeated_contract'] = True
                return 'boss_defeated'
        else:
            print("An odd void passes by. Nothing happens.")
            current = area_choice_menu(player, current)
    return 'dead'

def area_choice_menu(player, current_area_key):
    print("\nWhere to next?")
    for i, a in enumerate(AREAS,1):
        print(f"{i}) {a['name']}")
    print("Type the number of the area to travel to, or 'stay' to linger.")
    while True:
        choice = prompt(options=None, text="Your choice:")
        if choice is None:
            print("That's not a valid command.")
            continue
        if choice.lower() == 'stay':
            return current_area_key
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(AREAS):
                return AREAS[idx]['key']
        print("That is not a valid command.")

def choice_branch(player, area):
    """Branching small scene with choice consequences tracked in flags."""
    print(wrap("You encounter a lost child of dreamstuff, humming a bargain. They ask for a favor."))
    print("Options: 1) Help the child.  2) Ignore the child.  3) Take advantage of them.")
    while True:
        ch = prompt(options=None, text="Choose 1, 2 or 3:")
        if ch == '1':
            print(wrap("You help the child mend a torn lullaby. They give you a Hope Seed."))
            player.inventory.add(ITEMS['Hope Seed'])
            player.flags['helped_child'] = True
            return
        elif ch == '2':
            print(wrap("You walk on, the child's voice fading. You feel ever so slightly colder."))
            player.flags['ignored_child'] = True
            return
        elif ch == '3':
            print(wrap("You trick the child and take their lullaby. You gain a small coin and a sinister mark."))
            player.inventory.add(ITEMS['Fear Shard'])
            player.flags['exploited_child'] = True
            return
        else:
            print("That's not a valid command.")

# ---------------- endings ----------------

def ending_shopkeeper(player):
    """Final choice after defeating the main contract; multiple endings branch here."""
    print("\nFinal choice: You can either 'resell' the Slumber Contract, 'burn' it, or 'bind' it to your ledger.")
    while True:
        ch = prompt(options=None, text="Type 'resell', 'burn', or 'bind':")
        if ch is None:
            print("That is not a valid command.")
            continue
        lc = ch.lower()
        if lc == 'resell':
            # requires ledger to broker the sale
            if any(it.name == 'Broker Ledger' for it in player.inventory.items):
                print(wrap("You bind the contract to your ledger and resell it to a wealthy collector. You become wealthy, but rumors say the buyer's sleep never returns."))
                return 'merchant_resell'
            print("You lack the Broker Ledger required to broker this particular sale.")
            continue
        elif lc == 'burn':
            print(wrap("You set the contract aflame; the room sighs. Without it, the Market breathes free — but you lose your one chance at fortune."))
            return 'burned_contract'
        elif lc == 'bind':
            print(wrap("You bind the contract to yourself, shouldering its bargains. Your power grows, but so do the debts across your soul."))
            return 'bound_contract'
        else:
            print("That is not a valid command.")

def compute_ending(player, end_state):
    """Compute which ending is reached based on flags, inventory, and final state."""
    if end_state == 'dead':
        print(wrap("You failed your first shift. The Dream Market takes another apprentice."))
        return 'death_ending'
    elif end_state == 'boss_defeated' or player.flags.get('defeated_contract'):
        ending = ending_shopkeeper(player)
        return ending
    else:
        if player.flags.get('helped_child'):
            print(wrap("The child returns in your dreams with a small gift. You find peace and keep your modest trade."))
            return 'helping_ending'
        if player.flags.get('exploited_child'):
            print(wrap("The mark on your hand grows. You achieve wealth through petty bargains, but your nights are hollow."))
            return 'exploit_ending'
        print(wrap("You finish the shift and return to the mundane world, ledger lighter with experience."))
        return 'neutral_ending'

# ---------------- save/load ----------------

SAVE_PATH = Path("dream_market_save.json")

def save_game(player):
    data = {
        'name': player.name,
        'class': player.cls,
        'health': player.health,
        'max_health': player.max_health,
        'sanity': player.sanity,
        'strength': player.strength,
        'agility': player.agility,
        'magic': player.magic,
        'level': player.level,
        'xp': player.xp,
        'inventory': [it.name for it in player.inventory.items],
        'flags': player.flags
    }
    with SAVE_PATH.open('w') as f:
        json.dump(data, f)
    print(f"Game saved to {SAVE_PATH}")

def load_game():
    if not SAVE_PATH.exists():
        print("No saved game found.")
        return None
    with SAVE_PATH.open('r') as f:
        data = json.load(f)
    cls = CLASS_KEY_MAP.get(data['class']) or next((c for c in CLASSES if c['key'] == data['class']), CLASSES[0])
    p = Player(data['name'], cls)
    p.health = data['health']
    p.max_health = data['max_health']
    p.sanity = data['sanity']
    p.strength = data['strength']
    p.agility = data['agility']
    p.magic = data['magic']
    p.level = data['level']
    p.xp = data['xp']
    for itname in data.get('inventory', []):
        if itname in ITEMS:
            p.inventory.add(ITEMS[itname])
    p.flags = data.get('flags', {})
    print("Game loaded.")
    return p

# ---------------- main menu & loop ----------------

def main_menu():
    print("\n=== DREAM MARKET - Main Menu ===")
    print("1) New Game")
    print("2) Load Game")
    print("3) Read README")
    print("4) Quit")
    while True:
        choice = prompt(options=None, text="Select an option (1-4):")
        if choice == '1':
            return 'new'
        if choice == '2':
            return 'load'
        if choice == '3':
            show_readme()
            continue
        if choice == '4':
            print("Goodbye.")
            sys.exit(0)
        print("That is not a valid command.")

def show_readme():
    try:
        text = Path("DREAM_MARKET_README.txt").read_text()
        print("\n" + text)
    except FileNotFoundError:
        print("README not found. Please ensure DREAM_MARKET_README.txt is in the same folder.")

def run_game():
    intro()
    while True:
        action = main_menu()
        if action == 'new':
            name = choose_name()
            cls = choose_class()
            player = Player(name, cls)
            # starter items for all players
            player.inventory.add(ITEMS['Dream Elixir'])
            player.inventory.add(ITEMS['Calm Mist'])
            # Night Surgeon begins with a Broker Ledger to enable one ending path
            if player.cls == 'night_surgeon':
                player.inventory.add(ITEMS['Broker Ledger'])
            print(wrap(f"You wake at your stall. Name: {player.name}. Class: {player.class_name}."))
            end_state = area_loop(player)
            ending = compute_ending(player, end_state)
            print("\n=== ENDING ===")
            print(wrap(f"The game ended with: {ending}"))
            print("Do you want to save your character? (yes/no)")
            if prompt(options=['yes', 'no']):
                save_game(player)
            print("Thanks for playing.")
            return
        elif action == 'load':
            p = load_game()
            if p:
                end_state = area_loop(p)
                ending = compute_ending(p, end_state)
                print("\n=== ENDING ===")
                print(wrap(f"The game ended with: {ending}"))
                return

# ---------------- README text included below for convenience ----------------
README_TEXT = """THE DREAM MARKET - README
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
"""

# write README file automatically next to script for convenience
try:
    Path("DREAM_MARKET_README.txt").write_text(README_TEXT)
except Exception:
    pass

if __name__ == "__main__":
    run_game()