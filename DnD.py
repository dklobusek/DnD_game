import pandas as pd
import random as rd
import os, pickle, pygame
import pygame
import queue, time
import numpy as np
from shapely.geometry import LineString, box
from datetime import datetime

class Data:
    # Class for loading data, Singleton approach
    _instance = None
    
    def __new__(cls, *args, **kwargs):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__ (self):
        # if not hasattr(self, 'data_loaded'):  # Check if data is already loaded
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.load_all_data()
    
    def load_all_data(self):
        # Method to load all data
        self.races = self.load_races()
        self.classes = self.load_classes()
        self.armors = self.load_armors()
        self.shields = self.load_shields()
        self.weapons = self.load_weapons()
        self.fighter = self.load_fighter()
        self.data_loaded = True  # Mark that data has been loaded
        
    def reload_data(self):
        # Method to reload all data
        self.data_loaded = False
        self.load_all_data()

    def load_races(self):
        file_path = os.path.join(self.base_dir, 'DnD', 'race.csv')
        data = pd.read_csv(file_path, delimiter=";")
        races = {}
        for _,row in data.iterrows():
            race_name = row["race"]
            race_info = {col: row[col] for col in data.columns if col!= "race"}
            races[race_name] = race_info
        return races
    
    def load_armors(self):
        file_path = os.path.join(self.base_dir, 'DnD', 'armors.csv')
        data = pd.read_csv(file_path, delimiter=";")
        data_dict = {}
        for _,row in data.iterrows():
            data_header = row["armor"]
            data_info = {col: row[col] for col in data.columns if col!= "armor"}
            data_dict[data_header] = data_info
        return data_dict
    
    def load_shields(self):
        file_path = os.path.join(self.base_dir, 'DnD', 'shields.csv')
        data = pd.read_csv(file_path, delimiter=";")
        data_dict = {}
        for _,row in data.iterrows():
            data_header = row["shield"]
            data_info = {col: row[col] for col in data.columns if col!= "shield"}
            data_dict[data_header] = data_info
        return data_dict
    
    def load_weapons(self):
        file_path = os.path.join(self.base_dir, 'DnD', 'weapons.csv')
        data = pd.read_csv(file_path, delimiter=";")
        data_dict = {}
        for _,row in data.iterrows():
            data_header = row["weapon"]
            data_info = {col: row[col] for col in data.columns if col!= "weapon"}
            data_dict[data_header] = data_info
        return data_dict
    
    def load_classes(self):
        file_path = os.path.join(self.base_dir, 'DnD', 'classes.csv')
        data = pd.read_csv(file_path, delimiter=";", encoding='ISO-8859-1')
        classes = {}
        for _,row in data.iterrows():
            classes_name = row["class"]
            classes_info = {col: row[col] for col in data.columns if col!= "class"}
            classes[classes_name] = classes_info
        return classes
    
    def load_fighter(self):
        file_path = os.path.join(self.base_dir, 'DnD', 'fighter.csv')
        data = pd.read_csv(file_path, delimiter=";")
        data_dict = {}
        for _,row in data.iterrows():
            data_header = row["level"]
            data_info = {col: row[col] for col in data.columns if col!= "level"}
            data_dict[data_header] = data_info
        return data_dict
    
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
    
    def get_shields(self):
        if not hasattr(self, 'shields'):
            print("Loading shields...")
            self.shields = Data.load_shields(self)
        return self.shields
    
    def get_weapons(self):
        # If weapons haven't been loaded yet, load them
        if not hasattr(self, 'weapons'):
            print("Loading weapons...")
            self.weapons = Data.load_weapons(self)
        return self.weapons
    
    def get_fighter(self):
        if not hasattr(self, 'fighter'):
            self.weapons = Data.load_fighter(self)
        return self.fighter
        
class Character:
    #generating representation of character
    def __init__ (self, name, race=None, class_name = None, abilities = {}, abil_modifiers = None, hp = None, skills = None, features = None, level = 1, initiative = None):
        #TODO I switch order
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data = self.get_data_instance() #done
        
        self.instance_abil = Abilities(self)
        self.instance_classes = CharacterClass(self)
        self.instance_hp = HitPoints(self)
        self.instance_armor_class = ArmorClass(self)
        self.instance_equipment = Equipment(self)
        self.instance_modifiers = Modifiers(self)
        self.instance_features = Features(self)
        self.instance_skills = Skills(self)
        
        self.instance_fighter = Fighter(self)
        
        self.name = name
        self.race = race
        self.class_name = class_name
        self.abilities = abilities
        self.skills = skills
        self.features = features
        self.level = level
        self.initiative = initiative
        self.size = "normal"
        
        self.behaviour = None # TODO add a method
        
        self.actions = 1 # TODO add a method
        self.bonus_actions = 1 # TODO
        self.move_points = 30 # TODO add a method
        self.reactions = 1 # attack of opportunity
        
        self.c_actions = None # no of actions furing turn, default
        self.c_move_points = None # move points during turn, default
        self.c_attacks = None # no of attacks during turn
        self.c_reactions = None # attack of opportunity
        self.c_bonus_actions = None
        
        self.position = set()
        self.team = None # 1 team one, 2 team two
        self.control = None #1 AI controlled, 0 player controller
        
        self.wins = 0
        self.defeats = 0
        self.games = 0
        
    def __str__ (self):
        abilities_str = "\n".join([f"{key.capitalize():<15}: {value:>2}" for key, value in self.abilities.items()])
        return (f"\n\nName: {self.name}\nLevel: {self.level}\nRace: {self.race}\nCharacter class: {self.class_name}\nBase HP: {self.instance_hp.base_hp}\nArmor class: {self.instance_armor_class.armor_class}\n::: Abilities :::\n{abilities_str}\n{self.instance_equipment}Default behaviour: {self.behaviour}\nProf. bonus: {self.instance_modifiers.b_prof_bonus}\nTotal bonus to attack: {self.instance_modifiers.attack_mod_w1}\n{self.instance_features}\nSecond winds: {self.instance_fighter.second_winds}\nWeapon mastery: {self.instance_features.weapon_mastery}")

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
        character = cls(name=name) # creating an instance
        
        character.pick_level() 
        character.race = character.choose_race()
        character.class_name = character.instance_classes.choosing_class()
        character.abilities = character.instance_abil.gen_abilities() # plus calc modifiers
        character.instance_hp.calc_base_hp()
        character.choose_behaviour()
        character.instance_features.get_all()
        character.instance_features.update_all()
        
        # fighter method
        if character.class_name == "Fighter":
            character.instance_features.choose_fighting_style()
            character.instance_fighter.get_second_winds()
            character.instance_features.choose_weapon_mastery()
            
        character.instance_equipment.std_equip()
        character.instance_modifiers.update_attack_mod_w1()
        character.instance_modifiers.update_attack_mod_w2()
        
        return character
    
    @classmethod
    def create_new_auto_character(cls, name):
        #auto generating new char
        character = cls(name=name) # creating an instance
        
        character.pick_level() 
        character.race = character.choose_race()
        character.class_name = character.instance_classes.choosing_class()
        
        character.abilities = character.instance_abil.auto_gen_abilities() # plus calc modifiers
        character.instance_hp.calc_base_hp()
        character.behaviour = "melee"
        
        character.instance_features.get_all()
        character.instance_features.update_all()
        
        # fighter method
        if character.class_name == "Fighter":
            character.instance_features.auto_choose_fighting_style()
            character.instance_fighter.get_second_winds()
            character.instance_features.weapon_mastery = ['Greataxe', 'Greatsword', 'Longsword', 'Maul', 'Warhammer']
    
        character.instance_equipment.std_equip()
        character.instance_equipment.auto_first_weapon_init()
        character.instance_modifiers.update_attack_mod_w1()
        character.instance_modifiers.update_attack_mod_w2()
        
        return character
        
        
    def save_character(self):        
        folder = os.path.join(self.base_dir, 'saved')
        file_path = os.path.join(folder, f"{self.name}.pkl")
        with open(file_path, "wb") as save_file:
            pickle.dump(self, save_file)
        print(f"Character {self.name} saved successfully to {file_path}")
    
    def load_character(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(base_dir, 'saved')
        file_path = os.path.join(folder, filename)
        
        with open(file_path, "rb") as load_file:
            loaded_character = pickle.load(load_file)
        self.__dict__.update(loaded_character.__dict__)
        
        Character.re_calculate(self)
        
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
    
    def auto_pick_level(self, s, e):
        self.level = rd.randint(s,e)
    
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
    
    def choose_behaviour (self):
        list = ["ranged", "melee"]
        choose = input("Choose default behaviour for AI (ranged / melee): ")
        
        if choose in list:
            self.behaviour = choose
        else:
            print("Wrong behaviour")     
    
    def re_calculate(self):
        self.instance_abil.calculate_modifiers()
        self.instance_modifiers.update_attack_mod_w1()
        self.instance_modifiers.update_attack_mod_w2()
        self.instance_modifiers.update_hit_mod_w1()
        self.instance_armor_class.calculate_ac()
        self.instance_hp.update_hp()
        self.instance_hp.status = 1
        self.team = None # 1 team one, 2 team two
        self.control = None #1 AI controlled, 0 player controller
        
    
class Abilities:
    # there shouldn't be any method that initialize by its own
    def __init__ (self, character):
        self.character = character
        self.races = character.data.get_races()
        self.abilities = {}  # Initialize abilities as None
        self.temp_abilities = {}
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
    
    def auto_gen_abilities(self):
        gen_rd_abilities = self.auto_generate_initial_abilities()
        abilities = self.auto_assign_abilities(gen_rd_abilities)
        abilities = self.apply_racial_bonuses(abilities)
        abilities = self.apply_special_bonuses(abilities)
        
        self.abilities = abilities
        self.abil_modifiers = self.calculate_modifiers()
        
        return abilities
    
    def generate_initial_abilities(self):
        while True:
            temp =  [sum(sorted([rd.randint(1, 6) for _ in range(4)], reverse=True)[:3]) for _ in range(6)]
            x = input(f"Do you want to use this abilities? Press y for yes: {temp} : ").lower()
            if x == "y":
                return temp
    
    def auto_generate_initial_abilities(self):
        return [sum(sorted([rd.randint(1, 6) for _ in range(4)], reverse=True)[:3]) for _ in range(6)]
        
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
        
    def auto_assign_abilities(self, temp_stats):
        # appending rd numbers to abilities
        abilities = {"Strength": None, "Dexterity": None, "Constitution": None, "Intelligence": None, "Wisdom": None, "Charisma": None}
        
        temp_stats = sorted(temp_stats, reverse=True)
        
        for key, value in zip(abilities.keys(), temp_stats):
            abilities[key] = int(value)

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

class Fighter:
    def __init__ (self, character):
        self.character = character
        
        self.second_winds = 0
        self.c_second_winds = None
        
        self.action_surge = []
    
    def get_second_winds(self):
        lvl = self.character.level
        data = self.character.data.get_fighter()
        self.second_winds = data[lvl]["second_wind"]
    
    
class ArmorClass:
    def __init__ (self, character, armor_class =  10): #TODO implement a method to lower AC if dex is lower than 9
        self.armor_class = armor_class
        self.character = character
      
    def calculate_ac(self):
        # calculating armor class based on equipped armor and dexterity modifers, considering limitations (dex) of armor, RETURNING AND UPDATING ARMOR CLASS GLOBAL
        armor = self.character.instance_equipment.armor
        shield = self.character.instance_equipment.offhand
        shield = self.character.instance_equipment.offhand


        #base modifier from armor/shield
        a_0 = armor["armor_class"] if armor is not None else 10
        try:
            a_1 = shield["armor_class"] if shield is not None else 0
        except:
            a_1 = 0
        
        #additional modifiers
        a_2 = self.character.instance_modifiers.fs_ac
        
        #check dex mod compared to armor
        dex_mod = self.character.instance_abil.abil_modifiers["Dexterity"]
        max_dex_mod_armor = armor["max_dex_mod"] if armor is not None else 99
        if dex_mod>max_dex_mod_armor: a_01 = max_dex_mod_armor
        else: a_01 = dex_mod
        
        self.armor_class = a_0 + a_01 + a_1 + a_2
       
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
        
        # singleton for accesing instance of CharacterManager
        character_manager = CharacterManager._instance
        
        if self.status == 2 and dmg == 0:
            txt = (f"{self.character.name} is already stabilized!") # TODO to be removed
            print(txt)
            character_manager.ins_pgame.add_log (txt)
            return 2
        
        if self.status == 2 and dmg > 0 and critical:
            txt = f"{self.character.name} was stabilized, but it is not anymore!"# TODO to be removed
            print(txt)
            character_manager.ins_pgame.add_log (txt)
            self.status=0
            self.death_throw_count_plus += 2
            return 0
        
        # return 1 if char alive, 0 if unconscious, -1 if dead /// BEFORE TURN
        if self.current_hp>0 and self.status==1:
            return 1
        
        # if dmg was larger than pool hp then dead, set status to -1 /// DURING TURN #TODO needs to be reworked to account for current hp before last attack
        elif dmg>=self.base_hp:
            txt =  (f"{self.character.name} is dead! Damage {dmg} was too big for him to handle it.")
            print(txt)
            character_manager.ins_pgame.add_log (txt)
            self.status = -1
            
            self.character_manager.instance_event_manager.remove_char(self.character)
            
            return - 1
        
        # first damage to unconscious state, set character to unconscious /// DURING TURN
        elif self.current_hp<=0 and self.status == 1:
            txt =  (f"{self.character.name} is unconscious! Damage {dmg} was too big for him to handle it. He can still be revived")
            print(txt)
            character_manager.ins_pgame.add_log (txt)
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
                txt =  (f"{self.character.name} you are returning back to life!")
                print(txt)
                character_manager.ins_pgame.add_log (txt)
            elif roll >= 10:
                self.death_throw_count_minus += 1
            elif roll == 1:
                self.death_throw_count_plus += 2
            else:
                self.death_throw_count_plus += 1
                
            txt = (f"Death saving roll for {self.character.name}: {roll}, current status: M / P {self.death_throw_count_minus} {self.death_throw_count_plus}")
            print(txt)
            character_manager.ins_pgame.add_log (txt)
                
        #SECOND PART
        # check status based on death_throw_count, outside previous loop
        if self.death_throw_count_plus>=3:
            txt =  (f"{self.character.name} is dead! Death throw count reached 3 or beyond")
            print(txt)
            character_manager.ins_pgame.add_log (txt)
            self.death_throw_count_plus = 0
            self.death_throw_count_minus = 0
            self.status = -1
            
            self.character_manager.instance_event_manager.remove_char(self.character)
            
            return -1
        
        # return status unconscious, cannot move during
        elif self.death_throw_count_minus>=3:
            txt =  (f"{self.character.name} you are stabilized!")
            print(txt)
            character_manager.ins_pgame.add_log (txt)
            self.death_throw_count_plus = 0
            self.death_throw_count_minus = 0
            self.status = 2
            return 2
        
        else:
            return 0
        
    def decrease_target_hp(self, dmg):
        self.current_hp = max(0, self.current_hp - dmg)
                
    
    def heal_itself(self, heal):
        self.current_hp += min(heal, self.base_hp - self.current_hp)
    
    def get_current_hp_per(self):
        return self.current_hp / self.base_hp

class Features:
    def __init__ (self, character):
        self.character = character
        self.list = []
        
        self.extra_atk = None
        self.fighting_styles = []
        
        self.no_cleave = 1
        self.c_no_cleave = 0
        
        self.no_nick = 1
        self.c_no_nick = 0
        
        self.weapon_mastery = []
    
    def __str__(self):
        return (f"No. of attacks: {self.extra_atk}\nFighting style: {self.fighting_styles}")
    
    def get_all (self):
        self.list = []
        char_class = self.character.class_name.lower()
        method_name = f"get_{char_class}"
        c_lvl = self.character.level
        data = getattr(self.character.data, method_name)()
        
        for lvl in range (1, c_lvl+1):
            level_data = data.get(lvl, {})
            features = level_data.get("features", "")
            
            if features:
                split_features = [feature.strip() for feature in features.split(",")]
                self.list.extend(split_features)
    
    def update_ext_attacks(self):
        # find a "extra attack" feature in class features and count them TODO, other method two,three
        
        no = self.list.count("extra attack")
        self.extra_atk = no+1
        print(self.extra_atk)
    
    def update_all(self):
        self.update_ext_attacks()
    
    def choose_fighting_style (self):
        print (">>> AVAILABLE FIGHTING STYLES <<<")
        list = ["archery", "defense", "dueling", "great weapon fighting", "interception", "protection", "two weapon fighting"]
        print(" / ".join(list))
        
        # reset lists
        self.fighting_styles = []
        self.re_calc_fs()
        i=0
        no_of_fs = self.list.count("fighting style")
        
        while i < no_of_fs:
            fs = input("Choose one of the fighting style: ").lower()
            if fs in list:
                fs = fs.replace(" ", "_")
                method_name = f"fs_{fs}"
                action = getattr(self, method_name, None)
                self.fighting_styles.append(fs)
                action()
                i += 1
            else:
                print("Invalid fighting style")
    
    def auto_choose_fighting_style (self):
        list = ["archery", "defense", "dueling", "great weapon fighting", "interception", "protection", "two weapon fighting"]
        
        # reset lists
        self.fighting_styles = []
        self.re_calc_fs()
        i=0
        no_of_fs = self.list.count("fighting style")
        
        while i < no_of_fs:
            fs = rd.choice(list)
            if fs in list:
                fs = fs.replace(" ", "_")
                method_name = f"fs_{fs}"
                action = getattr(self, method_name, None)
                self.fighting_styles.append(fs)
                action()
                i += 1
            else:
                print("Invalid fighting style")
    
    def re_calc_fs (self):
        # zeroing all bonuses from fs
        self.character.instance_modifiers.fs_arch_bonus_atk = 0
        
        self.character.instance_modifiers.fs_ac = 0
        self.character.instance_armor_class.calculate_ac()
        
        self.character.instance_modifiers.fs_dmg_bonus = 0
    
    def fs_archery(self):
        # no need to recalculate, constant bonus
        self.character.instance_modifiers.fs_arch_bonus_atk = 2
        print("Fighting style archery is chosen")
    
    def fs_defense(self):
        if self.character.instance_equipment.armor is None:
            print("Fighting style defense is chosen, but requirements are not met - no armor.")
            return False
        
        if self.character.instance_equipment.armor["type"] in ["Light armor", "Medium armor", "Heavy armor"]:
            self.character.instance_modifiers.fs_ac = 1
            self.character.instance_armor_class.calculate_ac()
            
            print("Fighting style defense is chosen")
        else:
            print("Fighting style defense is chosen, but requirements are not met")
    
    def fs_dueling(self):
        try:
            #recalc needed when changing eq
            
            #reset at the beggining (in case of lost)
            self.character.instance_modifiers.fs_dmg_bonus = 0
            
            wp_1 = self.character.instance_equipment.first_weapon["grip"]
            wp_2 = self.character.instance_equipment.second_weapon
            
            if wp_1 == "one-handed" and wp_2 == None:
                self.character.instance_modifiers.fs_dmg_bonus = 2
                print("Fighting style dueling is active")
            else:
                print("Fighting style dueling is chosen, but requirements are not met")
        except:
            print("No weapon equipped, dueling fighting style not active. Equip weapon to activate it!")
    
    def fs_great_weapon_fighting(self):
        # method of checking
        try:
            if self.character.instance_equipment.first_weapon["grip"] == "two-handed" and "great_weapon_fighting" in self.list:
                return True
            else: return False
        except:
            pass
        
    def fs_interception(self):
        pass
    
    def fs_protection(self):
        pass
    
    def fs_two_weapon_fighting(self):
        pass

    def choose_weapon_mastery(self):
        lvl = self.character.level
        data = self.character.data.get_fighter()
        data_wp = self.character.data.get_weapons()
        self.weapon_mastery_count = data[lvl]["weapon_mastery"]
        
        #restarting
        self.weapon_mastery = []
        
        i= 0 
        while i < self.weapon_mastery_count:
            wm = (input("Choose weapon mastery: ")).title()
            if wm in data_wp.keys() and wm not in self.weapon_mastery:
                self.weapon_mastery.append(wm)
                i += 1
                print("Added")
            else:
                print("Wrong weapon") 
            
class Skills:
    def __init__ (self, character):
        self.character = character

class Modifiers:
    def __init__ (self, character):
        self.character = character
        self.ac_modifiers = None
        
        self.attack_mod_w1 = None
        self.attack_mod_w2 = None
        self.hit_mod_w1 = None
        self.hit_mod_w2 = None
        
        self.b_prof_bonus = 0 # basic proficiency bonus resulting from class and level
        self.fs_arch_bonus_atk = 0 # fighting style bonus to ranged weapons
        self.fs_ac = 0 # fighting style bonus to AC
        self.fs_dmg_bonus = 0 # damage bonus from dueling (holding one-handed weapon in two hands)
    
    def update_ac (self, ac):
        self.ac_modifiers = ac
        print(f"modify_ac function in Modifiers class, AC value: {ac}")
        
    def update_attack_mod_w1(self):
        #TODO add multiple bonuses
        
        mod1 = self.get_ability_bonus_w1()
        mod2 = self.get_basic_prof_bonus()
        mod3 = self.fs_arch_bonus_atk if self.character.instance_equipment.first_weapon["reach"]>10 else 0
        
        sum = mod1+mod2+mod3
        self.attack_mod_w1 = sum
        return sum
    
    def update_attack_mod_w2(self):
        #TODO add multiple bonuses
        try:
            mod1 = self.get_ability_bonus_w2()
            mod2 = self.get_basic_prof_bonus()
            mod3 = self.fs_arch_bonus_atk if self.character.instance_equipment.offhand["reach"]>10 else 0
            
            sum = mod1+mod2+mod3
            self.attack_mod_w2 = sum
            return sum
        except:
            pass
    
    def update_hit_mod_w1(self):
        mod1 = self.get_ability_bonus_w1()
        mod2 = self.fs_dmg_bonus
        
        sum = mod1+mod2
        
        self.hit_mod_w1 =sum
        
    def update_hit_mod_w2(self):
        mod1 = self.get_ability_bonus_w2()   
        sum = mod1
        
        self.hit_mod_w1 =sum
    
    def get_ability_bonus_w1(self):
        try:
            abil = self.character.instance_equipment.first_weapon.get("ability", 0).title()
            return self.character.instance_abil.abil_modifiers[abil]
        except:
            pass
    
    def get_ability_bonus_w2(self):
        try:
            abil = self.character.instance_equipment.offhand.get("ability", 0).title()
            return self.character.instance_abil.abil_modifiers[abil]
        except:
            pass
    
    
    def get_basic_prof_bonus(self):
        char_class = self.character.class_name.lower()
        method_name = f"get_{char_class}"
        lvl = self.character.level
        data = getattr(self.character.data, method_name)()
        
        prof_bonus = data.get(lvl, {}).get("prof_bonus")
        self.b_prof_bonus = prof_bonus
        return prof_bonus

class Equipment:
    #store information about character/enemy equipment and its modifiers, probably the biggest class there will be, or at least class that will draw the biggest amount information from csv file
    def __init__ (self, character):
        self.character = character
        self.armor = None
        self.body = None
        self.first_weapon = None
        self.offhand = None
        self.backup_weapon = None
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
    
    def std_equip(self):
        armors_list = self.character.data.get_armors()
        armor_choice = "Unarmored"
        self.armor = {"name": armor_choice, **armors_list[armor_choice]}
        
        weapon_list = self.character.data.get_weapons()
        weapon_choice = "Unarmed"
        self.first_weapon = {"name": weapon_choice, **weapon_list[weapon_choice]}
    
    def armor_init(self):
        #TODO choosing armor from list, need to check for proficiency and str required among other stuff
        armors_list = self.character.data.get_armors()
        for armor, values in armors_list.items():
            print (f"{armor} {values}", sep = "  ///  ")
        
        armor_choice = input("What armor do you want to wear?: ")
        
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
        
        item_choice = input("What weapon do you want to equip?: ")

        if item_choice in item_list:
            #condition - two handed
            if item_list[item_choice]["grip"] == "two-handed" and self.offhand is not None:
                print("You can't equip two-handed weapon with a shield/second weapon!")
                return False

            print(f"{item_choice} equipped!")
            #TODO if new armor it should follow the chain of actions AND: a) update weight (if new armor) b) modify armor class and pass argument about AC and Dex mod, c) check if this type of armor can be worn (probably the first thing) d), check the strength required, probably the second
            self.first_weapon = {"name": item_choice, **item_list[item_choice]}
        else:
            print("No weapon found")
    
    def auto_first_weapon_init(self):
        #TODO choosing weapon from list, need to check for proficiency and str required among other stuff
        wm_list = self.character.instance_features.weapon_mastery
        wm = rd.choice(wm_list)
        item_list = self.character.data.get_weapons()
        
        item_choice = wm
        
        if item_choice in item_list:
            print(f"{item_choice} equipped!")
            #TODO if new armor it should follow the chain of actions AND: a) update weight (if new armor) b) modify armor class and pass argument about AC and Dex mod, c) check if this type of armor can be worn (probably the first thing) d), check the strength required, probably the second
            self.first_weapon = {"name": item_choice, **item_list[item_choice]}
        else:
            print("No weapon found")
            
    def offhand_init(self):
        # TODO implement a method to choose second weapon and fight with it
        weapons_list = self.character.data.get_weapons()
        shields_list = self.character.data.get_shields()
        
        s_w = input("What do you want to equip? shield or weapon?: ").lower()
        
        if s_w in ("shield", "weapon") and self.first_weapon["grip"]=="two-handed":
            print("You cannot equip shield/weapon, if you wield two handed weapon")
        elif s_w == "shield":
            for item, stats in shields_list.items():
                print (f"{item} {stats}", sep = "  ///  ")
            item_choice = "shield"#input("What shield do you want to equip?: ")
            self.offhand = {"name": item_choice, **shields_list[item_choice]}
            print(f"{item_choice} equipped!")
        elif s_w == "weapon":
            for item, stats in weapons_list.items():
                print (f"{item} {stats}", sep = "  ///  ")
            item_choice = input("What weapon as second do you want to equip?: ")
            if item_choice in weapons_list and weapons_list[item_choice]["lh"]=="light":
                self.offhand = {"name": item_choice, **weapons_list[item_choice]}
            else:
                print("Wrong weapon")
        else:
            print("Wrong!")
    
    def offhand_unequip(self):
        if self.offhand is not None:
            self.offhand = None
            self.character.instance_armor_class.calculate_ac()
        else:
            print("There is nothing in the second hand!")
            
    def first_weapon_unequip(self):
        item_list = self.character.data.get_weapons()
        
        if self.first_weapon is not None:
            self.first_weapon = {"name": "unarmed", **item_list["Unarmed"]}
        else:
            print("There is nothing in the second hand!")
            
    def __str__(self):
        armor_name = self.armor["name"] if self.armor else "No armor"
        main_weapon_name = self.first_weapon["name"] if self.first_weapon else "no main weapon"
        offhand_name = self.offhand["name"] if self.offhand else "No shield/offhand"
        
        return (f"Armor: {armor_name}\n"
                f"Main weapon: {main_weapon_name}\n"
                f"Second weapon/shield: {offhand_name}\n")

class Action:
    # set of actions that can be done in/out of combat
    def __init__ (self, character_manager):
        self.character_manager = character_manager
        
    def reset_turn (self, c):
        
        class_name = c.class_name
        
        c.c_move_points = c.move_points
        c.c_actions = c.actions
        c.c_attacks = 0 # until char spend action
        c.c_bonus_actions = c.bonus_actions
        
        if class_name == "Fighter":
            c.instance_features.c_no_cleave = c.instance_features.no_cleave
        
    def choose_action(self, character):
        # function only for PLAYERS / outside combat
        
        actions_list = ["equip armor", "equip first weapon", "equip offhand", "fight style", "weapon mastery", "unequip"]
            
        # actions_list = ["move", "main attack", "equip armor", "equip body clothing", "equip first weapon", 
        #                 "equip weapon slot 2/shield", "equip weapon slot 3", "equip helmet", "equip googles", 
        #                 "equip boots", "equip belt", "equip glove", "equip ring slot 1", "equip ring slot 2", 
        #                 "equip amulet", "equip bracers", "equip tool sloot", "equip backpack", "equip quiver", 
        #                 "equip instrument", "equip spellbook"]

        while True:

            for action in actions_list:
                print(f"{action} / ", end="")
            
            action_input = input("\nWhat do you want to do? ").lower().strip()
            
            if action_input == "equip armor":
                self.equip_armor (character)
                continue
            elif action_input == "equip first weapon":
                self.equip_first_weapon (character)
                continue
            elif action_input == "equip offhand":
                self.equip_offhand (character)
                continue
            elif action_input == "fight style":
                character.instance_features.choose_fighting_style()
            elif action_input == "weapon mastery" and character.class_name == "Fighter":
                character.instance_features.choose_weapon_mastery()
            elif action_input == "pass":
                break
            elif action_input == "unequip":
                action_input = input("\nWhat do you want to unequip?  ").lower().strip()
                if action_input == "first weapon":
                    character.instance_equipment.first_weapon_unequip()
                elif action_input == "offhand":
                    character.instance_equipment.offhand_unequip()
            else:
                print ("Action not recognized or requirements not met. Type 'pass' to skip.")

    def get_possible_actions(self, character):
        
        actions = []
        
        #check for targets and append all functions that needs target to be > 0
        if self.get_targets(character):
            actions.append("main_attack")
        
        #check if target can move / for now it can always move, later check for conditions
        if self.can_move(character):
            actions.append("move_AI")

        return actions

    def can_move (self, character):
        return True
         
    def move(self, char, pos, mv_pts):
        # method for player move
        old_pos = char.position
        cost = self.character_manager.instance_event_manager.check_move(char, pos)
        
        if mv_pts>=cost:
            # check if pos is occupied (double condition, but can be useful later)
            for obj in self.character_manager.characters.values():
                if obj.position == pos:
                    return False
            self.character_manager.instance_action.attack_of_opportunity(char, old_pos, pos)
            self.character_manager.instance_board.update_player_position(char, pos)
            return cost
            
        else:
            return False
        
        # if not any(c.position == pos for c in self.character_manager.characters.values()):
        #     self.character_manager.instance_event_manager.update_player_position(char, pos)
        # else:
        #     print("That position is already occupied.")

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

            # Determine the opposing team
        opposing_team = (self.character_manager.instance_event_manager.team_two if character.team == 1 else self.character_manager.instance_event_manager.team_one)
        
        list_of_targets = []
        
        for target in opposing_team:
            d = self.character_manager.instance_event_manager.distance (character.position, target.position)
            if character.instance_equipment.first_weapon["reach"] > d:
                list_of_targets.append(target)
        return list_of_targets
    
    def choose_ranged_target (self, character):
        
        # check if char can use ranged attack, get possible targets
        if int(character.instance_equipment.first_weapon["reach"]) > 10:
            targets = self.get_targets_ranged (character)
            print (f"Potential targets to attack: {targets}")
        else:
            return False
        
        target_dict = {}
        
        # check 1st condition - attack modifiers and obstacles along the way   
        if targets:
            max_value = -float('inf')
            for target in targets:
                value = self.character_manager.instance_algorithms.check_path_to_target(character.position, target.position)
                target_dict[target] = value
        
            
            if targets:
                max_value = -float('inf')
                for target in targets:
                    current_value = self.character_manager.instance_algorithms.check_path_to_target(character.position, target.position)
                    if current_value > max_value:
                        max_value = current_value
                        best_target = target
                        print("xxx",best_target)
                
                    return best_target
        else:
            return False
           
    def equip_armor (self, character):
        if character:
            character.instance_equipment.armor_init()
            character.instance_armor_class.calculate_ac()
            
    def equip_first_weapon (self, character):
        if character:
            character.instance_equipment.first_weapon_init()
            character.instance_features.fs_dueling()
    
    def equip_offhand (self, character):
        if character:
            character.instance_equipment.offhand_init()
            character.instance_armor_class.calculate_ac()
            
    def check_advantage (self, character, target):
        # object expected
        if target.instance_hp.status in [-1,0,2]:
            print (f"{character.name} has an advantage against {target.name}")
            return True
        return False
    
    def check_disadvantage (self, character, target):
        # object expected # TODO
        return False
    
    def check_additional_modifiers (self, character, target):
        # return additional modifiers to the attack roll TODO
        return 0
    
    def pret_attack_bonus (self, c, t):
        if not target:
            target = self.character_manager.instance_AI.target
        
        cond = self.character_manager.instance_conditions
        
        if cond.can_graze(c):
            self.graze(c,t)
    
    def pre_attack (self, c, t=None):
        # get target if AI/None
        if not t:
            t = self.character_manager.instance_AI.target
            
        # get instance object if str
        if isinstance(t, str):
            t = self.character_manager.get_character(t)
        
        cond = self.character_manager.instance_conditions
        
        if cond.can_graze(c):
            self.graze(c,t)
        elif cond.can_nick(c):
            self.main_attack(c,t)
            self.second_attack(c,t)
        else:
            self.main_attack(c,t)
    
    def second_attack(self, character, target):
        roll, attack_modifier, attack_roll = self.attack_roll(character, target, 2)
        hit, critical = self.check_hit(roll, attack_roll, target)
        
        c_hit = f" target hit" if hit else " target missed"
        crit = f". Critical Hit!" if critical else ""
        txt = f"Offhand attack! {character.name} attacks {target.name}: {roll} + {attack_modifier} = {attack_roll},{c_hit}{crit}"
        self.character_manager.ins_pgame.add_log(txt)
        print(txt)
        
              # calculate damage, check in damage roll function for any immunities/reductions
        if hit:
            # check reaction (for now: interception)
            red = self.interception_check(target, character)
            
            #roll damage
            dmg = self.damage_roll(character, target, critical, 2, red)
            if red>=dmg: dmg
            else: dmg -= red
            
            #after hit decrease target hp and check status
            target.instance_hp.decrease_target_hp(dmg)
            target.instance_hp.check_status(dmg, critical)
            return True
                
        else:
            print(f"Target missed")
            return False
    
    def main_attack (self, character, target):
        
        # calculate attack roll against target with all modifiers
        roll, attack_modifier, attack_roll = self.attack_roll(character, target, 1)
        
        # check for hit
        hit, critical = self.check_hit(roll, attack_roll, target)
    
        c_hit = f" target hit" if hit else " target missed"
        crit = f". Critical Hit!" if critical else ""
        txt = f"{character.name} attacks {target.name}: {roll} + {attack_modifier} = {attack_roll},{c_hit}{crit}"
        self.character_manager.ins_pgame.add_log(txt)
        print(txt)
        
        # calculate damage, check in damage roll function for any immunities/reductions
        if hit:
            # check reaction (for now: interception)
            red = self.interception_check(target, character)
            
            #roll damage
            dmg = self.damage_roll(character, target, critical, red, 1)
            if red>=dmg: dmg
            else: dmg -= red
            
            #after hit decrease target hp and check status
            target.instance_hp.decrease_target_hp(dmg)
            target.instance_hp.check_status(dmg, critical)
            return True
                
        else:
            print(f"Target missed")
            return False
                
    def attack_roll(self, character, target, w):
        #TODO needs to be calculate only once when variable changes
        
        if w==1:
            character.instance_modifiers.update_attack_mod_w1()
            attack_modifier = character.instance_modifiers.attack_mod_w1
        elif w==2:
            character.instance_modifiers.update_attack_mod_w2()
            attack_modifier = character.instance_modifiers.attack_mod_w2
        
        # check if character has additional bonuses against target
        additional_mod = self.check_additional_modifiers (character, target)
        
        # check for advantage against target
        advantage = self.check_advantage(character, target)
        
        #check for protection
        disadvantage = self.protection_check(target, character)
        
        if advantage:
            roll = max(rd.randint(1, 20), rd.randint(1, 20))
            txt = f"Advantage against target!"
            self.character_manager.ins_pgame.add_log(txt)
        elif disadvantage:
            roll = min(rd.randint(1, 20), rd.randint(1, 20))
            txt = f"Disadvantage against target!"
            self.character_manager.ins_pgame.add_log(txt)
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
    
    def damage_roll(self, character, target, critical, red, w, no_dmg_mod = False):
        # TODO versatile method
        
        # no of dice and type of dice
        if w==1:
            wp_stat = [(character.instance_equipment.first_weapon["no_dice"]),(character.instance_equipment.first_weapon["dice_dmg"])]
        elif w==2:
            wp_stat = [(character.instance_equipment.offhand["no_dice"]),(character.instance_equipment.offhand["dice_dmg"])]
        else:
            raise ValueError ("no wp_stat, no w in previous function")
        
        # TODO check for any extra damage modifiers against target
        if no_dmg_mod == False and w==1:
            add_mod = character.instance_modifiers.hit_mod_w1
        elif no_dmg_mod == False and w==2:
            add_mod = character.instance_modifiers.hit_mod_w2
        else:
            add_mod = 0
        
        # damage roll / check for fighting style great_weapon_fighting
        if not character.instance_features.fs_great_weapon_fighting():
            if critical:
                dmg = sum(rd.randint(1,wp_stat[1]) for _ in range(wp_stat[0] * 2))
            else:
                dmg = sum(rd.randint(1,wp_stat[1]) for _ in range(wp_stat[0]))
        else:
            if critical:
                dmg = sum(3 if roll in [1, 2] else roll for roll in [rd.randint(1, wp_stat[1]) for _ in range(wp_stat[0] * 2)])
            else:
                dmg = sum(3 if roll in [1, 2] else roll for roll in [rd.randint(1, wp_stat[1]) for _ in range(wp_stat[0])])

        dmg_sum = dmg + add_mod
        
        #TODO check target for any resistance
        if red>=dmg_sum: dmg_sum = 0
        else: dmg_sum -= red
        
        
        txt = f"{character.name} hits {target.name} for {dmg} + {add_mod}"
        if red:
            txt += f" - {red}"
        txt += f" = {dmg_sum}"
                
        self.character_manager.ins_pgame.add_log(txt)
        print(txt)
        
        return dmg_sum
    
    def dash(self, c):
        if c.c_actions>0:
            c.c_actions -= 1
            c.c_move_points += c.move_points 
            return True
        else: return False
        
    def spend_action_points(self,c):
        if c.c_actions>0:
            c.c_actions -=1
        
    def spend_attacks_points(self,c):
        print(f"DEBUG: attacks: {c.c_attacks} actions: {c.c_actions}")
        if c.c_attacks==0 and c.c_actions>0:
            c.c_actions -= 1
            c.c_attacks = c.instance_features.extra_atk - 1
        elif c.c_attacks>0:
            c.c_attacks -= 1
        else:
            print(c.c_attacks, c.c_actions )
            raise AttributeError ("No attacks or actions")
        
    def spend_move_pts(self,c):
        cost = self.character_manager.instance_AI.pass_cost
        c.c_move_points -= cost
    
    def attack_of_opportunity(self, c, old_pos, new_pos):

        opposing_team = (self.character_manager.instance_event_manager.team_two if c.team == 1 else self.character_manager.instance_event_manager.team_one)
        
        for e in opposing_team:
            if e.c_reactions>0:
                if self.character_manager.instance_algorithms.check_weapon_reach(e) == 5:
                    if self.character_manager.instance_algorithms.is_adjacent(e.position, old_pos):
                        if not self.character_manager.instance_algorithms.is_adjacent(e.position, new_pos):
                            txt = f"Attack of opportunity! {e.name} attacks {c.name}"
                            self.character_manager.ins_pgame.add_log (txt)
                            self.main_attack(e,c)
                            e.c_reactions -= 1
                if self.character_manager.instance_algorithms.check_weapon_reach(e) == 10:
                    if self.character_manager.instance_algorithms.is_adjacent_10(e.position, old_pos):
                        if not self.character_manager.instance_algorithms.is_adjacent(e.position, new_pos):
                            txt = f"Attack of opportunity! {e.name} attacks {c.name}"
                            self.character_manager.ins_pgame.add_log (txt)
                            self.main_attack(e,c)
                            e.c_reactions -= 1     
                  
    def interception_check (self, target, enemy):
        # TODO check who is around target, maybe add a method later to store this information in Character class (quicker access)
        list = self.character_manager.instance_algorithms.check_char_surround(target)
        reduction = 0
        
        for char in list:
            savior = self.character_manager.get_character(char)
            
            if "interception" in savior.instance_features.fighting_styles and savior.c_reactions>0:
                if savior.instance_equipment.first_weapon is not None or savior.instance_equipment.offhand is not None:
                    reduction += rd.randint(1,10) + savior.instance_modifiers.b_prof_bonus
        
                    txt = f"{savior.name} protects {target.name} from {enemy.name} and reduce {reduction} dmg!"
                    self.character_manager.ins_pgame.add_log(txt)
                    print(txt)
                    savior.c_reactions -=1
        
        return reduction if reduction != 0 else False

    def protection_check (self, target, enemy):
        # TODO check who is around target, maybe add a method later to store this information in Character class (quicker access)
        list = self.character_manager.instance_algorithms.check_char_surround(target)
        try:
            for char in list:
                savior = self.character_manager.get_character(char)
                
                if "protection" in savior.instance_features.fighting_styles and savior.c_reactions>0 and savior.instance_equipment.offhand["name"]=="shield":
            
                        txt = f"{savior.name} tries to disturb {enemy.name} from attacking {target.name}"
                        self.character_manager.ins_pgame.add_log(txt)
                        print(txt)
                        savior.c_reactions -=1
                        return True
        except:
            return False
                
        return 
    
    def use_second_wind(self, c):
        #additional condition for human Player

        if c.instance_fighter.c_second_winds>0 and c.c_bonus_actions>0:
            heal = rd.randint(1,10) + c.level
        
            c.instance_hp.heal_itself(heal)
            
            c.instance_fighter.c_second_winds -= 1
            c.c_bonus_actions -= 1
            
            txt = f"{c.name} uses second wind ability and heal itself for  {heal} points"
            self.character_manager.ins_pgame.add_log(txt)
            print(txt)
        else:
            print("No more uses of second wind!")
    
    def cleave(self, c, t=None):
        print("Start cleave logic")
        c.instance_features.c_no_cleave -= 1
        #check target for AI
        if not t:
            t = self.character_manager.instance_AI.target
        
        # first attack on target
        check_for_cleave = self.main_attack(c,t)
        
        # if hitted - go with cleave logic, pick random target that is adjacent both to first target and attacker
        if check_for_cleave:
            e = self.character_manager.instance_algorithms.check_char_surround(t)
            print("e", e)
            te = [self.character_manager.get_character(ally) for ally in e]
            print("te", te)
            cleave_t = [enemy for enemy in te if self.character_manager.instance_algorithms.is_adjacent(c.position, enemy.position)]
            print("cleave_t", cleave_t)
            t2 = rd.choice(cleave_t) if cleave_t else False
            
            if t2:
                roll, attack_modifier, attack_roll = self.attack_roll(c, t2)
                hit, critical = self.check_hit(roll, attack_roll, t2)
                
                if hit:
                    crit = f". Critical Hit!" if critical else ""
                    cleave = f"Cleave attack! "
                    txt = f"{cleave}{c.name} attacks {t2.name}: {roll} + {attack_modifier} = {attack_roll} Target hit{crit}"
                    self.character_manager.ins_pgame.add_log(txt)
                    print(txt)
                    
                    # check reaction (for now: interception)
                    red = self.interception_check(t2, c)
                    
                    #roll damage
                    dmg = self.damage_roll(c, t2, critical, red, 1, True)
                    if red>=dmg: dmg
                    else: dmg -= red
                    
                    #after hit decrease target hp and check status
                    t2.instance_hp.decrease_target_hp(dmg)
                    status = t2.instance_hp.check_status(dmg, critical)
                    if status == -1:
                        self.character_manager.instance_event_manager.remove_char(t2)
                        print (f"Removing {t2.name} in main attack function from list")
                else:
                    print(f"Target missed")
                    cleave = f"Cleave attack! "
                    txt = f"{cleave}{c.name} attacks {t2.name}: {roll} + {attack_modifier} = {attack_roll} Target miss"
                    self.character_manager.ins_pgame.add_log(txt)
                    print(txt)
                    return 
            else:
                return False                
                
        else:
            return False
    
    def graze(self, c, t=None):
        if not t:
            t = self.character_manager.instance_AI.target
        
        if not self.main_attack(c,t):
            dmg = c.instance_modifiers.get_ability_bonus_w1()
            t.instance_hp.decrease_target_hp(dmg)
            t.instance_hp.check_status(dmg, False)
    
    def push(self,c,t):
    
        c.pos
        t.pos
        
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
    _instance = None  # Zmienna klasy do przechowywania instancji singletonu

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Tworzymy instancję, jeśli nie istnieje
            cls._instance = super(CharacterManager, cls).__new__(cls)
        return cls._instance
    
    def __init__ (self):
        if not hasattr(self, '_initialized'):
            self.instance_action = Action(self)
            self.instance_algorithms = Algorithms(self)
            self.instance_conditions = Conditions(self)
            self.instance_event_manager = EventManager(self)
            self.instance_AI = AI(self)
            self.instance_player = Player(self)
            self.instance_board = Board(self)
            
            self.event_queue = queue.Queue()
            self.ins_pgame = Pgame(self)
            
            self.characters = {}
            self.initiative_order = []
            
        self._initialized = True  
          
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
        
        self.mv_pts = None
        self.actions_pts = None
        
    def player_turn (self, character):
        print(f"\n>>> {character.name} turn <<<\n")
        
        #update board
        self.character_manager.ins_pgame.update_pygame(character)
        
        # reset state of the character
        self.character_manager.instance_action.reset_turn(character)
    
        # run the Pygame interpreter
        self.character_manager.ins_pgame.event_queue.put(('run_game', character))
        
    def interpret (self, char, pos):
        #interpret what user click on Pygame board and do appropriate action
        print (f"DEBUG: interpret function, for {char.name} on pos: {pos}")
        
        if self.character_manager.instance_algorithms.is_enemy (char, pos):
            e = self.character_manager.instance_algorithms.get_char_from_pos (pos)
            if self.valid_enemy (char, e) and self.character_manager.instance_conditions.have_actions_or_attacks(char):
                self.character_manager.instance_action.pre_attack(char, e)
                self.character_manager.instance_action.spend_attacks_points (char)
         
        else:
        # check possibility of movement
            cost = self.character_manager.instance_action.move(char, pos, char.c_move_points)
            if cost != False:
                char.c_move_points -= cost
                
        return False
        
    def is_char (self, pos):
        for obj in self.character_manager.characters.values():
            if obj.position == pos:
                return True
        return False
        ...
    
    def valid_enemy (self, char, enemy):
        #check the distance to the target
        check = self.character_manager.instance_algorithms.distance(char.position, enemy.position)
        
        dist = True if char.instance_equipment.first_weapon["reach"]>check and char.instance_equipment.first_weapon["reach"]>10 else False
        
        if enemy.instance_hp.status>-1 and (self.character_manager.instance_algorithms.is_adjacent_reach(char, enemy) or dist==True):
            return True
        else:
            return False

class Node:
    def __init__(self, children = None):
        self.children = children if children else []
    
    def add_child(self, child):
        self.children.append(child)
    
    def run():
        pass

class Selector(Node):
    def run(self):
        for child in self.children:
            if child.run():
                return True
        return False
    
class Sequence(Node):
    def run(self):
        for child in self.children:
            if not child.run():
                return False
        return True

class ConditionNode(Node):
    def __init__(self, condition_fn, *args):
        self.condition_fn = condition_fn
        self.args = args
    
    def run(self):
        # Wywołujemy condition_fn z argumentami
        result = self.condition_fn(*self.args)
        print(f"Condition {self.condition_fn.__name__} returned {result}")
        return result
    
class ActionNode(Node):
    
    def __init__(self, action_fn, *args):
        self.action_fn = action_fn
        self.args = args
        self.character_manager = CharacterManager()

    def run(self):
        self.action_fn(*self.args)
        print(f"Action {self.action_fn.__name__} executed.")
        
        if self.character_manager.ins_pgame:
            self.character_manager.ins_pgame.main_loop()

        time.sleep(0.5)
        return True
         
class Conditions:
    def __init__ (self, character_manager):
        self.character_manager = character_manager
    
    def surr_safe(self,c):
    # TODO implement a full method that is mutually exclusive with two other
        if c.instance_hp.get_current_hp_per()>0.4:
            return True
        else: return False
    
    def surr_threaten(self,c):
        # TODO implement a full method that is mutually exclusive with two other
        return False
    
    def surr_danger(self,c):
        # TODO implement a full method that is mutually exclusive with two other
        if c.instance_hp.get_current_hp_per()<0.4:
            return True
        else: return False
    
    def melee(self,c):
        return True if c.behaviour == "melee" else False
    
    def ranged(self,c):
         return True if c.behaviour == "ranged" and c.instance_equipment.first_weapon["reach"]>10 else False
    
    def pick_target(self, c):
        
        # TODO think if this function needs to return False at some point
        print("pick target function")
        final_weight = {}
        self.alg = self.character_manager.instance_algorithms
        
        opposing_team = (self.character_manager.instance_event_manager.team_two if c.team == 1 else self.character_manager.instance_event_manager.team_one)
        
        if not opposing_team: return False
        
        hp_dict = self.alg.check_hp (opposing_team) # check HP score
        hit_dict = self.alg.check_hit_prob(c, opposing_team) # check how hard is to hit the target
        dis_dict = self.alg.check_dist_melee (opposing_team, c) # check cost move to target from char position
        threat_dict = self.alg.check_threat (c, opposing_team) # check threat level
        
        print(f"DEBUG: HP: { {character.name: score for character, score in hp_dict.items()} } HIT: { {character.name: score for character, score in hit_dict.items()} } distance: { {character.name: score for character, score in dis_dict.items()} } threat: { {character.name: score for character, score in threat_dict.items()} }")
        
        for enemy in hp_dict.keys():
            hp_score = hp_dict[enemy] * 0.20
            hit_score = hit_dict[enemy] * 0.20
            threat_score = threat_dict[enemy] * 0.25
            dis_score = dis_dict[enemy] * 0.35

            total_score = (hp_score + hit_score + threat_score + dis_score) / 4

            final_weight[enemy] = total_score

        target = max(final_weight, key=final_weight.get)
        print(f"Picked target (based on weight) is: {target.name}")
        
        # update target information in AI class, from what other function can draw
        self.character_manager.instance_AI.target = target
        return True
    
    def pick_target_ranged(self, c):
        print("Pick target - ranged behaviour")
        final_weight = {}
        self.alg = self.character_manager.instance_algorithms
        
        opposing_team = (self.character_manager.instance_event_manager.team_two if c.team == 1 else self.character_manager.instance_event_manager.team_one)
        
        if not opposing_team: return False
        
        #all normalized to max 100
        hit_dict = self.alg.check_hit_prob(c, opposing_team) # check how hard is to hit the target
        hp_dict = self.alg.check_hp (opposing_team) # check % of HP
        dis_dict = self.alg.check_dist_melee (opposing_team, c) # check cost move to target from char position
        threat_dict = self.alg.check_threat (c, opposing_team) # check threat level
        
        # print(f"DEBUG: HP: { {character.name: score for character, score in hp_dict.items()} } AC: { {character.name: score for character, score in ac_dict.items()} } distance: { {character.name: score for character, score in dis_dict.items()} } threat: { {character.name: score for character, score in threat_dict.items()} }")
        
        for enemy in hp_dict.keys():
            hp_score = hp_dict[enemy] * 0.50
            hit_score = hit_dict[enemy] * 0.20
            threat_score = threat_dict[enemy] * 0.10
            dis_score = dis_dict[enemy] * 0.20

            total_score = (hp_score + hit_score + threat_score + dis_score) / 4

            final_weight[enemy] = total_score

        target = max(final_weight, key=final_weight.get)
        print(f"Picked target (based on weight) is: {target.name}")
        
        # update target information in AI class, from what other function can draw
        self.character_manager.instance_AI.target = target
        return True
    
    def have_actions_or_attacks(self,c):
        return True if c.c_actions>0 or c.c_attacks>0 else False
    
    def have_actions(self,c):
        return True if c.c_actions>0 else False
    
    def have_mv_pts(self,c):
        return True if c.c_move_points>4 else False
    
    def target_adj(self,c, t=None):
        if not t:
            t = self.character_manager.instance_AI.target
        tpos = t.position
        cpos = c.position
        x, y = cpos
        tx, ty = tpos
        return abs(x - tx) <= 1 and abs(y - ty) <= 1 and cpos != tpos
    
    def target_in_sight(self,c):
        # can move within actual mv_points
        t = self.character_manager.instance_AI.target
        mv = c.c_move_points
        cost = self.character_manager.instance_algorithms.check_target_cost (c, t.position)
        
        return True if mv>=cost else False

    def target_outof_sight(self,c):
        # can move within actual mv_points
        t = self.character_manager.instance_AI.target
        mv = c.c_move_points
        cost = self.character_manager.instance_algorithms.check_target_cost (c, t.position)
        
        return True if mv<=cost else False
    
    def can_cleave(self,c, t=None):
        if not t:
            t = self.character_manager.instance_AI.target
        
        c1 = True if c.instance_equipment.first_weapon["mastery"]=="cleave" else False
        c2 = True if c.instance_equipment.first_weapon["name"].title() in c.instance_features.weapon_mastery else False
        c3 = True if c.instance_features.c_no_cleave>0 else False
        c4 = True if self.character_manager.instance_algorithms.is_adjacent_reach(c,t) else False
        
        return c1 and c2 and c3 and c4
    
    def can_secondwind(self, c):
        return True if c.instance_fighter.second_winds>0 else False
    
    def can_graze(self, c):
        return (
            (c.instance_equipment.first_weapon.get("mastery") == "graze" and c.instance_equipment.first_weapon.get("name", "").title() in c.instance_features.weapon_mastery) or
            (c.instance_equipment.offhand.get("mastery") == "graze" and c.instance_equipment.offhand.get("name", "").title() in c.instance_features.weapon_mastery)
    )
    
    def can_bonus_attack(self, c):
        x = c.instance_equipment.first_weapon.get("lh") == "light"
        y = c.instance_equipment.offhand.get("lh") == "light"
        z = (c.instance_equipment.first_weapon.get("mastery") != "nick" and c.b_actions>0)
        
        return True if (x and y) and (c.bonus_actions>0) else False
    
    def can_nick(self, c):
        x = c.instance_equipment.first_weapon.get("lh") == "light"
        y = c.instance_equipment.offhand.get("lh") == "light"
        z = (c.instance_equipment.first_weapon.get("mastery") == "nick" and c.c_bonus_actions>0)
        
        return True if (x and y) and (z) else False

    def can_push(self,c,t):
        x = c.instance_equipment.first_weapon["mastery"] == "push"
        y = self.character_manager.instance_algorithms.is_adjacent_reach(c,t)
        s = t.size in ["large", "normal", "small", "tiny"]
        
        return True if (x and y and s) else False
    
class AI:
    def __init__ (self, character_manager):
        self.character_manager = character_manager
        
        self.target = None
        self.pass_cost = 0

    
    def AI_turn (self, c):
        print(f"\nAI {c.name} move")
        
        self.character_manager.ins_pgame.update_pygame (c)
        time.sleep(0.5)
        
        self.character_manager.instance_action.reset_turn(c)
        
        self.con = self.character_manager.instance_conditions
        self.act = self.character_manager.instance_action
        self.alg = self.character_manager.instance_algorithms
        
        self.target = None  
        
        bt =  Selector([
                Sequence([ # melee behaviour
                    ConditionNode(self.con.melee, c),
                    Selector([
                        Sequence([ # safe
                            ConditionNode(self.con.surr_safe, c),
                            ConditionNode(self.con.pick_target, c),
                            Selector([
                                Sequence([ # enemy is near
                                    ConditionNode(self.con.target_adj,c),
                                    ConditionNode(self.con.can_cleave, c),
                                    self.cleave_attack_bh(c),
                                    #self.main_attack_bh(c),
                                    ]),
                                Sequence([ # enemy is within standard move points
                                    ConditionNode(self.con.target_in_sight,c), 
                                    ConditionNode(self.con.have_actions_or_attacks, c),
                                    ConditionNode(self.con.have_mv_pts, c),
                                    ActionNode(self.alg.AI_move, c),
                                    ActionNode(self.act.spend_move_pts, c),
                                    self.main_attack_bh(c)
                                    ]),
                                Sequence([ # enemy is within dash move points
                                    ConditionNode(self.con.have_mv_pts, c),
                                    ConditionNode(self.con.target_outof_sight,c), 
                                    ActionNode(self.act.dash, c),
                                    ActionNode(self.alg.AI_move, c),
                                    ActionNode(self.act.spend_move_pts, c),
                                    ConditionNode(self.con.target_adj,c),
                                    self.main_attack_bh(c)
                                    ])
                                ])
                            ]),
                        Sequence([ # threaten
                                ConditionNode(self.con.surr_threaten, c)
                                ]),
                        Sequence([ # danger
                                ConditionNode(self.con.surr_danger, c),
                                ConditionNode(self.con.have_actions, c),
                                ActionNode(self.act.use_second_wind,c),
                                ActionNode(self.act.spend_action_points,c)
                                ])      
                            ]),
                        ]),
                Sequence([ # TODO ranged behaviour
                    ConditionNode(self.con.ranged, c), # check for behaviour and weapon
                    ActionNode(self.con.pick_target, c)
                    ])
            ])
        
        while bt.run():
            time.sleep(1)
            ...

    def main_attack_bh(self, c):
        return Sequence([
                    ConditionNode(self.con.have_actions_or_attacks, c),
                    ActionNode(self.act.pre_attack, c),
                    ActionNode(self.act.spend_attacks_points, c)
                    ])
    
    def cleave_attack_bh(self, c):
        return Sequence([
                    ConditionNode(self.con.have_actions_or_attacks, c),
                    ActionNode(self.act.cleave, c),
                    ActionNode(self.act.spend_attacks_points, c)
        ])
    
class Melee_behaviour():
    def __init__ (self, AIclass):
        self.AIclass = AIclass
        
    def begin(self, character):
        print(f"\n>>> {character.name} turn <<<\n")
        
        #update pygame info
        self.AIclass.update_char_pygame(character)
        
        character.c_move_points = character.move_points
        character.c_actions = character.actions
        character.c_attacks = 0 # until chare spend action 
        
        pygame.display.update()
        time.sleep (0.2)
        
        # decision tree
        
        
        while self.actions_pts>0:
            #try to attack target without move
            if self.AIclass.character_manager.instance_event_manager.is_adjacent (character.position, target.position):
                print("Attempting to attacking target from current position")
                self.AIclass.character_manager.instance_action.main_attack (character, target)
                self.actions_pts -= 1
                break
            
            #check distance to target 
            dist = self.AIclass.character_manager.instance_algorithms.check_target_cost (character, target.position)
            print (f"Distance to target is: {dist} : {character.name} to {target.name}")
            
            # if the target is within move distance: move&attack

            if character.c_move_points>=dist:
                cost = self.AIclass.move_AI (character, target, character.c_move_points)
                character.c_move_points -= cost
                self.AIclass.character_manager.instance_action.main_attack (character, target)
                self.actions_pts -= 1
                break
            
            #using dash to reach the targets if all other fails
            else:
                # dash mode
                self.mv_pts *= 2
                print("Moving to target, using dash")
                cost = self.AIclass.move_AI (character, target, self.mv_pts)
                self.mv_pts -= cost
                self.actions_pts -= 1
                break
            
        print (f"End of turn info: mov points: {self.mv_pts}, action pts: {self.actions_pts}") 
        
class Ranged_behaviour():
    def __init__ (self, AIclass):
        self.AIclass = AIclass

    def begin(self, character):
        print(f"\n>>> {character.name} turn <<<\n")
        
        #update Pygame info
        self.AIclass.update_char_pygame(character)
        
        final_weight = {}
        
        # check for enemy in reach distance (also check for char weapon)
        target = self.AIclass.character_manager.instance_action.choose_ranged_target (character)
        print ("Ranged behaviour")
        
     
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
        
        self.char = None # active char turn
    
    def reset_game (self):
        for c in self.character_manager.characters.values():
            if c.class_name == "Fighter":
                c.instance_fighter.c_second_winds = c.instance_fighter.second_winds
    
    def reactions_manage (self):
        for c in self.character_manager.characters.values():
            c.c_reactions = c.reactions
        
    def is_adjacent (self, pos, target):
        #check if pos is adjacent to target, 5 feet, 8 tiles
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

    def check_move(self, character, target_pos):
        # return cost of reaching target position
        
        min_pos = None
        self.path_queue = {}
        # for initial position, total dist = dist
        self.visited[character.position] = (0, self.distance(character.position, target_pos), self.distance(character.position, target_pos), None)
        
        while True:
            min_cost_pos = 0
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
                 
            # #checking if position is beyond character ability to move /// PLAYER
            # if move_points<min_cost_pos and is_Player:
            #     print("Target out of reach")
            #     self.path_queue.clear()
            #     self.visited.clear()
            #     return False
            
            # checking if pos is at target destination /// PLAYER and AI
            if min_pos == target_pos: #and is_Player and move_points>=min_cost_pos:
                print("Character reached destination")
                self.path_queue.clear()
                self.visited.clear()
                print("1", min_cost_pos)
                return int(min_cost_pos)
            
            #removing to be checked node from queue
            self.path_queue.pop(min_pos, None)
            
            # adding to be checked node to visited dict
            print("2", min_pos, min_cost_pos, min_distance, min_cost, min_parent)
            self.visited[min_pos] = (min_cost_pos, min_distance, min_cost, min_parent)
            
            #calculating position around new position
            new_positions = self.calc_path(min_pos, target_pos, min_cost_pos)

            # adding new node to be checked if cost is lower
            for pos, vals in new_positions.items():
                if pos not in self.path_queue or vals[2] < self.path_queue[pos][2]:
                    self.path_queue[pos] = vals
    
    def AI_check_move(self, character, target_pos, move_points, is_Player = False):
        print(f"DEBUG: Char {character.position} to target {target_pos} movepoints: {move_points}")
        #initialize variable
        
        min_pos = None
        adjacent_results = {}
        self.path_queue = {}
        
        # for initial position, total dist = dist
        self.visited[character.position] = (0, self.distance(character.position, target_pos), self.distance(character.position, target_pos), None)
        
        # list of all possible (empty) adjacent square around target, goal is to calculate all space around them
        target_neighbors = self.character_manager.instance_board.check_surrounding_occupied(target_pos)
            
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
        
        #checking if position is beyond character ability to move AI /// outside loop

        #adding last node to visited
        self.visited[min_pos] = (min_cost_pos, min_distance, min_cost, min_parent)
        # print(f"Adjacent result: {adjacent_results}")
        
        # IMPORTANT! choosing best position around target path to be processed
        min_pos = min(adjacent_results, key=lambda pos: adjacent_results[pos][0])
        # print(f"Best: {adjacent_results}")
        
        # print(f"DEBUG: movepoints {move_points} cost pos {min_cost_pos}")
        
        path = {}
        
        if (move_points >= min_cost_pos) and is_Player == False:
            print(f"DEBUG: target within reach, returning position to move: {min_pos}")
            self.path_queue.clear()
            self.visited.clear()
            sorted_path = self.sort_path(path)
            
            return min_pos, min_cost_pos
        
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
            
            return closest_position, closest_cost
    
    def sort_path (self, path):
        sorted_path = sorted(path.items(), key=lambda item: item[1][0])  # item[1][0] is the cost value
        
        # print("Sorted Path from Lowest to Highest Cost:")
        for pos, (cost, distance, total_cost, parent) in sorted_path:
            print(f"Position: {pos}, Cost: {cost}, Distance: {distance} Total distance: {total_cost} Parent: {parent}")
        # print(f" Path found: {sorted_path}")
        
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
        self.control_team_one = False
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
            self.team_one = [self.character_manager.get_character(member.strip().title()) for member in input("Team one, choose your team. Additional characters can be added after comma: ").split(",")]

            for character in self.character_manager.characters.values():
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
        print("remove",team)
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
        
        AI = False # if AI true then teams are automatically assigned
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
        
        #initialize Pygame
        self.character_manager.ins_pgame.initialize_screen()
        
        #start combat
        print(f"\nCombat started.")

        self.turn()
        
    def turn(self):
        
        no_team_one = 1
        no_team_two = 1
        round = 1
        
        self.reset_game()
        
        print("turn before while")
        
        while no_team_one > 0 and no_team_two > 0: 
            
            print(f"\n\n>>>>>> ROUND {round} <<<<<<")
            
            #reset state of reactions
            self.reactions_manage()
            
            no_of_char = len(self.character_manager.characters)
            self.turn_index = 0
            
            for _ in range(no_of_char):
        
                no_team_one = len(self.team_two)
                no_team_two = len(self.team_one)

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
                print(f"DEBUG: current char: {character_name}")
                status = current_character.instance_hp.check_status(0,0)
                if status == -1:
                    self.character_manager.instance_event_manager.remove_char(current_character)
                    print (f"Removing current character {current_character.name} in turn function")
                
                if status in [-1,0,2]:
                    self.turn_index += 1
                    continue
                
                self.char = current_character

                #refresh pygame window
                self.character_manager.ins_pgame.main_loop()
                
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
        self.size = 35
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
        # main function for updating char position - within board and in Character instance
        print(f"{character.name} move from {character.position} to {new_position}")
        if character.position != new_position:
            txt = txt = f"{character.name} moves from {character.position} to {new_position}"
            self.character_manager.ins_pgame.add_log (txt)
        
        #return old position state to original state
        old_position = character.position
        if old_position:
            old_x, old_y = old_position
            self.p_board[old_y][old_x] = self.i_board[old_y][old_x]
        
        new_x, new_y = new_position
        self.p_board[new_y][new_x] = character.name[:2]
        character.position = new_position
        
        # print("Current board state:")
        # for row in self.p_board:
        #     print(" ".join(row))
        # print("\n")
        
        if character.position != new_position:
            self.character_manager.ins_pgame.draw_board()
            
        try:
            self.character_manager.ins_pgame.update_pygame(character)
        except:
            pass
        
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
        
        self.path_queue = {}
        self.visited = {}    
    
    def is_char (self, pos):
        for obj in self.character_manager.characters.values():
            if obj.position == pos:
                return True
        return False
    
    def is_enemy (self, char, pos):
        
        opposing_team = (self.character_manager.instance_event_manager.team_two if char.team == 1 else self.character_manager.instance_event_manager.team_one)
        
        for obj in opposing_team:
            if obj.position == pos:
                return True
        return False
    
    def get_char_from_pos (self, pos):
        for c in self.character_manager.characters.values():
            if c.position == pos:
                return c
    
    def calc_pts_alongtheway (self, pos_start, pos_end):
        # returns squares that are intersected by line from start to end pos (straight ranged attack line)
        x1,y1 = pos_start
        x2,y2 = pos_end
        grid_size = 1
        min_overlap=0.1
        
        path = set()
        line = LineString([(x1 + 0.5, y1 + 0.5), (x2 + 0.5, y2 + 0.5)])

        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                cell = box(x, y, x + grid_size, y + grid_size)
                intersection = line.intersection(cell)

                if not intersection.is_empty and line.intersection(cell).length >= min_overlap:
                    path.add((x, y))
        path = [pos for pos in path if pos not in (pos_start, pos_end)]
        return list(path)
    
    def check_path_to_target (self, pos_start, pos_end):
        #iterate through the path and check conditions along the way, if it is obstructed then return diff level (for AI purposes)
        path = self.calc_pts_alongtheway (pos_start, pos_end)
        diff = 0
        path_len = len(path)
        dict = {}
        
        # check for any char in the way
        for char in self.character_manager.characters.values():
            if char.position in path:
                diff += 1
        
        # check for any map obstacle in the way (tree in v1.0)
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
    
    def is_adjacent_reach (self, c, t):
        print(c)
        reach = c.instance_equipment.first_weapon["reach"]
        c_pos = c.position
        t_pos = t.position
        if reach ==5:
            return self.is_adjacent (c_pos, t_pos)
        elif reach == 10:
            return self.is_adjacent_10 (c_pos, t_pos)
        else:
            print("Out of reach or ranged")
            return False
    
    def is_adjacent (self, pos, target):
        #check if pos is adjacent to target
        x, y = pos
        tx, ty = target
        return abs(x - tx) <= 1 and abs(y - ty) <= 1 and pos != target
    
    def is_adjacent_10 (self, pos, target):
        #check if pos is adjacent to target, 10 feet, 24 tiles
        x, y = pos
        tx, ty = target
        distance_x = abs(x - tx)
        distance_y = abs(y - ty)

        return 1 <= distance_x <= 2 and 1 <= distance_y <= 2 or (distance_x <= 2 and distance_y <= 2 and pos != target)
        
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

    def get_adjacent_path (self, character, target_pos, target_neighbors):
        
        adjacent_results = {}
        min_pos = None
        
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
            
            # checking if founded position is in neighbors, if True, removing neighbors from the list
            if min_pos in target_neighbors:
                adjacent_results[min_pos] = self.path_queue[min_pos]
                target_neighbors.remove(min_pos)
        
            if not target_neighbors:
                self.visited[min_pos] = (min_cost_pos, min_distance, min_cost, min_parent)
                return adjacent_results
            
            #removing to be checked node from queue
            self.path_queue.pop(min_pos, None)
            
            # adding to be checked node to visited dict
            self.visited[min_pos] = (min_cost_pos, min_distance, min_cost, min_parent)
            
            #calculating position around new position
            new_positions = self.calc_path(min_pos, target_pos, min_cost_pos)

            # adding new node to be checked if cost is lower
            for pos, vals in new_positions.items():
                if pos not in self.path_queue or vals[2] < self.path_queue[pos][2]:
                    self.path_queue[pos] = vals
    
    def check_target_cost (self, character, target_pos):
        
        #clearing path / initialize
        self.path_queue = {}
        self.visited = {}
        
        # for initial position, total dist = dist
        self.visited[character.position] = (0, self.distance(character.position, target_pos), self.distance(character.position, target_pos), None)
        
        # list of all possible (empty) adjacent square around target, goal is to calculate all space around them
        target_neighbors = self.character_manager.instance_board.check_surrounding_occupied(target_pos)
            
        adjacent_results = self.get_adjacent_path (character, target_pos, target_neighbors)
        
        # IMPORTANT! looking for quickest path to target and returning its cost
        min_cost = min(adjacent_results, key=lambda pos: adjacent_results[pos][0])
        min_cost_pos = adjacent_results[min_cost][0]
        
        return min_cost_pos
    
    def sort_path (self, path):
        sorted_path = sorted(path.items(), key=lambda item: item[1][0])  # item[1][0] is the cost value
        
        print("Sorted Path from Lowest to Highest Cost:")
        for pos, (cost, distance, total_cost, parent) in sorted_path:
            print(f"Position: {pos}, Cost: {cost}, Distance: {distance} Total distance: {total_cost} Parent: {parent}")
        print(f" Path found: {sorted_path}")
        
        return sorted_path
    
    def check_hp (self, e_team):
        score_dict = {}
        for enemy in e_team:
            c_hp = enemy.instance_hp.current_hp
            m_hp = enemy.instance_hp.base_hp
            ratio = c_hp / m_hp
            score = 100 - (ratio * 100)
            score_dict[enemy] = score
            
        max_value = max(score_dict.values())
        if max_value > 0:
            normalized_dict = {e: (x / max_value) * 100 for e, x in score_dict.items()}
        else:
            normalized_dict = score_dict  

        return normalized_dict
    
    def check_ac(self, e_team):
        score_dict = {}

        ac_min = min(enemy.instance_armor_class.armor_class for enemy in e_team)
        ac_max = max(enemy.instance_armor_class.armor_class for enemy in e_team)

        for enemy in e_team:
            ac = enemy.instance_armor_class.armor_class
            # Unikamy dzielenia przez zero, gdy wszyscy mają ten sam AC
            if ac_max == ac_min:
                score = 100  # Jeśli wszyscy mają ten sam AC, wszyscy są "łatwym" celem
            else:
                score = (1 - (ac - ac_min) / (ac_max - ac_min)) * 100  # Odwracamy skalowanie, aby mniejsze AC dawało większy wynik
            score_dict[enemy] = max(0, min(score, 100))  # upewniamy się, że wartości są w zakresie 0-100

        return score_dict
    
    def check_threat(self, c, e_team):
        
        score_dict = {}

        for enemy in e_team:
            reach = enemy.instance_equipment.first_weapon["reach"]
            score_1 = 25 if reach>5 else 50 if reach>10 else 0
            
            lvl = enemy.level
            score_3 = lvl * 5 # 5-100 pts
                
            score_4 = 100 if enemy.instance_hp.status==1 else 0
            
            score_sum = (score_1+score_3+score_4) / 4
            
            score_dict[enemy] = score_sum
            
        max_value = max(score_dict.values())
        normalized_dict = {e: (x / max_value) * 100 for e, x in score_dict.items()}
        
        return normalized_dict
    
    def check_dist_melee (self, e_team, char):
        
        score_dict = {}
        move_dict = {}
        
        for enemy in e_team:
            move_pts = self.check_target_cost (char, enemy.position)
            move_dict[enemy] = move_pts
        
        m_pts = char.move_points 
    
        for enemy, move_pts in move_dict.items():
            if move_pts <= m_pts:
                score_dict[enemy] = 100
            elif m_pts < move_pts <= m_pts * 2:
                score_dict[enemy] = 40
            else:
                score_dict[enemy] = 0
        
        max_value = max(score_dict.values())
        
        if max_value > 0:
            normalized_dict = {e: (x / max_value) * 100 for e, x in score_dict.items()}
        else:
            normalized_dict = score_dict  

        return normalized_dict   
    
    def AI_move(self, c, t=None, mv_pts=None):
        # move towards target
        t = self.character_manager.instance_AI.target
        mv_pts = c.c_move_points
        
        print(f"DEBUG: target: {t.name}, mvpoints: {mv_pts}, char: {c.name} ")
        old_pos = c.position
        
        new_pos, pts_cost = self.character_manager.instance_event_manager.AI_check_move(c, t.position, mv_pts, False)
        self.character_manager.instance_action.attack_of_opportunity(c, old_pos, new_pos)
        
        self.character_manager.instance_board.update_player_position(c, new_pos)
        self.character_manager.instance_AI.pass_cost = pts_cost
        return pts_cost
    
    def check_weapon_reach(self, c):
        reach = c.instance_equipment.first_weapon["reach"]
        return reach if reach in [5,10] else False
    
    def check_char_surround(self, character):
        # method for checking enemies
        
        board = self.character_manager.instance_board.p_board
        
        try:
            x, y = character.position
        except AttributeError:
            x, y = character
        
        team = (self.character_manager.instance_event_manager.team_two 
                        if character.team == 2 else self.character_manager.instance_event_manager.team_one)
        
        surrounding_characters = []
        
        moves = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),          (1, 0),
            (-1, 1),  (0, 1),  (1, 1) 
        ]
        
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy

            if 0 <= new_x < len(board[0]) and 0 <= new_y < len(board):
                occupant = board[new_y][new_x]
                for opponent in team:
                    if occupant == opponent.name[:2].title():
                        surrounding_characters.append(opponent.name)

        return surrounding_characters
    
    def check_char_surround_allies(self, character):
        # method for checking allies adjacent to char
        
        board = self.character_manager.instance_board.p_board
        
        try:
            x, y = character.position
        except AttributeError:
            x, y = character
        
        team = (self.character_manager.instance_event_manager.team_two 
                        if character.team == 1 else self.character_manager.instance_event_manager.team_one)
        print("team around char", team)
        
        surrounding_characters = []
        
        moves = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),          (1, 0),
            (-1, 1),  (0, 1),  (1, 1) 
        ]
        
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy

            if 0 <= new_x < len(board[0]) and 0 <= new_y < len(board):
                occupant = board[new_y][new_x]
                for opponent in team:
                    if occupant == opponent.name[:2].title():
                        surrounding_characters.append(opponent.name)

        return surrounding_characters
    
    def check_hit_possibility(self, c, e):
        mod = c.instance_modifiers.attack_mod_w1
        adv = self.character_manager.instance_action.check_advantage(c, e)
        dis = self.character_manager.instance_action.check_disadvantage(c, e)
        ac = e.instance_armor_class.armor_class
        
        needed_roll = max(ac - mod, 1)
        
        if needed_roll >= 21:
            return 5.0
        elif needed_roll <= 1:
            return 95.0
        
        # if normal roll
        if not adv and not dis:
            probability = (21 - needed_roll) / 20
    
        elif adv:
            probability = ((21 - needed_roll) ** 2) / 400
        
        elif dis:
            probability = 1 - (((needed_roll - 1) ** 2) / 400)
        
        print(round(probability * 100, 2))
        return round(probability * 100, 2)
    
    def check_hit_prob (self, c, opposing_team):
        
        score_dict = {}
        for e in opposing_team:
            x = self.check_hit_possibility(c,e)
            score_dict[e] = x
        
        max_value = max(score_dict.values())
        normalized_dict = {e: (x / max_value) * 100 for e, x in score_dict.items()}
        
        return normalized_dict


class MainMenu:
    def __init__ (self):
        self.character_manager = CharacterManager()
        self.event_queue = queue.Queue()  # Kolejka do komunikacji z wątkiem Pygame
    
    def display_menu(self):
        while True:
            print("\n-- MAIN MENU --")
            print("1. Create a new character")
            print("2. Auto generate new character")
            print("3. Load an existing character")
            print("4. Start game")
            print("5. Save current character")
            print("6. Display loaded character")
            print("7. Exit")
            
            # print(f"Current statistics:")
            # for char in self.character_manager.characters.values():
            #     print(f"\n{char.name}:\nWins:{char.wins}  Defeat: {char.defeats}  Games: {char.games}")

            choice = input("Choose an option: ")


            if choice == '1':
                self.create_character()
            elif choice == '2':
                self.auto_gen_character()
            elif choice == '3':
                self.load_character()
            elif choice == '4':
                self.start_game()
                #method for infinite games
                # n = 0
                # while n<20:
                #     self.start_game()
                #     n += 1
            elif choice == '5':
                self.save_character()
            elif choice == '6':
                self.display_loaded()
            elif choice == '7':
                print("Exiting game...")
                break
            else:
                print("Invalid choice, try again.")
    
    def create_character(self):
        name = input("Enter the name of new character: ")
        new_character = Character.create_new_character(name)
        self.character_manager.add_character(new_character)
        print(f"Character {name} created successfully!")
    
    def auto_gen_character(self):
        name = input("Enter the name of new character: ")
        new_character = Character.create_new_auto_character(name)
        self.character_manager.add_character(new_character)
        print(f"Character {name} created successfully!")
        
    def load_character(self):
        #TESTING MODE
        characters_to_load = ["Orc", "Aragorn", "Gimli", "Legolas","Uruk"]  # Lista nazw postaci do załadowania
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

class Pgame:
    def __init__(self, character_manager) -> None:
        
        self.running_main = True
        self.running_player = False
        
        self.character_manager = character_manager
        self.character = None
        self.event_queue = queue.Queue()  # Kolejka do komunikacji między wątkami
        self.refresh = True
        
        self.BS = 35 # TODO, need to copy from self.character_manager.instance_board.size
        self.tile_size = 30
        
        self.screen = None
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        
        # interface panel
        self.panel_width = 300
        self.frame_i = 20
        self.panel_height = None
        
        # background
        self.background = pygame.image.load("DnD_game/img/wall.png")
        self.background = pygame.transform.scale(self.background, (1500,1200))
        self.x_i = None
        self.y_i = None
        
        # panel background
        self.panel_bg = pygame.image.load("DnD_game/img/interface.jpg")
        self.panel_bg = pygame.transform.scale(self.panel_bg, (self.panel_width, self.tile_size * self.BS ))
        
        # board dimensions
        self.b_width = self.tile_size * self.BS
        self.b_height = self.tile_size * self.BS
        
        self.screen_width, self.screen_height = None, None
        
        # Wczytaj obraz tła panelu

        self.current_popup_pos = None
        self.current_popup_text = None

        self.colors = {
            "player": (0, 0, 255),  # Gracz - niebieski
            "enemy": (255, 0, 0),   # Wróg - czerwony
            "grass": (144, 238, 144),  # Jasny zielony dla trawy
            "forest": (34, 139, 34),   # Ciemny zielony dla lasu
            "mountain": (169, 169, 169),  # Szary dla gór
        }
        
        # logs
        self.logs = []  # Lista przechowująca logi (ostatnie 100 wpisów)
        self.max_logs = 100  # Maksymalna liczba przechowywanych wpisów
        self.log_scroll = 0  # Pozycja przewijania
        self.line_height = 20  # Wysokość jednej linii tekstu w logach
        
        #buttons
        self.button_pos = {}
        self.button_action = {}
    
    def initialize_screen(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1500, 1200))
        pygame.display.set_caption("Board Visualization")

        self.draw_board()
        self.draw_interface()
        
        self.main_loop()
        
    def update_pygame (self, char):
        
        self.character = char
        self.draw_turn_info()
        self.draw_board()
        self.draw_info()
        self.refresh = True

    def draw_board(self):
        self.screen.blit(self.background, (0, 0))
        self.screen_width, self.screen_height = self.screen.get_size()
    
        # Obliczenie offsetu (przesunięcia) w celu wyśrodkowania planszy
        screen_m_width = self.screen_width - self.panel_width
        self.offset_x = (screen_m_width - self.b_width) // 2
        self.offset_y = (self.screen_height - self.b_height) // 8
        
        frame_rect = pygame.Rect(self.offset_x - 5, self.offset_y - 5, self.b_width + 10, self.b_height + 10)  # Ramka wokół planszy
        pygame.draw.rect(self.screen, self.black, frame_rect, 4)  # 5 to grubość ramki
        
        for y in range(self.BS):
            for x in range(self.BS):
                rect = pygame.Rect(x * self.tile_size + self.offset_x, y * self.tile_size + self.offset_y, self.tile_size, self.tile_size)
                
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
            player_rect = pygame.Rect(x * self.tile_size + self.offset_x, y * self.tile_size + self.offset_y, self.tile_size, self.tile_size)
            pygame.draw.rect(self.screen, color, player_rect)
            
            # Dodajemy inicjały na planszy
            font = pygame.font.Font(None, 18)
            initials = font.render(character.name[:2], True, self.white)
            self.screen.blit(initials, (x * self.tile_size + 5 + self.offset_x, y * self.tile_size + 5 + self.offset_y))
        
        self.draw_interface()
        pygame.display.update()  # Aktualizacja całego ekranu

    def draw_interface(self):
        # auto fit method, no variables
                
        self.x_i = self.screen_width - self.panel_width - self.frame_i
        self.y_i = (self.screen_height - self.b_height) // 8
        
        # background
        panel_rect = pygame.Rect(self.x_i, self.y_i, self.panel_width, self.b_height)
        self.screen.blit(self.panel_bg, panel_rect)
        
        # frame around background
        self.frame_i2 = 4
        frame_rect = pygame.Rect(self.x_i-self.frame_i2, self.y_i, self.panel_width+self.frame_i2, self.b_height+self.frame_i2)
        pygame.draw.rect(self.screen, self.black, frame_rect, self.frame_i2)  # Rysowanie ramki wokół panelu

        self.draw_turn_info()
        self.draw_char_info()
        self.draw_end_turn_button()
        self.draw_info()
        self.draw_buttons()
    
    def draw_info(self):
        # Tworzenie maskującej powierzchni dla logów (obszar, w którym logi będą widoczne)
        info_surface = pygame.Surface((self.b_width + self.panel_width + (3 * self.frame_i), 100))
        
        # Tworzenie prostokąta dla powierzchni logów
        info_rect = pygame.Rect(self.offset_x - 4, self.offset_y + self.b_height + 17, self.b_width + self.panel_width + (3 * self.frame_i), 100)
        
        # Ustawienie tła na białe
        info_surface.fill(self.white)

        # Wyświetlanie logów
        max_lines = info_rect.height // self.line_height  # Maksymalna liczba wierszy w ramce
        visible_logs = self.logs[max(0, len(self.logs) - max_lines - self.log_scroll): len(self.logs) - self.log_scroll]
        visible_logs.reverse()
        
        log_font = pygame.font.SysFont('Arial', 16)  # Użyj czcionki Arial o rozmiarze 20
        
        # Rysowanie logów na nowej powierzchni
        for i, log in enumerate(visible_logs):
            log_surface = log_font.render(log, True, self.black)
            info_surface.blit(log_surface, (5, 5 + i * self.line_height))
        
        # Rysowanie powierzchni logów w ramce (przypisanie info_surface do ekranu)
        self.screen.blit(info_surface, info_rect)
        
        # adding frame
        pygame.draw.rect(self.screen, self.black, info_rect, 4)

        # Aktualizacja ekranu, aby logi się pojawiły
        pygame.display.update()

    def add_log(self, text):
        """Dodaje nowy wpis do logu wraz z aktualną godziną."""
        current_time = datetime.now().strftime("%H:%M:%S")  # Pobierz bieżącą godzinę w formacie HH:MM:SS
        log_entry = f"[{current_time}] {text}"  # Dodaj godzinę przed tekstem logu
        
        if len(self.logs) >= self.max_logs:
            self.logs.pop(0)  # Usuń najstarszy wpis, jeśli lista przekroczy limit 100
        self.logs.append(log_entry)
        
        self.draw_info()
        pygame.display.update()
        
    def handle_log_scroll(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.log_scroll = max(0, self.log_scroll - 1)
            elif event.button == 5:  # Scroll down
                max_lines = (self.b_height + 100) // self.line_height
                self.log_scroll = min(len(self.logs) - max_lines, self.log_scroll + 1)
        
    def draw_char_info (self):
        try:
            self.char_height = 400
            
            self.y_i3 = self.y_i2+self.turn_height+10
            
            header_rect = pygame.Rect(self.x_i2, self.y_i3, self.ins_panel_w, self.char_height)
            
            # Białe tło paska i ramka
            pygame.draw.rect(self.screen, self.white, header_rect)  
            pygame.draw.rect(self.screen, self.black, header_rect, 2)  # Ramka wokół paska
            
            turn_font = pygame.font.Font(None, 24)
            
            RACE = " ".join(["Race:", str(self.character.race)])
            CLASS = " ".join(["Class:", str(self.character.class_name)])
            LEVEL = " ".join(["Level:", str(self.character.level)])
            ABIL = "Abilities: " + "/".join(str(value) for value in self.character.abilities.values())
            HP = " ".join(["HitPoints:", str(self.character.instance_hp.current_hp), "/", str(self.character.instance_hp.base_hp)])
            BLANK = ""
            MOVE_POINTS = " ".join(["Move points:", str(self.character.c_move_points)])
            ACTIONS = " ".join(["Actions:", str(self.character.c_actions)])
            ATTACKS = " ".join(["Attacks:", str(self.character.c_attacks)])
            
            all_text_lines = [RACE, CLASS, LEVEL, ABIL, HP, BLANK, MOVE_POINTS, ACTIONS, ATTACKS ]

            y_offset = header_rect.top + 45
            
            for line in all_text_lines:
                turn_text = turn_font.render(line, True, self.black)
                turn_text_rect = turn_text.get_rect(topleft=(header_rect.left + 10, y_offset))
                self.screen.blit(turn_text, turn_text_rect)
                y_offset += turn_text.get_height() + 5  # Przesunięcie o wysokość linii + odstęp
        except:
            ...
        
    def draw_turn_info(self):
        try:
            char = self.character_manager.instance_event_manager.char
            
            # Rysowanie paska z nazwą postaci na górze z ramką
            self.turn_height = 60
            self.ins_panel_w = self.panel_width - 20
            
            self.x_i2 = self.x_i+8
            self.y_i2 = self.y_i+10
            
            header_rect = pygame.Rect(self.x_i2, self.y_i2, self.ins_panel_w, self.turn_height)
            
            # Białe tło paska i ramka
            pygame.draw.rect(self.screen, self.white, header_rect)  
            pygame.draw.rect(self.screen, self.black, header_rect, 2)  # Ramka wokół paska

            # Nazwa postaci (większa czcionka)
            name_font = pygame.font.Font(None, 32)
            name_text = name_font.render(self.character.name, True, self.black)
            name_text_rect = name_text.get_rect(center=(header_rect.centerx, header_rect.top + 20))
            self.screen.blit(name_text, name_text_rect)
            
            # Tekst "turn" (mniejsza czcionka)
            turn_font = pygame.font.Font(None, 24)
            turn_text = turn_font.render("turn", True, self.black)
            turn_text_rect = turn_text.get_rect(center=(header_rect.centerx, header_rect.top + 45))
            self.screen.blit(turn_text, turn_text_rect)
        except:
            ...
    
    def draw_buttons(self):
        try:
            self.button_w = 50
            self.button_h = 50
            
            offset = 0
            font = pygame.font.Font(None, 16)
            action_font = pygame.font.Font(None, 16)
            
            for i in range(19):
                header_rect = pygame.Rect(self.offset_x-self.button_w-15, self.offset_y + offset, self.button_w, self.button_h)
                
                pygame.draw.rect(self.screen, self.white, header_rect)  
                pygame.draw.rect(self.screen, self.black, header_rect, 2)
                
                # draw info
                if i < 9:
                    text = str(i+1)
                elif i == 9:
                    text = '0'
                else:
                    text = f"s{i-9}"
                
                text_surf = font.render(text, True, self.black)
                self.screen.blit(text_surf, (header_rect.x + 5, header_rect.y + 5))
                
                # store buttons position
                self.button_pos[i+1] = header_rect
                
                #store buttons 
                action_function, action_name =self.get_actions(i)
                
                self.button_action[i+1] = action_function
                
                #write txt

                action_text_surf = action_font.render(action_name, True, self.black)
                action_text_x = header_rect.x + (self.button_w - action_text_surf.get_width()) // 2
                action_text_y = header_rect.y + (self.button_h - action_text_surf.get_height()) // 2
                self.screen.blit(action_text_surf, (action_text_x, action_text_y))
                
                offset += self.button_h+10
        except Exception as e:
            print(f"Error drawing buttons: {e}")
        
    def check_quick_buttons_click(self, pos):
        print("checking check quick buttons click")
        # check if pos is one of the quick access buttons
        for button_number, rect in self.button_pos.items():
            if rect.collidepoint(pos):
                
                action = self.button_action.get(button_number)
                
                # get action if it is an action
                if action:
                    action()
                else:
                    print("No action")
  
    def get_actions(self, i): 
        
        list = {
            0: (lambda: self.pgame_dash(), "dash"),
            1: (lambda: self.pgame_cleave(), "cleave"),
            2: (lambda: self.pgame_secondwind(), "sec.wind"),
            3: (lambda: self.pgame_offhandattack(), "offhand")
            }
        
        if i in list:
            return list[i]
        else:
            return None

    def draw_end_turn_button(self):
        
        self.end_height = 100
        self.y_i10 = self.y_i+self.b_height-110
        
        button_rect = pygame.Rect(self.x_i2, self.y_i10, self.ins_panel_w, self.end_height)
        
        pygame.draw.rect(self.screen, self.white, button_rect)  # Białe tło przycisku
        pygame.draw.rect(self.screen, self.black, button_rect, 2)  # Ramka przycisku

        # Tekst "END TURN" na przycisku
        font = pygame.font.Font(None, 24)
        button_text = font.render("END TURN", True, self.black)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Zapisywanie prostokąta przycisku do atrybutu klasy dla łatwego dostępu
        self.end_turn_button_rect = button_rect
        
    def draw_popup(self, pos, text):

        popup_width, popup_height = 150, 50
        popup_x, popup_y = pos

        # Ustawienie prostokąta dla popupu przy myszy
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Rysowanie tła popupu
        pygame.draw.rect(self.screen, self.white, popup_rect)
        pygame.draw.rect(self.screen, self.black, popup_rect, 2)  # Ramka dla popupu

        # Dodanie tekstu
        font = pygame.font.Font(None, 20)
        popup_text = font.render(text, True, self.black)
        text_rect = popup_text.get_rect(center=popup_rect.center)
        self.screen.blit(popup_text, text_rect)

        # Aktualizacja ekranu, aby popup się pojawił
        pygame.display.update(popup_rect)

    def handle_right_click(self, pos):
        # Pobieranie pozycji myszy na planszy
        if self.offset_x <= pos[0] < self.b_width+self.offset_x and self.offset_y <= pos[1] < self.b_height+self.offset_y:
            grid_x = (pos[0]-self.offset_x) // self.tile_size
            grid_y = (pos[1]-self.offset_y) // self.tile_size
            pos_board = (grid_x, grid_y)
            
            self.current_popup_pos = pos
            self.current_popup_text = "Popup Text Example"
            
            self.draw_popup(pos, "b")

    def calculate_cost(self, pos_board, pos):
        if self.character_manager.instance_algorithms.is_char(pos_board):
            cost = "character"
        else:
            cost = str(self.character_manager.instance_event_manager.check_move(self.character, pos_board))

        # Przechowuj tekst popupu i pozycję
        self.current_popup_text = f"move pts: {cost}"
        self.current_popup_pos = pos  # Zapisujemy aktualną pozycję myszy
        
        # Wyświetlenie popupu tylko raz
        self.draw_popup(self.current_popup_pos, self.current_popup_text)

    def clear_popup(self, pos):
        # Wymiary popupu
        popup_width, popup_height = 150, 50
        popup_x, popup_y = pos

        # Ustawienie prostokąta dla popupu, który chcemy wyczyścić
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Rysowanie planszy na miejscu popupu, aby go wyczyścić
        pygame.draw.rect(self.screen, self.white, popup_rect)

        # Aktualizacja ekranu, aby wyczyścić popup
        pygame.display.update(popup_rect)
        
    def main_loop (self):
        print(">>>>>>>> MAIN LOOP PYGAME <<<<<<<<<<<<")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running_main = False
        
        if not self.event_queue.empty():
            message, character = self.event_queue.get()
            if message == 'run_game':
                self.run_game(character)

        
        self.draw_interface()
        self.draw_board()

        pygame.display.update()

    def run_game(self, character):
        self.character = character
        clock = pygame.time.Clock()
        last_pos = None

        self.refresh = True
        self.running_player = True

        while self.running_player:
            for event in pygame.event.get():
                # detecting right mouse click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    pos = event.pos
                    self.handle_right_click(pos)
                    self.refresh = True
                
                # detecting left mouse click
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    x, y = (pos[0]-self.offset_x) // self.tile_size, (pos[1]-self.offset_y) // self.tile_size
                    if event.button == 1 and 0 <= x < self.BS and 0 <= y < self.BS: 
                        click_pos = (x, y)
                        
                        cond = self.character_manager.instance_player.interpret(character, click_pos)
                        
                        if cond == False:
                            self.draw_board()
                            self.draw_interface()
                            self.refresh = True
                            continue
                    
                    # check END TURN button
                    if event.button == 1 and self.end_turn_button_rect.collidepoint(pos):
                        print("END TURN clicked")
                        self.running_player = False  # Przerwanie pętli, aby zakończyć `run_game`
                        self.refresh = True
                    
                    if event.button == 1:
                        self.check_quick_buttons_click(pos)
                
                # check mouse detection and clear popup
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                    if last_pos and last_pos != pos:
                        # clear popup if active
                        if self.current_popup_text:
                            self.clear_popup(self.current_popup_pos)
                            self.current_popup_text = ""  # Usunięcie tekstu popupu
                            self.refresh = True

                    last_pos = pos
                
                #always active, add more info to log
                self.handle_log_scroll(event)

            # Rysowanie planszy i interfejsu
            if self.refresh:
                self.draw_board()
                self.draw_interface()
                self.refresh = False
                
            if self.current_popup_text:
                self.draw_popup(self.current_popup_pos, self.current_popup_text)
                
            pygame.display.update()
            clock.tick(10)
    
    def get_click_pos(self):
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    
                    pos = event.pos
                    x, y = (pos[0]-self.offset_x) // self.tile_size, (pos[1]-self.offset_y) // self.tile_size
                    if event.button == 1 and 0 <= x < self.BS and 0 <= y < self.BS: 
                        click_pos = (x, y)
                        print(click_pos)
                        return click_pos
            clock.tick(60)

    def pgame_cleave(self):
        print("pgame_cleave")
        c = self.character
        pos = self.get_click_pos()
        print("pos: ",pos)
        
        t = self.character_manager.instance_algorithms.get_char_from_pos(pos) if self.character_manager.instance_algorithms.is_enemy(c,pos) else None
        
        if t and self.character_manager.instance_conditions.can_cleave(c,t):
            self.character_manager.instance_action.cleave(c,t)
        else:
            return False
    
    def pgame_secondwind(self):
        print("pgame second wind")
        c = self.character
        self.character_manager.instance_action.use_second_wind(c)
        
        self.draw_char_info()
    
    def pgame_dash(self):
        c = self.character
        self.character_manager.instance_action.dash(c)
        
        self.draw_char_info()
    
    def pgame_offhandattack(self):
        print("offhand attack")
        
        c = self.character
        pos = self.get_click_pos()
        print("pos: ",pos)
        
        t = self.character_manager.instance_algorithms.get_char_from_pos(pos) if self.character_manager.instance_algorithms.is_enemy(c,pos) else None

os.system('cls')
main_menu = MainMenu()
main_menu.display_menu()
pygame.quit()

# MANUAL TESTING METHOD testing repo

# y = "Orc"
# x = Character(name=y).load_character((y+".pkl"))
# x.bonus_actions = 1
# x.save_character()

'''
1. increase AI bt with second winds
'''