"""
This file contains code for the game "Life Simulation".
Author: DigitalCreativeApkDev

The game "Life Simulation" is inspired by Torn RPG (https://www.torn.com/), Stardew Valley
(https://www.stardewvalley.net/), and Pokemon games.
"""


# Game version: 1


# Importing necessary libraries
import sys
import uuid
import pickle
import copy
import random
from datetime import datetime, timedelta
import os
from functools import reduce

import mpmath
from mpmath import mp, mpf
from tabulate import tabulate

mp.pretty = True


# Creating static variables to be used throughout the game.


LETTERS: str = "abcdefghijklmnopqrstuvwxyz"
ELEMENT_CHART: list = [
    ["ATTACKING\nELEMENT", "TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
     "PURE",
     "LEGEND", "PRIMAL", "WIND"],
    ["DOUBLE\nDAMAGE", "ELECTRIC\nDARK", "NATURE\nICE", "FLAME\nWAR", "SEA\nLIGHT", "SEA\nMETAL", "NATURE\nWAR",
     "TERRA\nICE", "METAL\nLIGHT", "ELECTRIC\nDARK", "TERRA\nFLAME", "LEGEND", "PRIMAL", "PURE", "WIND"],
    ["HALF\nDAMAGE", "METAL\nWAR", "SEA\nWAR", "NATURE\nELECTRIC", "FLAME\nICE", "TERRA\nLIGHT", "FLAME\nMETAL",
     "ELECTRIC\nDARK", "TERRA", "NATURE", "SEA\nICE", "PRIMAL", "PURE", "LEGEND", "N/A"],
    ["NORMAL\nDAMAGE", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER",
     "OTHER",
     "OTHER", "OTHER", "OTHER"]
]


# Creating static functions to be used throughout the game.


def is_number(string: str) -> bool:
    try:
        mpf(string)
        return True
    except ValueError:
        return False


def tabulate_element_chart() -> str:
    return str(tabulate(ELEMENT_CHART, headers='firstrow', tablefmt='fancy_grid'))


def generate_random_name() -> str:
    res: str = ""  # initial value
    name_length: int = random.randint(5, 20)
    for i in range(name_length):
        res += LETTERS[random.randint(0, len(LETTERS) - 1)]

    return res.capitalize()


def triangular(n: int) -> int:
    return int(n * (n - 1) / 2)


def mpf_sum_of_list(a_list: list) -> mpf:
    return mpf(str(sum(mpf(str(elem)) for elem in a_list if is_number(str(elem)))))


def mpf_product_of_list(a_list: list) -> mpf:
    return mpf(reduce(lambda x, y: mpf(x) * mpf(y) if is_number(x) and
                                                      is_number(y) else mpf(x) if is_number(x) and not is_number(
        y) else mpf(y) if is_number(y) and not is_number(x) else 1, a_list, 1))


def get_elemental_damage_multiplier(element1: str, element2: str) -> mpf:
    if element1 == "TERRA":
        return mpf("2") if element2 in ["ELECTRIC, DARK"] else mpf("0.5") if element2 in ["METAL", "WAR"] else mpf("1")
    elif element1 == "FLAME":
        return mpf("2") if element2 in ["NATURE", "ICE"] else mpf("0.5") if element2 in ["SEA", "WAR"] else mpf("1")
    elif element1 == "SEA":
        return mpf("2") if element2 in ["FLAME", "WAR"] else mpf("0.5") if element2 in ["NATURE", "ELECTRIC"] else \
            mpf("1")
    elif element1 == "NATURE":
        return mpf("2") if element2 in ["SEA", "LIGHT"] else mpf("0.5") if element2 in ["FLAME", "ICE"] else mpf("1")
    elif element1 == "ELECTRIC":
        return mpf("2") if element2 in ["SEA", "METAL"] else mpf("0.5") if element2 in ["TERRA", "LIGHT"] else mpf("1")
    elif element1 == "ICE":
        return mpf("2") if element2 in ["NATURE", "WAR"] else mpf("0.5") if element2 in ["FLAME", "METAL"] else mpf("1")
    elif element1 == "METAL":
        return mpf("2") if element2 in ["TERRA", "ICE"] else mpf("0.5") if element2 in ["ELECTRIC", "DARK"] else \
            mpf("1")
    elif element1 == "DARK":
        return mpf("2") if element2 in ["METAL", "LIGHT"] else mpf("0.5") if element2 == "TERRA" else mpf("1")
    elif element1 == "LIGHT":
        return mpf("2") if element2 in ["ELECTRIC", "DARK"] else mpf("0.5") if element2 == "NATURE" else mpf("1")
    elif element1 == "WAR":
        return mpf("2") if element2 in ["TERRA", "FLAME"] else mpf("0.5") if element2 in ["SEA", "ICE"] else mpf("1")
    elif element1 == "PURE":
        return mpf("2") if element2 == "LEGEND" else mpf("0.5") if element2 == "PRIMAL" else mpf("1")
    elif element1 == "LEGEND":
        return mpf("2") if element2 == "PRIMAL" else mpf("0.5") if element2 == "PURE" else mpf("1")
    elif element1 == "PRIMAL":
        return mpf("2") if element2 == "PURE" else mpf("0.5") if element2 == "LEGEND" else mpf("1")
    elif element1 == "WIND":
        return mpf("2") if element2 == "WIND" else mpf("1")
    else:
        return mpf("1")


def resistance_accuracy_rule(accuracy: mpf, resistance: mpf) -> mpf:
    if resistance - accuracy <= mpf("0.15"):
        return mpf("0.15")
    else:
        return resistance - accuracy


def load_game_data(file_name):
    # type: (str) -> Game
    return pickle.load(open(file_name, "rb"))


def save_game_data(game_data, file_name):
    # type: (Game, str) -> None
    pickle.dump(game_data, open(file_name, "wb"))


def clear():
    # type: () -> None
    if sys.platform.startswith('win'):
        os.system('cls')  # For Windows System
    else:
        os.system('clear')  # For Linux System


# Creating necessary classes to be used throughout the game.


###########################################
# MINIGAMES
###########################################


class Minigame:
    """
    This class contains attributes of a minigame in this game.
    """

    POSSIBLE_NAMES: list = ["BOX EATS PLANTS", "MATCH WORD PUZZLE", "MATCH-3 GAME"]

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name if name in self.POSSIBLE_NAMES else self.POSSIBLE_NAMES[0]
        self.already_played: bool = False

    def reset(self):
        # type: () -> bool
        time_now: datetime = datetime.now()
        if self.already_played and time_now.hour > 0:
            self.already_played = False
            return True
        return False

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Minigame
        return copy.deepcopy(self)


###########################################
# MINIGAMES
###########################################


###########################################
# ADVENTURE MODE
###########################################


class Action:
    """
    This class contains attributes of an action which can be carried out during battles.
    """

    POSSIBLE_NAMES: list = ["NORMAL ATTACK", "NORMAL HEAL", "USE SKILL"]

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name if name in self.POSSIBLE_NAMES else self.POSSIBLE_NAMES[0]

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Action
        return copy.deepcopy(self)


class AwakenBonus:
    """
    This class contains attributes of the bonus gained for awakening a legendary creature.
    """


class Battle:
    """
    This class contains attributes of a battle in this game.
    """

    def __init__(self, trainer1):
        # type: (Trainer) -> None
        self.trainer1: Trainer = trainer1

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Battle
        return copy.deepcopy(self)


class PVPBattle(Battle):
    """
    This class contains attributes of a battle between players.
    """

    def __init__(self, trainer1, trainer2):
        # type: (Trainer, Trainer) -> None
        Battle.__init__(self, trainer1)
        self.trainer2: Trainer = trainer2


class WildBattle(Battle):
    """
    This class contains attributes of a battle against a legendary creature.
    """

    def __init__(self, trainer1, wild_legendary_creature):
        # type: (Trainer, LegendaryCreature) -> None
        Battle.__init__(self, trainer1)
        self.wild_legendary_creature: LegendaryCreature = wild_legendary_creature


class TrainerBattle(Battle):
    """
    This class contains attributes of a battle between legendary creature trainers.
    """

    def __init__(self, trainer1, trainer2):
        # type: (Trainer, Trainer) -> None
        Battle.__init__(self, trainer1)
        self.trainer2: Trainer = trainer2


class Planet:
    """
    This class contains attributes of the planet in this game.
    """

    def __init__(self, name, cities):
        # type: (str, list) -> None
        self.name: str = name
        self.__cities: list = cities

    def get_cities(self):
        # type: () -> list
        return self.__cities

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Planet
        return copy.deepcopy(self)


class City:
    """
    This class contains attributes of a city in this game.
    """

    def __init__(self, name, tiles):
        # type: (str, list) -> None
        self.name: str = name
        self.__tiles: list = tiles

    def get_tiles(self):
        # type: () -> list
        return self.__tiles

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> City
        return copy.deepcopy(self)


class CityTile:
    """
    This class contains attributes of a tile in a city.
    """

    def __init__(self, building=None, portal=None):
        # type: (Building or None, Portal or None) -> None
        self.building: Building or None = building
        self.portal: Portal or None = None
        self.__game_characters: list = []  # initial value

    def get_game_characters(self):
        # type: () -> list
        return self.__game_characters

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        pass

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        pass

    def __str__(self):
        # type: () -> str
        if isinstance(self.building, Building):
            return str(type(self).__name__) + "(" + str(self.building.name).upper() + ")"
        return str(type(self).__name__) + "(NONE)"

    def clone(self):
        # type: () -> CityTile
        return copy.deepcopy(self)


class Portal:
    """
    This class contains attributes of a portal from one city to another.
    """

    def __init__(self, location_to):
        # type: (AdventureModeLocation) -> None
        self.location_to: AdventureModeLocation = location_to

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Portal
        return copy.deepcopy(self)


class WallTile(CityTile):
    """
    This class contains attributes of a city tile with a wall where the player cannot be at.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self, None)


class WaterTile(CityTile):
    """
    This class contains attributes of a city tile of a body of water where the player cannot be at.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self, None)


class GrassTile(CityTile):
    """
    This class contains attributes of a city tile with grass where the player can encounter wild legendary creatures.
    """

    def __init__(self, building=None):
        # type: (Building or None) -> None
        CityTile.__init__(self, building)

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
        return False


class PavementTile(CityTile):
    """
    This class contains attributes of a tile with pavement where the player can walk safely without any distractions
    from wild legendary creatures.
    """

    def __init__(self, building=None):
        # type: (Building or None) -> None
        CityTile.__init__(self, building)

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
        return False


class Building:
    """
    This class contains attributes of a building in a city.
    """

    def __init__(self, name, floors):
        # type: (str, list) -> None
        self.name: str = name
        self.__floors: list = floors

    def get_floors(self):
        # type: () -> list
        return self.__floors

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Building
        return copy.deepcopy(self)


class ItemShop(Building):
    """
    This class contains attributes of an item shop to buy items in the adventure mode.
    """

    def __init__(self, floors, items_sold):
        # type: (list, list) -> None
        Building.__init__(self, "ITEM SHOP", floors)
        self.__items_sold: list = items_sold

    def get_items_sold(self):
        # type: () -> list
        return self.__items_sold


class FusionCenter(Building):
    """
    This class contains attributes of a fusion center used to fuse legendary creatures.
    """

    def __init__(self, floors):
        # type: (list) -> None
        Building.__init__(self, "FUSION CENTER", floors)


class BattleGym(Building):
    """
    This class contains attributes of a battle gym where CPU controlled trainers are available for the player to battle
    against.
    """

    def __init__(self, floors, gym_owner):
        # type: (list, CPUTrainer) -> None
        Building.__init__(self, "BATTLE GYM", floors)
        self.gym_owner: CPUTrainer = gym_owner


class Dungeon(Building):
    """
    This class contains attributes of an adventure mode dungeon where wild legendary creatures and CPU controlled
    trainers are available for the player to battle against.
    """

    def __init__(self, floors, dungeon_boss):
        # type: (list, CPUTrainer) -> None
        Building.__init__(self, "DUNGEON", floors)
        self.dungeon_boss: CPUTrainer = dungeon_boss


class Daycare(Building):
    """
    This class contains attributes of a daycare used to place legendary creatures to be trained automatically. In this
    case, the legendary creature being placed will automatically gain EXP.
    """

    MAX_LEGENDARY_CREATURES_PLACED: int = 5

    def __init__(self, floors):
        # type: (list) -> None
        Building.__init__(self, "DAYCARE", floors)
        self.__placed_legendary_creatures: list = []  # initial value

    def get_placed_legendary_creatures(self):
        # type: () -> list
        return self.__placed_legendary_creatures

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if len(self.__placed_legendary_creatures) < self.MAX_LEGENDARY_CREATURES_PLACED:
            self.__placed_legendary_creatures.append(legendary_creature)
            return True
        return False

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.__placed_legendary_creatures:
            self.__placed_legendary_creatures.remove(legendary_creature)
            return True
        return False


class Floor:
    """
    This class contains attributes of a floor in a building.
    """

    def __init__(self, name, floor_tiles):
        # type: (str, list) -> None
        self.name: str = name
        self.__floor_tiles: list = floor_tiles

    def get_tile_at(self, x, y):
        # type: (int, int) -> FloorTile or None
        if x < 0 or x >= len(self.__floor_tiles[0]) or y < 0 or y >= len(self.__floor_tiles):
            return None
        return self.__floor_tiles[y][x]

    def get_floor_tiles(self):
        # type: () -> list
        return self.__floor_tiles

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Floor
        return copy.deepcopy(self)


class FloorTile:
    """
    This class contains attributes of a tile in a building floor.
    """

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name
        self.__game_characters: list = []  # initial value

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
        return False

    def get_game_characters(self):
        # type: () -> list
        return self.__game_characters

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> FloorTile
        return copy.deepcopy(self)


class NormalFloorTile(FloorTile):
    """
    This class contains attributes of a normal floor tile.
    """

    def __init__(self):
        # type: () -> None
        FloorTile.__init__(self, "NORMAL FLOOR TILE")


class WildFloorTile(FloorTile):
    """
    This class contains attributes of a floor tile where wild legendary creatures can be encountered.
    """

    def __init__(self):
        # type: () -> None
        FloorTile.__init__(self, "WILD FLOOR TILE")


class BuildingEntryOrExit(FloorTile):
    """
    This class contains attributes of a tile used to enter or exit a building.
    """

    def __init__(self):
        # type: () -> None
        FloorTile.__init__(self, "BUILDING ENTRY OR EXIT TILE")


class StaircaseTile(FloorTile):
    """
    This class contains attributes of a staircase tile for the player to go upstairs/downstairs.
    """

    def __init__(self, can_go_upstairs, can_go_downstairs):
        # type: (bool, bool) -> None
        FloorTile.__init__(self, "STAIRCASE TILE")
        self.can_go_upstairs: bool = can_go_upstairs
        self.can_go_downstairs: bool = can_go_downstairs


###########################################
# ADVENTURE MODE
###########################################


###########################################
# INVENTORY
###########################################


class LegendaryCreatureInventory:
    """
    This class contains attributes of an inventory containing legendary creatures.
    """

    def __init__(self):
        # type: () -> None
        self.__legendary_creatures: list = []  # initial value

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> None
        self.__legendary_creatures.append(legendary_creature)

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.__legendary_creatures:
            self.__legendary_creatures.remove(legendary_creature)
            return True
        return False

    def get_legendary_creatures(self):
        # type: () -> list
        return self.__legendary_creatures

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> LegendaryCreatureInventory
        return copy.deepcopy(self)


class ItemInventory:
    """
    This class contains attributes of an inventory containing items.
    """

    def __init__(self):
        # type: () -> None
        self.__items: list = []  # initial value

    def add_item(self, item):
        # type: (Item) -> None
        self.__items.append(item)

    def remove_item(self, item):
        # type: (Item) -> bool
        if item in self.__items:
            self.__items.remove(item)
            return True
        return False

    def get_items(self):
        # type: () -> list
        return self.__items

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> ItemInventory
        return copy.deepcopy(self)


###########################################
# INVENTORY
###########################################


###########################################
# LEGENDARY CREATURE
###########################################


class BattleTeam:
    """
    This class contains attributes of a team brought to battles.
    """

    MAX_LEGENDARY_CREATURES: int = 5

    def __init__(self, legendary_creatures=None):
        # type: (list) -> None
        if legendary_creatures is None:
            legendary_creatures = []
        self.__legendary_creatures: list = legendary_creatures if len(legendary_creatures) <= \
                                                                  self.MAX_LEGENDARY_CREATURES else []
        self.leader: LegendaryCreature or None = None if len(self.__legendary_creatures) == 0 else \
            self.__legendary_creatures[0]

    def set_leader(self, leader=None):
        # type: (LegendaryCreature or None) -> None
        if leader not in self.__legendary_creatures or len(self.__legendary_creatures) == 0 or leader is None:
            self.leader = None
        else:
            self.leader = leader

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if len(self.__legendary_creatures) < self.MAX_LEGENDARY_CREATURES:
            legendary_creature_ids: list = [creature.legendary_creature_id for creature
                                            in self.__legendary_creatures]
            if legendary_creature.legendary_creature_id not in legendary_creature_ids:
                self.__legendary_creatures.append(legendary_creature)
                self.set_leader()
                return True
            return False
        return False

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.__legendary_creatures:
            self.__legendary_creatures.remove(legendary_creature)
            self.set_leader()
            return True
        return False

    def get_legendary_creatures(self):
        # type: () -> list
        return self.__legendary_creatures

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> BattleTeam
        return copy.deepcopy(self)


class LegendaryCreature:
    """
    This class contains attributes of a legendary creature in this game.
    """

    MIN_RATING: int = 1
    MAX_RATING: int = 6
    MIN_CRIT_RATE: mpf = mpf("0.15")
    MIN_CRIT_DAMAGE: mpf = mpf("1.5")
    MIN_RESISTANCE: mpf = mpf("0.15")
    MAX_RESISTANCE: mpf = mpf("1")
    MIN_ACCURACY: mpf = mpf("0")
    MAX_ACCURACY: mpf = mpf("1")
    MIN_ATTACK_GAUGE: mpf = mpf("0")
    FULL_ATTACK_GAUGE: mpf = mpf("1")
    MIN_EXTRA_TURN_CHANCE: mpf = mpf("0")
    MAX_EXTRA_TURN_CHANCE: mpf = mpf("0.5")
    MIN_COUNTERATTACK_CHANCE: mpf = mpf("0")
    MAX_COUNTERATTACK_CHANCE: mpf = mpf("1")
    MIN_REFLECTED_DAMAGE_PERCENTAGE: mpf = mpf("0")
    MIN_LIFE_DRAIN_PERCENTAGE: mpf = mpf("0")
    MIN_CRIT_RESIST: mpf = mpf("0")
    MAX_CRIT_RESIST: mpf = mpf("1")
    MIN_BENEFICIAL_EFFECTS: int = 0
    MAX_BENEFICIAL_EFFECTS: int = 10
    MIN_HARMFUL_EFFECTS: int = 0
    MAX_HARMFUL_EFFECTS: int = 10
    POTENTIAL_ELEMENTS: list = ["TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
                                "PURE", "LEGEND", "PRIMAL", "WIND", "BEAUTY", "MAGIC", "CHAOS", "HAPPY", "DREAM",
                                "SOUL"]
    DEFAULT_MAX_HP_PERCENTAGE_UP: mpf = mpf("0")
    DEFAULT_MAX_MAGIC_POINTS_PERCENTAGE_UP: mpf = mpf("0")
    DEFAULT_ATTACK_POWER_PERCENTAGE_UP: mpf = mpf("0")
    DEFAULT_ATTACK_SPEED_PERCENTAGE_UP: mpf = mpf("0")
    DEFAULT_DEFENSE_PERCENTAGE_UP: mpf = mpf("0")
    DEFAULT_CRIT_DAMAGE_UP: mpf = mpf("0")


class Skill:
    """
    This class contains attributes of a skill legendary creatures have.
    """


class ActiveSkill(Skill):
    """
    This class contains attributes of an active skill legendary creatures have.
    """


class PassiveSkill(Skill):
    """
    This class contains attributes of a passive skill legendary creatures have.
    """


class PassiveSkillEffect:
    """
    This class contains attributes of the effect of a passive skill.
    """


class LeaderSkill(Skill):
    """
    This class contains attributes of a leader skill legendary creatures have.
    """


class LeaderSkillEffect:
    """
    This class contains attributes of the effect of a leader skill.
    """


class DamageMultiplier:
    """
    This class contains attributes of the damage multiplier of a skill.
    """


class BeneficialEffect:
    """
    This class contains attributes of a beneficial effect a legendary creature has.
    """


class HarmfulEffect:
    """
    This class contains attributes of a harmful effect a legendary creature has.
    """


###########################################
# LEGENDARY CREATURE
###########################################


###########################################
# ITEMS
###########################################


class Item:
    """
    This class contains attributes of an item in this game.
    """


class TrainerItem(Item):
    """
    This class contains attributes of an item to be used by trainers.
    """


class Weapon(TrainerItem):
    """
    This class contains attributes of a weapon the trainers can bring to PVP battles.
    """


class Armor(TrainerItem):
    """
    This class contains attributes of an armor the trainers can bring to PVP battles.
    """


class Crop(TrainerItem):
    """
    This class contains attributes of a crop the trainers can grow in this game.
    """


class LegendaryCreatureItem(Item):
    """
    This class contains attributes of an item to be used by legendary creatures.
    """


class Egg(LegendaryCreatureItem):
    """
    This class contains attributes of an egg which can be hatched to produce a new legendary creature
    """


class Ball(LegendaryCreatureItem):
    """
    This class contains attributes of a ball used to catch a legendary creature.
    """


class Rune(LegendaryCreatureItem):
    """
    This class contains attributes of a rune used to strengthen legendary creatures.
    """


class SetEffect:
    """
    This class contains attributes of a set effect of a rune.
    """


class StatIncrease:
    """
    This class contains attributes of the increase in stats of a rune.
    """


class AwakenShard(Item):
    """
    This class contains attributes of an awaken shard to immediately awaken a legendary creature.
    """


class EXPShard(Item):
    """
    This class contains attributes of an EXP shard to increase the EXP of a legendary creature.
    """


class LevelUpShard(Item):
    """
    This class contains attributes of a shard used to immediately level up a legendary creature.
    """


class SkillLevelUpShard(Item):
    """
    This class contains attributes of a skill level up shard to immediately increase the level of a
    skill possessed by a legendary creature.
    """


###########################################
# ITEMS
###########################################


###########################################
# EXERCISE
###########################################


class ExerciseGym:
    """
    This class contains attributes of a gym where the player can improve his/her attributes.
    """


class FitnessType:
    """
    This class contains attributes of the type of fitness in an exercise gym.
    """


class TrainingOption:
    """
    This class contains attributes of a training option for fitness.
    """


###########################################
# EXERCISE
###########################################


###########################################
# PROPERTIES
###########################################


class Property:
    """
    This class contains attributes of a property the player can live in.
    """


class PropertyUpgrade:
    """
    This class contains attributes of an upgrade to a property a player owns.
    """


###########################################
# PROPERTIES
###########################################


###########################################
# JOBS AND SKILLS
###########################################


class JobRole:
    """
    This class contains attributes of a job role a player can get in this game.
    """


class Course:
    """
    This class contains attributes of a course the player can take in this game.
    """


###########################################
# JOBS AND SKILLS
###########################################


###########################################
# PLANTATION
###########################################


class Plantation:
    """
    This class contains attributes of player's plantation to grow crops.
    """


class Section:
    """
    This class contains attributes of a section in a plantation.
    """


class SectionTile:
    """
    This class contains attributes of a tile in a plantation section.
    """


###########################################
# PLANTATION
###########################################


###########################################
# GENERAL
###########################################


class GameCharacter:
    """
    This class contains attributes of a game character in this game.
    """

    def __init__(self, name, adventure_mode_location):
        # type: (str, AdventureModeLocation or None) -> None
        self.game_character_id: str = str(uuid.uuid1())  # generating random game character ID
        self.name: str = name
        self.adventure_mode_location: AdventureModeLocation or None = adventure_mode_location

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> GameCharacter
        return copy.deepcopy(self)


class NPC(GameCharacter):
    """
    This class contains attributes of a non-player character (NPC).
    """

    def __init__(self, name, adventure_mode_location, message):
        # type: (str, AdventureModeLocation, str) -> None
        GameCharacter.__init__(self, name, adventure_mode_location)
        self.message: str = message


class Trainer(GameCharacter):
    """
    This class contains attributes of a trainer in this game.
    """

    def __init__(self, name, adventure_mode_location):
        # type: (str, AdventureModeLocation or None) -> None
        GameCharacter.__init__(self, name, adventure_mode_location)


class PlayerTrainer(Trainer):
    """
    This class contains attributes of the player in this game.
    """


class CPUTrainer(Trainer):
    """
    This class contains attributes of a CPU controlled trainer.
    """


class AdventureModeLocation:
    """
    This class contains attributes of the location of a game character in adventure mode of this game.
    """

    def __init__(self, planet, city_index, city_tile_x, city_tile_y, floor_index, floor_tile_x, floor_tile_y):
        # type: (Planet, int, int, int, int, int, int) -> None
        self.planet: Planet = planet
        self.city_index: int = city_index
        self.city_tile_x: int = city_tile_x
        self.city_tile_y: int = city_tile_y
        self.floor_index: int = floor_index
        self.floor_tile_x: int = floor_tile_x
        self.floor_tile_y: int = floor_tile_y

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> AdventureModeLocation
        return copy.deepcopy(self)


class Jail:
    """
    This class contains attributes of the jail.
    """


class Hospital:
    """
    This class contains attributes of the hospital for injured game characters.
    """


class AwardCondition:
    """
    This class contains attributes of a condition for an award to be achieved.
    """

    def __init__(self, checked_player_attribute, min_value):
        # type: (str, int) -> None
        self.checked_player_attribute: str = checked_player_attribute
        self.min_value: int = min_value

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> AwardCondition
        return copy.deepcopy(self)


class Award:
    """
    This class contains attributes of an award a player can get for achieving something.
    """

    def __init__(self, name, description, condition):
        # type: (str, str, AwardCondition) -> None
        self.name: str = name
        self.description: str = description
        self.condition: AwardCondition = condition

    def condition_is_met(self, trainer):
        # type: (Trainer) -> bool
        try:
            return getattr(trainer, str(self.condition.checked_player_attribute)) >= self.condition.min_value
        except AttributeError:
            return False

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Award
        return copy.deepcopy(self)


class ResourceReward:
    """
    This class contains attributes of the resources gained for doing something.
    """

    def __init__(self, player_reward_exp=mpf("0"), player_reward_dollars=mpf("0"),
                 legendary_creature_reward_exp=mpf("0"), player_reward_items=None):
        # type: (mpf, mpf, mpf, list) -> None
        if player_reward_items is None:
            player_reward_items = []

        self.player_reward_exp: mpf = player_reward_exp
        self.player_reward_dollars: mpf = player_reward_dollars
        self.legendary_creature_reward_exp: mpf = legendary_creature_reward_exp
        self.__player_reward_items: list = player_reward_items

    def get_player_reward_items(self):
        # type: () -> list
        return self.__player_reward_items

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> ResourceReward
        return copy.deepcopy(self)


class Game:
    """
    This class contains attributes of saved game data.
    """

    def __str__(self):
        # type: () -> str
        res: str = str(type(self).__name__) + "("  # initial value
        index: int = 0  # initial value
        for item in vars(self).items():
            res += str(item[0]) + "=" + str(item[1])

            if index < len(vars(self).items()) - 1:
                res += ", "

            index += 1

        return res + ")"

    def clone(self):
        # type: () -> Game
        return copy.deepcopy(self)


###########################################
# GENERAL
###########################################


# Creating main function used to run the game.


def main() -> int:
    """
    This main function is used to run the game.
    :return: an integer
    """

    print("Welcome to 'Life Simulation' by 'NativeApkDev'.")
    print("This game is an offline adventure and simulation RPG allowing the player to ")
    print("choose various real-life actions.")
    print("Below is the element chart in 'Adventure Mode' of 'Life Simulation'.\n")
    print(str(tabulate_element_chart()) + "\n")
    print("The following elements do not have any elemental strengths nor weaknesses.")
    print("This is because they are ancient world elements. In this case, these elements will always ")
    print("be dealt with normal damage.\n")
    ancient_world_elements: list = ["BEAUTY", "MAGIC", "CHAOS", "HAPPY", "DREAM", "SOUL"]
    for i in range(0, len(ancient_world_elements)):
        print(str(i + 1) + ". " + str(ancient_world_elements[i]))

    return 0


if __name__ == '__main__':
    main()
