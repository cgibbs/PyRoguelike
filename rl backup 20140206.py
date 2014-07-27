import libtcodpy as libtcod
import math
import textwrap
import shelve
import string
import time
import random

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

INVENTORY_WIDTH = 50

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

MAP_WIDTH = 160
MAP_HEIGHT = 86

CAMERA_WIDTH = 80
CAMERA_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

BOSS_LEVEL_FREQ = 5 # levels at which bosses appear
FINAL_BOSS_LEVEL = 10 # level at which final boss appears (must be multiple 
                      # of BOSS_LEVEL_FREQ)

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
FOG_TORCH_RADIUS = 4

HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
FIREBALL_DAMAGE = 25
FIREBALL_RADIUS = 3
CONFUSED_NUM_TURNS = 10
CONFUSED_RANGE = 8
PUSH_RANGE = 3
ICE_WALL_RANGE = 8
ICE_WALL_DURATION = 8

MONSTER_CHASE_VALUE = 5 # number of turns for monsters to pursue player after
                        # leaving FOV

LEVEL_UP_BASE = 50
LEVEL_UP_FACTOR = 150
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30

HUNGER_MAX = 100

color_dark_wall     = libtcod.Color(  0,   0, 100)
color_light_wall    = libtcod.Color(130, 110,  50)
color_dark_ground   = libtcod.Color( 50,  50, 150)
color_light_ground  = libtcod.Color(200, 180,  50)
color_lava          = libtcod.Color(255,  68,  25)
color_acid          = libtcod.Color( 47, 245,  88)
color_lightning     = libtcod.Color(247, 250, 147)
color_sticky        = libtcod.yellow
color_water         = libtcod.Color( 56, 132, 255)
color_puddle        = libtcod.Color(137, 178, 245)
color_fog           = libtcod.Color(196, 200, 207)
color_blood         = libtcod.Color(131,   2,   2)

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Picogue', False)                        
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

descriptions = {'lesser healing potion': 'Bubbling and red, like every other healing potion ever made.',
                'healing potion': 'Bubbling and red, like every other healing potion ever made.',
                'greater healing potion': 'Bubbling and red, like every other healing potion ever made.',
                'scroll of confusion': 'This isn\'t really a \'scroll\', so much as a \'piece of paper filled with some sort of plant\'; try not to inhale while casting this spell.',
                'scroll of lightning': 'This spell fires a bolt of lightning at the nearest enemy, giving it a nice crispy layer.',
                'scroll of fireball': 'This spell hits an area with a large fireball, dealing damage to anything dumb enough to stand around (including you!).',
                'scroll of push': 'I\'m not going to tell you what this one does, but try it when enemies are close; you\'ll love it, I promise.',
                'scroll of ice wall': 'Creates a wall of ice in a cardinal direction from two selected points. The ice wall damages anyone standing near it, so don\'t block yourself in, stupid.',
                'sword': 'Pretty much what it says on the tin (that\'s not an idiom; you could only afford a tin sword).',
                'shield': 'You remember when you were a kid, and it snowed, and you would go out and slide down hills on garbage can lids? You can do that with this, too! However, the garbage can lid might offer more protection...',
                'butter knife': 'Your trusty slayer of dry toast; replace this as soon as possible.',
                'apple': 'A delicious Granny Smith apple.',
                'coconut bar': 'This says "James Almondysius Joyce" on the wrapper. It\'s a dense, Modernist candy bar, and takes about two years to finish, at which point you feel accomplished, but confused.',
                'peanut butter bar': 'This says "Arthur C. Clarke Bar" on the wrapper. It deals with a broad scope of flavors, and the ingredient list is very scientifically accurate.',
                'jellybeans': 'These say "The Great Gats\' Beans" on the wrapper. The golden beans taste like Champagne, and the green ones taste like foul dust, floating in the wake of dreams.',
                'licorice pastels': 'These say "Kurt Vonne-Good and Plenty" on the wrapper. They\'ve melted together, but a few seem to have come unstuck in the bag.',
                'chocolate morsels': 'These say "Rust in Peace... Tootsie Rolaris". The morsels are vaguely missile-shaped, and are partially coated in rust-colored sprinkles.',
                'can of spam': 'I can\'t think of a single funny thing that has ever been said or done which involved this food in any way whatsoever.',
                'sandwich': 'Why did you pick this up off of the dungeon floor? It wasn\'t even on a plate; it was just... Whatever. Just eat up, piggy.',
                'roast beef': 'Now, THIS is good eating. It\'s juicy and delicious, and smells faintly of healing potion.',
                'Orc': 'This brutish fellow seems somewhat displeased with you; dispatch him with all haste!',
                'Skeleton': 'I don\'t even want to talk about these, man. They send shivers down my spine.',
                'Mimic': 'This thing looks like an ordinary item, but with a mouthful of sharp teeth. They\'re just as lethal when mimicking tiny items, so keep your wits about you!',
                'Troll': 'FEE FYE FO F- oh wait, that\'s a giant. Trolls just roar, and pick their teeth with your femur. Try not to let that happen.',
                'Lich': 'Having trouble remembering how to pronounce "Lich"? Just remember: "Which Lich ate my soul in the ditch?", and not "Rick the Lich knows an immortality trick". Easy as pie.',
                'Dragon': 'Remember when you were a kid, and you caught lizards and did awful things to them? Well, they remembered.',
                'Boss dragon': 'Remember when you were an adult, and you stumbled into a dragon\'s den? Well, they remembered, and told their mum.'
                }

prefixes = {'fast': ['Blitz', 'Whip', 'Zip', 'Flash', 'Spring', 'Swift', 'Sparrow'],
            'strong': ['Brute', 'Crush', 'Slam', 'Punch', 'Grist'],
            'hp': ['Beef', 'Huge', 'Muscle', 'Gut']}

nouns = ['Heart', 'Claw', 'Arse', 'Crank', 'Knife', 'Blood', 'Hammer', 'Hook', 'Head']


# ---------- CLASSES - GENERAL ----------


class Object:
    def __init__(self, x, y, char, name, color, hunger_dec=1, hunger=100, blocks=False,
                 always_visible=False, fighter=None, ai=None, equipment=None, item=None,
                 inv=None, mod_set=None, mod_name=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.hunger_dec = hunger_dec
        self.hunger = hunger
        self.blocks = blocks
        self.always_visible = always_visible
        self.inv = inv
        self.spec = ''
        self.mod_name=mod_name # Strong, Weak, Electric, etc.

        # components, owned by the Object, which allow special behaviors

        self.fighter = fighter
        if self.fighter: # let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai: # let the ai component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item: # let the item component know who owns it
            self.item.owner = self

        self.equipment = equipment
        if self.equipment: # let the equipment component know what owns it
            self.equipment.owner = self
            self.item = Item() # a piece of equipment is always an Item (can be picked up and used)
            self.item.owner = self

        self.mod_set = mod_set # holds mods for object
        if self.mod_set is None:
            self.mod_set = set()

    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
        elif not is_blocked(self.x + dx, self.y):
            self.x += dx
        elif not is_blocked(self.x, self.y + dy):
            self.y += dy
        if self is not player and 'puddle' in map[self.x][self.y].mod_set:
            message("You hear splashing.", color_puddle)

    def move_towards(self, target_x, target_y):
        # vector from this object to target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (keeping direction), then round it and
        # convert to integer for map grid movement
        dx = dx / distance
        dy = dy / distance
        if dx < 0:
            dx = int(0 - math.ceil(abs(dx)))
        else:
            dx = int(math.ceil(dx))
        if dy < 0:
            dy = int(0 - math.ceil(abs(dy)))
        else:
            dy = int(math.ceil(dy))
        self.move(dx, dy)

    def distance(self, x, y):
        # return distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        # return distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    """def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) or \
           (self.always_visible and map[self.x][self.y].explored):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)"""

    def clear(self):
        libtcod.console_put_char(con, self.x-camera.x, self.y-camera.y, ' ', libtcod.BKGND_NONE)

    def send_to_back(self):
        # sets drawing order such that this object is drawn underneath other stuff
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def check_floor(self):
        # mod_set on objects holds resistances as the same value for Tile's mod_set
        tile = map[self.x][self.y]
        for mod in tile.mod_set:
            if mod not in self.mod_set:
                pass # TODO: handle damages, maybe as a list (for multiple damage types on floors)

    @property
    def full_name(self):
        if self.mod_name is not None:
            return self.mod_name + ' ' + self.name
        else:
            return self.name

class Player(Object):
    def move(self, dx, dy):
        global camera
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
        elif not is_blocked(self.x + dx, self.y):
            self.x += dx
        elif not is_blocked(self.x, self.y + dy):
            self.y += dy
        camera.move_to(player.x, player.y)

class Tile:
    def __init__(self, blocked, x, y, block_sight=None):
        # takes a set for modSet, and it determines the properties of a tile
        self.blocked = blocked
        self.explored = False
        self.x = x
        self.y = y
        self.H = None        # for use with A*
        self.parent = None
        self.mod_set = set()

        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        
    def add_mod(self, mod):
        self.mod_set.add(mod)

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return(center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CAMERA_WIDTH
        self.height = CAMERA_HEIGHT

    def fix_camera(self):
        if self.x < 0:
            self.x = 0
        elif self.x > (MAP_WIDTH - CAMERA_WIDTH):
            self.x = MAP_WIDTH - CAMERA_WIDTH
        if self.y < 0:
            self.y = 0
        elif self.y > (MAP_HEIGHT - CAMERA_HEIGHT):
            self.y = MAP_HEIGHT - CAMERA_HEIGHT

    def move_to(self, x, y):
        self.x = x - CAMERA_WIDTH/2
        self.y = y - CAMERA_HEIGHT/2
        self.fix_camera()
        
    
# ---------- CLASSES - COMBAT ----------


class Fighter:
    # combat-related properties and methods
    def __init__(self, hp, defense, power, attack_dice, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.attack_dice = attack_dice
        self.xp = xp
        self.death_function = death_function

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    @property
    def health_status(self):
        p = (self.hp * 100) / self.max_hp
        if p > 80:
            return 'Healthy'
        elif p > 60:
            return 'Lightly Injured'
        elif p > 40:
            return 'Injured'
        elif p > 20:
            return 'Badly Injured'
        elif p > 0:
            return 'Nearly Dead'
        elif p == 0:
            return 'Dead'
        
    def take_damage(self, damage):
        # separate from attack, for uses with stuff like poisons
        if damage > 0:
            self.hp -= damage

        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)
            if self.owner != player:
                player.fighter.xp += self.xp

    def attack(self, target):
        #global player
        damage = (self.power/2)
        #if (self.owner.inv is not None) and self.owner is not player:
        if (self.owner.inv is not None):
            for obj in self.owner.inv:
                if isinstance(obj.equipment, Weapon):
                    if obj.equipment.is_equipped:
                        damage += roll_dice(obj.equipment.attack_dice)
        else:
            damage += roll_dice(self.attack_dice)
        damage -= (target.fighter.defense/2)

        if damage > 0:
            message(self.owner.full_name + ' attacks ' + target.full_name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.full_name + ' attacks ' + target.full_name + ', but it has no effect!')

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


# ---------- CLASSES - AI ----------


class BasicMonster:
    # AI for basic (semi-brainless) monster
    def __init__(self):
            self.player_spotted = 0 # if monster has spotted player, give chase!
                                    # ticks down to 0, at which point monster
                                    # gives up
            
    def take_turn(self):
        # basic monster takes its turn, if visible
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            self.player_spotted = MONSTER_CHASE_VALUE

        if self.player_spotted > 0:
            # move to player
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)
            self.player_spotted -= 1

class SmartMonster:
    def __init__(self):
        self.player_known_location = None
        self.recalc_counter = None
        self.path = []
        self.target = None
        self.prev_target = None

    def take_turn(self):
        # Use a quick version of Dijkstra's pathfinding to attack the player.
        # Minimize damage along the way, if possible (from ice walls now, but
        # other stuff later, as well).
        # Also, make humanoid AI hold a "last known position" of player, 
        # go there if not in FOV, at which point it will be checked again by
        # take_turn() as normal

        # First step: get an A* implementation running, and understand how it works.
        #   Probably a good idea to use a similar map configuration to test.
        # Second step: implement it here.
        monster = self.owner
        if self.path is not None:
            pass # pursue the target; might need to be a call to an AI method
        elif libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            pass # get path with A* method

class ConfusedMonster:
    # AI for confused monster
    def __init__(self, old_ai, num_turns=CONFUSED_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
        
    def take_turn(self):
        if self.num_turns > 0:
            self.owner.move(libtcod.random_get_int(0,-1,1), libtcod.random_get_int(0,-1,1))
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.full_name + ' is no longer confused!', libtcod.red)

class MimicMonster:
    def take_turn(self):
        if self.owner.distance_to(player) <= 2:
            message('Suddenly, the ' + self.owner.full_name + ' springs to life! It\'s a mimic!', libtcod.red)
            self.owner.name = 'Mimic'
            ai = BasicMonster()
            ai.owner = self.owner
            self.owner.ai = ai
            self.owner.ai.take_turn()

class IceBlock:
    def take_turn(self):
        for object in objects:
            if self.owner.distance_to(object) <= 1 and object.fighter is not None:
                if object is not player:
                    message('The ice wall chills the ' + object.full_name + ' for 2 hit points.', libtcod.light_cyan)
                else:
                    message('The ice wall chills ' + object.full_name + ' for 2 hit points.', libtcod.light_cyan)
                object.fighter.take_damage(2)


# ---------- CLASSES - ITEMS ----------


class Item:
    # an item that can be picked up and used
    def __init__(self, use_function=None):
        self.use_function = use_function

    def use(self):
        # call the use_function, if defined

        # special case: if object has Equipment component, "use" toggles equip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        
        if self.use_function is None:
            message('The ' + self.owner.full_name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)
        
    def pick_up(self):
        # add to inventory, remove from map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.full_name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            if self.owner.full_name[0] not in 'aeiou':
                message('Picked up a ' + self.owner.full_name + '.', libtcod.yellow)
            else:
                message('Picked up an ' + self.owner.full_name + '.', libtcod.yellow)

            #special case: automatically equip, if slot is empty
            equipment = self.owner.equipment
            if equipment and not isinstance(equipment,Weapon) and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()
            if equipment and isinstance(equipment,Weapon):
                if get_equipped_in_slot('left hand') is None:
                    equipment.equip()

    def drop(self):
        # add to map at player's coordinates, and remove from inventory
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('Dropped a ' + self.owner.full_name + '.', libtcod.yellow)

class Food (Item):
    def __init__(self, value, freshness=-1, sec_function=None):
        Item.__init__(self)
        self.owner = None
        self.use_function=eat
        self.freshness = freshness # freshness of -1 means that the food never spoils
        self.value = value # how much hunger is restored
        self.sec_function = sec_function # some foods do special things in addition to being tasty

    def use(self): # cannot have target-based secondary functions
                   #(well, it CAN, but I don't want it to)
        self.use_function(self)
        if self.sec_function is not None:
            self.sec_function()
        inventory.remove(self.owner)

class Tome(Item):
    def __init__(self, use_function):
        Item.__init__(self, use_function)
        self.uses = 10
    def use(self):
        if self.use_function is None:
            message('The ' + self.owner.full_name + ' cannot be used.')
        else:
            self.use_function()
            self.uses -= 1
            if self.uses == 0:
                inventory.remove(self.owner)
                message('The ' + self.owner.full_name + ' crumbles into dust.', libtcod.violet)

class Equipment:
    # an object that can be equipped to provide bonuses
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot # tee hee! (don't be a baby, it's ironic.)
        self.is_equipped = False

    def toggle_equip(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        # equip object and show a message
        # dequip old item first

        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        message('Equipped ' + self.owner.full_name + ' on ' + self.slot + '.', libtcod.light_green)        

    def dequip(self):
        # dequip object and show a message
        if not self.is_equipped:
            return
        self.is_equipped = False
        message('Dequipped ' + self.owner.full_name + ' from ' + self.slot + '.', libtcod.light_yellow)

class Weapon(Equipment):
    def __init__(self, slot, attack_dice, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        Equipment.__init__(self, slot, power_bonus, defense_bonus, max_hp_bonus)
        self.attack_dice = attack_dice
    def equip(self):
        r_hand_check = get_equipped_in_slot('right hand')
        if r_hand_check is not None:
            old_equipment = get_equipped_in_slot('left hand')
            self.slot = 'left hand'
        else:
            old_equipment = r_hand_check
            self.slot = 'right hand'
        Equipment.equip(self)

    def dequip(self):
        Equipment.dequip(self)
        self.slot = 'hand'

                
# ---------- METHODS ----------


def handle_keys():
    global fov_recompute, keys, mouse, msg_index, game_msgs
    
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())    
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'

    if game_state == 'playing':
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1,1)
        elif key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1,1)
        elif key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1,-1)
        elif key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1,-1)
        elif key.vk == libtcod.KEY_KP5: # wait
            pass
        elif key.vk == libtcod.KEY_TAB:
            # show character info
            level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
            msgbox('Character Information\n' +
                   '\nName: ' + player.full_name +
                   '\nSpecialization: ' + player.spec +
                   '\nLevel: ' + str(player.level) +
                   '\nExperience: ' + str(player.fighter.xp) +
                   '\nExperience to level up: ' + str(level_up_xp) +
                   '\n\nMaximum HP: ' + str(player.fighter.max_hp) + ' (' + str(player.fighter.base_max_hp) + ')' +
                   '\nAttack: ' + str(player.fighter.power) + ' (' + str(player.fighter.base_power) + ')' +
                   '\nDefense: ' + str(player.fighter.defense) + ' (' + str(player.fighter.base_defense) + ')',
                   CHARACTER_SCREEN_WIDTH)
            return 'didnt-take-turn'
        elif key.vk == libtcod.KEY_PAGEUP:
            msg_index -= 5
            if msg_index < 0:
                msg_index = 0
            return 'didnt-take-turn'
        elif key.vk == libtcod.KEY_PAGEDOWN:
            msg_index += 5
            if msg_index > len(game_msgs) - MSG_HEIGHT:
                msg_index = len(game_msgs) - MSG_HEIGHT
            return 'didnt-take-turn'
        elif mouse.lbutton_pressed:
            # look at clicked
            look(get_names_under_mouse())
            return 'didnt-take-turn'
        else:
            key_char = chr(key.c)

            if key_char == 'g':
                # pick up item
                for object in objects:
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break
            if key_char == 'i':
                # show inventory
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other key to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                # show inventory; if item selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == '>':
                # go down stairs
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()

            if key_char == 'c':
                # carve a corpse into useable meat
                carve()
                return

            if key_char == 'l':
                choice = inventory_menu('Choose an item to examine.')
                render_all()
                if choice is not None:
                    look(choice.owner.full_name)

            if key_char == '?':
                keys_screen()

            if key_char == 'p': # debug commands
                cast_push()

            if key_char == 'w':
                cast_ice_wall()

            if key_char == 'a':
                cast_tile_effect('acid')

            if key_char == 'u':
                cast_tile_effect('puddle')
                
            if key_char == 'h':
                cast_lightning() # end debug commands
                    
            return 'didnt-take-turn'

def keys_screen():
    msgbox('CONTROLS:\n' +
           '\nArrow keys/Numpad: move' +
           '\nNumpad 5: wait one turn' +
           '\nTab: show character information' +
           '\nPgUp/PgDn: scroll message text' +
           '\ng: grab an item at your feet' +
           '\ni: show inventory' +
           '\nd: show inventory to drop an item' +
           '\nc: carve a corpse into meat' +
           '\nl: look at an item in the inventory' +
           '\n>: go down stairs',
           LEVEL_SCREEN_WIDTH)

def get_names_under_mouse():
    global mouse
    # returns a string with the names of all objects under the mouse
    (x, y) = (mouse.cx + camera.x, mouse.cy + camera.y)
    if y < SCREEN_HEIGHT and x < SCREEN_WIDTH and libtcod.map_is_in_fov(fov_map, x, y):
        names = [mod.capitalize() for mod in map[x][y].mod_set]
    else:
        names = []
        
    for obj in objects:
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
            names.append(obj.name)

    names = ', '.join(names)
    return names

def get_names_and_health_under_mouse():
    global mouse
    # returns a string with the names of all objects under the mouse
    (x, y) = (mouse.cx + camera.x, mouse.cy + camera.y)
    if y < SCREEN_HEIGHT and x < SCREEN_WIDTH and libtcod.map_is_in_fov(fov_map, x, y):
        names = [mod.capitalize() for mod in map[x][y].mod_set]
    else:
        names = []
    for obj in objects:
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
            if obj.fighter is not None:
                names.append(obj.name + ' (' + obj.fighter.health_status + ')')
            else:
                names.append(obj.name)

    names = ', '.join(names)
    return names

def get_full_names_under_mouse():
    global mouse
    # returns a string with the names of all objects under the mouse
    (x, y) = (mouse.cx + camera.x, mouse.cy + camera.y)
    if y < SCREEN_HEIGHT and x < SCREEN_WIDTH and libtcod.map_is_in_fov(fov_map, x, y):
        names = [mod.capitalize() for mod in map[x][y].mod_set]
    else:
        names = []
    for obj in objects:
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
            names.append(obj.full_name)

    names = ', '.join(names)
    return names

def look(names):
    for i in names.split(', '):
        if i in descriptions.keys():
            msgbox(descriptions[i])
            render_all()

def next_level():
    # advance player to the next dungeon level
    global dungeon_level
    
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp/4)

    message('After a moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    dungeon_level += 1
    make_map()
    initialize_fov()

def render_all():
    global fov_map, color_dark_wall, color_light_wall, color_dark_ground, color_light_ground
    global fov_recompute, hunger, msg_index

    if fov_recompute:
        # recompute FOV if need be (player movement or whatever)
        fov_recompute = False
        if 'fog' in map[player.x][player.y].mod_set:
            libtcod.map_compute_fov(fov_map, player.x, player.y, FOG_TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        else:
            libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        for y in range(camera.y, camera.y + CAMERA_HEIGHT):
            for x in range(camera.x, camera.x + CAMERA_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                mods = map[x][y].mod_set
                if not visible:
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_dark_ground, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x-camera.x, y-camera.y, libtcod.black, libtcod.BKGND_SET)
                else:
                    if wall:
                        #libtcod.console_set_default_foreground(con, libtcod.white)
                        libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_light_wall, libtcod.BKGND_SET)
                        
                    else:
                        if 'fog' in mods:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_fog, libtcod.BKGND_SET)
                        elif 'sticky' in mods:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_sticky, libtcod.BKGND_SET)
                        elif 'lava' in mods:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_lava, libtcod.BKGND_SET)
                        elif 'water' in mods:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_water, libtcod.BKGND_SET)
                        elif 'acid' in mods:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_acid, libtcod.BKGND_SET)
                        elif 'puddle' in mods:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_puddle, libtcod.BKGND_SET)
                        elif 'blood' in mods:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_blood, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x-camera.x, y-camera.y, color_light_ground, libtcod.BKGND_SET)
                    map[x][y].explored = True

    for object in objects: # prevents drawing over the player
        if object != player:
            if libtcod.map_is_in_fov(fov_map, object.x, object.y) or \
               (object.always_visible and map[object.x][object.y].explored):
                libtcod.console_set_default_foreground(con, object.color)
                libtcod.console_put_char(con, object.x-camera.x, object.y-camera.y, object.char, libtcod.BKGND_NONE)
    libtcod.console_set_default_foreground(con, player.color)
    libtcod.console_put_char(con, player.x-camera.x, player.y-camera.y, player.char, libtcod.BKGND_NONE)

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # basic GUI stuff
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    y = 1
    if len(game_msgs) > MSG_HEIGHT and (msg_index + MSG_HEIGHT) <= len(game_msgs):
        for (line, color) in game_msgs[msg_index : msg_index+MSG_HEIGHT]:
            libtcod.console_set_default_foreground(panel, color)
            libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1
    else:
        for (line, color) in game_msgs:
            libtcod.console_set_default_foreground(panel, color)
            libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1

    render_bar(1, 2, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)
    render_bar(1, 3, BAR_WIDTH, 'Hunger', player.hunger, HUNGER_MAX, libtcod.light_pink,
               libtcod.dark_pink)
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    render_bar(1, 4, BAR_WIDTH, 'XP', player.fighter.xp, level_up_xp, libtcod.green,
               libtcod.darker_green)
    
    libtcod.console_print_ex(panel, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    # render a stats bar (HP, exp, etc.)
    offset = (total_width / 4) - 1 # offset for rounding 
    divisor = total_width / 4      # rounding divisor
    bar_width = int(((float(value) + offset) / divisor) / (maximum / divisor) * total_width)

    # render background
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # render bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # centered text with values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))

def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    # create an off-screen console which represents the menu's window
    window = libtcod.console_new(width, height)

    # prints the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # prints all of the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of the "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0)

    time.sleep(0.1)
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    # convert the ASCII code to an index
    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None

def inventory_menu(header):
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        #options = [item.full_name for item in inventory]
        options = []
        sort_inventory()
        for item in inventory:
            text = item.full_name
            # show equip info, if equipment
            if item.equipment:
                if isinstance(item.equipment, Weapon):
                    text = text + ' (' + str(item.equipment.attack_dice[0]) + 'd' + str(item.equipment.attack_dice[1]) + ')'
                if item.equipment.is_equipped:
                    text = text + ' (on ' + item.equipment.slot + ')'
            elif isinstance(item.item, Tome):
                text += ' (' + str(item.item.uses) + ' uses)'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    if index is None or len(inventory) == 0:
        return None
    return inventory[index].item

def sort_inventory():
    global inventory
    equip_list = []
    item_list = []
    food_list = []
    for item in inventory:
        if item.equipment:
            equip_list.append(item)
        elif isinstance(item.item, Food):
            food_list.append(item)
        else:
            item_list.append(item)
    inventory = equip_list + item_list + food_list

def msgbox(text, width=50):
    menu(text, [], width)
    key = libtcod.console_wait_for_keypress(True)

def inputbox(text, width=50):
    global key, mouse

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    
    #calculate total height for the header (after auto-wrap) and one line per option
    text_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, text)
    if text == '':
        text_height = 1

    height = text_height + 2

    # create an off-screen console which represents the menu's window
    window = libtcod.console_new(width, height)

    # prints the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)

    # text entry and display loop
    command = ''
    while True:
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
        if key.vk =='':
            pass
        elif key.vk == libtcod.KEY_BACKSPACE:
            if len(command) > 0:
                command = command[0:-1]
        elif key.vk == libtcod.KEY_ESCAPE:
            return None
        elif key.vk == libtcod.KEY_ENTER:
            break
        else:
            k = chr(key.c)
            if k in string.ascii_letters:
                command += k
            
        libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT,text)
        
        libtcod.console_print_ex(window, 0, height - 1, libtcod.BKGND_NONE, libtcod.LEFT,  '>                       ')
        libtcod.console_flush()
        libtcod.console_print_ex(window, 0, height - 1, libtcod.BKGND_NONE, libtcod.LEFT,  '> ' + command)

        # blit the contents of the "window" to the root console
        x = SCREEN_WIDTH/2 - width/2
        y = SCREEN_HEIGHT/2 - height/2
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0)
        libtcod.console_flush()
        
    return command

def message(new_msg, color=libtcod.white):
    global msg_index
    # split the message, if need be
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # if full buffer, remove first line
        if len(game_msgs) == 100:
            del game_msgs[0]

        game_msgs.append( (line, color) )
        msg_index += 1
    if msg_index > MSG_HEIGHT:
        msg_index = len(game_msgs) - MSG_HEIGHT

def make_map():
    global map, objects, stairs, dungeon_level, camera

    if dungeon_level % BOSS_LEVEL_FREQ != 0:
        objects = [player]

        map = [[Tile(True, x, y)
                for y in range(MAP_HEIGHT) ]
               for x in range(MAP_WIDTH) ]

        rooms = []
        num_rooms = 0
    
        for r in range(MAX_ROOMS):
            w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
            y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

            new_room = Rect(x, y, w, h)

            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                create_room(new_room)
                place_objects(new_room)

                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                    camera.move_to(player.x, player.y)
                    
                else:
                    (prev_x, prev_y) = rooms[num_rooms-1].center()

                    if libtcod.random_get_int(0, 0, 1) == 1:
                        create_h_tunnel(prev_x, new_x, prev_y)
                        create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        create_v_tunnel(prev_y, new_y, prev_x)
                        create_h_tunnel(prev_x, new_x, new_y)

                rooms.append(new_room)
                num_rooms += 1
        stairs = Object(new_x, new_y, '>', 'stairs', libtcod.white, always_visible=True)
        objects.append(stairs)
        stairs.send_to_back() # drawn below monsters
        
    else:
        make_boss_map()

def make_boss_map():
    # creates boss maps, one for every five levels (I know that's only two,
    # shut up); if final stage, no stairs. 
    global map, objects, stairs, dungeon_level

    objects = [player]

    map = [[Tile(True, x, y)
            for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0
    
    w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
    y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

    entrance_room = Rect(MAP_WIDTH/4, (MAP_HEIGHT*3)/4, ROOM_MIN_SIZE, ROOM_MIN_SIZE)
    create_room(entrance_room)

    boss_room = Rect((MAP_WIDTH/4) - ROOM_MAX_SIZE, (MAP_HEIGHT/4), ROOM_MAX_SIZE * 2, ROOM_MAX_SIZE * 2)
    create_room(boss_room)

    (entrance_x, entrance_y) = entrance_room.center()
    player.x = entrance_x
    player.y = entrance_y
    camera.move_to(player.x - CAMERA_WIDTH/2, player.y - CAMERA_HEIGHT/2)
    (boss_x, boss_y) = boss_room.center()
    place_objects(boss_room)

    create_v_tunnel(boss_y, entrance_y, entrance_x)

    if dungeon_level != FINAL_BOSS_LEVEL:
        stairs = Object(new_x, new_y, '>', 'stairs', libtcod.white, always_visible=True)
        objects.append(stairs)
        stairs.send_to_back()

def create_room(room):
    global map
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def place_objects(room):
    # max number of monsters per room
    max_monsters = from_dungeon_level([[2,1], [3,4], [5,6], [1,10]])
    
    # spawn monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(x, y):
            monster = create_monster(x, y)
            objects.append(monster)

    # maximum number of items per room
    max_items = from_dungeon_level([[1,1], [2,4]])

    # spawn items
    num_items = libtcod.random_get_int(0,0, max_items)
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
        if not is_blocked(x,y):
            item = create_item(x, y)
            objects.append(item)
            item.send_to_back()

    # maximum number of food items per room
    max_food = max_items     # just for now, for the sake of tweaking
    
    # spawn food
    num_food = libtcod.random_get_int(0, 0, max_food)
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(x,y):
            food = create_food(x, y)                
            objects.append(food)
            food.send_to_back()

def create_monster(x, y):
    # chance of each monster (figure out a better way to handle boss frequency)
    monster_chances = {}
    monster_chances['orc']          = from_dungeon_level([[70,1], [0,5], [70,6], [0,10]])
    monster_chances['mimic']        = from_dungeon_level([[15,2], [0,5], [25,6],[0,10]])
    monster_chances['skeleton']     = from_dungeon_level([[25,2], [0,5], [60,6], [0,10]])
    monster_chances['troll']        = from_dungeon_level([[10,3], [0,5], [25,6], [0,10]])
    monster_chances['lich']         = from_dungeon_level([[10,3], [0,5], [35,6], [0,10]])
    monster_chances['dragon']       = from_dungeon_level([[100,5], [0,6]])
    monster_chances['boss_dragon']  = from_dungeon_level([[100,FINAL_BOSS_LEVEL]])
    
    choice = random_choice(monster_chances)

    if choice == 'orc':
        fighter_component = Fighter(hp=15, defense=0, power=0, xp=15, attack_dice=(1,4),
                                    death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'O', 'Orc', libtcod.desaturated_green,
                         blocks=True, fighter=fighter_component,
                         ai=ai_component)
    elif choice == 'skeleton':
        fighter_component = Fighter(hp=26, defense=2, power=2, attack_dice=(1,6),
                                    xp=25, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'S', 'Skeleton', libtcod.grey,
                         blocks=True, fighter=fighter_component,
                         ai=ai_component)
    elif choice == 'mimic':
        fighter_component = Fighter(hp=25, defense=2, power=3, attack_dice=(2,4),
                                    xp=50, death_function=mimic_death)
        ai_component = MimicMonster()
        item = create_item(x, y) # item for the mimic to... mimic
        monster = Object(x, y, item.char, item.full_name, item.color,
                         blocks=True, fighter=fighter_component, ai=ai_component, inv=[item])
    elif choice == 'troll':
        fighter_component = Fighter(hp=54, defense=3, power=3, attack_dice=(2,8),
                                    xp=150, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'T', 'Troll', libtcod.darker_green,
                         blocks=True, fighter=fighter_component,
                         ai=ai_component)
    elif choice == 'lich':
        fighter_component = Fighter(hp=45, defense=5, power=3, attack_dice=(2,6),
                                    xp=240, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'L', 'Lich', libtcod.desaturated_blue,
                         blocks=True, fighter=fighter_component,
                         ai=ai_component)
    elif choice == 'dragon':
        fighter_component = Fighter(hp=100, defense=4, power=5, attack_dice=(2,10),
                                    xp=500, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'D', 'Dragon', libtcod.desaturated_red,
                         blocks=True, fighter=fighter_component,
                         ai=ai_component) 
    elif choice == 'boss_dragon':
        fighter_component = Fighter(hp=160, defense=6, power=6, attack_dice=(2,12),
                                    xp=1000, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'D', 'Dragon', libtcod.desaturated_red,
                         blocks=True, fighter=fighter_component,
                         ai=ai_component)

    c = libtcod.random_get_int(0, 1, 100)

    if c < 7:
        m = libtcod.random_get_int(0, 1, 3)
        n = random.choice(nouns)
        if m == 1:
            monster.fighter.attack_dice = (monster.fighter.attack_dice[0]+1, monster.fighter.attack_dice[1]) #fast monsters get another die
            pre = random.choice(prefixes['fast'])
        elif m == 2:
            monster.fighter.attack_dice = (monster.fighter.attack_dice[0], monster.fighter.attack_dice[1]+2) #strong monsters get a bigger die
            pre = random.choice(prefixes['strong'])
        elif m == 3:
            monster.fighter.hp += 20 #hp monsters get more hp
            pre = random.choice(prefixes['hp'])
        monster.name = pre + n + ' the ' + monster.name
        print monster.name
        monster.color = libtcod.grey
        monster.fighter.xp += monster.fighter.xp/2
    return monster


def create_item(x, y):
    # chance of each item (default is 0 at level 1, goes up after)
    item_chances = {}
    item_chances['heal_lesser'] = 35
    item_chances['heal'] = from_dungeon_level([[20,4], [40,6]])
    item_chances['heal_greater'] = from_dungeon_level([[20,6], [40,8]])
    item_chances['confuse'] = from_dungeon_level([[20,2]])
    item_chances['lightning'] = from_dungeon_level([[25,4]])
    item_chances['fireball'] = from_dungeon_level([[25, 5]])
    item_chances['push'] = from_dungeon_level([[15,4], [25,7]])
    item_chances['ice_wall'] = from_dungeon_level([[20,2], [30, 5]])
    item_chances['sword'] = from_dungeon_level([[20,3],[30,6]])
    item_chances['shield'] = from_dungeon_level([[12,3],[24,6]])
    item_chances['tome_heal_lesser'] = from_dungeon_level([[5,2]])
    item_chances['tome_heal'] = from_dungeon_level([[5,4], [10,7]])
    item_chances['tome_heal_greater'] = from_dungeon_level([[5,6], [10,9]])
    
    choice = random_choice(item_chances)
    
    if choice == 'heal_lesser':
        item_component = Item(use_function=cast_heal_lesser)
        item = Object(x, y, '!', 'lesser healing potion', libtcod.violet, item=item_component)
    elif choice == 'heal':
        item_component = Item(use_function=cast_heal)
        item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
    elif choice == 'heal_greater':
        item_component = Item(use_function=cast_heal_greater)
        item = Object(x, y, '!', 'greater healing potion', libtcod.violet, item=item_component)
    elif choice == 'tome_heal_lesser':
        item_component = Tome(cast_heal_lesser)
        item = Object(x, y, '=', 'tome of lesser healing', libtcod.blue, item=item_component)
    elif choice == 'tome_heal':
        item_component = Tome(cast_heal)
        item = Object(x, y, '=', 'tome of healing', libtcod.blue, item=item_component)
    elif choice == 'tome_heal_greater':
        item_component = Tome(cast_heal_greater)
        item = Object(x, y, '=', 'tome of greater healing', libtcod.blue, item=item_component)
    elif choice == 'lightning':
        item_component = Item(use_function=cast_lightning)
        item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)
    elif choice == 'confuse':
        item_component = Item(use_function=cast_confuse)
        item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)
    elif choice == 'fireball':
        item_component = Item(use_function=cast_fireball)
        item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
    elif choice == 'push':
        item_component = Item(use_function=cast_push)
        item = Object(x, y, '#', 'scroll of push', libtcod.light_yellow, item=item_component)
    elif choice == 'ice_wall':
        item_component = Item(use_function=cast_ice_wall)
        item = Object(x, y, '#', 'scroll of ice wall', libtcod.light_yellow, item=item_component)
    elif choice == 'sword':
        equipment_component = Weapon(slot='hand', power_bonus=2, attack_dice=(1,8))
        item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
    elif choice == 'shield':
        equipment_component = Weapon(slot='hand', defense_bonus=1, attack_dice=(0,0))
        item = Object(x, y, '[', 'shield', libtcod.sky, equipment=equipment_component)

    return item

def create_food(x, y):
    # chance of each food item
    food_chances = {}
    food_chances['apple'] = 35
    food_chances['coconut_bar'] = from_dungeon_level([[20,2]])
    food_chances['peanut_butter_bar'] = from_dungeon_level([[20,2]])
    food_chances['jellybeans'] = from_dungeon_level([[20,2]])
    food_chances['licorice_pastels'] = from_dungeon_level([[20,2]])
    food_chances['chocolate_morsels'] = from_dungeon_level([[20,2]])
    food_chances['spam'] = from_dungeon_level([[20,2]])
    food_chances['sandwich'] = from_dungeon_level([[25,4]])
    food_chances['roast_beef'] = from_dungeon_level([[25, 5]])

    choice = random_choice(food_chances)
    
    if choice == 'apple':
        food_component = Food(10, freshness=50)
        food = Object(x, y, 'a', 'apple', libtcod.light_pink, item=food_component)
    elif choice == 'coconut_bar':
        food_component = Food(20, freshness=100)
        food = Object(x, y, 'c', 'coconut bar', libtcod.light_pink, item=food_component)
    elif choice == 'peanut_butter_bar':
        food_component = Food(20, freshness=100)
        food = Object(x, y, 'c', 'peanut butter bar', libtcod.light_pink, item=food_component)
    elif choice == 'jellybeans':
        food_component = Food(20, freshness=100)
        food = Object(x, y, 'c', 'jellybeans', libtcod.light_pink, item=food_component)
    elif choice == 'licorice_pastels':
        food_component = Food(20, freshness=100)
        food = Object(x, y, 'c', 'licorice pastels', libtcod.light_pink, item=food_component)
    elif choice == 'chocolate_morsels':
        food_component = Food(20, freshness=100)
        food = Object(x, y, 'c', 'chocolate morsels', libtcod.light_pink, item=food_component)
    elif choice == 'spam':
        food_component = Food(35, freshness=-1)
        food = Object(x, y, 'p', 'can of spam', libtcod.light_pink, item=food_component)
    elif choice == 'sandwich':
        food_component = Food(40, freshness=40)
        food = Object(x, y, 's', 'sandwich', libtcod.light_pink, item=food_component)
    else:
        food_component = Food(80, freshness=30, sec_function=cast_heal_lesser)
        food = Object(x, y, 'r', 'roast beef', libtcod.light_pink, item=food_component)

    return food

def random_choice_index(chances):
    # choose from list of chances, returning its index.
    # the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    # choose from a dictionary of chances, returning a key.
    # also, chance has a HUGE dict
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def from_dungeon_level(table):
    # return a value that depends on level
    # table specifies what happens after each level, default is 0
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def is_blocked(x, y):
    if map[x][y].blocked:
        return True

    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def closest_monster(max_range):
    # find closest enemy, up to range, in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            dist = player.distance_to(object)
            if dist < closest_dist:
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def target_tile(max_range=None):
    # return the position of a tile left-clicked in the player's FOV (optionally in a range) or
    # (None,None) if right-clicked
    global key, mouse
    while True:
        # render the screen, erasing inventory and showing names of objects under the mouse
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (mouse.cx + camera.x, mouse.cy + camera.y)

        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x,y) <= max_range)):
            return(x, y)
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None,None)

def target_monster(max_range=None):
    # returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:
            return None

        # return the first clicked monster, otherwise continue looking
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj

def in_player_range(max_range=None):
    # returns list of monsters within a range around the player, within the FOV
    monsters = []
    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            if max_range:
                dist = player.distance_to(object)
                if dist <= max_range:
                    monsters.append(object)
            else:
                monsters.append(object)
    return monsters

def in_object_range(obj, max_range):
    # returns list of monsters within a range around the object
    monsters = []
    for object in objects:
        if object.fighter:
            dist = obj.distance_to(object)
            if dist <= max_range:
                monsters.append(object)

    return monsters

def player_move_or_attack(dx, dy):
    global fov_recompute
    
    x = player.x + dx
    y = player.y + dy
    
    # check for attackable object
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break
    
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx,dy)
        fov_recompute = True

def check_level_up():
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your skill in combat is renowned! You\'ve reached level ' + str(player.level) + '!', libtcod.green)

        # choose a level-up bonus
        choice = None
        while choice == None:
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP, from ' + str(player.fighter.base_max_hp) + ')',
                           'Strength (+1 attack, from ' + str(player.fighter.base_power) + ')',
                           'Agility (+1 defense, from ' + str(player.fighter.base_defense) + ')'],
                          LEVEL_SCREEN_WIDTH)

            if choice == 0:
                player.fighter.base_max_hp += 20
            elif choice == 1:
                player.fighter.base_power += 1
            elif choice == 2:
                player.fighter.base_defense += 1
            player.fighter.hp = player.fighter.max_hp

def check_hunger():
    global steps, hunger_msg # if True, the player has been informed
    steps += 1
    if steps == 5:
        for item in inventory: # rot the food
            if isinstance(item.item, Food):
                if item.item.freshness > 0:
                    item.item.freshness -= 1
                elif item.item.freshness == 0:
                    try:
                        item.full_name.index('fresh')
                    except ValueError:
                        try:
                            item.name.index('rotten')
                        except ValueError:
                            item.name = 'rotten ' + item.name
                    item.name = item.name.replace('fresh','rotten')
                    
        if player.hunger > 0:
            player.hunger -= 1
        else: 
            player.fighter.take_damage(player.hunger_dec)
            
        if player.hunger < 40 and player.hunger % 5 == 0:
            message('Your stomach growls.', libtcod.light_pink)
        if player.hunger == 20:
            message('You are beginning to feel dizzy from hunger.', libtcod.light_pink)
        if player.hunger == 0 and hunger_msg == False:
            message('Your body is starting to consume itself. Find food now!', libtcod.red)
            hunger_msg = True
        steps = 0

def check_ice_counter():
    global ice_counter, objects
    if ice_counter is not None: 
        if ice_counter > 0:
            ice_counter -= 1
        else:
            for obj in objects[:]:          # so that it doesn't modify the list over which it's iterating, causing
                                            # screwy behavior (like only half of the ice blocks disappearing)
                if obj.name == 'ice wall':
                    objects.remove(obj)
            ice_counter = None
        

def get_equipped_in_slot(slot):
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj): # change this is you want monster equipment
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []

def eat(owner):
    # should be player-only, for now
    # kinda hacky, but using self is invalid, so the message uses owner.owner instead
    global hunger_msg
    message('You eat the ' + owner.owner.full_name + '.') 
    if owner.freshness != 0:
        hunger_msg = False # no longer consuming self, so warn them again next time
        message('Mmm! It\'s quite tasty, for something you just found in a dungeon.', libtcod.light_pink)
        player.hunger += owner.value
        if player.hunger > HUNGER_MAX:
            player.hunger = HUNGER_MAX
    else:
        message('Blech! It\'s spoiled!', libtcod.orange) # add a debuff or poison, eventually
        player.hunger -= owner.value
        if player.hunger < 0:
            player.hunger = 0

def carve():
    # carve the meat from an enemy's dead, deceased, lifeless body
    # hacky use of repeated code from closest_monster to save some refactoring
    closest_enemy = None
    closest_dist = 1
    for object in objects:
        if not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y) and object.item is None:
            dist = player.distance_to(object)
            if dist < closest_dist:
                closest_enemy = object
                closest_dist = dist
    if closest_enemy is None:
        message('You must be standing on a corpse to carve (put on some old boots first).')
    else:
        try:
            closest_enemy.full_name.index('Skele')
        except ValueError:
            if libtcod.random_get_int(0,0,10) < 8:
                food_component = Food(30, freshness=40)
                food = Object(0, 0, '#', 'fresh meat', libtcod.light_pink, item=food_component)
                inventory.append(food)
                message('You manage to carve some edible meat from the corpse.', libtcod.light_pink)
            else:
                message('You ham-fistedly hack up the corpse, leaving nothing big enough to take with you.')
            objects.remove(closest_enemy)
            return
            
        message('It\'s a Skeleton, bro. I think someone beat you to it.', libtcod.white)
        message('Still... you kick the bones around, because fuck Skeletons!', libtcod.white)
        objects.remove(closest_enemy) # in case the skeleton is in the way of another corpse

def roll_dice(dice):
    return sum(libtcod.random_get_int(0,1,dice[1]) for i in range(0,dice[0]))

def check_floor():
    for obj in objects:
        mods = map[obj.x][obj.y].mod_set.difference(obj.mod_set) # items in tile.mod_set and not in obj.mod_set
        ele_damage(obj, mods)
            

def ele_damage(obj, mods, damage=None):
    # deal elemental damage for each modifier from a floor tile
    # written to be useable for other elemental damage
    global map
    
    if not isinstance(mods, set):
        mods = set([mods])
    if damage is None:
            damage = roll_dice((1,3))
    if obj.fighter is not None:   
        if ('lava' or 'fire') in mods:
            message(obj.full_name + ' is burned for ' + str(damage) + ' hit points!', color_lava)
            obj.fighter.take_damage(damage)
        if 'acid' in mods:
            message(obj.full_name + ' is corroded for ' + str(damage) + ' hit points!', color_acid)
            obj.fighter.take_damage(damage)
        if 'lightning' in mods:
            lightning_on_tile(obj.x, obj.y, damage)
            

def lightning_on_tile(x,y, damage):
    # hit the tile with lightning, and conduct the electricity to other wet tiles
    first_tile = map[x][y]
    if 'water' in first_tile.mod_set or 'puddle' in first_tile.mod_set:
        tiles = [first_tile]
        for t in tiles:
            tile_list = [map[x][t.y-1:t.y+2] for x in range(t.x-1,t.x+2)]
            for l in tile_list:
                for tile in l:
                    #if ('puddle' in tile.mod_set or 'water' in tile.mod_set) and tile not in tiles:
                    if ('puddle' or 'water') in tile.mod_set and tile not in tiles:
                        tiles.append(tile) # purposely modifying the list being iterated over
        for t in tiles:
            for o in objects:
                if o.fighter is not None and (o.x, o.y) == (t.x, t.y):
                    message(o.full_name + ' is shocked for ' + str(damage) + ' hit points!', color_lightning)
                    o.fighter.take_damage(damage)
                        
    else:
        for o in objects:# if obj at tile, FIX         
            if o.fighter is not None and (o.x, o.y) == (x, y):
                message(o.full_name + ' is shocked for ' + str(damage) + ' hit points!', color_lightning)
                o.fighter.take_damage(damage)


# ---------- "Spell" Methods ----------


def cast_heal():
    # heal the owner
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)

def cast_heal_lesser():
    # heal the owner
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    message('Your wounds start to feel a bit better!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT/2)

def cast_heal_greater():
    # heal the owner
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    message('Your wounds start to feel much better!', libtcod.light_violet)
    player.fighter.heal(int(HEAL_AMOUNT*1.5)) # int-wrapped as a safety measure

def cast_lightning():
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:
        message('No enemy close enough to strike.', libtcod.red)
        return 'cancelled'

    message('A lightning bolt shoots out and strikes the ' + monster.full_name +
            ' with a peal of thunder!', color_lightning)
    ele_damage(monster, 'lightning', 20)

def cast_confuse():
    # ask player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(CONFUSED_RANGE)
    if monster is None:
        message('No enemy close enough to confuse.', libtcod.red)
        return 'cancelled'

    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster # tell the new component who owns it
    message('The eyes of the ' + monster.full_name + ' look glassy, as it begins to gibber and stumble around.', libtcod.light_green)

def cast_fireball():
    # ask for a target tile
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None:
        return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

    for obj in objects:
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter and obj != player:
            message('The ' + obj.full_name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)
    if player.distance(x, y) <= FIREBALL_RADIUS:
        message(player.full_name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
        player.fighter.take_damage(FIREBALL_DAMAGE)

def cast_push():
    monsters = in_player_range(PUSH_RANGE)
    if monsters == []:
        message('No enemies within range.', libtcod.red)
        return 'cancelled'
    for monster in monsters:
        dx = monster.x - player.x
        dy = monster.y - player.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = dx / distance
        dy = dy / distance
        if dx < 0:
            dx = int(0 - math.ceil(abs(dx)))
        else:
            dx = int(math.ceil(dx))
        if dy < 0:
            dy = int(0 - math.ceil(abs(dy)))
        else:
            dy = int(math.ceil(dy))

        damage = 5
        while not is_blocked(monster.x + dx, monster.y + dy):
            monster.move(dx, dy)
            damage += 2
        
        message(monster.full_name + ' hit the wall, causing ' + str(damage) + ' hit points\' worth of fractures!', libtcod.orange)
        monster.fighter.take_damage(damage)

def cast_ice_wall():
    # ask player for end-points of a continuous ice wall; damages nearby enemies
    global ice_counter, fov_recompute
    
    message('Choose two tiles in a cardinal line.', libtcod.light_cyan)
    beg = target_tile(ICE_WALL_RANGE)
    if beg[0] is None: return 'cancelled'
    libtcod.console_set_char_background(con, beg[0], beg[1], libtcod.orange, libtcod.BKGND_SET)
    libtcod.console_flush()
    end = target_tile(ICE_WALL_RANGE)
    if end[0] is None: return 'cancelled'
    if not (beg[0] == end[0] or beg[1] == end[1]):
        message('Not a straight line.', libtcod.red)
        fov_recompute = True
        render_all()
        libtcod.console_flush()
        return 'cancelled'
    else:
        if beg[1] == end[1]:
            d = end[0] - beg[0]
            if d > 0:
                for x in range(beg[0], beg[0] + d + 1):
                    ai_component = IceBlock()
                    block = Object(x, beg[1], '*', 'ice wall', libtcod.light_cyan,
                             blocks=True, ai=ai_component)
                    objects.append(block)
            else:
                for x in range(beg[0], beg[0] + d - 1, -1):
                    ai_component = IceBlock()
                    block = Object(x, beg[1], '*', 'ice wall', libtcod.light_cyan,
                             blocks=True, ai=ai_component)
                    objects.append(block)
            
        else:
            d = end[1] - beg[1]
            if d > 0:
                for y in range(beg[1], beg[1] + d + 1):
                    ai_component = IceBlock()
                    block = Object(beg[0], y, '*', 'ice wall', libtcod.light_cyan,
                             blocks=True, ai=ai_component)
                    objects.append(block)
            else:
                for y in range(beg[1], beg[1] + d - 1, -1):
                    ai_component = IceBlock()
                    block = Object(beg[0], y, '*', 'ice wall', libtcod.light_cyan,
                             blocks=True, ai=ai_component)
                    objects.append(block)

        ice_counter = ICE_WALL_DURATION
    fov_recompute = True
    libtcod.console_flush()

def tile_effect(x, y, effect, of_ten=7):
    # ask player for center of an acid splash, which is permanent, and deals damage to anything on the tile
    if x is None or y is None: return 'cancelled'
    l = [map[xl][y-1:y+2] for xl in range(x-1,x+2)]
    for tile_list in l:
        for tile in tile_list:
            r = libtcod.random_get_int(0,1,10)
            if r <= of_ten:
                tile.add_mod(effect)
    fov_recompute = True
    libtcod.console_flush()

def cast_tile_effect(effect):
    global fov_recompute
    # ask player for center of an acid splash, which is permanent, and deals damage to anything on the tile
    message('Choose a tile.', libtcod.light_cyan)
    (x,y) = target_tile()
    if x is None or y is None: return 'cancelled'
    tile_effect(x, y, effect)

def cast_puddle(): # these are just helper methods for Item's `use_function`
    cast_tile_effect('puddle')
def cast_acid():
    cast_tile_effect('acid')
def cast_lava():
    cast_tile_effect('lava')

    

# ---------- METHODS - DEATH ----------


def player_death(player):
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'

    # make player into a corpse
    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster):
    # turn monster into corpse; doesn't block, can't attack or be attacked,
    # and doesn't move
    message(monster.full_name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + 'EXP.', libtcod.green)
    monster.char = '%'
    monster.color = libtcod.red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.full_name
    if monster.inv is not None:
        for i in monster.inv:
            i.x = monster.x
            i.y = monster.y
            objects.append(i)
    monster.send_to_back()
    tile_effect(monster.x, monster.y, 'blood', 5)

def mimic_death(monster):
    # turn monster into corpse; doesn't block, can't attack or be attacked,
    # and doesn't move
    message(monster.full_name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + 'EXP.', libtcod.green)
    objects.remove(monster)
    if monster.inv is not None:
        for i in monster.inv:
            i.x = monster.x
            i.y = monster.y
            objects.append(i)

def boss_death(monster):
    global game_state
    
    monster_death(monster)
    msgbox('You have conquered the dungeon, and proven your worth! Congrats! There will be some rewards here,' +
            ' eventually.')

    # save the player's information to the Hall of Legends here
    game_state = 'won'


# ---------- Main Loop Initialization


def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level, steps, hunger_msg, ice_counter
    global msg_index, camera
    msg_index = 0

    name = inputbox('Enter your name, brave warrior\n')
    if name == '':
        name = 'Player'
    elif name is None:
        main_menu()
    else:
        name = name.capitalize()

    inventory = []
    game_msgs = []

    message('Prepare to perish in a game of Chance, stranger. Welcome to Picogue!', libtcod.red)
    message('Press \'?\' for help.', libtcod.red)

    libtcod.console_flush()
    
    # create player object
    choice = None

    while choice is None:
        choice = menu('Choose a specialization', ['Swordsman', 'Dodgemaster', 'Juggernaut', 'Highlander',
                                         'Street Fighter', 'Priest'], 50)

        if choice == 0:
            fighter_component = Fighter(hp=100, defense=1, power=1, xp=0, attack_dice=(1,4),
                                        death_function=player_death)
            player = Player(0, 0, '@', name, libtcod.white, blocks=True, fighter=fighter_component)

            equipment_component = Weapon(slot='hand', power_bonus=1, attack_dice=(1,6))
            obj = Object(0, 0, '-', 'sword', libtcod.sky, equipment=equipment_component)
            inventory.append(obj)
            equipment_component.equip()
            obj.always_visible = True

            player.spec = 'Swordsman'
            
        elif choice == 1:
            fighter_component = Fighter(hp=100, defense=1, power=1, xp=0, attack_dice=(1,4),
                                        death_function=player_death)
            player = Player(0, 0, '@', name, libtcod.white, blocks=True, fighter=fighter_component)
            
            equipment_component = Weapon(slot='hand', power_bonus=1, attack_dice=(1,6))
            obj = Object(0, 0, '-', 'butter knife', libtcod.sky, equipment=equipment_component)
            inventory.append(obj)
            equipment_component.equip()
            obj.always_visible = True

            player.spec = 'Dodgemaster'

        elif choice == 2:
            fighter_component = Fighter(hp=120, defense=1, power=1, xp=0, attack_dice=(1,4),
                                        death_function=player_death)
            player = Player(0, 0, '@', name, libtcod.white, blocks=True, fighter=fighter_component)
            
            equipment_component = Weapon(slot='hand', power_bonus=1, attack_dice=(1,6))
            obj = Object(0, 0, '-', 'butter knife', libtcod.sky, equipment=equipment_component)
            inventory.append(obj)
            equipment_component.equip()
            obj.always_visible = True

            player.spec = 'Juggernaut'

        elif choice == 3:
            fighter_component = Fighter(hp=100, defense=1, power=1, xp=0, attack_dice=(1,4),
                                        death_function=player_death)
            player = Player(0, 0, '@', name, libtcod.white, blocks=True, fighter=fighter_component)
            
            equipment_component = Weapon(slot='hand', power_bonus=1, attack_dice=(1,8))
            obj = Object(0, 0, '/', 'claymore', libtcod.sky, equipment=equipment_component)
            inventory.append(obj)
            equipment_component.equip()
            obj.always_visible = True

            player.spec = 'Highlander'

        elif choice == 4:
            fighter_component = Fighter(hp=100, defense=1, power=1, xp=0, attack_dice=(1,6),
                                        death_function=player_death)
            player = Player(0, 0, '@', name, libtcod.white, blocks=True, fighter=fighter_component)

            player.spec = 'Street Fighter'

        elif choice == 5:
            fighter_component = Fighter(hp=100, defense=1, power=1, xp=0, attack_dice=(1,6),
                                        death_function=player_death)
            player = Player(0, 0, '@', name, libtcod.white, blocks=True, fighter=fighter_component)

            equipment_component = Weapon(slot='hand', attack_dice=(1,4))
            obj = Object(0, 0, '+', 'cross', libtcod.sky, equipment=equipment_component)
            equipment_component.equip()
            inventory.append(obj)
            obj.always_visible = True

            item_component = Tome(cast_heal_lesser)
            item = Object(0, 0, '=', 'tome of lesser healing', libtcod.blue, item=item_component)
            inventory.append(obj)

            player.spec = "Healer"

    player.level = 1
    player.inv = inventory

    hunger_msg = False
    steps = 0

    ice_counter = None

    dungeon_level = 1
    camera = Camera(0, 0)
    make_map()
    initialize_fov()

    game_state = 'playing'

def initialize_fov():
    libtcod.console_clear(con)
    global fov_recompute, fov_map
    fov_recompute = True

    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight,
                                       not map[x][y].blocked)

def main_menu():
    img = libtcod.image_load('menu_background.png')
    while not libtcod.console_is_window_closed():
        libtcod.image_blit_2x(img, 0, 0, 0)
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'PICOGUE')
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'By kcg')
        choice = menu('', ['Play a new game', 'Continue last game', 'View Hall of Legends', 'Quit'], 24)

        if choice == 0:
            new_game()
            play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                msgbox('\nNo saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:
            load_legends()
        elif choice == 3:
            break

def save_game():
    # open a new empty shelve (possible overwrite) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['stairs_index'] = objects.index(stairs)
    file['dungeon_level'] = dungeon_level
    file['steps'] = steps
    file['player_index'] = objects.index(player) # index of player in object list
                        # can't use "file['player'] = player", because player is a
                        # reference, and shelve recursively grabs referenced objects.
                        # Thus, you'd have two separate copies of player.
    file['ice_counter'] = ice_counter
    file['msg_index'] = msg_index
    file.close()

def load_game():
    global map, objects, player, inventory, game_msgs, game_state, stairs, dungeon_level, steps, hunger
    global msg_index, ice_counter
    msg_index = 0

    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    stairs = objects[file['stairs_index']]
    dungeon_level = file['dungeon_level']
    steps = file['steps']
    ice_counter = file['ice_counter']
    msg_index = file['msg_index']
    file.close()

    initialize_fov()

def load_legends():
    f = open('lgnds', 'r')
    msgbox(f.read())
    f.close()

def write_legends(data):
    f = open('lgnds', 'a')
    f.write(data + '\n')
    f.close()

# ---------- Main Loop ----------


def play_game():
    global key, mouse, msg_index

    player_action = None

    mouse = libtcod.Mouse()
    key = libtcod.Key()

    while not libtcod.console_is_window_closed():
        if game_state == 'playing' and player_action != 'didnt-take-turn': # AI loop
            check_hunger()
            check_ice_counter()
            check_level_up()
            check_floor()
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
        if game_state == 'won':
            player_data = player.name + ", Level " + str(player.level) + ' ' + player.spec
            write_legends(player_data)
            load_legends()
            break
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        libtcod.console_flush()

        for object in objects:
            object.clear()
        
        player_action = handle_keys()
        
        if player_action == 'exit':
            save_game()
            break


# ---------- Program ----------

main_menu()
