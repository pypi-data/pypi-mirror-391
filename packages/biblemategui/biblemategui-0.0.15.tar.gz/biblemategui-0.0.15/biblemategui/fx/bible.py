from nicegui import ui
import re

def luV(event):
    b, c, v = event.args
    ui.notify(f"b: {b}, c: {c}, v: {v}")
    
    # Create a context menu at the click position
    with ui.context_menu() as menu:
        ui.menu_item('Bible Commentaries', on_click=lambda: ui.navigate.to('/tool/commentary'))
        ui.menu_item('Cross-references', on_click=lambda: ui.navigate.to('/tool/xref'))
        ui.menu_item('Treasury of Scripture Knowledge', on_click=lambda: ui.navigate.to('/tool/tske'))
        ui.menu_item('Discourse Analysis', on_click=lambda: ui.navigate.to('/tool/discourse'))
        ui.menu_item('Morphological Data', on_click=lambda: ui.navigate.to('/tool/morphology'))
        ui.menu_item('Translation Spectrum', on_click=lambda: ui.navigate.to('/tool/translations'))
    menu.open()

def regexp(expr, case_sensitive=False):
    reg = re.compile(expr, flags=0 if case_sensitive else re.IGNORECASE)
    return reg.search(item) is not None

def getBibleChapter(db, b, c) -> str:
    query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
    content = ""
    with apsw.Connection(db) as connn:
        #connn.createscalarfunction("REGEXP", regexp)
        cursor = connn.cursor()
        cursor.execute(query, (b, c))
        if scripture := cursor.fetchone():
            content = scripture[0]
    return content

def getBibleBookList(db) -> list:
    query = "SELECT DISTINCT Book FROM Verses ORDER BY Book"
    bookList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query)
        bookList = sorted([book[0] for book in cursor.fetchall() if not book[0] == 0])
    return bookList

def getBilbeChapterList(db, b) -> list:
    query = "SELECT DISTINCT Chapter FROM Verses WHERE Book=? ORDER BY Chapter"
    chapterList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query, (b,))
        chapterList = sorted([chapter[0] for chapter in cursor.fetchall()])
    return chapterList

def getBibleVerseList(db, b, c) -> list:
    query = "SELECT DISTINCT Verse FROM Verses WHERE Book=? AND Chapter=? ORDER BY Verse"
    verseList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query, (b, c))
        verseList = sorted([verse[0] for verse in cursor.fetchall()])
    return verseList