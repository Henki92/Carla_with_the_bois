​#Carla with the bois
Author: Henrik Eriksson
Jonas Lundberg
Fredrik Andreeeeeeen
Jonas Garsten

##### Running Carla

./CarlaUE4.exe -benchmark -fps=10 -resx=1024 -resy=576 -quality-level=low

./CarlaUE4.exe -benchmark -fps=31 -resx=720 -resy=480 -quality-level=low -carla-server

./CarlaUE4.exe -benchmark -fps=20 -resx=1280 -resy=720 -quality-level=medium -carla-server

python spawn_npc.py -n 80

python dynamic_weather.py

python manual_control.py



##### Setting paths

Python Version 3.7.3
Set path:
	1. windows + e
	2. Right click this computer -> properties
	3. Advanced System Settings
	4. Environment Variables
	5. Under System Variables find Path and double click it.
	6. Paste path to python (3.7.3 in C:\Users\cjvp2x\AppData\Local\Programs\Python\Python37-32)
	7. Paste path to pip (C:\Users\cjvp2x\AppData\Local\Programs\Python\Python37\Scripts)
	8. For python 2.x located in C:\Python.....

##### Installing requirements

pip install -r PythonAPI/examples/requirements.txt
pip install -r PythonAPI/util/requirements.txt
pip install -r PythonAPI/carla/requirements.txt

##### Bug fixes

###### If you encounter error "No module agents" add following after imports in .py file:

`try:  
	sys.path.append('../carla')   
except IndexError:  
	pass`

###### If encounter mono = default_font if default_font in fonts else fonts[0] IndexError: list index out of range

replace all "mono" to "arial" in .py


