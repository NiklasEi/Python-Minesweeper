import pygame
import numpy as np

# number of mines in the game
numberOfMines = 40
sizeOfGrid = 20

# array with information for each slot
#   any number from 0 to 8 is a warning
#   9 is a mine
grid = np.zeros((sizeOfGrid, sizeOfGrid), np.int)

# boolean array to save covered/uncovered info about every slot
uncovered = np.zeros((sizeOfGrid, sizeOfGrid), np.dtype(bool))

# boolean array to save flagged/un-flagged info about every slot
flagged = np.zeros((sizeOfGrid, sizeOfGrid), np.dtype(bool))

# if this is false all events (exept quit events) are ignored
play = False


def get_surrounding_slots(slot_to_check):
    """
    Get surrounding slots of a given slot
    :return list with surrounding slots
    """
    # check for slot at the corners of the grid
    if slot_to_check == 0:
        slots = [1, 1 + sizeOfGrid, sizeOfGrid]
    elif slot_to_check == sizeOfGrid - 1:
        slots = [slot_to_check - 1, slot_to_check + sizeOfGrid - 1, slot_to_check + sizeOfGrid]
    elif slot_to_check == sizeOfGrid**2 - sizeOfGrid:
        slots = [slot_to_check - sizeOfGrid, slot_to_check - sizeOfGrid + 1, slot_to_check + 1]
    elif slot_to_check == sizeOfGrid**2 - 1:
        slots = [slot_to_check - 1, slot_to_check - sizeOfGrid, slot_to_check - sizeOfGrid - 1]

    # check for slot at the edges of the grid
    elif slot_to_check / sizeOfGrid == 0:
        slots = [slot_to_check - 1, slot_to_check + 1, slot_to_check + sizeOfGrid - 1, slot_to_check + sizeOfGrid, slot_to_check + sizeOfGrid + 1]
    elif slot_to_check / sizeOfGrid == sizeOfGrid - 1:
        slots = [slot_to_check - 1, slot_to_check + 1, slot_to_check - sizeOfGrid + 1, slot_to_check - sizeOfGrid, slot_to_check - sizeOfGrid - 1]
    elif slot_to_check % sizeOfGrid == 0:
        slots = [slot_to_check - sizeOfGrid, slot_to_check + sizeOfGrid, slot_to_check - sizeOfGrid + 1, slot_to_check + 1, slot_to_check + sizeOfGrid + 1]
    elif slot_to_check % sizeOfGrid == sizeOfGrid - 1:
        slots = [slot_to_check - 1, slot_to_check - sizeOfGrid - 1, slot_to_check - sizeOfGrid, slot_to_check + sizeOfGrid - 1, slot_to_check + sizeOfGrid]

    # 'normal' case in the middle of the grid
    else:
        slots = [slot_to_check - sizeOfGrid - 1, slot_to_check - sizeOfGrid, slot_to_check - sizeOfGrid + 1, slot_to_check - 1, slot_to_check + 1, slot_to_check + sizeOfGrid - 1, slot_to_check + sizeOfGrid, slot_to_check + sizeOfGrid + 1]

    return slots


def get_surrounding_mines(slot_to_check):
    """
    Get the number of mines around a given slot
    :return number of mines
    """
    mines = 0

    slots = get_surrounding_slots(slot_to_check)

    # go through the surrounding slots and count the mines
    for i in slots:
        if grid[i % sizeOfGrid][i / sizeOfGrid] == 9:
            mines += 1
    return mines


# randomly distribute the mines
for i in range(numberOfMines):
    slot = np.random.random_integers(0, sizeOfGrid**2 - 1)

    # get a new slot as long as there is already a mine at the current one
    while grid[slot % sizeOfGrid][slot / sizeOfGrid] == 9:
        slot = np.random.random_integers(0, sizeOfGrid**2 - 1)

    # place the mine
    grid[slot % sizeOfGrid][slot / sizeOfGrid] = 9

# calculate and save the number of surrounding mines for all slots
for i in range(sizeOfGrid**2):
    if grid[i % sizeOfGrid][i / sizeOfGrid] != 9:
        grid[i % sizeOfGrid][i / sizeOfGrid] = get_surrounding_mines(i)

# initialize pygame
pygame.init()
# set the display size (our pictures are 15*15 so 150*150 will result in a 10*10 grid)
screen = pygame.display.set_mode((15 * sizeOfGrid, 15 * sizeOfGrid))
# set the display caption
pygame.display.set_caption("minesweeper")

# load all images
cover = pygame.image.load("pics/10.png")
warning0 = pygame.image.load("pics/0.png")
warning1 = pygame.image.load("pics/1.png")
warning2 = pygame.image.load("pics/2.png")
warning3 = pygame.image.load("pics/3.png")
warning4 = pygame.image.load("pics/4.png")
warning5 = pygame.image.load("pics/5.png")
warning6 = pygame.image.load("pics/6.png")
warning7 = pygame.image.load("pics/7.png")
warning8 = pygame.image.load("pics/8.png")
mine = pygame.image.load("pics/9.png")
flag = pygame.image.load("pics/11.png")

# save the pictures in a map for easier access
pics = {0: warning0,
        1: warning1,
        2: warning2,
        3: warning3,
        4: warning4,
        5: warning5,
        6: warning6,
        7: warning7,
        8: warning8,
        9: mine
        }


def show():
    """
    Reload the screen
    Use the current grid and cover/flag information to
    update the players screen
    """

    # empty the screen
    screen.fill(0)

    # loop over all slots
    for column in range(sizeOfGrid):
        for row in range(sizeOfGrid):
            # calculate x and y in pixels
            x, y = column * 15, row * 15

            # check for status of the slot and place the corresponding picture
            if uncovered[column][row]:
                screen.blit(pics[grid[column][row]], (x, y))
                continue
            elif flagged[column][row]:
                screen.blit(flag, (x, y))
                continue
            else:
                screen.blit(cover, (x, y))
                continue

    # update the players screen
    pygame.display.flip()


def won():
    """
    Check whether the game was won or not

    :return game is won
    """
    slots = 0
    for column in range(sizeOfGrid):
        for row in range(sizeOfGrid):
            if not uncovered[column][row]:
                slots += 1

    return slots == numberOfMines


def uncover(clicked_slot):
    """
    When the player clicks an empty slot the game should
    uncover all surrounding slots up until the first warnings
    """

    # set containing the slots that will be uncovered
    slots_to_uncover = set()
    slots_to_uncover.add(clicked_slot)

    # set containing all slots to check in the next iteration
    new_slots_to_uncover = set()

    # add all surrounding slots to the slots to check
    for i in get_surrounding_slots(clicked_slot):
        new_slots_to_uncover.add(i)

    # as long as there are slots to check...
    while len(new_slots_to_uncover) > 0:
        # loop through them and check each of them
        #   if they are not jet in slots_to_uncover add them
        #   if the slot is empty add all surrounding slots to the slots to check in the nex iteration
        for current_slot in new_slots_to_uncover.copy():
            if current_slot in slots_to_uncover:
                new_slots_to_uncover.remove(current_slot)
                continue

            slots_to_uncover.add(current_slot)
            new_slots_to_uncover.remove(current_slot)

            if grid[current_slot % sizeOfGrid][current_slot / sizeOfGrid] == 0:
                for new_slot in get_surrounding_slots(current_slot):
                    new_slots_to_uncover.add(new_slot)

    for to_uncover in slots_to_uncover:
        uncovered[to_uncover % sizeOfGrid][to_uncover / sizeOfGrid] = True



# open the screen for the player
show()

# start accepting events
play = True

# permanently check for events and react on them
while True:
    # go through all events and check the types
    for event in pygame.event.get():
        # quit the game when the player closes it
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        # now check for left and right click

        # left click
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            # return if the game is finished (lost or won)
            if not play:
                continue

            # get the current position of the cursor
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]

            # do nothing if the slot is already uncovered or flaged
            if uncovered[x / 15][y / 15]:
                break
            elif flagged[x / 15][y / 15]:
                break

            # if the slot is a bomb the game is lost
            if grid[x / 15][y / 15] == 9:
                print "you clicked on a mine! You lost the game"
                pygame.display.set_caption("lost")

                # stop accepting events
                play = False

                # uncover the slot and update the screen
                uncovered[x / 15][y / 15] = True
                show()
                break

            # uncover the slot and update the screen
            uncovered[x / 15][y / 15] = True

            if grid[x / 15][y / 15] == 0:
                uncover(x / 15 + (y / 15) * sizeOfGrid)

            show()

            # check weather the game was won
            if won():
                print "you won the game"
                pygame.display.set_caption("won")
                play = False

        # right click
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]:
            if not play:
                continue
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]
            # do nothing if the slot is uncovered
            if uncovered[x / 15][y / 15]:
                break

            # remove an existing flag
            if flagged[x / 15][y / 15]:
                flagged[x / 15][y / 15] = False
                show()
                break

            # place a flag and update the screen
            flagged[x / 15][y / 15] = True
            show()
