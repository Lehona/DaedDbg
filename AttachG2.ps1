$procID = get-process Gothic2 | select -expand id

gdb-python27 -p $procID -x start_dbg