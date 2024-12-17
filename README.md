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
                - playlists
                    - list1.plf
                    - list2.plf

## Windows

### Song View

The song view is a simple window that displays the chordpro file. The chords are presented inline as bolded.

![image](https://github.com/user-attachments/assets/49b3ccae-3713-4e48-863e-1b6ff23b3d9d)

### Song List

The song list windows displays a grid with the databasse Id; chordpro Title, and Subtitile; the Book with subdirectory name; and the relative path name. Move around the grid using standard directional keys and mouse clicks. Left clicking in the file name cell will pop up a simple edit window.

![image](https://github.com/user-attachments/assets/101ecf72-7459-458b-a2aa-d57d647733ad)

#### Books Tab Buttons

Book List - drop down list of available books. These are subdirectories in the showpro directory. In book mode the status will state the the number with book songs.

Rebuild - rebuids the database and indexes. This is required when adding or removing new songs or books from the showpro directory. It will update the song database and indexes. This will recreate the song ids based on the input files.

#### Search Tab Buttons

Search - does an indexed word search of all the songs in the database. It uses a full word, not a wild card, so enter a full word to get expected results. The search can use up to two different words with the operator relationship between them. The operators are And, Or, or Not. In search mode the status will state the number with search songs.

First word - first word of search.

Operator List - drop down list of operators.

Second word - second word of search.

Clear - clear the search mode and return to book mode.

#### PlayList Buttons

Play List - drop down list of open playlists. The Unsaved list is always available to capture new songs. It must be saved to be reused in another session.

Open - open a play list file. A playlist just references songs in the books.

Save - save the play list. It can be saved to a different file name which will create a copy. The default extension is plf for play, list, file.

Clear - clears the file list songs. It does not save so the original is available unless replaced by save.

Delete - clears the file list songs and deletes the playlist file.

#### Song List Hot Keys

The hot keys allow the operator to modify the song view window and the buttons without needing mouse clicks or continuing to change window focus between the list and view. Column Headings will sort the column by entry.

| Key        | Action                                                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------- |
| enter      | Display song in view window or Left Mouse click any column but File. On File will open edit window.                               |
| Alt-enter  | Add current selection to active playlist or Right Mouse click.                                                                    |
| del        | Mark song as DEL, on PlayList remove from playlist.                                                                               |
| Alt 1-3    | Switch tabs. 1 - Book, 2 - Search, 3 - Playlist or Left Mouse click on tab.                                                       |
| A-Z        | In Title or Subtitle will sort column and go to first entry starting with the letter pressed. Disabled on Playlist.               |
| `          | Backquote will pop up a simple edit window to modify cordpro file.                                                                |
| 0, 1, 2, 3 | Set stars to zero (white), one (yellow), two (green), or three (green).                                                           |
| [          | Left square bracket will transpose down one step on view window.                                                                  |
| ]          | Right square backet will transpose up one step on view window.                                                                    |
| /          | Back Slash will save transpose to song file.                                                                                      |
| ,          | Comma will toggle chord colors                                                                                                    |
| .          | Period will sort the column containing selected.                                                                                  |
| <          | Less than will go to first row.                                                                                                   |
| >          | Greater than will go to last row.                                                                                                 |
| Ctrl-Left  | Zoom In on view window                                                                                                            |
| Ctrl-Right | Zoom out on view window                                                                                                           |
| Ctrl-Down  | Scroll view window down one line                                                                                                  |
| Ctrl-Up    | Scroll view window up one line                                                                                                    |
| Alt-Down   | Next song                                                                                                                         |
| Alt-Up     | Previous song                                                                                                                     |
| Shirt-Down | Playlist only: move song down in list.                                                                                            |
| Shift-Up   | Playlist only: move song up in list.                                                                                              |
| esc        | Quit and close XshowPro.                                                                                                          |

## Chordpro

For details on the chordpro file format or to get a program for printing songs or books visit the chordpro site: https://www.chordpro.org/

To keep it simple only a few chordpro directives are supported. 

The title {title: text} or {t: text} will diplay the text at the top of the file and usually contains the name of the song. The words from this field are indexed for the search.

The subtitle {subtitle: text} or {st: text} will display the text on the next line after the title and usually contains the artist that made the song popular. The words from this field are indexed fo the search.

The square bracess [ ] for chrods are bolded and displayed inline.

The chorus {start_of_chorus} ... {end_of_chorus} or the short form {soc} ... {eoc} will indent the text.

The bridge {start_of_bridge} ... {end_of_bridge} or the short form {sob} ... {eob} will shade highlight the text. It is sometimes used for non-singing lyrics for timing and melody for instrumentals.

The comment {comment: text}, {c: text}, {comment_italic: text}, or {ci: text} all will display the text in italics.

All other single line directives are ignored.

For the range directives that contain start and end the containing text is displayed in the current font. Since the view window uses a mono space font tab lines are displayed correctly.

The only non-chordpro feature is the support for imbedded urls. If the song view window is in focus and the url is clicked the application will open your default browser with the link.




