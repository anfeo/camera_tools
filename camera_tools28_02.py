bl_info = {
    "name": "Camera Tools",
    "author": "Alfonso Annarumam",
    "version": (0, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Tools",
    "description": "Manage Camera anche create path for animation ",
    "warning": "",
    "wiki_url": "",
    "category": "Camera",
    }


import bpy
from bpy.types import Menu, Panel, UIList, PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, FloatProperty, PointerProperty
from bpy.types import Menu, Panel, UIList, PropertyGroup, Operator


def main(context):
    loc_list = []
    rot_list = []
    sec_list =[]
    wait_list =[]
    frame_h_list =[]
    frame_t_list =[]
    scene = context.scene
    
    fps = scene.render.fps
    
    
    cam_list = scene.cameraitems
    frame = scene.cameraprop.frame
    
    for cam in cam_list:
        name = cam.name
        sec = cam.sec
        wait = cam.wait
        frame_t = cam.frame_t
        frame_h = cam.frame_h
        ob = scene.objects[name]
        if ob.type == 'CAMERA':
            
            loc_list.append(ob.location)
            rot_list.append(ob.rotation_euler)
            sec_list.append(sec)
            wait_list.append(wait)
            frame_h_list.append(frame_h)
            frame_t_list.append(frame_t)

    bpy.ops.object.camera_add()
    context.object.name = "CameraMorph"
    cam = context.object
    scene.camera = cam
    for loc,rot,sec,wait,frame_h,frame_t in zip(loc_list,rot_list,sec_list,wait_list,frame_h_list,frame_t_list):
        
        cam.location = loc
        cam.rotation_euler = rot
        #print(matr)
        bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot')
        if frame:
            frame_range = frame_h
        else:
            frame_range = sec*fps
        scene.frame_current += frame_range
        #print(wait)
        if frame:
            if frame_t == 0:
                bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot')
                scene.frame_current += 1

                
                print("do")
            else:   
                bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot') 
                scene.frame_current += fram_t
        else:
            if wait == 0.00:
                bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot')
                scene.frame_current += 1

                
                print("do")
            else:   
                bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot') 
                scene.frame_current += fps*wait

            


        

class CAMERA_OT_camera_operator(Operator):
    """Make Render Camera"""
    bl_idname = "camera.camera_operator"
    bl_label = "UI Camera Operator"
    
    name : StringProperty()
    op : StringProperty()
    
    switch : BoolProperty()
    select : BoolProperty()
    hide : BoolProperty()
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        
        
        name = self.name
        scene = context.scene
        camera = scene.objects[name]
        if self.op == "switch":
            scene.camera = camera
        if self.op == "hide":
            camera.hide_viewport = self.hide
        if self.op == "select":
            camera.select_set(self.select)
            
        return {'FINISHED'}
class SCENE_OT_camera_item_remove(Operator):
    """Remove and select a new layer group"""
    bl_idname = "scene.camera_item_remove"
    bl_label = "Remove Camera to list for Camera Tools"
    
    camera_idx : IntProperty()
    
#    @classmethod
#    def poll(cls, context):
#        return bool(context.scene)

    def execute(self, context):
        scene = context.scene
        camera_idx = self.camera_idx

        scene.cameraitems.remove(camera_idx)
        if scene.cameraitems_index > len(scene.cameraitems) - 1:
            scene.cameraitems_index = len(scene.cameraitems) - 1

        return {'FINISHED'}



class SCENE_OT_camera_item_move(Operator):
    """Add and select a new layer group"""
    bl_idname = "scene.camera_item_move"
    bl_label = "Move Camera in list for Camera Tools"
    
    move : StringProperty()
    camera_idx : IntProperty()
    
    @classmethod
    def poll(cls, context):
        return bool(context.scene)

    def execute(self, context):
        scene = context.scene
        cameraitems = scene.cameraitems
        camera_idx = self.camera_idx
        if self.move == 'UP':
            cameraitems.move(camera_idx, camera_idx-1)
            scene.cameraitems_index = camera_idx-1    
        if self.move == 'DOWN':
            cameraitems.move(camera_idx, camera_idx+1)
            scene.cameraitems_index = camera_idx+1

        return {'FINISHED'}


class SCENE_OT_camera_item_add(Operator):
    """Add and select a new layer group"""
    bl_idname = "scene.camera_item_add"
    bl_label = "Add Camera to list for Camera Tools"

    

    def execute(self, context):
        scene = context.scene
        cameraitems = scene.cameraitems
        
        for cam in context.selected_objects:
            if cam.type == 'CAMERA':
                 
                camera_idx = len(cameraitems)
                camera_item = cameraitems.add()
                camera_item.name = cam.name
                
                scene.cameraitems_index = camera_idx

        return {'FINISHED'}

class PROP_PG_camera_tools(PropertyGroup):


    frame : BoolProperty(name="Frames", default=False)

class ITEM_PG_camera_tools(PropertyGroup):


    camera : StringProperty(name="Cameras")
    sec : FloatProperty(default=2.0, description="Second of camera stay hold", name="Hold",min=0, soft_min=0, soft_max=360.0)
    wait : FloatProperty(default=0.0, description="Second to wait to switch camera", name="Time",min=0, soft_min=0, soft_max=360.0)
    frame_h : IntProperty(default=50, description="Frames to wait to switch camera", name="Hold",min=0)
    frame_t : IntProperty(default=0, description="Frames of camera stay hold", name="Time",min=0)
    
class LIST_UL_camera_items_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        camera_item = item

        cameraprop = context.scene.cameraprop
        
        if cameraprop.frame:
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                layout.prop(camera_item, "name", text="", emboss=False)
                layout.prop(camera_item, "frame_h", text="", emboss=False)
                layout.prop(camera_item, "frame_t", text="", emboss=False)
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
        else:
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                layout.prop(camera_item, "name", text="", emboss=False)
                layout.prop(camera_item, "sec", text="", emboss=False)
                layout.prop(camera_item, "wait", text="", emboss=False)


            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
            
            
class PANEL_PT_camera_tools_items(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera Tools"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "PANEL_PT_camera_tools"
    

    def draw(self, context):
        scene = context.scene
        group_idx = scene.cameraitems_index

        layout = self.layout
        
        
        row = layout.row()
        row.label(text="Camera")
        row.label(text="Hold")
        row.label(text="Time")
        
        
        row = layout.row()
        row.template_list("LIST_UL_camera_items_list", "", scene, "cameraitems", scene, "cameraitems_index")

        col = row.column(align=True)
        col.operator("scene.camera_item_add", icon='ADD', text="")
        col.operator("scene.camera_item_remove", icon='REMOVE', text="").camera_idx = group_idx
        up = col.operator("scene.camera_item_move", icon='TRIA_UP', text="")
        down =col.operator("scene.camera_item_move", icon='TRIA_DOWN', text="")
        up.camera_idx = group_idx
        down.camera_idx = group_idx
        up.move = 'UP'
        down.move = 'DOWN'
        
        row = layout.row()
        row.operator("scene.camera_morph", text="Camera morph")
       
            
        frame = "show Frame"
        row.prop(scene.cameraprop, "frame", text=frame)
#        if bool(scene.layergroups):
#            layout.prop(scene.layergroups[group_idx], "layers", text="", toggle=True)
#            layout.prop(scene.layergroups[group_idx], "name", text="Name:")


class PANEL_PT_camera_tools(Panel):
    """Manage Camera"""
    bl_label = "Camera Tools"
    bl_idname = "PANEL_PT_camera_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Tools"
    
    
    def draw(self, context):
        
        layout = self.layout
        
        riga = layout.row()
        
        riga.label(text="Camera in Scene")
        
        objs = context.scene.objects
        
        for obj in objs:
            
            
            if obj.type == 'CAMERA':
                riga2 = layout.row()
                
                riga2.prop(obj, "name", text="")
                #riga2.operator (
                #riga2.prop(obj, "select", text="")
                #riga2.prop(obj, "hide", text="")
                if obj.hide_viewport:
                    h_icon = 'HIDE_ON'
                else:
                    h_icon = 'HIDE_OFF'
                    
                hide = riga2.operator("camera.camera_operator", text="", icon=h_icon)
                hide.name = obj.name
                hide.op = "hide"
                hide.switch = False
                hide.hide = not obj.hide_viewport
                hide.select = False
                
                
                if obj.select_get():
                    s_icon = 'RESTRICT_SELECT_OFF'
                else:
                    s_icon = 'RESTRICT_SELECT_ON'
                select = riga2.operator("camera.camera_operator", text="", icon=s_icon)
                select.op = "select"
                select.select = not obj.select_get()
                select.switch = False
                select.name = obj.name
                select.hide = False
               
                if context.scene.camera == obj:
                    c_icon = 'RESTRICT_RENDER_OFF'
                else:
                    c_icon = 'OUTLINER_DATA_CAMERA'
                
                switch = riga2.operator("camera.camera_operator", text="", icon=c_icon)
                switch.op = "switch"
                switch.name = obj.name
                switch.switch = True
                switch.hide = False
                switch.select = False

       
class SCENE_OT_camera_morph(Operator):
    """Camera Morph"""
    bl_idname = "scene.camera_morph"
    bl_label = "Camera Morph"
    
   
    
    def execute(self, context):
        
        main(context)
        return {'FINISHED'}
    
    
classes = (
    CAMERA_OT_camera_operator,
    SCENE_OT_camera_morph,
    PANEL_PT_camera_tools,
    LIST_UL_camera_items_list,
    
    ITEM_PG_camera_tools,
    PROP_PG_camera_tools,
    PANEL_PT_camera_tools_items,
    SCENE_OT_camera_item_add,
    SCENE_OT_camera_item_remove,
    SCENE_OT_camera_item_move
    
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.cameraitems = CollectionProperty(type=ITEM_PG_camera_tools)
    # Unused, but this is needed for the TemplateList to work...
    bpy.types.Scene.cameraitems_index = IntProperty(default=-1)
    bpy.types.Scene.cameraprop = PointerProperty(type=PROP_PG_camera_tools)
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.cameraitems_index
    del bpy.types.Scene.cameraitems 
    del bpy.types.Scene.cameraprop 
    



if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.camera.camera_morph()
