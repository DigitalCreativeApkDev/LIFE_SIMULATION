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

    POSSIBLE_NAMES: list = []

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name
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


class Battle:
    """
    This class contains attributes of a battle in this game.
    """


class PVPBattle(Battle):
    """
    This class contains attributes of a battle between players.
    """


class WildBattle(Battle):
    """
    This class contains attributes of a battle against a legendary creature.
    """


class TrainerBattle(Battle):
    """
    This class contains attributes of a battle between legendary creature trainers.
    """


class Planet:
    """
    This class contains attributes of the planet in this game.
    """


class City:
    """
    This class contains attributes of a city in this game.
    """


class CityTile:
    """
    This class contains attributes of a tile in a city.
    """


class WallTile(CityTile):
    """
    This class contains attributes of a city tile with a wall where the player cannot be at.
    """


class WaterTile(CityTile):
    """
    This class contains attributes of a city tile of a body of water where the player cannot be at.
    """


class GrassTile(CityTile):
    """
    This class contains attributes of a city tile with grass where the player can encounter wild legendary creatures.
    """


class PavementTile(CityTile):
    """
    This class contains attributes of a tile with pavement where the player can walk safely without any distractions
    from wild legendary creatures.
    """


class Building:
    """
    This class contains attributes of a building in a city.
    """


class ItemShop(Building):
    """
    This class contains attributes of an item shop to buy items in the adventure mode.
    """


class BattleGym(Building):
    """
    This class contains attributes of a battle gym where CPU controlled trainers are available for the player to battle
    against.
    """


class Dungeon(Building):
    """
    This class contains attributes of an adventure mode dungeon where wild legendary creatures and CPU controlled
    trainers are available for the player to battle against.
    """


class Daycare(Building):
    """
    This class contains attributes of a daycare used to place legendary creatures to be trained automatically. In this
    case, the legendary creature being placed will automatically gain EXP.
    """


class Floor:
    """
    This class contains attributes of a floor in a building.
    """


class FloorTile:
    """
    This class contains attributes of a tile in a building floor.
    """


class NormalFloorTile(FloorTile):
    """
    This class contains attributes of a normal floor tile.
    """


class WildFloorTile(FloorTile):
    """
    This class contains attributes of a floor tile where wild legendary creatures can be encountered.
    """


class BuildingEntryOrExit(FloorTile):
    """
    This class contains attributes of a tile used to enter or exit a building.
    """


class StaircaseTile(FloorTile):
    """
    This class contains attributes of a staircase tile for the player to go upstairs/downstairs.
    """


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


class ItemInventory:
    """
    This class contains attributes of an inventory containing items.
    """


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


class LegendaryCreature:
    """
    This class contains attributes of a legendary creature in this game.
    """


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


class EvolutionCandy(Item):
    """
    This class contains attributes of an evolution candy to immediately evolve a legendary creature.
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


class NPC(GameCharacter):
    """
    This class contains attributes of a non-player character (NPC).
    """


class Trainer(GameCharacter):
    """
    This class contains attributes of a trainer in this game.
    """


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


class Award:
    """
    This class contains attributes of an award a player can get for achieving something.
    """


class ResourceReward:
    """
    This class contains attributes of the resources gained for doing something.
    """


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
