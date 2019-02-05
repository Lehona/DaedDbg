# DaedDbg
DaedDbg is a collection of python scripts that enable debugging of Daedalus-Bytecode in gdb. There are several new gdb commands (explained later on) and a short powershell file AttachG2.ps1 provided to attach gdb to an already running Gothic 2.

### Installation
DaedDbg requires [Python 2.7 (x86)](https://www.python.org/download/releases/2.7/) and a python-enabled gdb. 
* **Installing Python** After [downloading Python 2.7 (x86)](https://www.python.org/download/releases/2.7/), add the Python27/bin folder to your PATH environment variable. If you don't know how to do this, you can learn about it [here](https://docs.alfresco.com/4.2/tasks/fot-addpath.html).
* **Installing gdb** The easiest place to acquire gdb on Windows is from [MinGW](http://www.mingw.org/). After installing MinGW, add the MinGW/bin-folder to your PATH variable as described above. You can now either install gdb-python via the MinGW GUI or via the command line by running `mingw-get install gdb-python`. It will download the necessary files and put them into the MinGW/bin folder.
* **Setting up Powershell (optional)** If you want to run DaedDbg from an open Powershell console (instead of starting the script from the file browser), you will need to configure windows to allow execution of downloaded powershell scripts. To do this, open powershell and execute `Set-ExecutionPolicy -Scope CurrentUser Unrestricted`, then hit either Y/J (Yes/Ja) or A (Yes, all). 


### Usage
To start debugging, first start Gothic 2 and load into the game, either by starting a new game or loading a savefile that you want to debug. After setting up the required situation in Gothic 2, attach the debugger by running the AttachG2.ps1 file with powershell. Gothic 2 will continue execution until the first token of the content parser is executed, at which point the program will stop and gdb prints some tokens that are about to be executed. Now you can start issueing commands and debug.

###### Commands
* **dstep into** This command will execute a single daedalus token.
* **dstep over** This command works just like 'dstep into', unless the next token is a zPAR_TOK_CALL (a daedalus function call), in which case execution will proceed until that function returns. This essentially treats the daedalus function as a single token.
* **dbreak arg** This command sets a daedalus breakpoint at arg, which can either be a function name or an offset. Offsets are marked by a preceding asterisk (*), e.g. 'dbreak INIT_GLOBAL' or 'dbreak *0x123abc'. When the given location is executed, gdb will stop and let you issue further commands, e.g. inspect variables or start single-stepping through the function. 
* **dibreaks** Using this command you can list all currently active daedalus breakpoints. The mnemonic stands for 'daedalus-info-breakpoints'. There is currently no command to delete a breakpoint. 
* **dx arg** This command lets you examine the content of the variable arg by printing its value to the console. Only integer variables are supported by this command, but in future releases instances and strings will be available, too. Note that local variables have to be prefixed by the function name, e.g. 'dx INIT_GLOBAL.MYVAR'.
* **dcurrentfunc** Prints the daedalus function that is currently being executed. When in bytecode that is outside the original codestack (i.e. generated at runtime), this will print [UNKNOWN].
* **doption tokens arg** Sets the amount of tokens to be printed during stepping to arg (must be an integer). 
* **continue** Continue execution normally. If you don't have a breakpoint set (or don't want to wait) you can halt execution with CTRL+C (may need to spam this multiple times until execution halts). It is recommended but not always required to step a single token (i.e. type 'dstep into') after halting execution via CTRL+C to return the debugger to a known state.
* **kill** Quit Gothic 2 (will ask for confirmation).
* **quit** Quit the Debugger without closing Gothic 2 (will ask for confirmation to close the debugger).

### FAQ
 * **Q: These commands are really long and annoying to type. Any help?**
 * A: gdb commands are prefix-aware. This means you can type any prefix instead of the whole command, as long as it is unambiguous. Examples include typing 'c' instead of 'continue' or 'dc' instead of 'dcurrentfunc'. The same is true for all partial commands (separated by spaces), e.g. 'ds i' insted of 'dstep into'. Just hitting return on an empty command line will resend the most recent command, so you can quickly single-step through tokens by typing 'ds i' once and then just continuously pressing return.
 * **Q: I'm only seeing a small part of the Daedalus bytecode, can I somehow view more?**
 * A: You can configure the amount of tokens printed via `doption tokens x`, but I recommend using [DecDat](https://forum.worldofplayers.de/forum/threads/1151032-Tool-DecDat) or [ReaDat](https://forum.worldofplayers.de/forum/threads/1101745-Tool-ReaDat) to browse the complete bytecode while debugging. They offer a much more powerful (graphical) interface than DaedDbg ever will.
 


### Known Issues
* The newest version of gdb-python on MinGW has a bug that sometimes effectively kills the program that is being debugged. This is a race condition and does therefore not occur every time. gdb will output something along the lines of "PC register not available" when this happens and currently there is no workaround for this except restarting both gdb and Gothic 2. As far as I know, only gdb versions 7.3 - 7.5 are affected by this.
* Due to the python code that is run every time a single daedalus token is processed by Gothic, the framerate drops to an unusuable value (below 1 FPS) even when not in debugging mode (i.e. single-stepping). This makes it nearly impossible to debug problems that occur very rarely (e.g. in a dialog). A possible workaround would be to halt execution via MEM_InfoBox() in the scripts and only then attach the debugger. This might be possible to fix in future releases and there will be an effort to do so.
* The zPAR_TOK_PUSHARRAYVAR token is currently not being decoded correctly, causing a python exception to be thrown when trying to print it. This only affects the display of the current and future tokens, but not the functionality of the debugger. External Tools such as [ReaDat](https://forum.worldofplayers.de/forum/threads/1101745-Tool-ReaDat) and [DecDat](https://forum.worldofplayers.de/forum/threads/1151032-Tool-DecDat) can be used to correctly show the tokens at the problematic offset. 