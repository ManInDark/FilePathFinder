import argparse
import pathlib
import curses
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", dest="path", type=pathlib.Path, required=False)
args = parser.parse_args()

wd: pathlib.Path = pathlib.Path.cwd() if args.path is None else args.path
wd = wd.resolve().absolute()
index: int = 0

def select_color(file: pathlib.Path) -> int:
    if file.is_dir():
        return 2
    if file.is_file() and file.stat().st_mode & 0o111:
        return 3
    return 1

def print_files(term: curses.window, dir_size: int):
    term.addstr(0, 0, ">>> " + str(wd))

    for i in range(1, curses.LINES):
        term.addstr(i, 0, "|")
    files = wd.glob("*")
    for i, file in enumerate(files):
        if i >= curses.LINES - 1:
            break
        term.addstr(i + 1, 4, str(file.name), curses.color_pair(select_color(file)))

    term.refresh()


def cd(newdir):
    global wd, index
    wd = newdir
    index = 0

def update(term: curses.window):
    global wd, index
    


    while True:
        term.clear()
        dir_size = len(list(wd.glob("*")))
        print_files(term, dir_size)
        term.addstr(index + 1, 2, ">", curses.color_pair(2))

        key: int = term.getch()
        if key == curses.KEY_DOWN:
            index += 1
            if index >= dir_size or index >= curses.LINES - 1:
                index = 0
        elif key == curses.KEY_UP:
            index -= 1
            if index < 0:
                index = min(dir_size - 1, curses.LINES - 2)
        elif key == 10: # Return
            wd = list(wd.glob("*"))[index]
            if not wd.is_dir():
                break
            else:
                cd(wd)
        elif key == 60: # <
            cd(wd.parent)

        term.refresh()

# curses wrapper
def main(term: curses.window):
    # COLORS
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # default
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK) # directory
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) # executable

    curses.curs_set(0)

    update(term)


curses.wrapper(main)
print(wd)