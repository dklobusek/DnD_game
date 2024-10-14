import pandas as pd
import random as rd
import os, pickle, pygame
import pygame
import queue, time
import numpy as np
from shapely.geometry import LineString, box

class Data:
    # Class for loading data, Singleton approach
    _instance = None
    
    def __new__(cls, *args, **kwargs):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__ (self):
        # if not hasattr(self, 'data_loaded'):  # Check if data is already loaded
        self.load_all_data()
    
    def load_all_data(self):
        # Method to load all data
        self.races = self.load_races()
        self.classes = self.load_classes()
        self.armors = self.load_armors()
        self.weapons = self.load_weapons()
        self.data_loaded = True  # Mark that data has been loaded
        
    def reload_data(self):
        # Method to reload all data
        self.data_loaded = False
        self.load_all_data()

    def load_races(self):
        data = pd.read_csv('DnD/race.csv', delimiter=";")
        races = {}
        for _,row in data.iterrows():
            race_name = row["race"]
            race_info = {col: row[col] for col in data.columns if col!= "race"}
            races[race_name] = race_info
        return races
    
    def load_armors(self):
        data = pd.read_csv('DnD/armors.csv', delimiter=";")
        data_dict = {}
        for _,row in data.iterrows():
            data_header = row["armor"]
            data_info = {col: row[col] for col in data.columns if col!= "armor"}
            data_dict[data_header] = data_info
        return data_dict
    
    def load_weapons(self):
        data = pd.read_csv('DnD/weapons.csv', delimiter=";")
        data_dict = {}
        for _,row in data.iterrows():
            data_header = row["weapon"]
            data_info = {col: row[col] for col in data.columns if col!= "weapon"}
            data_dict[data_header] = data_info
        return data_dict
    
    def load_classes(self):
        data = pd.read_csv('DnD/classes.csv', delimiter=";", encoding='ISO-8859-1')
        classes = {}
        for _,row in data.iterrows():
            classes_name = row["class"]
            classes_info = {col: row[col] for col in data.columns if col!= "class"}
            classes[classes_name] = classes_info
        return classes
    
    def get_races(self):
        return self.races
    
    def get_classes(self):
        return self.classes
    
    def get_armors(self):
        # If armors haven't been loaded yet, load them
        if not hasattr(self, 'armors'):
            print("Loading armors...")
            self.armors = Data.load_armors(self)
        return self.armors
    
    def get_weapons(self):
        # If weapons haven't been loaded yet, load them
        if not hasattr(self, 'weapons'):
            print("Loading weapons...")
            self.weapons = Data.load_weapons(self)
        return self.weapons
    
class Character:
    #generating representation of character
    def __init__ (self, name, race=None, class_name = None, abilities = {}, abil_modifiers = None, hp = None, skills = None, features = None, level = 1, initiative = None):
        #TODO I switch order
        self.data = self.get_data_instance() #done
        
        self.instance_abil = Abilities(self)
        self.instance_classes = CharacterClass(self)
        self.instance_hp = HitPoints(self)
        self.instance_armor_class = ArmorClass(self)
        self.instance_equipment = Equipment(self)
        self.instance_modifiers = Modifiers(self)
        
        self.name = name
        self.race = race
        self.class_name = class_name
        self.abilities = abilities
        self.skills = skills
        self.features = features
        self.level = level
        self.initiative = initiative
        
        self.position = set()
        self.team = None # 1 team one, 2 team two
        self.control = None #1 AI controlled, 0 player controller
        
        self.wins = 0
        self.defeats = 0
        self.games = 0
        
    def __str__ (self):
        abilities_str = "\n".join([f"{key.capitalize():<15}: {value:>2}" for key, value in self.abilities.items()])
        return (f"Name: {self.name}\nLevel: {self.level}\nRace: {self.race}\nCharacter class: {self.class_name}\nBase HP: {self.instance_hp.base_hp}\nArmor class: {self.instance_armor_class.armor_class}\n::: Abilities :::\n{abilities_str}\n{self.instance_equipment}\n\n")

    @staticmethod
    def get_data_instance():
        # Method to get the singleton instance of the Data class
        if not hasattr(Character, '_data_instance'):
            Character._data_instance = Data()  # Create the Data instance if it doesn't exist
        return Character._data_instance
    
    def __getstate__(self):
        # Zbiera stan obiektu do zapisu
        state = self.__dict__.copy()
        if 'data' in state:
            del state['data']  # Usunięcie atrybutu data, by nie zapisywać Singletona Data
        return state

    def __setstate__(self, state):
        # Ustawia stan obiektu podczas wczytywania
        self.__dict__.update(state)
        self.data = Data()  # Ponowne ustawienie odniesienia do Singletona Data
    
    @classmethod
    def create_new_character(cls,name):
        #creating a character from scratch
        character = cls(name=name)
        character.pick_level()
        character.race = character.choose_race()
        character.class_name = character.instance_classes.choosing_class()
        character.abilities = character.instance_abil.gen_abilities()
        character.instance_hp.calc_base_hp()
        
        return character
    
    def save_character(self):        
        folder_path = 'saved'
        
        file_path = os.path.join(folder_path, f"{self.name}.pkl")
        with open(file_path, "wb") as save_file:
            pickle.dump(self, save_file)
        print(f"Character {self.name} saved successfully to {file_path}")
    
    def load_character(self, filename):
        
        folder_path = 'saved'
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, "rb") as load_file:
            loaded_character = pickle.load(load_file)
        self.__dict__.update(loaded_character.__dict__)
        
        # Character.re_calculate(self)
        
        return loaded_character

    def pick_level(self):
        while True:
            try:
                level = int(input("\nAt what level you want your character to be? Choose between 1 and 20: "))
                print()
                self.level = level
                break
            except:
                raise ValueError ("Wrong level. Choose again")
    
    def choose_race(self):
        print (">>> AVAILABLE RACES <<<")
        print(" /// ".join([key for key in self.data.get_races().keys()]))
        while True:
            choose_race = input(f"\n\nChoose a race:\n >>> ").title()
            if choose_race not in self.data.get_races().keys():
                print("Wrong race, choose again")
            else:
                break
        return choose_race
    
    def roll_initiative (self):
        roll = rd.randint(1,20)
        self.initiative = roll + self.instance_abil.abil_modifiers["Dexterity"]
        return self.initiative
    
    def re_calculate(self):
        self.instance_abil.calculate_modifiers()
        # self.instance_armor_class.calculate_ac()
        self.instance_hp.update_hp()
        self.instance_hp.status = 1
        self.team = None # 1 team one, 2 team two
        self.control = None #1 AI controlled, 0 player controller
    
class Abilities:
    # there shouldn't be any method that initialize by its own
    def __init__ (self, character):
        self.character = character
        self.races = character.data.get_races()
        self.abilities = None  # Initialize abilities as None
        self.temp_abilities = None
        self.abil_modifiers = {}

    def gen_abilities(self):
        while True:
            gen_rd_abilities = self.generate_initial_abilities()
            abilities = self.assign_abilities(gen_rd_abilities)
            abilities = self.apply_racial_bonuses(abilities)
            abilities = self.apply_special_bonuses(abilities)
            
            for key,value in abilities.items():
                print(f"{key.capitalize():<15}: {value:>2}")
            again = input("Do you want to save those values or do you want to generate them once again? Press Y for again.\n >>> ").lower()
                
            if again != "y":
                break
            
        self.abilities = abilities
        self.abil_modifiers = self.calculate_modifiers()
        
        return abilities
    
    def generate_initial_abilities(self):
        while True:
            temp =  [sum(sorted([rd.randint(1, 6) for _ in range(4)], reverse=True)[:3]) for _ in range(6)]
            x = input(f"Do you want to use this abilities? Press y for yes: {temp} : ").lower()
            if x == "y":
                return temp
        
    def default_abilities(self):
        return {"Strength": 15,
            "Dexterity": 14,
            "Constitution": 13,
            "Intelligence": 12,
            "Wisdom": 10,
            "Charisma": 8}
        
    def assign_abilities(self, temp_stats):
        # appending rd numbers to abilities
        abilities = {"Strength": None, "Dexterity": None, "Constitution": None, "Intelligence": None, "Wisdom": None, "Charisma": None}
        for key in abilities:
            while abilities[key] is None:
                try:
                    stat = int(input(f"\nChoose a value from available stats {temp_stats}\n{key} >>> "))
                    if stat not in temp_stats:
                        print("Invalid choice, pick again!")
                    else:
                        abilities[key] = stat 
                        temp_stats.remove(stat)
                except:
                    print(f"Invalid input! Please choose only a number from list\n")
        return abilities
                
    def apply_racial_bonuses(self, abilities):
        # updating racial bonuses abilities
        for key,value in self.races.items():
            if self.character.race == key:
                for abil, bonus in value.items():
                    if abil.capitalize() in abilities and pd.notna(bonus):
                        abilities[abil.capitalize()] += int(bonus)
        return abilities
                        
    def apply_special_bonuses(self, abilities):                    
        # additional exception for half-elf or other races (possible in future 5.5ed), checking for csv abilities and looping over it
        try:
            bonus_abil = int(self.races[self.character.race].get("special_attribute_mod"))# name of the column, might be dependent on csv, consider to change
        except:
            bonus_abil = None
        if self.character.race in self.races and bonus_abil is not None:
            count = 1
            list_abil = []
            for _ in range(bonus_abil):
                while count<bonus_abil+1:
                    print(count, bonus_abil)
                    abil = input(f"As Half-Elf you have an option to increase two abilities by one point. Choose ability no {count}:\n>>> ")
                    if abil.capitalize() in abilities and abil not in list_abil:
                        abilities[abil.capitalize()] += 1
                        list_abil.append(abil)
                        count += 1
                        print(f"{abil} updated! \n")
                    else:
                        print(f"Wrong ability. Remember that you cannot choose same ability twice\n")
        return abilities
    
    def update_temp_abilities(self, abilities, abil_modifiers):
        #iteration through abilities and updating them with TODO, needs work - abil_modifiers is NOT this
        for ability, base_value in abilities.items():
            temp_abilities = base_value + abil_modifiers.get(ability,0)

    def calculate_modifiers(self):
        #TODO first update temporary abilities (possible modifiers from spells etc.) and then calculate modifiers... think about this in future and about resources consumption, might be heavy CPU/GPU dependent
        #self.update_temp_abilities()
        mod = {}
        for key,value in self.abilities.items():
                mod[key] = (value - 10) // 2
        self.abil_modifiers = mod
        
class CharacterClass:
    def __init__ (self, character):
        # there shouldn't be any method that initialize by its own, except loading data
        self.character = character
        self.classes = character.data.get_classes()
        self.class_name = None
    
    def choosing_class (self):
        print (">>> AVAILABLE CLASSES <<<")
        print(" /// ".join(key for key in self.classes.keys()))
        while True:
            choose_class = input(f"\n\nChoose class:\n >>> ").title()
            if choose_class not in self.classes:
                print("Wrong race, choose again")
            else:
                break
        self.class_name = choose_class
        return choose_class

class ArmorClass:
    def __init__ (self, character, armor_class =  10): #TODO implement a method to lower AC if dex is lower than 9
        self.armor_class = armor_class
        self.character = character
      
    def calculate_ac(self):
        # calculating armor class based on equipped armor and dexterity modifers, considering limitations (dex) of armor, RETURNING AND UPDATING ARMOR CLASS GLOBAL
        armor = self.character.instance_equipment.armor
        print(armor)
    # try:
        ac_armor = armor["armor_class"]
        max_dex_mod_armor = armor["max_dex_mod"]
    # except:
    #     raise ValueError("Calculate AC, armor not found")
    #     ac_armor = 10
    #     max_dex_mod_armor = 99
            
        dex_mod = self.character.instance_abil.abil_modifiers["Dexterity"]
        
        if dex_mod>max_dex_mod_armor:
            self.armor_class = max_dex_mod_armor+ac_armor
        else:
            self.armor_class = dex_mod+ac_armor
        return 
       
class HitPoints:
    #TODO, implement a way to increase hitpoints if constituion is modified
    def __init__ (self, character):
        self.character = character
        self.base_hp = None
        self.temp_hp = None
        self.current_hp = None
        self.death_throw_count_plus = 0
        self.death_throw_count_minus = 0
        
        self.status = 1
        self.classes = character.data.get_classes()
        
    def calc_base_hp (self):
        # calculate hit points on character creation
        class_hp_dice = self.classes[self.character.class_name]["hit_dice"]
        print(f"Calculating base HP for {self.character.name}. Base HP dice is {class_hp_dice}")
        
        #calculating modifiers, for CON additions to HitPoints
        self.character.instance_abil.calculate_modifiers()
        
        #base HP for level 1, full dice number
        base_hp = class_hp_dice
        print(f"Base HP, level 1 {base_hp}")
        
        #rolling HP for all levels beyond 1 and adding to the pooll
        base_hp += sum([rd.randint(1, class_hp_dice) for _ in range(self.character.level-1)])
        print(f"Base HP, level 1+x {base_hp}")
        
        # add HP that result from constitution modifiers
        cons_hp = (self.character.instance_abil.abil_modifiers["Constitution"]) * self.character.level
        base_hp += cons_hp
        print(f"Base HP, level 1+x + CON {base_hp}")
        
        #check for any classes abilities that permamently increase hit_points
        hp_mod = self.classes[self.character.class_name].get("hp_mod", 0)
        if hp_mod > 0:
            base_hp += hp_mod * self.character.level
        
        self.base_hp = base_hp
        
        #updating temporary HP and current HP, to fill None with values
        self.update_hp()
        
        print (f"{self.character.name} your base HP is {self.base_hp}")
    
    def calc_temp_hp (self):
        # TODO implement a method to add modifiers from temporary constituion
        self.temp_hp = self.base_hp
    
    def calc_current_hp (self):
        # TODO HP thats change dynamically, e.g. during fight
        self.current_hp = self.temp_hp
    
    def update_hp (self):
        self.calc_temp_hp()
        self.calc_current_hp()

    def check_status (self, dmg, critical):
        if self.status == 2 and dmg == 0:
            print (f"{self.character.name} is already stabilized!") # TODO to be removed
            return 2
        
        if self.status == 2 and dmg > 0 and critical:
            print (f"{self.character.name} was stabilized, but it is not anymore!") # TODO to be removed
            self.status=0
            self.death_throw_count_plus += 2
            return 0
        
        # return 1 if char alive, 0 if unconscious, -1 if dead /// BEFORE TURN
        if self.current_hp>0 and self.status==1:
            return 1
        
        # if dmg was larger than pool hp then dead, set status to -1 /// DURING TURN #TODO needs to be reworked to account for current hp before last attack
        elif dmg>=self.base_hp:
            print (f"{self.character.name} is dead! Damage {dmg} was too big for him to handle it.")
            self.status = -1
            return - 1
        
        # first damage to unconscious state, set character to unconscious /// DURING TURN
        elif self.current_hp<=0 and self.status == 1:
            print (f"{self.character.name} is unconscious! Damage {dmg} was too big for him to handle it. He can still be revived")
            self.status = 0
            return 0
        
        # if critical hit and unconscious, DnD 5.0 rule, add +2 towards death  /// DURING TURN
        elif critical==1 and self.status==0: # if 
            self.death_throw_count_plus += 2
        
        # basic check if HP 0 or lower  /// BEFORE TURN
        elif self.current_hp<=0 and self.status==0:
            roll = rd.randint(1,20)
            if roll == 20:
                self.current_hp = 1
                self.status = 1
                self.death_throw_count_plus = 0
                self.death_throw_count_minus = 0
                print (f"You are returning back to life!")
            elif roll >= 10:
                self.death_throw_count_minus += 1
            elif roll == 1:
                self.death_throw_count_plus += 2
            else:
                self.death_throw_count_plus += 1
                
            print(f"Death saving roll for {self.character.name}: {roll}, current status: M / P {self.death_throw_count_minus} {self.death_throw_count_plus}")
                
        #SECOND PART
        # check status based on death_throw_count, outside previous loop
        if self.death_throw_count_plus>=3:
            print (f"{self.character.name} is dead! Death throw count reached 3 or beyond")
            self.death_throw_count_plus = 0
            self.death_throw_count_minus = 0
            self.status = -1
            return -1
        
        # return status unconscious, cannot move during
        elif self.death_throw_count_minus>=3:
            print (f"{self.character.name} you are stabilized!")
            self.death_throw_count_plus = 0
            self.death_throw_count_minus = 0
            self.status = 2
            return 2
        
        else:
            return 0
        
    def decrease_target_hp(self, dmg):
        self.current_hp -= dmg
        
class Modifiers:
    def __init__ (self, character):
        self.character = character
        self.ac_modifiers = None
        self.main_attack_mod = None
    
    def update_ac (self, ac):
        self.ac_modifiers = ac
        print(f"modify_ac function in Modifiers class, AC value: {ac}")
        
    def update_main_attack_mod(self):
        #TODO add multiple bonuses
        mod = self.character.instance_abil.abil_modifiers["Strength"] # basic attack bonus resulting from strength
        self.main_attack_mod = mod
        return mod

class Equipment:
    #store information about character/enemy equipment and its modifiers, probably the biggest class there will be, or at least class that will draw the biggest amount information from csv file
    def __init__ (self, character):
        self.character = character
        self.armor = None
        self.body = None
        self.first_weapon = None
        self.second_weapon = None
        self.backup_weapon = None
        self.shield = None
        self.helmet = None
        self.eyes = None
        self.cloak = None
        self.boots = None
        self.belts = None
        self.gloves = None
        self.ring_1 = None
        self.ring_2 = None
        self.amulet = None
        self.bracers = None
        self.backpack = None
        self.tool_slot = None
        self.quiver = None
        self.instrument = None
        self.spellbook = None
        
    def armor_init(self):
        #TODO choosing armor from list, need to check for proficiency and str required among other stuff
        armors_list = self.character.data.get_armors()
        for armor, values in armors_list.items():
            print (f"{armor} {values}", sep = "  ///  ")
        
        armor_choice = input("What armor do you want to wear?")
        
        if armor_choice in armors_list:
            print("New armor equipped!")
            #TODO if new armor it should follow the chain of actions AND: a) update weight (if new armor) b) modify armor class and pass argument about AC and Dex mod, c) check if this type of armor can be worn (probably the first thing) d), check the strength required, probably the second
            self.armor = {"name": armor_choice, **armors_list[armor_choice]}
        else:
            print("No armor")
            
    def first_weapon_init(self):
        #TODO choosing weapon from list, need to check for proficiency and str required among other stuff
        item_list = self.character.data.get_weapons()
        for item, stats in item_list.items():
            print (f"{item} {stats}", sep = "  ///  ")
        
        item_choice = input("What armor do you want to wear?")
        
        if item_choice in item_list:
            print("New first weapon equipped!")
            #TODO if new armor it should follow the chain of actions AND: a) update weight (if new armor) b) modify armor class and pass argument about AC and Dex mod, c) check if this type of armor can be worn (probably the first thing) d), check the strength required, probably the second
            self.first_weapon = {"name": item_choice, **item_list[item_choice]}
        else:
            print("No weapon found")
            
    def __str__ (self):
        return (f"Armor: {self.armor["name"]}\nMain weapon: {self.first_weapon["name"]}\n")

class Action:
    # set of actions that can be done in/out of combat
    def __init__ (self, character_manager):
        self.character_manager = character_manager
        self.event_queue = queue.Queue()
        self.screen = None

    def choose_action(self, character):
        # function only for PLAYERS
        # return input(f"\n{character.name} what do you want to do? ").lower().strip()
        
            
        actions_list = ["move", "main attack", "equip armor", "equip body clothing", "equip first weapon", 
                        "equip weapon slot 2/shield", "equip weapon slot 3", "equip helmet", "equip googles", 
                        "equip boots", "equip belt", "equip glove", "equip ring slot 1", "equip ring slot 2", 
                        "equip amulet", "equip bracers", "equip tool sloot", "equip backpack", "equip quiver", 
                        "equip instrument", "equip spellbook"]
        
        # Get the player's input
        action_input = input("What do you want to do? ").lower().strip()
        
        # Split input into action and target (if target exists)
        parts = action_input.split(maxsplit=1)
        command = parts[0]
        target = (parts[1] if len(parts) > 1 else None).title()  # target is the second word, if present
        
        # Normalize the list items by converting them to lowercase and replacing spaces with underscores
        actions_mapping = {action.lower().replace(" ", "_"): action for action in actions_list}
        
        # Search for a partial match in the input command
        for normalized_action, original_action in actions_mapping.items():
            if command in normalized_action:
                if "attack" in normalized_action and target:
                    #check for valid enemy
                    return target
                
                # if not attack
                action_method = getattr(self, normalized_action, None)
                if action_method:
                    action_method(character)
                else:
                    print(f"Action '{original_action}' is not yet implemented.")
                return  # Exit after the first match

        print("Action not recognized. Please try again.")

    def get_possible_actions(self, character):
        
        actions = []
        
        #check for targets and append all functions that needs target to be > 0
        if self.get_targets(character):
            actions.append("main_attack")
        
        #check if target can move / for now it can always move, later check for conditions
        if self.can_move(character):
            actions.append("move_AI")

        return actions
    
    def initialize_screen(self):
        pygame.init()
        screen = pygame.display.set_mode((1200, 1200))
        pygame.display.set_caption("Board Visualization")
        return screen

    def can_move (self, character):
        return True
         
    def move(self, character):
        # checking if Pygame screen is ON
        if self.screen is None:
            self.screen = self.initialize_screen()
        
        print (f"{character.name} your move")
        move = Move(character, self.character_manager, self.event_queue, self.screen)
        move.run_game()  # Uruchom run_game bezpośrednio zamiast w wątku

        # Oczekiwanie na wynik z kolejki
        pos = self.event_queue.get()
        
        #check cost of the move using A*
        # self.character_manager.instance_event_manager.check_move(character, pos)
        
        print(f"Selected position: {pos}")
        if not any(c.position == pos for c in self.character_manager.characters.values()):
            self.character_manager.instance_event_manager.update_player_position(character, pos)
        else:
            print("That position is already occupied.")

    def get_targets(self, character):
        # TODO iterate through enemy team and check if any of the target can be attacked, check for weapon reach (glaive or distance)
    
        list_of_targets = []
        
        # check for potential targets
        if character.team == 1:
            for target in self.character_manager.instance_event_manager.team_two:
                if self.character_manager.instance_event_manager.is_adjacent(character.position, target.position) and target.instance_hp.status>-1:
                    list_of_targets.append(target)
        elif character.team == 2:
            for target in self.character_manager.instance_event_manager.team_one:
                if self.character_manager.instance_event_manager.is_adjacent(character.position, target.position) and target.instance_hp.status>-1:
                    list_of_targets.append(target)
        
        return list_of_targets
    
    def get_targets_ranged(self, character):
        # TODO iterate through enemy team and check if any of the target can be attacked, check for weapon reach (glaive or distance)

        list_of_targets = []
        
        # check for potential targets
        if character.team == 1:
            for target in self.character_manager.instance_event_manager.team_two:
                if target.instance_hp.status>-1:
                    list_of_targets.append(target)
        elif character.team == 2:
            for target in self.character_manager.instance_event_manager.team_one:
                if target.instance_hp.status>-1:
                    list_of_targets.append(target)
        
        # self.character_manager.instance_AI.targets = list_of_targets
        print(f"DEBUG: potential targets {list_of_targets}")
        return list_of_targets
    
    def can_attack_ranged (self, character):
        # check if char can use ranged attack, calculate target
        if int(character.instance_equipment.first_weapon["reach"]) > 10:
            targets = self.get_targets_ranged (character)
            print (f"Potential targets to attack: {targets}")
            if targets:
                max_value = -float('inf')
                for target in targets:
                    current_value = self.character_manager.instance_algorithms.check_path_to_target(character.position, target.position)
                    if current_value > max_value:
                        max_value = current_value
                        best_target = target
                        print(best_target)
                
                d = self.character_manager.instance_event_manager.distance (character.position, best_target.position)
                print(f"Distance to target {d}")
                if character.instance_equipment.first_weapon["reach"] > d:
                    return best_target
        else:
            return False
        
        
    def equip_armor (self, character):
        if character:
            character.instance_equipment.armor_init()
            #character.instance_modifiers.update_ac(armor["Armor class"])
            character.instance_armor_class.calculate_ac()
            #character.armor_class = AC
            
    def equip_first_weapon (self, character):
        if character:
            character.instance_equipment.first_weapon_init()
            
    def check_advantage (self, character, target):
        # object expected
        if target.instance_hp.status in [-1,0,2]:
            print (f"{character.name} has an advantage against {target.name}")
            return True
        return False
    
    def check_additional_modifiers (self, character, target):
        # return additional modifiers to the attack roll TODO
        return 0
    
    def main_attack (self, character, target):
        # get instance object if str
        if isinstance(target, str):
            target = self.character_manager.get_character(target)
            
        print(f"Attempting to attack {target.name}")
        
        if target is None:
            raise AttributeError(f"Target '{target}' not found or not an object.")
        
        # check if character has additional bonuses against target
        additional_mod = self.check_additional_modifiers (character, target)
        
        # check for advantage against target
        advantage = self.check_advantage(character, target)

        # calculate attack roll against target with all modifiers
        roll, attack_modifier, attack_roll = self.attack_roll(character, advantage, additional_mod)
        print(f"{character.name} attacks {target.name}: {roll} + {attack_modifier} = {attack_roll}")
        
        # check for hit
        hit, critical = self.check_hit(roll, attack_roll, target)
        
        # calculate damage, check in damage roll function for any immunities/reductions
        if hit:
            dmg = self.damage_roll(character, target, critical)
            #after hit decrease target hp and check status
            target.instance_hp.decrease_target_hp(dmg)
            status = target.instance_hp.check_status(dmg, critical)
            if status == -1:
                self.character_manager.instance_event_manager.remove_char(target)
                print (f"Removing {target.name} in main attack function from list")
                
            
            
        else:
            print(f"Target missed")
                
    def attack_roll(self, character, advantage, additional_mod):
        #TODO needs to be calculate only once when variable changes
        character.instance_modifiers.update_main_attack_mod()
        attack_modifier = character.instance_modifiers.main_attack_mod
        
        if advantage:
            roll = max(rd.randint(1, 20), rd.randint(1, 20))
        else:
            roll = rd.randint(1,20)
        
        attack_roll = roll + attack_modifier + additional_mod
        
        return [roll, attack_modifier+additional_mod, attack_roll]
    
    def check_hit(self, roll, attack_roll, target):
        # returning info about hit and if it is critical, booleans
        if roll==20:
            print ("Critical hit!")
            return True, True
        elif roll==1:
            return False, False
        else:
            x = attack_roll>=target.instance_armor_class.armor_class
            # TODO implement a way for ranged weapons
            if x and target.instance_hp.status in [-1,0,2]:
                print("Critical hit!")
                return True, True
            elif x: return True, False
            else: return False, False
    
    def damage_roll(self, character, target, critical):
        # TODO versatile method
        
        # no of dice and type of dice
        wp_stat = [(character.instance_equipment.first_weapon["no_dice"]),(character.instance_equipment.first_weapon["dice_dmg"])]
        # TODO check for any extra damage modifiers against target
        add_mod = 0
        
        #check for modifiers from strength/dexterity (based from weapon)
        dmg_mod = character.instance_abil.abil_modifiers["Strength"]
        
        if critical:
            dmg = sum(rd.randint(1,wp_stat[1]) for _ in range(wp_stat[0] * 2))
        else:
            dmg = sum(rd.randint(1,wp_stat[1]) for _ in range(wp_stat[0]))
        
        dmg_sum = dmg + add_mod + dmg_mod
        
        #TODO check target for any resistance
        
        print (f"{character.name} hits {target.name} for {dmg_sum}: {dmg} + {dmg_mod+add_mod}")
        return dmg_sum
                  
class InitiativeTracker:# TODO, maybe in the future
    def __init__ (self):
        self.turn_order = []
        
    def add_character(self, character):
        self.turn_order.append
    
    def determine_initiative_order (self):
        self.turn_order.sort(key=lambda x: x.initiative.roll, reverse=True)
        for character in self.turn_order:
            print(f"{character.name}: {character.initiative}")
    ...

class CharacterManager:
    def __init__ (self):
        self.instance_action = Action(self)
        self.instance_event_manager = EventManager(self)
        self.instance_AI = AI(self)
        self.instance_player = Player(self)
        self.instance_board = Board(self)
        self.instance_algorithms = Algorithms(self)
        
        self.characters = {}
        self.initiative_order = []
        
    def add_character(self, character):
        self.characters[character.name] = character
    
    def get_character(self, name):
        character = self.characters.get(name, None)
        if character is None:
            print(f"Character '{name}' not found in characters.")
        return character
    
    def roll_initiative_for_all(self):
        self.initiative_order = []
        for character in self.characters.values():
            initiative_roll = character.roll_initiative()  # Assuming Character class has a method `roll_initiative()`
            self.initiative_order.append((character.name, initiative_roll))
        
        # Sort characters based on their initiative rolls, in descending order
        self.initiative_order.sort(key=lambda x: x[1], reverse=True)
    
    def display_turn_order(self):
        print("Initiative rolls:")
        for name, initiative in self.initiative_order:
            print(f"{name}: {initiative}")

class Player:
    def __init__ (self, character_manager):
        self.character_manager = character_manager
        self.move_points = 30
        self.possible_attacks = 1
        self.bonus_action_available = True
    
    def player_turn (self, character):
        choose_action = self.choose_action(character)
        
        if choose_action == "attack":
            target = self.pick_enemy()
            if self.character_manager.instance_action.get_targets(character, target):
                self.character_manager.instance_action.main_attack(character, target)
        elif choose_action == "move":
            self.character_manager.instance_action.move(character)

    
    def pick_enemy(self):
        # choosing enemy
        while True:
            choose_target = (input("Pick enemy to attack: ")).title()
            x = self.character_manager.get_character(choose_target)
            if choose_target in self.character_manager.instance_event_manager.team_two and x.instance_hp.status>-1:
                return self.character_manager.get_character(choose_target)
            elif choose_target == "pass":
                print ("Skipping move")
                break
            else:
                print ("Invalid target")

class AI:
    def __init__ (self, character_manager):
        self.character_manager = character_manager
        # self.targets = None # list of targets in each turn, reset after turn is over
    
    def AI_turn (self, character):
        print(f"\nAI {character.name} your move!")
        while True:
            #check if char can attack from distance
            target = self.character_manager.instance_action.can_attack_ranged (character)
            if target:
                self.character_manager.instance_action.main_attack (character, target)
                break
        
            #check if targets can be attacked by AI
            targets = self.character_manager.instance_action.get_targets(character)
            
            #check if targets can be attacked
            if not targets:
                print(f"DEBUG: AI moving!")
                self.move_AI(character)
                break
            
            if targets:
                target = self.AI_choose_enemy(targets)
                print(f"DEBUG: AI attacking!")
                self.character_manager.instance_action.main_attack(character, target)
                break
            
    def AI_choose_enemy (self, targets):
        random_target = rd.choice(targets)
        return random_target
        
    def AI_pick_target_to_go(self, character):
        # choosing enemy from self list, random choice, cannot be attacked
        list = []
        
        if character.team == 1:
            for target in self.character_manager.instance_event_manager.team_two:
                list.append(target)
        if character.team == 2:
            for target in self.character_manager.instance_event_manager.team_one:
                list.append(target)
                
        choose_target = rd.choice(list)
        return choose_target
    
    def move_AI(self, character):
        #find a path to one of the potential targets
        
        target = self.AI_pick_target_to_go(character)
        print (f"{character.name} on {character.position} is going towards {target.name} on {target.position}")
        
        pos = self.character_manager.instance_event_manager.AI_check_move(character, target.position, 30, False)
        self.character_manager.instance_board.update_player_position(character, pos)
        
        if self.character_manager.instance_action.screen is None:
            self.character_manager.instance_action.screen = self.character_manager.instance_action.initialize_screen()
        
        move = Move(character, self.character_manager, self.character_manager.instance_action.event_queue, self.character_manager.instance_action.screen)
        move.draw_board()
        
        pygame.event.pump()
        time.sleep(2.0)
     
class EventManager:
    def __init__ (self, character_manager):
        self.character_manager = character_manager
        self.turn_index = 0
        self.team_two = []
        self.team_one = []
        self.control_team_one = None
        self.control_team_two = None
        
        # board and move variables
        self.path_queue = {}
        self.visited = {}
    
    def is_adjacent (self, pos, target):
        #check if pos is adjacent to target
        x, y = pos
        tx, ty = target
        return abs(x - tx) <= 1 and abs(y - ty) <= 1 and pos != target
        
    def distance (self, pos, target):
        x1,y1 = pos
        x2,y2 = target
        d = float(np.sqrt((x2 - x1)**2 + (y2 - y1)**2)) * 5
        return d

    def move_cost(self, new_pos, old_pos):
        #TODO modify in future for terrain
        x1,y1 = old_pos
        x2,y2 = new_pos
        
        if x1==x2 or y1==y2:
            cost = 5
        else:
            cost = 7.5

        # check if new pos is hill, if is cost x2
        if self.character_manager.instance_board.i_board[y2][x2] == self.character_manager.instance_board.board_signs[2]:
            cost *=2
            
        return cost
    
    def calc_path(self, old_pos, tar_pos, cost_old):
        # print(f"DEBUG Checking {old_pos}:")
        x, y = old_pos
        surround = {}
        
        moves = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),          (1, 0),
            (-1, 1),  (0, 1),  (1, 1) 
        ]
        
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy
            pos = new_x, new_y

            # Sprawdzenie, czy nowe współrzędne są w granicach planszy i nie były wcześniej odwiedzone
            if 0 <= new_x < len(self.character_manager.instance_board.p_board[0]) and 0 <= new_y < self.character_manager.instance_board.size and pos not in self.visited:
                # Sprawdzenie, czy pole jest oznaczone jako "E"
                if self.character_manager.instance_board.p_board[new_y][new_x] in self.character_manager.instance_board.board_signs:
                    d = self.distance([new_x, new_y], tar_pos)
                    cost = self.move_cost([new_x, new_y], [x, y]) + cost_old
                    total = d + cost
                    surround[(new_x, new_y)] = (cost, d, total, old_pos)
        
        #print(f"DEBUG: calc_path, {surround} \n\n")
        return surround

    def check_move(self, character, target_pos, move_points, is_Player = True):
        
        #initialize variable
        min_pos = None
        adjacent_results = {}
        self.visited[character.position] = (0, 0 , 0, None)
        
        # checking for target neighbours
        target_neighbors = self.check_char_surround(target_pos)
        target_neighbors.append(target_pos)
        target_neighbors = [(neighbor) for neighbor in target_neighbors]
        print(f"Target neighboors: {target_neighbors}")
        
        while True:
            min_cost_pos = 0
            min_cost = float('inf')
            
            if not self.queue:
                print(f"DEBUG, {character.position} {target_pos} {self.visited}")
                self.queue = self.calc_path(tuple(character.position), target_pos, 0, self.visited)
            
            # iterate through queue and find optimal path (min_pos) for the cost (min_cost_pos)
            for position, values in self.queue.items():
                cost, distance, total_cost, parent = values
                if total_cost<min_cost:
                    min_cost = total_cost
                    min_pos = position
                    min_cost_pos = cost
                    print (f"New cheapest found COST: {min_cost_pos} POSITION: {min_pos} TOTAL DISTANCE: {min_cost}")
                 
            #checking if position is beyond character ability to move /// PLAYER
            if move_points<min_cost_pos and is_Player:
                print("Target out of reach")
                self.queue.clear()
                self.visited.clear()
                return True
            
            # checking if pos is at target destination /// PLAYER and AI
            if min_pos == target_pos and is_Player:
                print("Character reached destination")
                self.queue.clear()
                self.visited.clear()
                return False
            
            print (f"Checking if min_pos: {min_pos} is in target neighboors: {target_neighbors}")
            if min_pos in target_neighbors and is_Player==False:
                break
            
            
            #removing to be checked node from queue
            self.queue.pop(min_pos, None)
            
            # adding to be checked node to visited dict
            self.visited[min_pos] = (min_cost_pos, distance, min_cost, parent)
            
            #calculating position around new position
            new_positions = self.calc_path(min_pos, target_pos, min_cost_pos, self.visited)

            # adding new node to be checked if cost is lower
            for pos, vals in new_positions.items():
                if pos not in self.queue or vals[2] < self.queue[pos][2]:
                    self.queue[pos] = vals
        
        #checking if position is beyond character ability to move /// AI /// outdside loop
        if (move_points < min_cost_pos) and is_Player==False:
            print("Checking condition for AI, target not reached")
            path = {}
            #adding last node to visited
            self.visited[min_pos] = (min_cost_pos, distance, min_cost, parent)
            
            #building path back
            while min_pos is not None:
                values = self.visited[min_pos]
                if min_pos in self.visited:
                    path[min_pos] = (values[0], values[3])
                    # print(f"DEBUG: {min_pos} {values[3]}")
                    min_pos = values[3]
            
            closest_position = None
            closest_cost = float('-inf')  # Start with the lowest possible value
            
            for position, (cost, _) in path.items():
                if cost <= 30 and (closest_position is None or cost > closest_cost):
                    closest_position = position
                    closest_cost = cost
            print(f"New position for character.name: {closest_position}")
            return closest_position
    
    def AI_check_move(self, character, target_pos, move_points, is_Player = False):
        
        #initialize variable
        min_pos = None
        adjacent_results = {}
        self.path_queue = {}
        
        # for initial position, total dist = dist
        self.visited[character.position] = (0, self.distance(character.position, target_pos), self.distance(character.position, target_pos), None)
        
        # list of all possible (empty) adjacent square around target, goal is to calculate all space around them
        target_neighbors = self.character_manager.instance_board.check_surrounding_occupied(target_pos)

        self.path_queue = {}
            
        while True:
            min_cost = float('inf')
            
            # first node, if no items in queue
            if not self.path_queue:
                self.path_queue = self.calc_path(character.position, target_pos, 0)
            
            # iterate through queue and find optimal path (min_pos) for the cost (min_cost_pos)
            for position, values in self.path_queue.items():
                cost, distance, total_cost, parent = values
                if total_cost < min_cost:
                    min_pos = position
                    min_cost_pos = cost
                    min_distance = distance
                    min_cost = total_cost
                    min_parent = parent
                    
                    #print (f"DEBUG New cheapest found COST: POSITION: {min_pos} COST: {min_cost_pos} DISTANCE: {min_distance} TOTAL DISTANCE: {min_cost}")
            
            # checking if founded position is in neighbors, if True, removing neighbors from the list
            if min_pos in target_neighbors and is_Player == False:
                adjacent_results[min_pos] = self.path_queue[min_pos]
                target_neighbors.remove(min_pos)
                #print (f"DEBUG: Path found. min_pos is in neigbbours {min_pos} neighbor: {target_neighbors}")
        
            if not target_neighbors:
                break
            
            #removing to be checked node from queue
            #print(f"DEBUG: remove from queue {min_pos}")
            self.path_queue.pop(min_pos, None)
            
            # adding to be checked node to visited dict
            #print(f"DEBUG: adding to visited: {min_pos} with values: {min_cost_pos} / {min_distance} / {min_cost} / {parent}")
            self.visited[min_pos] = (min_cost_pos, min_distance, min_cost, min_parent)
            
            #calculating position around new position
            #print(f"DEBUG: calculating calcpath for: {min_pos}")
            new_positions = self.calc_path(min_pos, target_pos, min_cost_pos)

            # adding new node to be checked if cost is lower
            for pos, vals in new_positions.items():
                if pos not in self.path_queue or vals[2] < self.path_queue[pos][2]:
                    self.path_queue[pos] = vals
                    #print(f"{pos} added to checked queue")
            time.sleep(0)
        
        #checking if position is beyond character ability to move AI /// outside loop

        #adding last node to visited
        self.visited[min_pos] = (min_cost_pos, min_distance, min_cost, min_parent)
        print(f"Adjacent result: {adjacent_results}")
        
        # IMPORTANT! choosing best position around target path to be processed
        min_pos = min(adjacent_results, key=lambda pos: adjacent_results[pos][0])
        print(f"Best: {adjacent_results}")
        
        print(f"DEBUG: movepoints {move_points} cost pos {min_cost_pos}")
        
        path = {}
        
        if (move_points >= min_cost_pos) and is_Player == False:
            print(f"DEBUG: target within reach, returning position to move: {min_pos}")
            self.path_queue.clear()
            self.visited.clear()
            sorted_path = self.sort_path(path)
            
            return min_pos
        
        if (move_points < min_cost_pos) and is_Player == False:
            print("Checking condition for AI, target not reached")
            #building path back
            while min_pos is not None:
                values = self.visited[min_pos]
                if min_pos in self.visited:
                    path[min_pos] = (values[0], values[1], values[2], values[3])
                    # print(f"DEBUG: {min_pos} {values[3]}")
                    min_pos = values[3]
            
            closest_position = None
            closest_cost = float('-inf')  # Start with the lowest possible value
            
            for position, (cost, distance, total_cost, parent) in path.items():
                if cost <= move_points and (closest_position is None or cost > closest_cost):
                    closest_position = position
                    closest_cost = cost
            print(f"New position for AI: {closest_position}")
            
            self.path_queue.clear()
            self.visited.clear()
            sorted_path = self.sort_path(path)
            
            return closest_position
    
    def sort_path (self, path):
        sorted_path = sorted(path.items(), key=lambda item: item[1][0])  # item[1][0] is the cost value
        
        print("Sorted Path from Lowest to Highest Cost:")
        for pos, (cost, distance, total_cost, parent) in sorted_path:
            print(f"Position: {pos}, Cost: {cost}, Distance: {distance} Total distance: {total_cost} Parent: {parent}")
        print(f" Path found: {sorted_path}")
        
        return sorted_path

    def check_char_surround (self, character):
        try:
            x,y = character.position
        except:
            x,y = character
            
        surrounding_positions = []
        
        moves = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),          (1, 0),
        (-1, 1),  (0, 1),  (1, 1) 
        ]
        
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy

        # Sprawdź, czy nowa pozycja jest w granicach planszy
            if 0 <= new_x < len(self.board[0]) and 0 <= new_y < len(self.board):
                surrounding_positions.append((new_x, new_y))

        return surrounding_positions
    
    def teams_control(self):
        # if True then AI control
        self.control_team_one = True
        self.control_team_two = True
        
    def update_characters_info(self):
        teams = [(self.team_one, 1, self.control_team_one), (self.team_two, 2, self.control_team_two)]
        
        for team, team_number, is_controlled_by_ai in teams:
            for character in team:
                character.team = team_number
                character.control = 1 if is_controlled_by_ai else 0
    
    def teams(self, AI):
        # if AI then teams are chosen automatically
        # clearing teams before starting new combat
        self.team_one.clear()
        self.team_two.clear()
        
        if not AI:
            self.team_one = input("Team one, choose your team. Additional characters can be added after comma: ").split(",").title()
            self.team_one = [character.strip() for character in self.team_one]
            
            for character in self.character_manager.characters:
                if character not in self.team_one:
                    self.team_two.append(character)
            print(f"Team one: {self.team_one} /// Team two: {self.team_two}")
        else:
            # AI logic to create balanced teams
            # rd.shuffle(characters)  # Shuffle characters to make the selection less predictable TODO
            
            team_one_level = 0
            team_two_level = 0

            for character in self.character_manager.characters.values():
                char_level = character.level
                
                # Assign to the team with the lower total level to keep balance
                if team_one_level <= team_two_level:
                    self.team_one.append(character)
                    team_one_level += char_level
                else:
                    self.team_two.append(character)
                    team_two_level += char_level
        
        print(f"DEBUG: team one: {self.team_one} team two: {self.team_two}")
            
    def get_team (self, character):
        print (f"DEBUG: character in team {character.name} in {self.team_one} / {self.team_two}")
        if character in self.team_two:
            return 2
        elif character in self.team_one:
            return 1
        else: raise ValueError ("Shouldn't be possible")
    
    def remove_char (self, character):
        team = self.get_team(character)
        print(team)
        if team == 2:
            self.team_two.remove(character)
        elif team == 1:
            self.team_one.remove(character)
        else: print (f"DEBUG, remove char {character.name} from team {team}")
    
    def next_action(self):
        os.system('cls')
        # self.character_manager.instance_event_manager.start_combat()
        
        action = int(input(f"\n1. START COMBAT\n2. OTHER ACTIONS\n>>>"))
        if action == 1:
            self.character_manager.instance_event_manager.start_combat()
        if action == 2:
            while True:
                character_name = input("Which character you want to control?: ")
                if character_name in self.character_manager.characters.keys():
                    character = self.character_manager.get_character(character_name)
                    self.character_manager.instance_action.choose_action(character)
                else:
                    print("Exiting to main menu")
                    break
        else:
            print("Exiting to main menu")
            pass
            
    def start_combat(self):
        
        AI = True # if AI true then teams are automatically assigned
        # creating teams and assigning char to them
        self.character_manager.instance_board.final_board()
        
        self.teams(AI)
        
        self.character_manager.roll_initiative_for_all()
        self.character_manager.display_turn_order()
        
        #randomly generating position for teams
        self.character_manager.instance_board.initial_position()
        
        #check which teams are AI/Player controlled
        self.teams_control()
        
        #updating information in character instance about team and control
        self.update_characters_info()
        
        #start combat
        print(f"\nCombat started.")
        self.turn()
    
    def turn(self):
        # setting 1 for purpose of condition while loop
        no_team_one = 1
        no_team_two = 1
        round = 1
         
        while no_team_one > 0 and no_team_two > 0: 
            
            print(f"\n\n>>>>>> ROUND {round} <<<<<<")
            no_of_char = len(self.character_manager.characters)
            self.turn_index = 0
            
            for _ in range(no_of_char):
                
                if self.character_manager.instance_action.screen is not None:
                    pygame.event.pump()
                
                no_team_one = len(self.team_two)
                no_team_two = len(self.team_one)
                # print(f"DEBUG: no of teams in 1/2 {no_team_one} {no_team_two}")
                if no_team_one==0:
                    print ("Team one, you won the battle!")
                    self.character_manager.instance_action.screen = None
                    pygame.quit()
                    
                    for char in self.team_one:
                        char.wins += 1
                        char.games += 1
                    
                    for char in self.team_two:
                        char.defeats += 1
                        char.games += 1
                    
                    break
                
                elif no_team_two==0:
                    print ("Team two, you won the battle!")
                    self.character_manager.instance_action.screen = None
                    pygame.quit()
                    
                    for char in self.team_two:
                        char.wins += 1
                        char.games += 1
                
                    for char in self.team_one:
                        char.defeats += 1
                        char.games += 1
                    
                    break
                
                character_name,_ = self.character_manager.initiative_order[self.turn_index]
                current_character = self.character_manager.get_character(character_name)
                # print(f"DEBUG: current char: {character_name}")
                status = current_character.instance_hp.check_status(0,0)
                if status == -1:
                    self.character_manager.instance_event_manager.remove_char(current_character)
                    print (f"Removing current character {current_character.name} in turn function")
                
                if status in [-1,0,2]:
                    self.turn_index += 1
                    continue
                # print(f"DEBUG, team 1/2, type of object: {type(self.team_one)} {type(self.team_two)}")
                
                if current_character in self.team_one:
                    if self.control_team_one:
                        self.character_manager.instance_AI.AI_turn(current_character)
                    else:
                        self.character_manager.instance_player.player_turn(current_character)
                elif current_character in self.team_two:
                    if self.control_team_two:
                        self.character_manager.instance_AI.AI_turn(current_character)
                    else:
                        self.character_manager.instance_player.player_turn(current_character)
                        
                self.turn_index += 1
                
                # checking before next turn if there is any enemy/player left   
            round +=1

class Board:
    def __init__ (self, character_manager):
        self.character_manager = character_manager
        
        self.i_board = []
        self.p_board = []
        
        self.center_x = None
        self.center_y = None
        self.size = None
        self.tiles = None
        self.board_signs = []
        
        self.used_positions = set()
    
    def create_blank_board (self):
        # generate board, in future add a method for picking betweens different setups
        self.i_board = [[self.board_signs[0] for _ in range(self.size)] for _ in range(self.size)]
        self.center_x, self.center_y = self.size // 2, self.size // 2
        self.tiles = self.size**2
    
    def generate_terrain(self, tile_no1_perc, tile_no2_perc):
        tile_no1 = int(self.tiles * tile_no1_perc)
        tile_no2 = int(self.tiles * tile_no2_perc)

        return tile_no1, tile_no2
    
    def generate_area(self, symbol, num_tiles, avoid_positions=None):
        if avoid_positions is None:
            avoid_positions = set()

        positions = set()
        positions.add((self.center_x, self.center_y))
        self.i_board[self.center_y][self.center_x] = symbol

        while len(positions) < num_tiles:
            x, y = rd.choice(list(positions))
            # random direction
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
            rd.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.size and 0 <= ny < self.size):
                    if self.i_board[nx][ny] != " /\\":
                        self.i_board[ny][nx] = symbol
                        positions.add((nx, ny))
                        break
    
    def final_board (self):
        # main function
        self.size = 40
        self.board_signs = [" . "," | "," /\\"]
        
        # method for creating empty board
        self.create_blank_board()
        
        tile_no1_perc = 0.2
        tile_no2_perc = 0.1
        first_tiles, second_tiles = self.generate_terrain(tile_no1_perc, tile_no2_perc)
        
        self.board = self.generate_area(self.board_signs[1], first_tiles)
        self.board = self.generate_area(self.board_signs[2], second_tiles, self.board_signs[1])
        
        for row in self.i_board:
            print("".join(row))
        
        self.p_board = [row[:] for row in self.i_board]
    
    def get_rd_position (self,center):
        # Generate a rd position around the center within a range of -1 to 1
        x, y = center

        while True:
            new_x = x + rd.choice([-1, 0, 1])
            new_y = y + rd.choice([-1, 0, 1])
            position = (new_x, new_y)
            if position not in self.used_positions and 0 <= new_x < self.size and 0 <= new_y < self.size:
                self.used_positions.add(position)
                return position
        
    def initial_position(self):
        
        # Generate rd central points for both teams
        team_one_center = (rd.randint(2, self.size - 3), rd.randint(self.size - 6, self.size - 2))
        team_two_center = (rd.randint(2, self.size - 3), rd.randint(1, 5))
        
        self.used_positions = set()  # To ensure no overlapping positions

        for char in self.character_manager.instance_event_manager.team_two:
            print(f"DEBUG: team two {self.character_manager.instance_event_manager.team_two}")
        for char in self.character_manager.instance_event_manager.team_one:
            print(f"DEBUG: team one {self.character_manager.instance_event_manager.team_one}")
        
        # Assign rd clustered positions for team two
        for char in self.character_manager.instance_event_manager.team_two:
            print(f"DEBUG: char object: {char.name}")
            position = self.get_rd_position(team_two_center)
            char.position = position
            self.update_player_position(char, position)

        # Assign rd clustered positions for team one
        for char in self.character_manager.instance_event_manager.team_one:
            print(f"DEBUG: char object: {char.name}")
            position = self.get_rd_position(team_one_center)
            char.position = position
            self.update_player_position(char, position)
    
    def update_player_position(self, character, new_position):
        # main function for updating player position - within board and in Character instance
        print(f"{character.name} move from {character.position} to {new_position}")
        
        #return old position state to original state
        old_position = character.position
        if old_position:
            old_x, old_y = old_position
            self.p_board[old_y][old_x] = self.i_board[old_y][old_x]
        
        new_x, new_y = new_position
        self.p_board[new_y][new_x] = character.name[:2]
        character.position = new_position
        
        print("Current board state:")
        for row in self.p_board:
            print(" ".join(row))
        print("\n")
        
    def check_surrounding_occupied(self, pos):
        x, y = pos

        surrounding_positions = []

        moves = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),          (1, 0),
            (-1, 1),  (0, 1),  (1, 1)
        ]

        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy

            # TODO if len==1 then free, assume that char has min. 2 letter
            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                if self.p_board[new_y][new_x] in self.board_signs:
                    surrounding_positions.append((new_x, new_y))

        return surrounding_positions

class Algorithms():
    def __init__ (self, character_manager):
        self.character_manager = character_manager
    
    def calc_pts_alongtheway (self, pos_start, pos_end):
        
        x1,y1 = pos_start
        x2,y2 = pos_end
        grid_size = 1
        min_overlap=0.1
        
        path = set()
        line = LineString([(x1 + 0.5, y1 + 0.5), (x2 + 0.5, y2 + 0.5)])

        # Iterujemy po komórkach siatki
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                cell = box(x, y, x + grid_size, y + grid_size)
                intersection = line.intersection(cell)

                # Sprawdzamy, czy długość przecięcia jest wystarczająco długa
                if not intersection.is_empty and line.intersection(cell).length >= min_overlap:
                    path.add((x, y))
        path = [pos for pos in path if pos not in (pos_start, pos_end)]
        return list(path)
    
    def check_path_to_target (self, pos_start, pos_end):
        #iterate through the path and check conditions along the way, if it is obstructed then return diff level (for AI purposes)
        path = self.calc_pts_alongtheway (pos_start, pos_end)
        diff = 0
        path_len = len(path)
        
        #for each character in the path
        for char in self.character_manager.characters.values():
            if char.position in path:
                diff += 1
        
        #for each tree in the path
        for pos in path:
            if self.character_manager.instance_board.p_board[pos[0]][pos[1]] in self.character_manager.instance_board.board_signs[1]:
                diff += 0.5
        try:
            perc = diff / path_len
        except:
            print ("Possible attack of opportunity")
            return 10
        
        # AI LOGIC REWARD
        if perc > 0.5:
            # TODO disadvantage, +5 AC to target
            return 15
        elif perc> 0.3:
            # TODO +5 AC to target
            return 30
        elif perc> 0.1:
            # TODO +2 AC to target
            return 50
        else: return 100
        

class MainMenu:
    def __init__ (self):
        self.character_manager = CharacterManager()
        self.event_queue = queue.Queue()  # Kolejka do komunikacji z wątkiem Pygame
    
    def display_menu(self):
        while True:
            print("\n-- MAIN MENU --")
            print("1. Create a new character")
            print("2. Load an existing character")
            print("3. Start game")
            print("4. Save current character")
            print("5. Display loaded character")
            print("6. Exit")
            
            print(f"Current statistics:")
            for char in self.character_manager.characters.values():
                print(f"\n{char.name}:\nWins:{char.wins}  Defeat: {char.defeats}  Games: {char.games}")

            choice = input("Choose an option: ")


            if choice == '1':
                self.create_character()
            elif choice == '2':
                self.load_character()
            elif choice == '3':
                self.start_game()
                # n = 0
                # while n<20:
                #     self.start_game()
                #     n += 1
            elif choice == '4':
                self.save_character()
            elif choice == '5':
                self.display_loaded()
            elif choice == '6':
                print("Exiting game...")
                break
            else:
                print("Invalid choice, try again.")
    
    def create_character(self):
        name = input("Enter the name of new character: ")
        new_character = Character.create_new_character(name)
        self.character_manager.add_character(new_character)
        print(f"Character {name} created successfully!")
    
    def load_character(self):
        #TESTING MODE
        characters_to_load = ["Milva", "Ghoul", "Aragorn", "Gimli","Geralt", "Legolas"]  # Lista nazw postaci do załadowania
        for name in characters_to_load:
            file_name = f"{name}.pkl"
            try:
                loading_character = Character.load_character(self, file_name)
                self.character_manager.add_character(loading_character)
                print(f"Character {name} loaded successfully!")
            except FileNotFoundError:
                print(f"Character file '{file_name}' not found!")
        
        #MAIN FUNCTION
        # name = input("Enter the name of the character to load: ")
        # file_name = f"{name}.pkl"
        # try:
        #     loading_character = Character.load_character(self,file_name)
        #     self.character_manager.add_character(loading_character)
        #     print(f"Character {name} loaded successfully!")
        # except FileNotFoundError:
        #     print(f"Character file '{file_name}' not found!")
            
    def save_character(self):
        for save_char_name, char_instance in self.character_manager.characters.items():
            Character.save_character(char_instance)
    
    def display_loaded(self):
        for save_char_name, char_instance in self.character_manager.characters.items():
            print(char_instance)
    
    def start_game(self):
        self.clear_game_cache()
        EventManager.next_action(self)
        
    def clear_game_cache(self):
        #TODO for testing purposes
        for char in self.character_manager.characters.values():
            char.position = set()
        for char in self.character_manager.characters.values():
            Character.re_calculate(char)
        self.character_manager.instance_event_manager.board = []
        ...

class Move:
    def __init__(self, character, character_manager, event_queue, screen) -> None:
        self.character = character
        self.character_manager = character_manager
        self.tile_size = 30
        self.screen = screen  # Przekazujemy ekran Pygame jako argument
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.event_queue = event_queue  # Kolejka do komunikacji między wątkami

        self.colors = {
            "player": (0, 0, 255),  # Gracz - niebieski
            "enemy": (255, 0, 0),   # Wróg - czerwony
            "grass": (144, 238, 144),  # Jasny zielony dla trawy
            "forest": (34, 139, 34),   # Ciemny zielony dla lasu
            "mountain": (169, 169, 169),  # Szary dla gór
        }

    def draw_board(self):
        self.screen.fill(self.white)
        
        for y in range(40):
            for x in range(40):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                
                # Dobieranie koloru w zależności od symbolu w self.i_board
                terrain_type = self.character_manager.instance_board.i_board[y][x]
                
                if terrain_type == " . ":  # grass
                    color = self.colors["grass"]
                elif terrain_type == " | ":  # forest
                    color = self.colors["forest"]
                elif terrain_type == " /\\":  # hills
                    color = self.colors["mountain"]
                else:
                    color = self.white  # Domyślnie białe tło dla nieznanych symboli

                pygame.draw.rect(self.screen, color, rect)  # Rysowanie pola planszy
                pygame.draw.rect(self.screen, self.black, rect, 1)  # Obrys kratki


        for character in self.character_manager.characters.values():
            if not hasattr(character, 'position'):
                print(f"{character.name} has no position attribute!")
                continue

            
            x, y = character.position
            team_two = self.character_manager.instance_event_manager.team_two
            team_one = self.character_manager.instance_event_manager.team_one
            
            if character not in team_one and character not in team_two:
                continue  # Przeskoczenie tej postaci

            
            color = self.colors["player"] if character in team_one else self.colors["enemy"]
            player_rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
            pygame.draw.rect(self.screen, color, player_rect)
            
            # Dodajemy inicjały na planszy
            font = pygame.font.Font(None, 18)
            initials = font.render(character.name[:2], True, self.white)
            self.screen.blit(initials, (x * self.tile_size + 5, y * self.tile_size + 5))
        
        pygame.display.update()  # Aktualizacja całego ekranu

    def run_game(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = event.pos
                        x, y = pos[0] // self.tile_size, pos[1] // self.tile_size
                        
                        print("Current positions:")
                        for char in self.character_manager.characters.values():
                            print(f"{char.name} is at {char.position}")
                         
                        cost = self.character_manager.instance_event_manager.check_move(self.character, (x,y), 30, True)
                        if cost==True:
                            continue
                        
                        # Sprawdzamy, czy wybrane pole nie jest zajęte
                        if not any(tuple(c.position) == (x, y) for c in self.character_manager.characters.values()):
                            self.character_manager.instance_event_manager.update_player_position(self.character, (x,y))
                            # self.character.position = (x,y)
                            self.draw_board()
                            self.event_queue.put((x, y))
                            return  # Kończymy tylko pętlę, nie zamykając Pygame
                        else:
                            print("Occupied!")
            # Rysowanie planszy
            self.draw_board()
            clock.tick(30)

os.system('cls')


main_menu = MainMenu()
main_menu.display_menu()



pygame.quit()

# MANUAL TESTING METHOD testing repo

# y = "Ghoul"
# x = Character(name=y).load_character((y+".pkl"))
# x.wins = 0

# x.save_character() testowe zmiany