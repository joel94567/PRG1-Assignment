# STEP 1 - skeleton: main menu only
import sys

WELCOME = """\
---------------- Welcome to Sundrop Caves! ----------------
You spent all your money to get the deed to a mine, a small
  backpack, a simple pickaxe and a magical portal stone.

How quickly can you get the 500 GP you need to retire
  and live happily ever after?
-----------------------------------------------------------
"""

def new_game():
    print("New game: (not implemented yet).")

def load_game():
    print("Load saved game: (not implemented yet).")

def main_menu():
    print(WELCOME)
    while True:
        print("\n--- Main Menu ----")
        print("(N)ew game")
        print("(L)oad saved game")
        print("(Q)uit")
        choice = input("Your choice? ").strip().lower()
        if choice == 'n':
            new_game()
        elif choice == 'l':
            load_game()
        elif choice == 'q':
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Try N, L or Q.")

if __name__ == "__main__":
    main_menu()

from random import randint
import json
import os

player = {}
game_map = []
fog = []

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]  # For advanced feature 

prices = {
    'copper': (1, 3),
    'silver': (5, 8),
    'gold': (10, 18)
}

SAVE_FILE = "savegame.json"

# Load map from file
def load_map(filename, map_struct):
    global MAP_WIDTH, MAP_HEIGHT
    with open(filename, 'r') as map_file:
        lines = [line.rstrip("\n") for line in map_file]
        map_struct.clear()
        for line in lines:
            map_struct.append(list(line))
    MAP_WIDTH = len(map_struct[0])
    MAP_HEIGHT = len(map_struct)

# Clear fog in 3×3 area around player
def clear_fog(fog, player):
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx = player['x'] + dx
            ny = player['y'] + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                fog[ny][nx] = game_map[ny][nx]

# Initialise game
def initialise_game():
    load_map("level1.txt", game_map)
    fog.clear()
    for _ in range(MAP_HEIGHT):
        fog.append(["?" for _ in range(MAP_WIDTH)])
    player.clear()
    player['name'] = input("Greetings, miner! What is your name? ")
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['capacity'] = 10
    player['GP'] = 0
    player['day'] = 1
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY
    player['portal'] = (0, 0)
    player['pickaxe'] = 1
    clear_fog(fog, player)
    print(f"Pleased to meet you, {player['name']}. Welcome to Sundrop Town!")

# Draw full map with fog
def draw_map():
    print("+" + "-" * MAP_WIDTH + "+")
    for y in range(MAP_HEIGHT):
        row = ""
        for x in range(MAP_WIDTH):
            if x == player['x'] and y == player['y']:
                row += "M"
            else:
                row += fog[y][x]
        print("|" + row + "|")
    print("+" + "-" * MAP_WIDTH + "+")

# Draw 3×3 viewport
def draw_view():
    print("+---+")
    for dy in range(-1, 2):
        row = "|"
        for dx in range(-1, 2):
            nx = player['x'] + dx
            ny = player['y'] + dy
            if nx == player['x'] and ny == player['y']:
                row += "M"
            elif 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                row += game_map[ny][nx]
            else:
                row += "#"
        row += "|"
        print(row)
    print("+---+")

# Show player information
def show_information():
    print("----- Player Information -----")
    print(f"Name: {player['name']}")
    print(f"Portal position: {player['portal']}")
    print(f"Pickaxe level: {player['pickaxe']} (copper only)")
    print("------------------------------")
    load = player['copper'] + player['silver'] + player['gold']
    print(f"Load: {load} / {player['capacity']}")
    print("------------------------------")
    print(f"GP: {player['GP']}")
    print(f"Steps taken: {player['steps']}")
    print("------------------------------")

# Save game
def save_game():
    data = {
        "player": player,
        "fog": fog,
        "game_map": game_map
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    print("Game saved.")

# Load game
def load_game():
    if not os.path.exists(SAVE_FILE):
        print("No saved game found.")
        return False
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    player.clear()
    player.update(data["player"])
    fog.clear()
    fog.extend(data["fog"])
    game_map.clear()
    game_map.extend(data["game_map"])
    return True

# Sell ore in town
def sell_ore():
    total_gp = 0
    for mineral in ['copper', 'silver', 'gold']:
        amount = player[mineral]
        if amount > 0:
            price = randint(*prices[mineral])
            gain = amount * price
            print(f"You sell {amount} {mineral} ore for {gain} GP.")
            player['GP'] += gain
            total_gp += gain
            player[mineral] = 0
    if total_gp > 0:
        print(f"You now have {player['GP']} GP!")

# Buy backpack upgrade
def buy_stuff():
    while True:
        print("----------------------- Shop Menu -------------------------")
        cost = player['capacity'] * 2
        print(f"(B)ackpack upgrade to carry {player['capacity']+2} items for {cost} GP")
        print("(L)eave shop")
        print(f"GP: {player['GP']}")
        choice = input("Your choice? ").lower()
        if choice == "b":
            if player['GP'] >= cost:
                player['GP'] -= cost
                player['capacity'] += 2
                print(f"Congratulations! You can now carry {player['capacity']} items!")
            else:
                print("Not enough GP!")
        elif choice == "l":
            break

# Enter mine loop
def enter_mine():
    while True:
        print(f"\nDAY {player['day']}")
        draw_view()
        load = player['copper'] + player['silver'] + player['gold']
        print(f"Turns left: {player['turns']}    Load: {load} / {player['capacity']}    Steps: {player['steps']}")
        action = input("(WASD) to move (M)ap, (I)nfo, (P)ortal, (Q)uit: ").lower()

        if action in ['w', 'a', 's', 'd']:
            move_player(action)
            if player['turns'] <= 0:
                print("You are exhausted.")
                use_portal()
                break
        elif action == "m":
            draw_map()
        elif action == "i":
            show_information()
        elif action == "p":
            use_portal()
            break
        elif action == "q":
            break

# Move player
def move_player(direction):
    dx, dy = 0, 0
    if direction == 'w': dy = -1
    elif direction == 's': dy = 1
    elif direction == 'a': dx = -1
    elif direction == 'd': dx = 1

    nx = player['x'] + dx
    ny = player['y'] + dy

    if not (0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT):
        print("You can't go that way.")
    else:
        target = game_map[ny][nx]
        load = player['copper'] + player['silver'] + player['gold']
        if target in mineral_names:
            if load >= player['capacity']:
                print("You can't carry any more.")
            elif target == 'C':  # Basic: copper only
                mined = randint(1, 5)
                if load + mined > player['capacity']:
                    mined = player['capacity'] - load
                    print(f"...but you can only carry {mined} more piece(s)!")
                player['copper'] += mined
                print(f"You mined {mined} piece(s) of copper.")
                game_map[ny][nx] = " "
                fog[ny][nx] = " "
                player['x'], player['y'] = nx, ny
                player['steps'] += 1
            else:
                print("You can't mine that with your current pickaxe.")
        else:
            player['x'], player['y'] = nx, ny
            player['steps'] += 1

    player['turns'] -= 1
    clear_fog(fog, player)

# Use portal
def use_portal():
    player['portal'] = (player['x'], player['y'])
    print("You place your portal stone here and zap back to town.")
    sell_ore()
    player['day'] += 1
    player['x'], player['y'] = 0, 0
    player['turns'] = TURNS_PER_DAY
    clear_fog(fog, player)
    if player['GP'] >= WIN_GP:
        print(f"Woo-hoo! Well done, {player['name']}! You win!")
        print(f"It only took you {player['day']} days and {player['steps']} steps.")
        main_menu()

# Town menu loop
def town_menu():
    sell_ore()
    while True:
        print(f"\nDAY {player['day']}")
        print("----- Sundrop Town -----")
        print("(B)uy stuff")
        print("See Player (I)nformation")
        print("See Mine (M)ap")
        print("(E)nter mine")
        print("Sa(V)e game")
        print("(Q)uit to main menu")
        choice = input("Your choice? ").lower()
        if choice == "b":
            buy_stuff()
        elif choice == "i":
            show_information()
        elif choice == "m":
            draw_map()
        elif choice == "e":
            enter_mine()
        elif choice == "v":
            save_game()
        elif choice == "q":
            break

# Main menu loop
def main_menu():
    while True:
        print("\n--- Main Menu ----")
        print("(N)ew game")
        print("(L)oad saved game")
        print("(Q)uit")
        choice = input("Your choice? ").lower()
        if choice == "n":
            initialise_game()
            town_menu()
        elif choice == "l":
            if load_game():
                print("Game loaded.")
                town_menu()
        elif choice == "q":
            exit()

# Game start
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.\n")
print(f"How quickly can you get the {WIN_GP} GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")

main_menu()
