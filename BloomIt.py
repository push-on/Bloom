bl_info = {
    "name": "Bloom Effect Toggle",
    "blender": (4, 2, 0),
    "category": "Render",
    "version": (1, 0, 0),
    "author": "Imran Hossain",
    "description": "Adds a panel to toggle bloom effect in the viewport and compositor",
}

import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import BoolProperty, PointerProperty

def update_bloom(self, context):
    if self.use_bloom:
        add_bloom(context)
    else:
        remove_bloom(context)

class BloomProperties(PropertyGroup):
    use_bloom: BoolProperty(
        name="Use Bloom",
        description="Enable/Disable Bloom effect",
        default=False,
        update=update_bloom
    )

def add_bloom(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            if hasattr(space.shading, 'use_compositor'):
                space.shading.use_compositor = 'ALWAYS'
            if space.shading.type != 'RENDERED':
                space.shading.type = 'RENDERED'
    
    context.scene.use_nodes = True
    
    tree = context.scene.node_tree
    
    glare_node = next((node for node in tree.nodes if node.type == 'GLARE'), None)
    
    if not glare_node:
        glare_node = tree.nodes.new(type='CompositorNodeGlare')
        glare_node.glare_type = 'BLOOM'
        glare_node.quality = 'HIGH'
        
        composite_node = next((node for node in tree.nodes if node.type == 'COMPOSITE'), None)
        
        if composite_node:
            render_layers = next((node for node in tree.nodes if node.type == 'R_LAYERS'), None)
            if render_layers:
                tree.links.new(render_layers.outputs['Image'], glare_node.inputs['Image'])
                tree.links.new(glare_node.outputs['Image'], composite_node.inputs['Image'])

def remove_bloom(context):
    tree = context.scene.node_tree
    glare_node = next((node for node in tree.nodes if node.type == 'GLARE'), None)
    if glare_node:
        tree.nodes.remove(glare_node)
    
    render_layers = next((node for node in tree.nodes if node.type == 'R_LAYERS'), None)
    composite_node = next((node for node in tree.nodes if node.type == 'COMPOSITE'), None)
    if render_layers and composite_node:
        tree.links.new(render_layers.outputs['Image'], composite_node.inputs['Image'])

class RENDER_PT_viewport_setup(Panel):
    bl_label = "BLOOM"
    bl_idname = "RENDER_PT_viewport_setup"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = -1
    
    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        bloom_props = scene.bloom_properties
        layout.prop(bloom_props, "use_bloom", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bloom_props = scene.bloom_properties

        if bloom_props.use_bloom:
            tree = context.scene.node_tree
            glare_node = next((node for node in tree.nodes if node.type == 'GLARE'), None)
            if glare_node:
                layout.use_property_split = True
                layout.use_property_decorate = False
                
                col = layout.column()
                col.prop(glare_node, "glare_type", text="Glare Type")
                col.prop(glare_node, "quality", text="Quality")
                for input_name, input_socket in glare_node.inputs.items():
                    if input_socket.enabled and not input_socket.is_linked:
                        col.prop(input_socket, "default_value", text=input_name)
                col.prop(glare_node, "mix", text="Mix")
                col.prop(glare_node, "size", text="Size")

def register():
    bpy.utils.register_class(BloomProperties)
    bpy.types.Scene.bloom_properties = PointerProperty(type=BloomProperties)
    bpy.utils.register_class(RENDER_PT_viewport_setup)

def unregister():
    bpy.utils.unregister_class(RENDER_PT_viewport_setup)
    del bpy.types.Scene.bloom_properties
    bpy.utils.unregister_class(BloomProperties)

if __name__ == "__main__":
    register()
