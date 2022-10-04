if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit
start /min "activate.bat"
cd C:\Users\jonat\Documents\PythonProjects\ChurchManager
python cm.py
exit