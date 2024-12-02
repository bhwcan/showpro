# XshowPro

## Summary

XshowPro is an application to display chordpro file formats on a large display for guitar or ukulele groups. It consists of two windows: one for the song view, typically on a large TV screen or monitor, and a song list window to select and search from your library of chordpro files, typically on a laptop display. If you have only one display both windows can be displayed on the same screen. 

## Requirements

XshowPro is a python script using wxPython. It will run on any supported platform. It has been tested on MacOS, Ubuntu, and Windows. There is a built xshowpro.exe file available for Windows. For other platforms download the source and run the python script. See the python documentation for installation of python and wsPython. 

It works best from a laptop connected to a large display so it has the large display for the song view and the song list can be operated by the the group leader or designated member.

For first time usage copy your cordpro files to one or more subdirectoris in the "showpro" folder. Execute xshowpro and click on the [Rebuild] button to create your first database and indexes. Any time files or directories are added or removed you will need to rebuild. It only supports one level of subdrectories which are displayed in the song list window as Books.

## File System

It uses chordpro files installed in subdirectories under the users Documents folder in a folder called "showpro". The database and index files are also in that directory.

    – Users_HOME : users home directory which is platform specific
        – Documents : users documents folder
            - showpro : xshowpro files and database dirctory
                - Book 1 : subdirectory containing song files
                    - song1.pro : chordpro song file (ends with pro)
                    - song2.pro
                - Book 2
                    - song2.pro
                    - song3.pro
                - booksidx.dat : book index file
                - songs.dat : songs database
                - songsidx.dat : songs word index file

## Windows

### Song View

The song view is a simple window that displays the chordpro file. The chords are presented inline as bolded.

![2024-12-02-08-35-27-image](https://github.com/user-attachments/assets/f04686d9-2c61-42ad-8210-21919380f82e)

#### Song View Menu

- File
  - About - simple message
- Zoom
  - Zoom In - increase font size
  - Zoom Out - decrease font size
- Color
  - Bold - bold the chords
  - Red - bold and red chords
  - Blue - bold and blue chords
  - Green - bold and green chords
- Transpose
  - Up + - transpose up one step (key)
  - Down + - transpose down one step (key)
  - Save - save the transpose to the chordpro file

### Song List

The song list windows displays a grid with the databasse Id; chordpro Title, and Subtitile; the Book with subdirectory name; and the relative path name. Move around the grid using standard directional keys and mouse clicks. Left clicking in the file name cell will pop up a simple edit window.

![2024-12-02-09-23-59-image](https://github.com/user-attachments/assets/fc15a75e-f5e9-49a9-a5c2-133d25016af7)

#### Song List Buttons

Book - drop down list of available books. These are subdirectories in the showpro directory. In book mode the status will state the the number with book songs.

Search - does an indexed word search of all the songs in the database. It uses a full word, not a wild card, so enter a full word to get expected results. The search can use up to two different words with the operator relationship between them. The operators are And, Or, AndNot, OrNot. In search mode the status will state the number with search songs.

Clear - clear the search mode and return to book mode.

Reload - reload the database and indexes. This is required when adding or removing new songs or books from the showpro directory. It will update the song database and indexes.

Column Headings - will order (sort) the column by entry.

#### Song List Hot Keys

The hot keys allow the operator to modify the song view window and the buttons without needing mouse clicks or continuing to change window focus between the list and view.

| Key     | Action                                                                                                                            |
| ------- | --------------------------------------------------------------------------------------------------------------------------------- |
| enter   | Display song in view window                                                                                                       |
| b       | Enter the book drop down to select a new book                                                                                     |
| s       | Enter the first word box for search. To move between buttons use tab and shift-tab. Search starts when Search button is pressed.  |
| c       | Select clear button, enter to press                                                                                               |
| e       | Edit will pop up a simple edit window to modify cordpro file                                                                      |
| 0       | Bold chords in view window                                                                                                        |
| 1       | Red chords in view window                                                                                                         |
| 2       | Blue chords in view window                                                                                                        |
| 3       | Green chords in view window                                                                                                       |
| z       | Zoom In on view window                                                                                                            |
| x       | Zoom out on view window                                                                                                           |
| t       | Transpose up on view window                                                                                                       |
| y       | Transpose down on view window                                                                                                     |
| u       | Save transpose to song file                                                                                                       |
| m       | Scroll view window down one line                                                                                                  |
| k       | Scroll view window up one line                                                                                                    |
| o       | Order (sort) the column containing selected.                                                                                      |
| q       | Quit and close XshowPro.                                                                                                          |

## Chordpro

For details on the chordpro file format or to get a program for printing songs or books visit the chordpro site: https://www.chordpro.org/

To keep it simple only a few chordpro directives are supported. 

The title {title: text} or {t: text} will diplay the text at the top of the file and usually contains the name of the song. The words from this field are indexed for the search.

The subtitle {subtitle: text} or {st: text} will display the text on the next line after the title and usually contains the artist that made the song popular. The words from this field are indexed fo the search.

The square bracess [ ] for chrods are bolded and displayed inline.

The chorus {start_of_chorus} ... {end_of_chorus} or the short form {soc} ... {eoc} will indent the text.

The comment {comment: text}, {c: text}, {comment_italic: text}, or {ci: text} all will display the text in italics.

All other single line directives are ignored.

For the range directives that contain start and end the containing text is displayed in the current font. Since the view window uses a mono space font tab lines are displayed correctly.

The only non-chordpro feature is the support for imbedded urls. If the song view window is in focus and the url is clicked the application will open your default browser with the link.




