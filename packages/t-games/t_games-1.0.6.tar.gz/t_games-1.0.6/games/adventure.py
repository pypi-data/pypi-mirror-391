import os
import time
import sys

class TextAdventure:
    def __init__(self):
        self.player_name = ""
        self.current_location = "start"
        self.inventory = []
        self.game_state = {
            "has_key": False,
            "door_unlocked": False,
            "talked_to_wizard": False,
            "has_sword": False,
            "dragon_defeated": False,
            "treasure_found": False,
            "has_map": False,
            "has_torch": False,
            "cave_explored": False,
            "riddle_solved": False,
            "ghost_befriended": False,
            "has_amulet": False,
            "bridge_repaired": False,
            "troll_defeated": False,
            "has_rope": False,
            "secret_passage_found": False,
            "ancient_guardian_defeated": False,
            "crystal_activated": False,
            "has_shield": False,
            "library_explored": False,
            "potion_brewed": False
        }
        self.health = 100
        self.game_over = False
        self.gold = 50
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def slow_print(self, text, delay=0.03):
        """Print text with typewriter effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    
    def print_separator(self):
        """Print a decorative separator"""
        print("\n" + "=" * 70 + "\n")
    
    def show_hint(self):
        """Show context-sensitive hints based on current location and progress"""
        location = self.current_location
        
        print("\n" + "=" * 70)
        print("HINTS".center(70))
        print("=" * 70)
        
        if location == "start":
            print("\n🗺️  Explore all four directions from the village square")
            print("🔍  Try examining objects like the well")
            print("💰  Visit the shop early to buy useful items (torch is important!)")
            print("🌲  The forest to the north holds many secrets")
        
        elif location == "forest":
            print("\n🕳️  There's a cave to the north - you'll need light to explore it")
            print("🌳  The clearing to the east has something important")
        
        elif location == "cave":
            print("\n🔦  You need a TORCH to explore safely (buy from shop for 10 gold)")
            print("💎  Exploring the cave will reward you with gold")
        
        elif location == "clearing":
            print("\n🗝️  Don't forget to take the SILVER KEY!")
            print("❓  The altar has a riddle - the answer is something that repeats sound")
            print("💀  There's a cemetery to the north with more secrets")
        
        elif location == "cemetery":
            print("\n👻  Talk to the ghost to gain access to the mausoleum")
            print("🧿  The amulet inside will save your life once!")
        
        elif location == "tower":
            print("\n🔑  Use the SILVER KEY from the forest clearing to unlock the door")
            print("⬇️  Don't forget to explore the basement (go DOWN)")
        
        elif location == "basement":
            print("\n🪢  Take the ROPE - you'll need it to repair the bridge later")
            print("🗺️  The map shows secret locations")
        
        elif location == "tower_inside":
            print("\n🧙  Talk to the wizard to learn about your quest")
            print("⚔️  Take the ENCHANTED SWORD - it's essential for combat")
            print("📚  Visit the library to gain knowledge")
            print("⬆️  Go up to the tower top for a good view")
        
        elif location == "library":
            print("\n📖  Reading books will help you defeat the ancient guardian")
            print("🧪  The potion recipe is advanced content")
        
        elif location == "shop":
            print("\n💰  Recommended purchases:")
            print("   - Torch (10g) - ESSENTIAL for cave exploration")
            print("   - Health Potion (20g) - Restores health")
            print("   - Shield (30g) - Reduces damage in combat")
        
        elif location == "gate":
            print("\n🐉  West leads to the dragon's lair (final boss)")
            print("🌉  South leads to a bridge with challenges")
            print("🏔️  North leads to mountain trails with secrets")
        
        elif location == "bridge":
            print("\n🧌  You can fight the troll OR pay 50 gold")
            print("🪢  Use ROPE to repair the bridge before crossing")
            print("🏝️  The island beyond has powerful artifacts")
        
        elif location == "island":
            print("\n📚  You need the SWORD and LIBRARY KNOWLEDGE to defeat the guardian")
            print("💎  The Power Crystal increases your strength")
        
        elif location == "mountains":
            print("\n🗿  Look for the secret passage - it contains legendary armor")
        
        elif location == "lair":
            print("\n⚔️  Make sure you have the ENCHANTED SWORD before fighting!")
            print("🛡️  Having a SHIELD and ARMOR reduces damage significantly")
            print("🧿  The Protection Amulet can save you from death")
            print("🏆  After defeating the dragon, explore EAST and WEST chambers")
        
        elif location in ["east_chamber", "west_chamber"]:
            print("\n👑  The Crown in the EAST chamber completes the main quest")
            print("🥚  The Dragon Egg in the WEST chamber is a bonus treasure")
            print("💰  Don't forget to grab gold from the west chamber!")
        
        else:
            print("\nExplore your surroundings and interact with everything!")
        
        print("\n" + "=" * 70)

    def show_status(self):
        """Display player status"""
        print(f"\n[Health: {self.health}/100] [Gold: {self.gold}] [Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}]")
        self.print_separator()
    
    def get_location_description(self):
        """Get description for current location"""
        locations = {
            "start": {
                "name": "Village Square",
                "description": "You stand in the center of a small village. The sun is setting, casting long shadows across the cobblestone square. To the NORTH, you see a dark forest. To the EAST is a mysterious old tower. To the SOUTH lies a quiet village shop. To the WEST, the village gate leads to the outside world. A WELL sits in the center of the square.",
                "options": ["north", "east", "south", "west", "examine well", "inventory"]
            },
            "forest": {
                "name": "Dark Forest",
                "description": "The forest is dense and mysterious. Ancient trees tower above you, their branches blocking most of the sunlight. You hear strange sounds in the distance. There's a clearing to the EAST, a CAVE entrance to the NORTH, and you can go back SOUTH to the village.",
                "options": ["north", "east", "south", "look", "search"]
            },
            "cave": {
                "name": "Dark Cave",
                "description": "The cave is pitch black and damp. Water drips from the ceiling. You can barely see anything without light. Strange echoes bounce off the walls. You sense something valuable might be here.",
                "options": ["south", "explore", "use torch", "search"]
            },
            "clearing": {
                "name": "Forest Clearing",
                "description": "You find yourself in a peaceful clearing. In the center lies an old stone altar with strange runes carved into it. A silver KEY glints in the fading light. To the NORTH, you see an ancient CEMETERY.",
                "options": ["take key", "north", "west", "south", "examine altar"]
            },
            "cemetery": {
                "name": "Ancient Cemetery",
                "description": "Weathered tombstones stand in rows, covered in moss. A ghostly figure floats near a large mausoleum. The air is cold and misty. The ghost seems to be guarding something.",
                "options": ["talk to ghost", "examine mausoleum", "south", "search"]
            },
            "mausoleum": {
                "name": "Inside Mausoleum",
                "description": "The mausoleum is dark and filled with ancient coffins. On a stone pedestal, you see a glowing AMULET. Strange whispers echo through the chamber.",
                "options": ["take amulet", "examine coffins", "exit"]
            },
            "tower": {
                "name": "Mysterious Tower",
                "description": "An ancient stone tower looms before you. The heavy wooden door is locked with an ornate mechanism. Strange symbols glow faintly on the door frame. You notice stairs leading DOWN to a basement.",
                "options": ["unlock door", "down", "west", "examine door"]
            },
            "basement": {
                "name": "Tower Basement",
                "description": "A dusty basement filled with old crates and barrels. You see a ROPE coiled in the corner and what looks like an old MAP on the wall. Rats scurry in the shadows.",
                "options": ["take rope", "take map", "up", "search crates"]
            },
            "tower_inside": {
                "name": "Inside the Tower",
                "description": "The tower's interior is filled with ancient books and magical artifacts. A WIZARD in flowing robes stands before a crystal ball, observing you with interest. Stairs lead UP to the tower top. A door leads to the LIBRARY.",
                "options": ["talk to wizard", "take sword", "up", "library", "down"]
            },
            "tower_top": {
                "name": "Tower Top",
                "description": "From the top of the tower, you have a commanding view of the land. You can see the dragon's lair in the distance, a mysterious island across the river, and mountains to the far north. A telescope points toward the stars.",
                "options": ["use telescope", "down", "look around"]
            },
            "library": {
                "name": "Ancient Library",
                "description": "Thousands of dusty books line the shelves from floor to ceiling. A large tome sits open on a reading desk, showing a recipe for a powerful POTION. You see books about dragons, magic, and ancient legends.",
                "options": ["read books", "take potion recipe", "back", "search"]
            },
            "shop": {
                "name": "Village Shop",
                "description": "A cozy shop filled with various goods. The shopkeeper greets you warmly. You see health potions (20 gold), a TORCH (10 gold), and a SHIELD (30 gold) on display.",
                "options": ["buy potion", "buy torch", "buy shield", "talk", "north"]
            },
            "gate": {
                "name": "Village Gate",
                "description": "You stand at the western gate of the village. Beyond lies a treacherous mountain pass. To the SOUTH is a rickety BRIDGE over a deep chasm. In the distance WEST, you can see smoke rising from the dragon's lair. To the NORTH, mountain trails lead upward.",
                "options": ["west", "north", "south", "east"]
            },
            "bridge": {
                "name": "Rickety Bridge",
                "description": "An old wooden bridge spans a deep chasm. The planks look rotten and unstable. A TROLL sits beneath the bridge, blocking the path. Beyond the bridge, you see a mysterious ISLAND with ancient ruins.",
                "options": ["cross bridge", "talk to troll", "fight troll", "repair bridge", "north"]
            },
            "island": {
                "name": "Mysterious Island",
                "description": "The island is covered in ancient ruins and overgrown vegetation. A massive stone GUARDIAN statue stands in the center. Strange energy emanates from a CRYSTAL embedded in the statue's chest.",
                "options": ["examine guardian", "take crystal", "examine ruins", "back"]
            },
            "mountains": {
                "name": "Mountain Trail",
                "description": "The mountain trail is steep and treacherous. Snow covers the higher peaks. You see a SECRET PASSAGE partially hidden behind rocks. An EAGLE circles overhead.",
                "options": ["enter passage", "climb higher", "south", "call eagle"]
            },
            "secret_passage": {
                "name": "Secret Mountain Passage",
                "description": "A hidden tunnel leads deep into the mountain. Ancient carvings cover the walls, telling stories of old battles. At the end, you find a chamber with legendary armor and weapons.",
                "options": ["take armor", "examine carvings", "exit"]
            },
            "lair": {
                "name": "Dragon's Lair",
                "description": "You enter a massive cavern filled with piles of gold and treasure. At the far end, a MASSIVE DRAGON sleeps on a mountain of coins. Its scales shimmer in the torch light. You notice multiple exits leading to different treasure chambers.",
                "options": ["fight dragon", "sneak to treasure", "east chamber", "west chamber", "flee"]
            },
            "east_chamber": {
                "name": "Eastern Treasure Chamber",
                "description": "This chamber contains ancient artifacts and magical items. You see the legendary CROWN OF KINGS on a pedestal, surrounded by protective runes.",
                "options": ["take crown", "examine runes", "back"]
            },
            "west_chamber": {
                "name": "Western Treasure Chamber",
                "description": "This chamber is filled with mountains of gold coins and precious gems. Among the treasure, you spot the DRAGON'S EGG, said to grant immense power.",
                "options": ["take egg", "take gold", "examine treasures", "back"]
            }
        }
        
        return locations.get(self.current_location, locations["start"])
    
    def handle_action(self, action):
        """Process player actions"""
        action = action.lower().strip()
        
        # Universal commands
        if action in ["inventory", "i"]:
            if self.inventory:
                print(f"\nYou are carrying: {', '.join(self.inventory)}")
            else:
                print("\nYour inventory is empty.")
            return
        
        if action in ["look", "l"]:
            location = self.get_location_description()
            print(f"\n{location['description']}")
            return
        
        if action in ["help", "h"]:
            print("\nAvailable commands: north, south, east, west, take, use, talk, fight, look, inventory, help, quit")
            print("\nType 'hint' for gameplay tips!")
            return
        
        if action == "hint":
            self.show_hint()
            return

            return
        
        if action in ["quit", "exit", "q"]:
            self.game_over = True
            return
        
        # Location-specific actions
        if self.current_location == "start":
            if action == "north":
                self.current_location = "forest"
                self.slow_print("\nYou venture into the dark forest...")
            elif action == "east":
                self.current_location = "tower"
                self.slow_print("\nYou approach the mysterious tower...")
            elif action == "south":
                self.current_location = "shop"
                self.slow_print("\nYou enter the village shop...")
            elif action == "west":
                self.current_location = "gate"
                self.slow_print("\nYou walk towards the village gate...")
            elif action in ["examine well", "well", "look well"]:
                if not self.game_state["has_torch"] and "Torch" not in self.inventory:
                    print("\nYou peer into the well and notice something shiny at the bottom. But it's too dark to see clearly.")
                else:
                    print("\nThe well is deep and dark. Fresh water flows at the bottom.")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "forest":
            if action == "north":
                self.current_location = "cave"
                self.slow_print("\nYou enter the dark cave...")
            elif action == "east":
                self.current_location = "clearing"
                self.slow_print("\nYou push through the undergrowth and find a clearing...")
            elif action == "south":
                self.current_location = "start"
                self.slow_print("\nYou return to the village square...")
            elif action == "search":
                print("\nYou search the forest but find nothing of interest. Perhaps you should explore the CAVE to the north or the CLEARING to the east.")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "cave":
            if action in ["explore", "search"]:
                if "Torch" in self.inventory or self.game_state["has_torch"]:
                    if not self.game_state["cave_explored"]:
                        self.slow_print("\nYou light your torch and explore the cave...")
                        time.sleep(1)
                        self.slow_print("You discover ancient cave paintings and a small chest!")
                        self.gold += 30
                        self.game_state["cave_explored"] = True
                        print(f"\nYou found 30 gold! Total gold: {self.gold}")
                    else:
                        print("\nYou've already explored this cave thoroughly.")
                else:
                    print("\nIt's too dark to explore safely. You need a torch!")
            elif action in ["use torch"]:
                if "Torch" in self.inventory:
                    print("\nYour torch illuminates the cave. Use EXPLORE to search the area.")
                else:
                    print("\nYou don't have a torch.")
            elif action == "south":
                self.current_location = "forest"
                print("\nYou exit the cave...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "clearing":
            if action in ["take key", "get key", "pick up key"]:
                if not self.game_state["has_key"]:
                    self.inventory.append("Silver Key")
                    self.game_state["has_key"] = True
                    self.slow_print("\nYou pick up the silver key. It feels warm to the touch and pulses with magical energy.")
                else:
                    print("\nYou already took the key.")
            elif action == "north":
                self.current_location = "cemetery"
                self.slow_print("\nYou cautiously enter the ancient cemetery...")
            elif action in ["examine altar", "look altar"]:
                if not self.game_state["riddle_solved"]:
                    self.slow_print("\nThe altar displays a riddle carved in stone:")
                    time.sleep(1)
                    print("\n'I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?'")
                    answer = input("\nYour answer: ").lower().strip()
                    if "echo" in answer:
                        self.slow_print("\nThe altar glows brightly! You solved the riddle!")
                        self.game_state["riddle_solved"] = True
                        self.health = min(100, self.health + 20)
                        print(f"\nYour health increased by 20! Current health: {self.health}")
                    else:
                        print("\nThe altar remains silent. That's not the right answer.")
                else:
                    print("\nThe altar glows softly, its riddle already solved.")
            elif action == "west":
                self.current_location = "forest"
                self.slow_print("\nYou return to the dark forest...")
            elif action == "south":
                self.current_location = "start"
                self.slow_print("\nYou make your way back to the village...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "cemetery":
            if action in ["talk to ghost", "talk ghost", "speak"]:
                if not self.game_state["ghost_befriended"]:
                    self.slow_print("\nThe ghost speaks in a hollow voice:")
                    time.sleep(0.5)
                    self.slow_print("'I have guarded this place for centuries...'")
                    time.sleep(0.5)
                    self.slow_print("'If you promise to use the amulet for good, you may enter the mausoleum.'")
                    self.game_state["ghost_befriended"] = True
                else:
                    print("\nThe ghost nods at you peacefully.")
            elif action in ["examine mausoleum", "enter mausoleum", "mausoleum"]:
                if self.game_state["ghost_befriended"]:
                    self.current_location = "mausoleum"
                    self.slow_print("\nThe mausoleum door creaks open...")
                else:
                    print("\nThe ghost blocks your path. Perhaps you should talk to it first.")
            elif action == "south":
                self.current_location = "clearing"
                print("\nYou leave the cemetery...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "mausoleum":
            if action in ["take amulet", "get amulet"]:
                if not self.game_state["has_amulet"]:
                    self.inventory.append("Protection Amulet")
                    self.game_state["has_amulet"] = True
                    self.slow_print("\nYou take the Protection Amulet. A warm glow surrounds you!")
                    print("\nThe amulet will protect you from one fatal blow!")
                else:
                    print("\nYou already have the amulet.")
            elif action in ["exit", "leave", "out"]:
                self.current_location = "cemetery"
                print("\nYou exit the mausoleum...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "tower":
            if action in ["unlock door", "use key", "open door", "enter"]:
                if self.game_state["has_key"]:
                    if not self.game_state["door_unlocked"]:
                        self.game_state["door_unlocked"] = True
                        self.current_location = "tower_inside"
                        self.slow_print("\nThe key fits perfectly! The door swings open with a loud creak...")
                        time.sleep(1)
                        self.slow_print("You step inside the tower...")
                    else:
                        self.current_location = "tower_inside"
                        print("\nYou enter the tower...")
                else:
                    print("\nThe door is locked. You need a key to open it.")
            elif action in ["down", "basement"]:
                self.current_location = "basement"
                self.slow_print("\nYou carefully descend the stairs to the basement...")
            elif action in ["examine door", "look door"]:
                print("\nThe door has an ornate lock with mystical symbols. It looks like it needs a special key.")
            elif action == "west":
                self.current_location = "start"
                self.slow_print("\nYou return to the village square...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "basement":
            if action in ["take rope", "get rope"]:
                if "Rope" not in self.inventory:
                    self.inventory.append("Rope")
                    self.game_state["has_rope"] = True
                    print("\nYou take the sturdy rope. This could be useful for climbing or repairs!")
                else:
                    print("\nYou already have the rope.")
            elif action in ["take map", "get map"]:
                if "Ancient Map" not in self.inventory:
                    self.inventory.append("Ancient Map")
                    self.game_state["has_map"] = True
                    self.slow_print("\nYou take the ancient map. It shows secret locations and treasures!")
                else:
                    print("\nYou already have the map.")
            elif action in ["search crates", "search"]:
                if self.gold < 100:
                    self.gold += 15
                    print(f"\nYou find 15 gold hidden in the crates! Total gold: {self.gold}")
                else:
                    print("\nYou've already searched the crates.")
            elif action == "up":
                self.current_location = "tower"
                print("\nYou climb back up to the tower entrance...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "tower_inside":
            if action in ["talk to wizard", "talk wizard", "speak"]:
                if not self.game_state["talked_to_wizard"]:
                    self.game_state["talked_to_wizard"] = True
                    self.slow_print("\nThe wizard speaks in a deep, echoing voice:")
                    time.sleep(0.5)
                    self.slow_print("'Ah, a brave soul enters my domain. I sense you seek adventure.'")
                    time.sleep(0.5)
                    self.slow_print("'Take the enchanted sword from the wall. You will need it to face the dragon.'")
                    time.sleep(0.5)
                    self.slow_print("'The beast hoards a legendary treasure beyond the western gate.'")
                    time.sleep(0.5)
                    self.slow_print("'Visit my library to learn more about ancient magic and creatures.'")
                else:
                    print("\nThe wizard nods at you knowingly. 'Go forth, brave warrior. Remember, knowledge is power.'")
            elif action in ["take sword", "get sword", "pick up sword"]:
                if not self.game_state["has_sword"]:
                    self.inventory.append("Enchanted Sword")
                    self.game_state["has_sword"] = True
                    self.slow_print("\nYou take the magnificent sword from the wall. It glows with magical power!")
                else:
                    print("\nYou already have the sword.")
            elif action in ["up", "upstairs"]:
                self.current_location = "tower_top"
                self.slow_print("\nYou climb the spiral staircase to the top of the tower...")
            elif action in ["library", "enter library"]:
                self.current_location = "library"
                self.slow_print("\nYou enter the ancient library...")
            elif action in ["down", "exit", "leave"]:
                self.current_location = "tower"
                print("\nYou exit the tower...")
            elif action in ["look around", "search"]:
                print("\nYou see ancient tomes, magical artifacts, a beautiful sword mounted on the wall, and a door leading to the library.")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "tower_top":
            if action in ["use telescope", "telescope", "look telescope"]:
                self.slow_print("\nYou peer through the telescope...")
                time.sleep(1)
                self.slow_print("You see the dragon's lair clearly, with multiple chambers filled with treasure!")
                time.sleep(1)
                print("\nYou notice the dragon seems to be sleeping. This is your chance!")
            elif action == "down":
                self.current_location = "tower_inside"
                print("\nYou descend the stairs...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "library":
            if action in ["read books", "read", "study"]:
                if not self.game_state["library_explored"]:
                    self.slow_print("\nYou spend time reading the ancient books...")
                    time.sleep(1)
                    self.slow_print("You learn about dragon weaknesses, ancient artifacts, and powerful spells!")
                    self.game_state["library_explored"] = True
                    print("\nYour knowledge has increased! You feel more confident.")
                else:
                    print("\nYou've already studied these books thoroughly.")
            elif action in ["take potion recipe", "take recipe"]:
                if "Potion Recipe" not in self.inventory:
                    self.inventory.append("Potion Recipe")
                    print("\nYou take the potion recipe. It requires: herbs, crystal dust, and dragon scale.")
                else:
                    print("\nYou already have the recipe.")
            elif action in ["back", "exit"]:
                self.current_location = "tower_inside"
                print("\nYou return to the main tower room...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "shop":
            if action in ["buy potion", "buy", "potion"]:
                if self.gold >= 20:
                    if "Health Potion" not in self.inventory:
                        self.inventory.append("Health Potion")
                        self.gold -= 20
                        print(f"\nYou purchase a health potion for 20 gold. Remaining gold: {self.gold}")
                    else:
                        print("\nYou already have a health potion.")
                else:
                    print("\nYou don't have enough gold! (Need 20 gold)")
            elif action in ["buy torch"]:
                if self.gold >= 10:
                    if "Torch" not in self.inventory:
                        self.inventory.append("Torch")
                        self.gold -= 10
                        self.game_state["has_torch"] = True
                        print(f"\nYou purchase a torch for 10 gold. Remaining gold: {self.gold}")
                    else:
                        print("\nYou already have a torch.")
                else:
                    print("\nYou don't have enough gold! (Need 10 gold)")
            elif action in ["buy shield"]:
                if self.gold >= 30:
                    if "Shield" not in self.inventory:
                        self.inventory.append("Shield")
                        self.gold -= 30
                        self.game_state["has_shield"] = True
                        print(f"\nYou purchase a shield for 30 gold. Remaining gold: {self.gold}")
                        print("\nThe shield will reduce damage in combat!")
                    else:
                        print("\nYou already have a shield.")
                else:
                    print("\nYou don't have enough gold! (Need 30 gold)")
            elif action == "talk":
                print("\nShopkeeper: 'Welcome! I have healing potions (20g), torches (10g), and shields (30g). Adventure can be dangerous!'")
            elif action == "north":
                self.current_location = "start"
                print("\nYou leave the shop and return to the village square...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "gate":
            if action in ["west", "enter lair"]:
                self.current_location = "lair"
                self.slow_print("\nYou bravely approach the dragon's lair...")
                time.sleep(1)
            elif action == "north":
                self.current_location = "mountains"
                self.slow_print("\nYou begin climbing the mountain trail...")
            elif action == "south":
                self.current_location = "bridge"
                self.slow_print("\nYou approach the rickety bridge...")
            elif action == "east":
                self.current_location = "start"
                print("\nYou return to the village square...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "bridge":
            if action in ["cross bridge", "cross"]:
                if self.game_state["bridge_repaired"]:
                    self.current_location = "island"
                    self.slow_print("\nYou safely cross the sturdy bridge to the mysterious island...")
                elif self.game_state["troll_defeated"]:
                    print("\nThe bridge is still too unstable to cross safely. Maybe you can REPAIR it with the right materials.")
                else:
                    print("\nThe troll blocks your path! You must defeat it or talk to it first.")
            elif action in ["talk to troll", "talk troll"]:
                self.slow_print("\nThe troll grunts:")
                time.sleep(0.5)
                print("'You want cross bridge? Give troll 50 gold, or troll smash!'")
                if self.gold >= 50:
                    pay = input("\nPay 50 gold? (y/n): ").lower()
                    if pay == 'y':
                        self.gold -= 50
                        self.game_state["troll_defeated"] = True
                        print(f"\nYou pay the troll 50 gold. Remaining gold: {self.gold}")
                        print("The troll grunts happily and moves aside!")
                else:
                    print("\nYou don't have enough gold.")
            elif action in ["fight troll", "fight", "attack"]:
                if self.game_state["has_sword"]:
                    self.slow_print("\nYou engage the troll in combat!")
                    time.sleep(1)
                    damage = 30 if not self.game_state["has_shield"] else 15
                    self.health -= damage
                    print(f"\nYou defeat the troll but take {damage} damage! Health: {self.health}")
                    self.game_state["troll_defeated"] = True
                else:
                    print("\nYou have no weapon! The troll laughs at you.")
            elif action in ["repair bridge", "repair"]:
                if "Rope" in self.inventory:
                    self.slow_print("\nYou use the rope to repair and reinforce the bridge...")
                    time.sleep(1)
                    self.game_state["bridge_repaired"] = True
                    print("\nThe bridge is now safe to cross!")
                else:
                    print("\nYou need rope to repair the bridge.")
            elif action == "north":
                self.current_location = "gate"
                print("\nYou return to the village gate...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "island":
            if action in ["examine guardian", "look guardian"]:
                print("\nThe massive stone guardian stands motionless, with a glowing crystal in its chest.")
                if not self.game_state["ancient_guardian_defeated"]:
                    print("You sense ancient magic protecting this place.")
            elif action in ["take crystal", "get crystal"]:
                if self.game_state["ancient_guardian_defeated"]:
                    if not self.game_state["crystal_activated"]:
                        self.inventory.append("Power Crystal")
                        self.game_state["crystal_activated"] = True
                        self.slow_print("\nYou take the Power Crystal! It glows with immense magical energy!")
                        print("\nYour power has increased!")
                    else:
                        print("\nYou already have the crystal.")
                else:
                    self.slow_print("\nThe guardian awakens and blocks your path!")
                    time.sleep(1)
                    if self.game_state["has_sword"] and self.game_state["library_explored"]:
                        self.slow_print("Using your knowledge from the library, you strike at its weak point!")
                        time.sleep(1)
                        self.slow_print("The guardian crumbles to pieces!")
                        self.game_state["ancient_guardian_defeated"] = True
                    else:
                        print("\nYou're not strong enough to defeat it. You need more power and knowledge!")
            elif action in ["back", "bridge"]:
                self.current_location = "bridge"
                print("\nYou cross back over the bridge...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "mountains":
            if action in ["enter passage", "passage"]:
                self.current_location = "secret_passage"
                self.slow_print("\nYou squeeze through the hidden passage...")
            elif action == "south":
                self.current_location = "gate"
                print("\nYou descend back to the village gate...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "secret_passage":
            if action in ["take armor", "get armor"]:
                if "Legendary Armor" not in self.inventory:
                    self.inventory.append("Legendary Armor")
                    self.health = 100
                    self.slow_print("\nYou don the Legendary Armor! Your health is fully restored!")
                    print("\nYou feel invincible!")
                else:
                    print("\nYou're already wearing the armor.")
            elif action in ["exit", "out"]:
                self.current_location = "mountains"
                print("\nYou exit the secret passage...")
            else:
                print("\nYou can't do that here.")
            if action in ["unlock door", "use key", "open door"]:
                if self.game_state["has_key"]:
                    if not self.game_state["door_unlocked"]:
                        self.game_state["door_unlocked"] = True
                        self.current_location = "tower_inside"
                        self.slow_print("\nThe key fits perfectly! The door swings open with a loud creak...")
                        time.sleep(1)
                        self.slow_print("You step inside the tower...")
                    else:
                        self.current_location = "tower_inside"
                        print("\nYou enter the tower...")
                else:
                    print("\nThe door is locked. You need a key to open it.")
            elif action in ["examine door", "look door"]:
                print("\nThe door has an ornate lock with mystical symbols. It looks like it needs a special key.")
            elif action == "west":
                self.current_location = "start"
                self.slow_print("\nYou return to the village square...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "tower_inside":
            if action in ["talk to wizard", "talk wizard", "speak"]:
                if not self.game_state["talked_to_wizard"]:
                    self.game_state["talked_to_wizard"] = True
                    self.slow_print("\nThe wizard speaks in a deep, echoing voice:")
                    time.sleep(0.5)
                    self.slow_print("'Ah, a brave soul enters my domain. I sense you seek adventure.'")
                    time.sleep(0.5)
                    self.slow_print("'Take the enchanted sword from the wall. You will need it to face the dragon.'")
                    time.sleep(0.5)
                    self.slow_print("'The beast hoards a legendary treasure beyond the western gate.'")
                else:
                    print("\nThe wizard nods at you knowingly. 'Go forth, brave warrior.'")
            elif action in ["take sword", "get sword", "pick up sword"]:
                if not self.game_state["has_sword"]:
                    self.inventory.append("Enchanted Sword")
                    self.game_state["has_sword"] = True
                    self.slow_print("\nYou take the magnificent sword from the wall. It glows with magical power!")
                else:
                    print("\nYou already have the sword.")
            elif action in ["down", "exit", "leave"]:
                self.current_location = "tower"
                print("\nYou exit the tower...")
            elif action in ["look around", "search"]:
                print("\nYou see ancient tomes, magical artifacts, and a beautiful sword mounted on the wall.")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "shop":
            if action in ["buy potion", "buy", "potion"]:
                if "Health Potion" not in self.inventory:
                    self.inventory.append("Health Potion")
                    print("\nYou purchase a health potion. (You somehow had the gold...)")
                else:
                    print("\nYou already have a health potion.")
            elif action == "talk":
                print("\nShopkeeper: 'Welcome! I have healing potions if you need them. Adventure can be dangerous!'")
            elif action == "north":
                self.current_location = "start"
                print("\nYou leave the shop and return to the village square...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "gate":
            if action in ["enter lair", "west", "continue", "forward"]:
                self.current_location = "lair"
                self.slow_print("\nYou bravely enter the dragon's lair...")
                time.sleep(1)
            elif action == "east":
                self.current_location = "start"
                print("\nYou return to the village square...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "lair":
            if action in ["fight dragon", "fight", "attack"]:
                if self.game_state["has_sword"]:
                    self.slow_print("\nYou draw your enchanted sword and charge at the dragon!")
                    time.sleep(1)
                    self.slow_print("The dragon awakens with a mighty roar!")
                    time.sleep(1)
                    self.slow_print("You engage in an epic battle...")
                    time.sleep(1)
                    
                    # Calculate damage based on equipment
                    damage = 40
                    if self.game_state["has_shield"]:
                        damage -= 15
                    if "Legendary Armor" in self.inventory:
                        damage -= 10
                    if self.game_state["has_amulet"] and damage >= self.health:
                        print("\nThe Protection Amulet saves you from a fatal blow!")
                        self.inventory.remove("Protection Amulet")
                        damage = self.health - 1
                    
                    self.health -= damage
                    
                    if self.health > 0:
                        self.slow_print("With skill and courage, you strike the final blow!")
                        time.sleep(1)
                        self.slow_print("The dragon falls defeated!")
                        self.game_state["dragon_defeated"] = True
                        print(f"\nYou took {damage} damage. Remaining health: {self.health}")
                        print("\nYou can now explore the treasure chambers to the EAST and WEST!")
                    else:
                        self.health = 0
                else:
                    self.slow_print("\nYou have no weapon! The dragon's fiery breath engulfs you...")
                    self.health = 0
            elif action in ["east chamber", "east"]:
                if self.game_state["dragon_defeated"]:
                    self.current_location = "east_chamber"
                    self.slow_print("\nYou enter the eastern treasure chamber...")
                else:
                    print("\nThe dragon blocks your path! You must defeat it first.")
            elif action in ["west chamber", "west"]:
                if self.game_state["dragon_defeated"]:
                    self.current_location = "west_chamber"
                    self.slow_print("\nYou enter the western treasure chamber...")
                else:
                    print("\nThe dragon blocks your path! You must defeat it first.")
            elif action in ["sneak to treasure", "sneak"]:
                if self.game_state["dragon_defeated"]:
                    print("\nThe dragon is already defeated. You can freely explore the treasure chambers!")
                else:
                    self.slow_print("\nYou attempt to sneak past the dragon...")
                    time.sleep(1)
                    self.slow_print("The dragon's eye suddenly opens! It catches you!")
                    time.sleep(1)
                    self.slow_print("The dragon's flames consume you...")
                    self.health = 0
            elif action in ["flee", "run", "escape"]:
                self.current_location = "gate"
                print("\nYou flee from the lair back to the village gate!")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "east_chamber":
            if action in ["take crown", "get crown"]:
                if not self.game_state["treasure_found"]:
                    self.game_state["treasure_found"] = True
                    self.slow_print("\nYou take the legendary CROWN OF KINGS!")
                    time.sleep(1)
                    self.slow_print("This ancient artifact grants wisdom and authority to its bearer!")
                    time.sleep(1)
                    self.slow_print("\nYou have completed your quest! You are victorious!")
                    self.game_over = True
                else:
                    print("\nYou already have the crown.")
            elif action == "back":
                self.current_location = "lair"
                print("\nYou return to the main lair...")
            else:
                print("\nYou can't do that here.")
        
        elif self.current_location == "west_chamber":
            if action in ["take egg", "get egg"]:
                if "Dragon Egg" not in self.inventory:
                    self.inventory.append("Dragon Egg")
                    self.slow_print("\nYou carefully take the Dragon's Egg!")
                    print("\nThis legendary artifact pulses with ancient power!")
                else:
                    print("\nYou already have the dragon egg.")
            elif action in ["take gold", "get gold"]:
                self.gold += 100
                print(f"\nYou gather 100 gold coins! Total gold: {self.gold}")
            elif action == "back":
                self.current_location = "lair"
                print("\nYou return to the main lair...")
            else:
                print("\nYou can't do that here.")
    
    def play(self):
        """Main game loop"""
        self.clear_screen()
        
        # Introduction
        print("\n" + "=" * 70)
        print("THE DRAGON'S TREASURE".center(70))
        print("A Text Adventure".center(70))
        print("=" * 70 + "\n")
        
        time.sleep(1)
        self.player_name = input("What is your name, brave adventurer? ").strip()
        if not self.player_name:
            self.player_name = "Hero"
        
        print(f"\nWelcome, {self.player_name}!")
        time.sleep(1)
        
        self.slow_print("\nYour quest: Find the legendary treasure guarded by an ancient dragon.")
        time.sleep(1)
        self.slow_print("But beware... danger lurks in every shadow...")
        time.sleep(2)
        
        input("\nPress Enter to begin your adventure...")
        
        # Main game loop
        while not self.game_over and self.health > 0:
            self.clear_screen()
            
            location = self.get_location_description()
            
            print(f"\n{'=' * 70}")
            print(f"Location: {location['name']}")
            print(f"{'=' * 70}\n")
            
            print(location['description'])
            
            self.show_status()
            
            print("What do you do?")
            print(f"Suggested actions: {', '.join(location['options'][:4])}, help")
            
            action = input("\n> ").strip()
            
            if action:
                self.handle_action(action)
                
                if self.health <= 0:
                    self.clear_screen()
                    print("\n" + "=" * 70)
                    print("GAME OVER".center(70))
                    print("=" * 70 + "\n")
                    print(f"You have fallen, {self.player_name}. Your adventure ends here...")
                    print("\nBetter luck next time!")
                    break
                
                if not self.game_over:
                    input("\nPress Enter to continue...")
        
        if self.game_state["treasure_found"]:
            self.clear_screen()
            print("\n" + "=" * 70)
            print("VICTORY!".center(70))
            print("=" * 70 + "\n")
            print(f"Congratulations, {self.player_name}!")
            print("You have found the legendary treasure and defeated the dragon!")
            print("Your name will be remembered throughout the ages!")
            print("\n" + "=" * 70 + "\n")


def main():
    while True:
        game = TextAdventure()
        game.play()
        
        play_again = input("\nPlay again? (y/n): ").lower()
        if play_again != 'y':
            print("\nThanks for playing!")
            break


if __name__ == "__main__":
    main()
