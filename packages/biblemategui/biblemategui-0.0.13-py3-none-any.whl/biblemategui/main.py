#!/usr/bin/env python3
from nicegui import ui

from biblemategui import BIBLEMATEGUI_APP_DIR

from biblemategui.pages.home import *

from biblemategui.pages.bibles.original_reader import original_reader
from biblemategui.pages.bibles.original_interlinear import original_interlinear
from biblemategui.pages.bibles.original_parallel import original_parallel
from biblemategui.pages.bibles.original_discourse import original_discourse
from biblemategui.pages.bibles.original_linguistic import original_linguistic

from biblemategui.pages.tools.audio import bibles_audio

import os

# --- Define the Pages ---
# We define our pages first. The create_menu() function will be
# called inside each page function to add the shared navigation.

"""
q - query
t - token
m - menu

b - book
c - chapter
v - verse

bb - default bible
cc - default commentary
ee - default encyclopedia
ll - default lexicon
"""

book_number, chapter_number, verse_number = 1, 1, 1

# Home Page

@ui.page('/')
def page_home(b: int | None = None, c: int | None = None, v: int | None = None):
    """
    Home page that accepts an optional 'q' q parameter.
    Example: /?b=1&c=1&v=1
    """
    global book_number, chapter_number, verse_number
    if b:
        book_number = b
    if c:
        chapter_number = c
    if v:
        chapter_number = v
        
    create_menu() # Add the shared menu
    create_home_layout()

# Settings

@ui.page('/settings')
def page_Settings(q: str | None = None, m: bool = True):
    if m:
        create_menu()
    with ui.column().classes('w-full items-center'):
        ui.label('BibleMate AI').classes('text-2xl mt-4')
        ui.notify("This feature is currently in progress.")

# Entry_point

def main():
    # --- Run the App ---
    # Make sure to replace the secret!
    ui.run(
        storage_secret='REPLACE_ME_WITH_A_REAL_SECRET', # TODO
        port=8888,
        title='BibleMate AI',
        favicon=os.path.join(BIBLEMATEGUI_APP_DIR, 'eliranwong.jpg')
    )

main()