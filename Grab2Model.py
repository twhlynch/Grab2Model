import bpy, os, sys, json
from mathutils import Quaternion, Vector
from google.protobuf import json_format
from generated import types_pb2, level_pb2

def getLevelJson(data):
    level = level_pb2.Level()
    level.ParseFromString(data.read())
    return json_format.MessageToDict(level)

def create_cube(position, rotation, scale, color):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object

        cube.location = position
        cube.rotation_mode = 'QUATERNION'
        cube.rotation_quaternion = Quaternion(rotation)
        cube.scale = scale

def process_node(node):
    if 'levelNodeStatic' in node:
        static_node = node['levelNodeStatic']
        if 'position' not in static_node:
            static_node['position'] = {'x': 0, 'y': 0, 'z': 0}
        position = Vector((
            static_node['position'].get('x', 0),
            static_node['position'].get('y', 0),
            static_node['position'].get('z', 0)
        ))
        if 'rotation' not in static_node:
            static_node['rotation'] = {'w': 0, 'x': 0, 'y': 0, 'z': 0}
        rotation = Quaternion((
            static_node['rotation'].get('w', 0),
            static_node['rotation'].get('x', 0),
            static_node['rotation'].get('y', 0),
            static_node['rotation'].get('z', 0)
        ))
        if 'scale' not in static_node:
            static_node['scale'] = {'x': 0, 'y': 0, 'z': 0}
        scale = Vector((
            static_node['scale'].get('x', 0)/2,
            static_node['scale'].get('y', 0)/2,
            static_node['scale'].get('z', 0)/2
        ))
        if 'color' not in static_node:
            static_node['color'] = {'r': 0, 'g': 0, 'b': 0}
        color = static_node.get('color', {'r': 0, 'g': 0, 'b': 0})

        create_cube(position, rotation, scale, color)

    elif 'levelNodeGroup' in node:
        group_node = node['levelNodeGroup']
        if 'position' not in group_node:
            group_node['position'] = {'x': 0, 'y': 0, 'z': 0}
        group_position = Vector((
            group_node['position'].get('x', 0),
            group_node['position'].get('y', 0),
            group_node['position'].get('z', 0)
        ))
        if 'rotation' not in group_node:
            group_node['rotation'] = {'w': 0, 'x': 0, 'y': 0, 'z': 0}
        group_rotation = Quaternion((
            group_node['rotation'].get('w', 0),
            group_node['rotation'].get('x', 0),
            group_node['rotation'].get('y', 0),
            group_node['rotation'].get('z', 0)
        ))
        if 'scale' not in group_node:
            group_node['scale'] = {'x': 0, 'y': 0, 'z': 0}
        group_scale = Vector((
            group_node['scale'].get('x', 0),
            group_node['scale'].get('y', 0),
            group_node['scale'].get('z', 0)
        ))
        children = group_node['childNodes']

        for child_node in children:
            if 'position' not in child_node:
                child_node['position'] = {'x': 0, 'y': 0, 'z': 0}
            child_position = Vector((
                child_node['position'].get('x', 0),
                child_node['position'].get('y', 0),
                child_node['position'].get('z', 0)
            )) + group_position
            if 'rotation' not in child_node:
                child_node['rotation'] = {'w': 0, 'x': 0, 'y': 0, 'z': 0}
            child_rotation = Quaternion((
                group_rotation[i] + child_node['rotation'].get('w', 0) if i == 0 else child_node['rotation'].get('x', 0) if i == 1 else
                child_node['rotation'].get('y', 0) if i == 2 else child_node['rotation'].get('z', 0)
                for i in range(4)
            ))
            if 'scale' not in child_node:
                child_node['scale'] = {'x': 0, 'y': 0, 'z': 0}
            child_scale = Vector((
                child_node['scale'].get('x', 0),
                child_node['scale'].get('y', 0),
                child_node['scale'].get('z', 0)
            )) * group_scale
            if 'color' not in child_node:
                child_node['color'] = {'r': 0, 'g': 0, 'b': 0}
            child_color = child_node.get('color', {'r': 0, 'g': 0, 'b': 0})

            child_node = {
                'levelNodeStatic': {
                    'position': {'x': child_position[0], 'y': child_position[1], 'z': child_position[2]},
                    'rotation': {'w': child_rotation[0], 'x': child_rotation[1], 'y': child_rotation[2], 'z': child_rotation[3]},
                    'scale': {'x': child_scale[0], 'y': child_scale[1], 'z': child_scale[2]},
                    'color': {'r': child_color['r'], 'g': child_color['g'], 'b': child_color['b']}
                }
            }

            process_node(child_node)

def boolJoinAll():
    scene_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    target_obj = scene_objects[0]
    for obj in scene_objects[1:]:
        bool_mod = target_obj.modifiers.new(name="Boolean", type='BOOLEAN')
        bool_mod.object = obj
        bool_mod.operation = 'UNION'

        bpy.context.view_layer.objects.active = target_obj
        bpy.ops.object.modifier_apply({"object": target_obj}, modifier=bool_mod.name)

        bpy.context.view_layer.objects.active = target_obj
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()

        bpy.ops.object.mode_set(mode='OBJECT')

        target_obj = scene_objects[0]

    for obj in scene_objects[1:]:
        if hasattr(obj, 'delete'):
            obj.delete()

def main(level_file):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    with open(level_file, 'rb') as f:
        json_data = getLevelJson(f)
    nodes = json_data['levelNodes']
    for node in nodes:
        process_node(node)
    bpy.ops.export_scene.obj(filepath=level_file[:-6] + '.obj')
    boolJoinAll()
    bpy.ops.export_scene.obj(filepath=level_file[:-6] + '-joined.obj')

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: blender --background --python level_to_obj.py <level_file>")
        exit(1)
    level_file = sys.argv[4]

    main(level_file)