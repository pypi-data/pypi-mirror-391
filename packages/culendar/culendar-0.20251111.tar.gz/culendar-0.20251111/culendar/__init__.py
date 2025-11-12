#!/usr/bin/env python3
from curses import wrapper

from .culendar import Culendar


def main(stdscr, *args):
    Culendar(stdscr).run_loop()


def run(args=None):
    """here starts culendar!"""
    if args is None:
        from sys import argv as args
    wrapper(main, *args)


if __name__ == "__main__":
    run()
