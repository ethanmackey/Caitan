import random
from enum import Enum
from collections import defaultdict

class ResourceType(Enum):
    BRICK = "brick"
    LUMBER = "lumber"
    ORE = "ore"
    GRAIN = "grain"
    WOOL = "wool"

class Player:
    def __init__(self, player_id):
        self.id = player_id

        self.resources = {"brick" : 0, "lumber" : 0, "ore" : 0, "grain" : 0, "wool" : 0}
        self.legacyResources = {"brick" : 0, "lumber" : 0, "ore" : 0, "grain" : 0, "wool" : 0}
        self.roadSpots = set()
        self.settlementSpots = set()
        self.citySpots = set()

        self.victory_points = 0
        self.downDevs = {"knight" : 0, "victoryPoint" : 0, "roadBuilding" : 0, "yearOfPlenty" : 0, "monopoly" : 0}
        self.newDevs = {"knight" : 0, "victoryPoint" : 0, "roadBuilding" : 0, "yearOfPlenty" : 0, "monopoly" : 0}
        self.upDevs = {"knight" : 0, "victoryPoint" : 0, "roadBuilding" : 0, "yearOfPlenty" : 0, "monopoly" : 0}
        self.largest_army = False
        self.longest_road = False

class TileSpace:
    def __init__(self, resource, number, adjSettlements):
        self.resource = resource
        self.number = number
        self.adjSettlements = adjSettlements

class RoadSpace:
    def __init__(self, adjRoads, adjSettlements):
        self.hasRoad = False
        self.controller = None
        self.adjRoads = adjRoads
        self.adjSettlements = adjSettlements

class SettlementSpace:
    def __init__(self, adjSettlements, adjRoads):
        self.blocked = False
        self.adjSettlements = adjSettlements
        self.adjRoads = adjRoads
        self.hasSettlement = False
        self.hasCity = False
        self.controller = None

def tileFindAdjSettlements(n):
    if n == 1:
        return [1, 4, 5, 8, 9, 13]
    elif n == 2:
        return [2, 5, 6, 9, 10, 14]
    elif n == 3:
        return [3, 6, 7, 10, 11, 15]
    elif n == 4:
        return [8, 12, 13, 17, 18, 23]
    elif n == 5:
        return [9, 13, 14, 18, 19, 24]
    elif n == 6:
        return [10, 14, 15, 19, 20, 25]
    elif n == 7:
        return [11, 15, 16, 20, 21, 26]
    elif n == 8:
        return [17, 22, 23, 28, 29, 34]
    elif n == 9:
        return [18, 23, 24, 29, 30, 35]
    elif n == 10:
        return [19, 24, 25, 30, 31, 36]
    elif n == 11:
        return [20, 25, 26, 31, 32, 37]
    elif n == 12:
        return [21, 26, 27, 32, 33, 38]
    elif n == 13:
        return [29, 34, 35, 39, 40, 44]
    elif n == 14:
        return [30, 35, 36, 40, 41, 45]
    elif n == 15:
        return [31, 36, 37, 41, 42, 46]
    elif n == 16:
        return [32, 37, 38, 42, 43, 47]
    elif n == 17:
        return [40, 44, 45, 48, 49, 52]
    elif n == 18:
        return [41, 45, 46, 49, 50, 53]
    elif n == 19:
        return [42, 46, 47, 50, 51, 54]

def roadFindAdjRoads(n):
    if n == 1:
        return [2, 7]
    elif n == 2:
        return [1, 3, 8]
    elif n == 3:
        return [2, 4, 8]
    elif n == 4:
        return [3, 5, 9]
    elif n == 5:
        return [4, 6, 9]
    elif n == 6:
        return [5, 10]
    
    elif n == 7:
        return [1, 11, 12]
    elif n == 8:
        return [2, 3, 13, 14]
    elif n == 9:
        return [4, 5, 15, 16]
    elif n == 10:
        return [6, 17, 18]
    
    elif n == 11:
        return [7, 12, 19]
    elif n == 12:
        return [7, 11, 13, 20]
    elif n == 13:
        return [8, 12, 14, 20]
    elif n == 14:
        return [8, 13, 15, 21]
    elif n == 15:
        return [9, 14, 16, 21]
    elif n == 16:
        return [9, 15, 17, 22]
    elif n == 17:
        return [10, 16, 18, 22]
    elif n == 18:
        return [10, 17, 23]
    
    elif n == 19:
        return [11, 24, 25]
    elif n == 20:
        return [12, 13, 26, 27]
    elif n == 21:
        return [14, 15, 28, 29]
    elif n == 22:
        return [16, 17, 30, 31]
    elif n == 23:
        return [18, 32, 33]
    

    elif n == 24:
        return [19, 25, 34]
    elif n == 25:
        return [19, 24, 26, 35]
    elif n == 26:
        return [20, 25, 27, 35]
    elif n == 27:
        return [20, 26, 28, 36]
    elif n == 28:
        return [21, 27, 29, 36]
    elif n == 29:
        return [21, 28, 30, 37]
    elif n == 30:
        return [22, 29, 31, 37]
    elif n == 31:
        return [22, 30, 32, 38]
    elif n == 32:
        return [23, 31, 33, 38]
    elif n == 33:
        return [23, 32, 39]
    
    elif n == 34:
        return [24, 40]
    elif n == 35:
        return [25, 26, 41, 42]
    elif n == 36:
        return [27, 28, 43, 44]
    elif n == 37:
        return [29, 30, 45, 46]
    elif n == 38:
        return [31, 32, 47, 48]
    elif n == 39:
        return [33, 49]
    
    elif n == 40:
        return [34, 41, 50]
    elif n == 41:
        return [35, 40, 42, 50]
    elif n == 42:
        return [35, 41, 43, 51]
    elif n == 43:
        return [36, 42, 44, 51]
    elif n == 44:
        return [36, 43, 45, 52]
    elif n == 45:
        return [37, 44, 46, 52]
    elif n == 46:
        return [37, 45, 47, 53]
    elif n == 47:
        return [38, 46, 48, 53]
    elif n == 48:
        return [38, 47, 49, 54]
    elif n == 49:
        return [39, 48, 54]
    
    elif n == 50:
        return [40, 41, 55]
    elif n == 51:
        return [42, 43, 56, 57]
    elif n == 52:
        return [44, 45, 58, 59]
    elif n == 53:
        return [46, 47, 60, 61]
    elif n == 54:
        return [48, 49, 62]
    
    elif n == 55:
        return [50, 56, 63]
    elif n == 56:
        return [51, 55, 57, 63]
    elif n == 57:
        return [51, 56, 58, 64]
    elif n == 58:
        return [52, 57, 59, 64]
    elif n == 59:
        return [52, 58, 60, 65]
    elif n == 60:
        return [53, 59, 61, 65]
    elif n == 61:
        return [53, 60, 62, 66]
    elif n == 62:
        return [54, 61, 66]
    
    elif n == 63:
        return [55, 56, 67]
    elif n == 64:
        return [57, 58, 68, 69]
    elif n == 65:
        return [59, 60, 70, 71]
    elif n == 66:
        return [61, 62, 72]
    
    elif n == 67:
        return [63, 68]
    elif n == 68:
        return [64, 67, 69]
    elif n == 69:
        return [64, 68, 70]
    elif n == 70:
        return [65, 69, 71]
    elif n == 71:
        return [65, 70, 72]
    elif n == 72:
        return [66, 71]

def roadFindAdjSettlements(n):
    if n == 1:
        return [1, 4]
    elif n == 2:
        return [1, 5]
    elif n == 3:
        return [2, 5]
    elif n == 4:
        return [2, 6]
    elif n == 5:
        return [3, 6]
    elif n == 6:
        return [3, 7]
    
    elif n == 7:
        return [4, 8]
    elif n == 8:
        return [5, 9]
    elif n == 9:
        return [6, 10]
    elif n == 10:
        return [7, 11]
    
    elif n == 11:
        return [8, 12]
    elif n == 12:
        return [8, 13]
    elif n == 13:
        return [9, 13]
    elif n == 14:
        return [9, 14]
    elif n == 15:
        return [10, 14]
    elif n == 16:
        return [10, 15]
    elif n == 17:
        return [11, 15]
    elif n == 18:
        return [11, 16]
    
    elif n == 19:
        return [12, 17]
    elif n == 20:
        return [13, 18]
    elif n == 21:
        return [14, 19]
    elif n == 22:
        return [15, 20]
    elif n == 23:
        return [16, 21]
    
    elif n == 24:
        return [17, 22]
    elif n == 25:
        return [17, 23]
    elif n == 26:
        return [18, 23]
    elif n == 27:
        return [18, 24]
    elif n == 28:
        return [19, 24]
    elif n == 29:
        return [19, 25]
    elif n == 30:
        return [20, 25]
    elif n == 31:
        return [20, 26]
    elif n == 32:
        return [21, 26]
    elif n == 33:
        return [21, 27]
    
    elif n == 34:
        return [22, 28]
    elif n == 35:
        return [23, 29]
    elif n == 36:
        return [24, 30]
    elif n == 37:
        return [25, 31]
    elif n == 38:
        return [26, 32]
    elif n == 39:
        return [27, 33]
    
    elif n == 40:
        return [28, 34]
    elif n == 41:
        return [29, 34]
    elif n == 42:
        return [29, 35]
    elif n == 43:
        return [30, 35]
    elif n == 44:
        return [30, 36]
    elif n == 45:
        return [31, 36]
    elif n == 46:
        return [31, 37]
    elif n == 47:
        return [32, 37]
    elif n == 48:
        return [32, 38]
    elif n == 49:
        return [33, 38]
    
    elif n == 50:
        return [34, 39]
    elif n == 51:
        return [35, 40]
    elif n == 52:
        return [36, 41]
    elif n == 53:
        return [37, 42]
    elif n == 54:
        return [38, 43]
    
    elif n == 55:
        return [39, 44]
    elif n == 56:
        return [40, 44]
    elif n == 57:
        return [40, 45]
    elif n == 58:
        return [41, 45]
    elif n == 59:
        return [41, 46]
    elif n == 60:
        return [42, 46]
    elif n == 61:
        return [42, 47]
    elif n == 62:
        return [43, 47]

    elif n == 63:
        return [44, 48]
    elif n == 64:
        return [45, 49]
    elif n == 65:
        return [46, 50]
    elif n == 66:
        return [47, 51]
    
    elif n == 67:
        return [48, 52]
    elif n == 68:
        return [49, 52]
    elif n == 69:
        return [49, 53]
    elif n == 70:
        return [50, 53]
    elif n == 71:
        return [50, 54]
    elif n == 72:
        return [51, 54]

def settlementFindAdjSettlements(n):
    if n == 1:
        return [4, 5]
    elif n == 2:
        return [5, 6]
    elif n == 3:
        return [6, 7]
    
    elif n == 4:
        return [1, 8]
    elif n == 5:
        return [1, 2, 9]
    elif n == 6:
        return [2, 3, 10]
    elif n == 7:
        return [3, 11]
    
    elif n == 8:
        return [4, 12, 13]
    elif n == 9:
        return [5, 13, 14]
    elif n == 10:
        return [6, 14, 15]
    elif n == 11:
        return [7, 15, 16]
    
    elif n == 12:
        return [8, 17]
    elif n == 13:
        return [8, 9, 18]
    elif n == 14:
        return [9, 10, 19]
    elif n == 15:
        return [10, 11, 20]
    elif n == 16:
        return [11, 21]
    
    elif n == 17:
        return [12, 22, 23]
    elif n == 18:
        return [13, 23, 24]
    elif n == 19:
        return [14, 24, 25]
    elif n == 20:
        return [15, 25, 26]
    elif n == 21:
        return [16, 26, 27]
    
    elif n == 22:
        return [17, 28]
    elif n == 23:
        return [17, 18, 29]
    elif n == 24:
        return [18, 19, 30]
    elif n == 25:
        return [19, 20, 31]
    elif n == 26:
        return [20, 21, 32]
    elif n == 27:
        return [21, 33]
    
    elif n == 28:
        return [22, 34]
    elif n == 29:
        return [23, 34, 35]
    elif n == 30:
        return [24, 35, 36]
    elif n == 31:
        return [25, 36, 37]
    elif n == 32:
        return [26, 37, 38]
    elif n == 33:
        return [27, 38]
    
    elif n == 34:
        return [28, 29, 39]
    elif n == 35:
        return [29, 30, 40]
    elif n == 36:
        return [30, 31, 41]
    elif n == 37:
        return [31, 32, 42]
    elif n == 38:
        return [32, 33, 43]
    
    elif n == 39:
        return [34, 44]
    elif n == 40:
        return [35, 44, 45]
    elif n == 41:
        return [36, 45, 46]
    elif n == 42:
        return [37, 46, 47]
    elif n == 43:
        return [38, 47]
    
    elif n == 44:
        return [39, 40, 48]
    elif n == 45:
        return [40, 41, 49]
    elif n == 46:
        return [41, 42, 50]
    elif n == 47:
        return [42, 43, 51]
    
    elif n == 48:
        return [44, 52]
    elif n == 49:
        return [45, 52, 53]
    elif n == 50:
        return [46, 53, 54]
    elif n == 51:
        return [47, 54]
    
    elif n == 52:
        return [48, 49]
    elif n == 53:
        return [49, 50]
    elif n == 54:
        return [50, 51]

def settlementFindAdjRoads(n):
    if n == 1:
        return [1, 2]
    elif n == 2:
        return [3, 4]
    elif n == 3:
        return [5, 6]
    elif n == 4:
        return [1, 7]
    elif n == 5:
        return [2, 3, 8]
    elif n == 6:
        return [4, 5, 9]
    elif n == 7:
        return [6, 10]
    elif n == 8:
        return [7, 11, 12]
    elif n == 9:
        return [8, 13, 14]
    elif n == 10:
        return [9, 15, 16]
    elif n == 11:
        return [10, 17, 18]
    elif n == 12:
        return [11, 19]
    elif n == 13:
        return [12, 13, 20]
    elif n == 14:
        return [14, 15, 21]
    elif n == 15:
        return [16, 17, 22]
    elif n == 16:
        return [18, 23]
    elif n == 17:
        return [19, 24, 25]
    elif n == 18:
        return [20, 26, 27]
    elif n == 19:
        return [21, 28, 29]
    elif n == 20:
        return [22, 30, 31]
    elif n == 21:
        return [23, 32, 33]
    elif n == 22:
        return [24, 34]
    elif n == 23:
        return [25, 26, 35]
    elif n == 24:
        return [27, 28, 36]
    elif n == 25:
        return [29, 30, 37]
    elif n == 26:
        return [31, 32, 38]
    elif n == 27:
        return [33, 39]
    elif n == 28:
        return [34, 40]
    elif n == 29:
        return [35, 41, 42]
    elif n == 30:
        return [36, 43, 44]
    elif n == 31:
        return [37, 45, 46]
    elif n == 32:
        return [38, 47, 48]
    elif n == 33:
        return [39, 49]
    elif n == 34:
        return [40, 41, 50]
    elif n == 35:
        return [42, 43, 51]
    elif n == 36:
        return [44, 45, 52]
    elif n == 37:
        return [46, 47, 53]
    elif n == 38:
        return [48, 49, 54]
    elif n == 39:
        return [50, 55]
    elif n == 40:
        return [51, 56, 57]
    elif n == 41:
        return [52, 58, 59]
    elif n == 42:
        return [53, 60, 61]
    elif n == 43:
        return [54, 62]
    elif n == 44:
        return [55, 56, 63]
    elif n == 45:
        return [57, 58, 64]
    elif n == 46:
        return [59, 60, 65]
    elif n == 47:
        return [61, 62, 66]
    elif n == 48:
        return [63, 67]
    elif n == 49:
        return [64, 68, 69]
    elif n == 50:
        return [65, 70, 71]
    elif n == 51:
        return [66, 72]
    elif n == 52:
        return [67, 68]
    elif n == 53:
        return [69, 70]
    elif n == 54:
        return [71, 72]

def color_tile(tile_code, resource):
    colors = {
        "g": "\033[93m",
        "l": "\033[38;5;22m",
        "w": "\033[92m",
        "b": "\033[91m",
        "o": "\033[90m",
        "d": "\033[95m",
    }
    reset = "\033[0m"
    resource_letter = resource[:1].lower()
    color = colors.get(resource_letter, "")
    return f"{color}{tile_code}{reset}"

def printBoard(board):
    sv = {}
    for i in range(1, 55):
        key = f"s{i}"
        if board[key].hasSettlement:
            sv[key] = f"{board[key].controller}s"
        elif board[key].hasCity:
            sv[key] = f"{board[key].controller}c"
        elif board[key].blocked:
            sv[key] = "~~"
        else:
            sv[key] = "--"

    rv = {}
    for i in range(1, 73):
        key = f"r{i}"
        rv[key] = board[key].controller if board[key].hasRoad else " "

    tv = {}
    for i in range(1, 20):
        key = f"t{i}"
        temp = f"{(board[key].number)}"
        if board[key].number in (10, "10"):
            temp = "!"
        elif board[key].number in (11, "11"):
            temp = "@"
        elif board[key].number in (12, "12"):
            temp = "#"
        tile_code = f"{temp}{board[key].resource[:1].lower()}"
        tv[key] = color_tile(tile_code, board[key].resource)
    
    ascii_art = [
    f"               {sv["s1"]}        {sv["s2"]}        {sv["s3"]}",
    f"           /{rv["r1"]}/    \\{rv["r2"]}\\/{rv["r3"]}/    \\{rv["r4"]}\\/{rv["r5"]}/    \\{rv["r6"]}\\",
    f"          {sv["s4"]}        {sv["s5"]}        {sv["s6"]}        {sv["s7"]}",
    f"         |{rv["r7"]}|   {tv["t1"]}  |{rv["r8"]}|   {tv["t2"]}   |{rv["r9"]}|  {tv["t3"]}   |{rv["r10"]}|",
    f"          {sv["s8"]}        {sv["s9"]}        {sv["s10"]}        {sv["s11"]}",
    f"       /{rv["r11"]}/   \\{rv["r12"]}\\/{rv["r13"]}/    \\{rv["r14"]}\\/{rv["r15"]}/    \\{rv["r16"]}\\/{rv["r17"]}/    \\{rv["r18"]}\\",
    f"     {sv["s12"]}        {sv["s13"]}        {sv["s14"]}        {sv["s15"]}        {sv["s16"]}",
    f"    |{rv["r19"]}|   {tv["t4"]}  |{rv["r20"]}|   {tv["t5"]}  |{rv["r21"]}|   {tv["t6"]}   |{rv["r22"]}|  {tv["t7"]}   |{rv["r23"]}|",
    f"     {sv["s17"]}        {sv["s18"]}        {sv["s19"]}        {sv["s20"]}        {sv["s21"]}",   
    f" /{rv["r24"]}/    \\{rv["r25"]}\\/{rv["r26"]}/    \\{rv["r27"]}\\/{rv["r28"]}/    \\{rv["r29"]}\\/{rv["r30"]}/    \\{rv["r31"]}\\/{rv["r32"]}/    \\{rv["r33"]}\\",
    f" {sv["s22"]}       {sv["s23"]}        {sv["s24"]}        {sv["s25"]}        {sv["s26"]}       {sv["s27"]}",
    f"|{rv["r34"]}|  {tv["t8"]}  |{rv["r35"]}|   {tv["t9"]}  |{rv["r36"]}|   {tv["t10"]}   |{rv["r37"]}|  {tv["t11"]}   |{rv["r38"]}|  {tv["t12"]}  |{rv["r39"]}|",
    f" {sv["s28"]}       {sv["s29"]}        {sv["s30"]}        {sv["s31"]}        {sv["s32"]}       {sv["s33"]}",
    f" \\{rv["r40"]}\\    /{rv["r41"]}/\\{rv["r42"]}\\    /{rv["r43"]}/\\{rv["r44"]}\\    /{rv["r45"]}/\\{rv["r46"]}\\    /{rv["r47"]}/\\{rv["r48"]}\\    /{rv["r49"]}/",
    f"     {sv["s34"]}        {sv["s35"]}        {sv["s36"]}        {sv["s37"]}        {sv["s38"]}",
    f"    |{rv["r50"]}|   {tv["t13"]}  |{rv["r51"]}|   {tv["t14"]}  |{rv["r52"]}|   {tv["t15"]}   |{rv["r53"]}|  {tv["t16"]}   |{rv["r54"]}|",
    f"     {sv["s39"]}        {sv["s40"]}        {sv["s41"]}        {sv["s42"]}        {sv["s43"]}",
    f"     \\{rv["r55"]}\\     /{rv["r56"]}/\\{rv["r57"]}\\    /{rv["r58"]}/\\{rv["r59"]}\\    /{rv["r60"]}/\\{rv["r61"]}\\     /{rv["r62"]}/",
    f"          {sv["s44"]}        {sv["s45"]}        {sv["s46"]}        {sv["s47"]}",
    f"         |{rv["r63"]}|   {tv["t17"]}  |{rv["r64"]}|   {tv["t18"]}   |{rv["r65"]}|  {tv["t19"]}   |{rv["r66"]}|",
    f"          {sv["s48"]}        {sv["s49"]}        {sv["s50"]}        {sv["s51"]}",
    f"	  \\{rv["r67"]}\\     /{rv["r68"]}/\\{rv["r69"]}\\    /{rv["r70"]}/\\{rv["r71"]}\\     /{rv["r72"]}/",
    f"	       {sv["s52"]}        {sv["s53"]}        {sv["s54"]}"
    ]

    for line in ascii_art:
        print(line)


class CatanGame:
    RESOURCE_NAMES = [resource.value for resource in ResourceType]
    DEV_CARD_TYPES = ["knight", "victoryPoint", "roadBuilding", "yearOfPlenty", "monopoly"]
    BUILD_COSTS = {
        "road": {"brick": 1, "lumber": 1},
        "settlement": {"brick": 1, "lumber": 1, "grain": 1, "wool": 1},
        "city": {"grain": 2, "ore": 3},
        "dev": {"ore": 1, "grain": 1, "wool": 1},
    }
    DEV_CARD_COUNTS = {"knight": 14, "victoryPoint": 5, "roadBuilding": 2, "yearOfPlenty": 2, "monopoly": 2}
    PIECE_LIMITS = {"roads": 15, "settlements": 5, "cities": 4}
    PORTS = {
        1: "grain", 4: "grain",
        3: "any", 7: "any",
        12: "ore", 17: "ore",
        22: "any", 28: "any",
        39: "wool", 44: "wool",
        48: "brick", 52: "brick",
        50: "any", 54: "any",
        43: "lumber", 47: "lumber",
        2: "any", 5: "any",
    }

    def __init__(self, num_players=4):
        if num_players != 4:
            raise ValueError("Traditional base Catan requires exactly 4 players")
        self.num_players = num_players
        self.players = [Player(i) for i in range(num_players)]
        self.current_player = 0
        self.turn_number = 0
        self.game_over = False
        self.winner = None
        self.robber_tile = None
        self.bank = {resource: 19 for resource in self.RESOURCE_NAMES}
        self.played_dev_this_turn = False
        self.board = self._initialize_board()
        self._run_initial_placement()
        self._refresh_all_player_options()

    def print_board(self):
        printBoard(self.board)

    def _initialize_board(self):
        board = {}
        resource_tiles = (
            ["brick"] * 3
            + ["lumber"] * 4
            + ["grain"] * 4
            + ["wool"] * 4
            + ["ore"] * 3
            + ["desert"]
        )
        random.shuffle(resource_tiles)
        number_tiles = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

        resources_by_tile = {}
        for tile_id in range(1, 20):
            resources_by_tile[tile_id] = resource_tiles.pop()

        numbers_by_tile = self._assign_number_tokens(resources_by_tile, number_tiles)
        for tile_id in range(1, 20):
            resource = resources_by_tile[tile_id]
            number = 0 if resource == "desert" else numbers_by_tile[tile_id]
            if resource == "desert":
                self.robber_tile = tile_id
            board[f"t{tile_id}"] = TileSpace(resource, number, tileFindAdjSettlements(tile_id))

        for road_id in range(1, 73):
            board[f"r{road_id}"] = RoadSpace(roadFindAdjRoads(road_id), roadFindAdjSettlements(road_id))

        for settlement_id in range(1, 55):
            board[f"s{settlement_id}"] = SettlementSpace(
                settlementFindAdjSettlements(settlement_id), settlementFindAdjRoads(settlement_id)
            )

        dev_stack = []
        for card, count in self.DEV_CARD_COUNTS.items():
            dev_stack.extend([card] * count)
        random.shuffle(dev_stack)
        board["devStack"] = dev_stack
        return board

    def _assign_number_tokens(self, resources_by_tile, number_tiles):
        non_desert_tiles = [tile_id for tile_id, resource in resources_by_tile.items() if resource != "desert"]
        for _ in range(1000):
            shuffled = number_tiles[:]
            random.shuffle(shuffled)
            candidate = dict(zip(non_desert_tiles, shuffled))
            if not self._has_adjacent_red_numbers(candidate):
                return candidate
        return dict(zip(non_desert_tiles, number_tiles))

    def _has_adjacent_red_numbers(self, numbers_by_tile):
        red_tiles = {tile_id for tile_id, number in numbers_by_tile.items() if number in (6, 8)}
        for tile_id in red_tiles:
            current_settlements = set(tileFindAdjSettlements(tile_id))
            for other_id in red_tiles:
                if tile_id != other_id and current_settlements.intersection(tileFindAdjSettlements(other_id)):
                    return True
        return False

    def _run_initial_placement(self):
        placement_order = list(range(self.num_players)) + list(reversed(range(self.num_players)))
        for round_index, player_id in enumerate(placement_order):
            settlement_id = random.choice(self.legal_settlement_spots(player_id, setup=True))
            self._place_settlement(player_id, settlement_id, setup=True)
            road_options = [road_id for road_id in settlementFindAdjRoads(settlement_id) if not self.board[f"r{road_id}"].hasRoad]
            self._place_road(player_id, random.choice(road_options))
            if round_index >= self.num_players:
                self._grant_starting_resources(player_id, settlement_id)

    def _grant_starting_resources(self, player_id, settlement_id):
        for tile_id in range(1, 20):
            tile = self.board[f"t{tile_id}"]
            if tile.resource != "desert" and settlement_id in tile.adjSettlements:
                self._take_from_bank(tile.resource, 1, self.players[player_id])
                self.players[player_id].legacyResources[tile.resource] += 1

    def roll_dice(self):
        return random.randint(1, 6) + random.randint(1, 6)

    def collect_resources(self, roll):
        if roll == 7:
            self._handle_seven(self.current_player)
            return

        payouts_by_resource = {resource: [] for resource in self.RESOURCE_NAMES}
        for tile_id in range(1, 20):
            tile = self.board[f"t{tile_id}"]
            if tile.number != roll or tile_id == self.robber_tile or tile.resource == "desert":
                continue
            for settlement_id in tile.adjSettlements:
                settlement = self.board[f"s{settlement_id}"]
                if settlement.hasSettlement:
                    payouts_by_resource[tile.resource].append((settlement.controller, 1))
                elif settlement.hasCity:
                    payouts_by_resource[tile.resource].append((settlement.controller, 2))

        for resource, payouts in payouts_by_resource.items():
            total_needed = sum(amount for _, amount in payouts)
            if total_needed > self.bank[resource]:
                continue
            for player_id, amount in payouts:
                self._take_from_bank(resource, amount, self.players[player_id])
                self.players[player_id].legacyResources[resource] += amount

    def _handle_seven(self, player_id):
        for player in self.players:
            if self._resource_count(player) > 7:
                self._discard_random_resources(player, self._resource_count(player) // 2)
        self._move_robber_and_steal(player_id)

    def _discard_random_resources(self, player, amount):
        for _ in range(amount):
            available = [resource for resource, count in player.resources.items() if count > 0]
            if not available:
                return
            resource = random.choice(available)
            player.resources[resource] -= 1
            self.bank[resource] += 1

    def _move_robber_and_steal(self, player_id):
        choices = [tile_id for tile_id in range(1, 20) if tile_id != self.robber_tile]
        self.robber_tile = random.choice(choices)
        victims = []
        for settlement_id in self.board[f"t{self.robber_tile}"].adjSettlements:
            settlement = self.board[f"s{settlement_id}"]
            if (settlement.hasSettlement or settlement.hasCity) and settlement.controller != player_id:
                victim = self.players[settlement.controller]
                if self._resource_count(victim) > 0 and victim.id not in victims:
                    victims.append(victim.id)
        if victims:
            self._steal_random_resource(player_id, random.choice(victims))

    def _steal_random_resource(self, player_id, victim_id):
        victim = self.players[victim_id]
        resources = [resource for resource, count in victim.resources.items() if count > 0]
        if not resources:
            return False
        resource = random.choice(resources)
        victim.resources[resource] -= 1
        self.players[player_id].resources[resource] += 1
        return True

    def legal_settlement_spots(self, player_id, setup=False):
        if self._settlement_count(player_id) >= self.PIECE_LIMITS["settlements"]:
            return []
        spots = []
        for settlement_id in range(1, 55):
            settlement = self.board[f"s{settlement_id}"]
            if settlement.hasSettlement or settlement.hasCity or settlement.blocked:
                continue
            if setup or any(
                self.board[f"r{road_id}"].hasRoad and self.board[f"r{road_id}"].controller == player_id
                for road_id in settlement.adjRoads
            ):
                spots.append(settlement_id)
        return spots

    def can_build_settlement(self, player_id):
        return bool(self.legal_settlement_spots(player_id)) and self._can_afford(player_id, self.BUILD_COSTS["settlement"])

    def build_settlement(self, player_id):
        spots = self.legal_settlement_spots(player_id)
        if not spots or not self._can_afford(player_id, self.BUILD_COSTS["settlement"]):
            return False
        self._spend(player_id, self.BUILD_COSTS["settlement"])
        self._place_settlement(player_id, random.choice(spots))
        self.update_longest_road()
        self._check_winner(player_id)
        return True

    def _place_settlement(self, player_id, settlement_id, setup=False):
        settlement = self.board[f"s{settlement_id}"]
        settlement.hasSettlement = True
        settlement.hasCity = False
        settlement.controller = player_id
        settlement.blocked = True
        for adjacent_id in settlement.adjSettlements:
            self.board[f"s{adjacent_id}"].blocked = True
        self.players[player_id].victory_points += 1
        self._refresh_all_player_options()

    def legal_city_spots(self, player_id):
        if self._city_count(player_id) >= self.PIECE_LIMITS["cities"]:
            return []
        return [
            settlement_id
            for settlement_id in range(1, 55)
            if self.board[f"s{settlement_id}"].hasSettlement
            and self.board[f"s{settlement_id}"].controller == player_id
        ]

    def can_build_city(self, player_id):
        return bool(self.legal_city_spots(player_id)) and self._can_afford(player_id, self.BUILD_COSTS["city"])

    def build_city(self, player_id):
        spots = self.legal_city_spots(player_id)
        if not spots or not self._can_afford(player_id, self.BUILD_COSTS["city"]):
            return False
        self._spend(player_id, self.BUILD_COSTS["city"])
        spot = random.choice(spots)
        settlement = self.board[f"s{spot}"]
        settlement.hasSettlement = False
        settlement.hasCity = True
        self.players[player_id].victory_points += 1
        self._refresh_all_player_options()
        self._check_winner(player_id)
        return True

    def legal_road_spots(self, player_id, free=False):
        if self._road_count(player_id) >= self.PIECE_LIMITS["roads"]:
            return []
        spots = []
        for road_id in range(1, 73):
            road = self.board[f"r{road_id}"]
            if not road.hasRoad and self._road_has_player_connection(player_id, road_id):
                spots.append(road_id)
        return spots

    def _road_has_player_connection(self, player_id, road_id):
        road = self.board[f"r{road_id}"]
        for settlement_id in road.adjSettlements:
            settlement = self.board[f"s{settlement_id}"]
            if (settlement.hasSettlement or settlement.hasCity) and settlement.controller == player_id:
                return True
            if (settlement.hasSettlement or settlement.hasCity) and settlement.controller != player_id:
                continue
            for adjacent_road_id in settlement.adjRoads:
                adjacent_road = self.board[f"r{adjacent_road_id}"]
                if adjacent_road.hasRoad and adjacent_road.controller == player_id:
                    return True
        return False

    def can_build_road(self, player_id):
        return bool(self.legal_road_spots(player_id)) and self._can_afford(player_id, self.BUILD_COSTS["road"])

    def build_road(self, player_id, free=False):
        spots = self.legal_road_spots(player_id, free=free)
        if not spots:
            return False
        if not free and not self._can_afford(player_id, self.BUILD_COSTS["road"]):
            return False
        if not free:
            self._spend(player_id, self.BUILD_COSTS["road"])
        self._place_road(player_id, random.choice(spots))
        self.update_longest_road()
        self._check_winner(player_id)
        return True

    def _place_road(self, player_id, road_id):
        road = self.board[f"r{road_id}"]
        road.hasRoad = True
        road.controller = player_id
        self._refresh_all_player_options()

    def compute_longest_road(self, player_id):
        player_roads = {
            road_id: self.board[f"r{road_id}"].adjSettlements
            for road_id in range(1, 73)
            if self.board[f"r{road_id}"].hasRoad and self.board[f"r{road_id}"].controller == player_id
        }
        incident = defaultdict(list)
        for road_id, (a, b) in player_roads.items():
            incident[a].append((road_id, b))
            incident[b].append((road_id, a))

        def blocked(vertex):
            settlement = self.board[f"s{vertex}"]
            return (settlement.hasSettlement or settlement.hasCity) and settlement.controller != player_id

        def dfs(vertex, visited_roads):
            best = 0
            for road_id, next_vertex in incident[vertex]:
                if road_id in visited_roads:
                    continue
                visited_roads.add(road_id)
                length = 1
                if not blocked(next_vertex):
                    length += dfs(next_vertex, visited_roads)
                best = max(best, length)
                visited_roads.remove(road_id)
            return best

        return max((dfs(vertex, set()) for vertex in incident), default=0)

    def update_longest_road(self):
        current_holder = next((player for player in self.players if player.longest_road), None)
        lengths = {player.id: self.compute_longest_road(player.id) for player in self.players}

        if current_holder and lengths[current_holder.id] >= 5:
            challenger = current_holder
            challenger_length = lengths[current_holder.id]
            for player in self.players:
                if lengths[player.id] > challenger_length:
                    challenger = player
                    challenger_length = lengths[player.id]

            if challenger.id == current_holder.id:
                return

            current_holder.longest_road = False
            current_holder.victory_points -= 2
            challenger.longest_road = True
            challenger.victory_points += 2
            self._check_winner(challenger.id)
            return

        if current_holder:
            current_holder.longest_road = False
            current_holder.victory_points -= 2

        best_length = max(lengths.values())
        if best_length < 5:
            return
        best_players = [player for player in self.players if lengths[player.id] == best_length]
        if len(best_players) != 1:
            return

        best_player = best_players[0]
        best_player.longest_road = True
        best_player.victory_points += 2
        self._check_winner(best_player.id)

    def can_port(self, player_id):
        return bool(self.legal_bank_trades(player_id))

    def port(self, player_id):
        trades = self.legal_bank_trades(player_id)
        if not trades:
            return False
        give, receive, ratio = random.choice(trades)
        player = self.players[player_id]
        player.resources[give] -= ratio
        self.bank[give] += ratio
        return self._take_from_bank(receive, 1, player)

    def legal_bank_trades(self, player_id):
        player = self.players[player_id]
        trades = []
        for give in self.RESOURCE_NAMES:
            ratio = self._trade_ratio(player_id, give)
            if player.resources[give] >= ratio:
                for receive in self.RESOURCE_NAMES:
                    if receive != give and self.bank[receive] > 0:
                        trades.append((give, receive, ratio))
        return trades

    def _trade_ratio(self, player_id, resource):
        ports = self._player_ports(player_id)
        if resource in ports:
            return 2
        if "any" in ports:
            return 3
        return 4

    def _player_ports(self, player_id):
        ports = set()
        for settlement_id, port in self.PORTS.items():
            settlement = self.board[f"s{settlement_id}"]
            if (settlement.hasSettlement or settlement.hasCity) and settlement.controller == player_id:
                ports.add(port)
        return ports

    def can_buy_dev_card(self, player_id):
        return bool(self.board["devStack"]) and self._can_afford(player_id, self.BUILD_COSTS["dev"])

    def buy_dev_card(self, player_id):
        if not self.can_buy_dev_card(player_id):
            return False
        self._spend(player_id, self.BUILD_COSTS["dev"])
        card = self.board["devStack"].pop()
        player = self.players[player_id]
        if card == "victoryPoint":
            player.upDevs["victoryPoint"] += 1
            player.victory_points += 1
            self._check_winner(player_id)
        else:
            player.newDevs[card] += 1
        return True

    def can_play_dev_card(self, player_id):
        if self.played_dev_this_turn:
            return False
        player = self.players[player_id]
        return any(player.downDevs[card] > 0 for card in ("knight", "roadBuilding", "yearOfPlenty", "monopoly"))

    def play_dev_card(self, player_id):
        if not self.can_play_dev_card(player_id):
            return False
        player = self.players[player_id]
        available = [card for card in ("knight", "roadBuilding", "yearOfPlenty", "monopoly") for _ in range(player.downDevs[card])]
        card = random.choice(available)
        player.downDevs[card] -= 1
        player.upDevs[card] += 1
        self.played_dev_this_turn = True

        if card == "knight":
            self._move_robber_and_steal(player_id)
            self.update_largest_army()
        elif card == "roadBuilding":
            for _ in range(2):
                if not self.build_road(player_id, free=True):
                    break
        elif card == "yearOfPlenty":
            for _ in range(2):
                available_resources = [resource for resource in self.RESOURCE_NAMES if self.bank[resource] > 0]
                if available_resources:
                    self._take_from_bank(random.choice(available_resources), 1, player)
        elif card == "monopoly":
            resource = random.choice(self.RESOURCE_NAMES)
            for opponent in self.players:
                if opponent.id == player_id:
                    continue
                amount = opponent.resources[resource]
                opponent.resources[resource] = 0
                player.resources[resource] += amount
        self._check_winner(player_id)
        return True

    def update_largest_army(self):
        current_holder = next((player for player in self.players if player.largest_army), None)
        holder_knights = current_holder.upDevs["knight"] if current_holder else 2
        challenger = current_holder
        challenger_knights = holder_knights
        for player in self.players:
            knights = player.upDevs["knight"]
            if knights >= 3 and knights > challenger_knights:
                challenger = player
                challenger_knights = knights

        if current_holder and challenger and challenger.id != current_holder.id:
            current_holder.largest_army = False
            current_holder.victory_points -= 2
        if challenger and not challenger.largest_army and challenger_knights >= 3:
            challenger.largest_army = True
            challenger.victory_points += 2
            self._check_winner(challenger.id)

    def play_turn(self, player_id):
        if self.game_over:
            return None
        if player_id != self.current_player:
            raise ValueError(f"It is player {self.current_player}'s turn, not player {player_id}'s")
        self._mature_dev_cards(player_id)
        self.played_dev_this_turn = False
        turn_number = self.turn_number
        victory_points_start = self.players[player_id].victory_points
        robber_tile_start = self.robber_tile
        roll = self.roll_dice()
        self.collect_resources(roll)
        actions_taken = 0
        action_records = []
        while not self.game_over and actions_taken < 100:
            actions = ["end_turn"]
            if self.can_build_settlement(player_id):
                actions.append("settlement")
            if self.can_build_city(player_id):
                actions.append("city")
            if self.can_build_road(player_id):
                actions.append("road")
            if self.can_port(player_id):
                actions.append("trade")
            if self.can_buy_dev_card(player_id):
                actions.append("buyDev")
            if self.can_play_dev_card(player_id):
                actions.append("playDev")

            action = random.choice(actions)
            if action == "end_turn":
                action_records.append(
                    {
                        "turn_number": turn_number,
                        "action_order": len(action_records) + 1,
                        "player_id": player_id,
                        "action_type": "end_turn",
                        "success": 1,
                        "victory_points_after": self.players[player_id].victory_points,
                    }
                )
                break
            success = False
            if action == "settlement":
                success = self.build_settlement(player_id)
            elif action == "city":
                success = self.build_city(player_id)
            elif action == "road":
                success = self.build_road(player_id)
            elif action == "trade":
                success = self.port(player_id)
            elif action == "buyDev":
                success = self.buy_dev_card(player_id)
            elif action == "playDev":
                success = self.play_dev_card(player_id)
            action_records.append(
                {
                    "turn_number": turn_number,
                    "action_order": len(action_records) + 1,
                    "player_id": player_id,
                    "action_type": action,
                    "success": int(success),
                    "victory_points_after": self.players[player_id].victory_points,
                }
            )
            actions_taken += 1

        self.current_player = (self.current_player + 1) % self.num_players
        self.turn_number += 1
        return {
            "turn_number": turn_number,
            "player_id": player_id,
            "dice_roll": roll,
            "actions_taken": actions_taken,
            "victory_points_start": victory_points_start,
            "victory_points_end": self.players[player_id].victory_points,
            "robber_tile_start": robber_tile_start,
            "robber_tile_after": self.robber_tile,
            "robber_moved": int(robber_tile_start != self.robber_tile),
            "game_over": int(self.game_over),
            "actions": action_records,
        }

    def _mature_dev_cards(self, player_id):
        player = self.players[player_id]
        for card in self.DEV_CARD_TYPES:
            player.downDevs[card] += player.newDevs[card]
            player.newDevs[card] = 0

    def get_game_state(self):
        return {
            "players": [
                {
                    "id": player.id,
                    "resources": player.resources,
                    "legacyResources": player.legacyResources,
                    "victory_points": player.victory_points,
                    "downDevs": player.downDevs,
                    "newDevs": player.newDevs,
                    "upDevs": player.upDevs,
                    "longest_road": player.longest_road,
                    "largest_army": player.largest_army,
                }
                for player in self.players
            ],
            "current_player": self.current_player,
            "turn_number": self.turn_number,
            "game_over": self.game_over,
            "winner": self.winner,
            "robber_tile": self.robber_tile,
            "bank": self.bank,
        }

    def _can_afford(self, player_id, cost):
        player = self.players[player_id]
        return all(player.resources[resource] >= amount for resource, amount in cost.items())

    def _spend(self, player_id, cost):
        player = self.players[player_id]
        for resource, amount in cost.items():
            player.resources[resource] -= amount
            self.bank[resource] += amount

    def _take_from_bank(self, resource, amount, player):
        if self.bank[resource] < amount:
            return False
        self.bank[resource] -= amount
        player.resources[resource] += amount
        return True

    def _resource_count(self, player):
        return sum(player.resources.values())

    def _settlement_count(self, player_id):
        return sum(
            1
            for settlement_id in range(1, 55)
            if self.board[f"s{settlement_id}"].hasSettlement
            and self.board[f"s{settlement_id}"].controller == player_id
        )

    def _city_count(self, player_id):
        return sum(
            1
            for settlement_id in range(1, 55)
            if self.board[f"s{settlement_id}"].hasCity
            and self.board[f"s{settlement_id}"].controller == player_id
        )

    def _road_count(self, player_id):
        return sum(
            1
            for road_id in range(1, 73)
            if self.board[f"r{road_id}"].hasRoad and self.board[f"r{road_id}"].controller == player_id
        )

    def _refresh_all_player_options(self):
        for player in self.players:
            player.roadSpots = set(self.legal_road_spots(player.id)) if hasattr(self, "board") else set()
            player.settlementSpots = set(self.legal_settlement_spots(player.id)) if hasattr(self, "board") else set()
            player.citySpots = set(self.legal_city_spots(player.id)) if hasattr(self, "board") else set()

    def _check_winner(self, player_id):
        if self.players[player_id].victory_points >= 10:
            self.game_over = True
            self.winner = player_id
