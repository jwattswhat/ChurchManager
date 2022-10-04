import os
os.chdir("C:\\Users\\jonat\\Documents\\PythonProjects\\HymnSelect\\Music")
dir = os.listdir()
for file in dir:
    on = os.path.splitext(file)
    n = file[:3]
    nn = "LSB" + n + on[1]
    print ("Renaming {on} to {nn}".format(on=file,nn=nn))
    os.rename(file,nn)
