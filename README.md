# Grab2Model

Convert Grab levels into .obj files that you can use externally.
"Grab is a very effective 3d modelling tool."

- Install Blender and add it to path
- Update `generated` folder from [Slin/GRAB-Level-Format](https://github.com/Slin/GRAB-Level-Format/tree/main) (main/tools/generated)
- Copy `generated` folder into your blender install "Blender X.X\X.X\python\lib" folder
- Run `pip install -r requirements.txt --target "C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\lib"` replacing the target with your blender install
- `blender --background --python Grab2Model.py <level_file>`