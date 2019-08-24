"""
 対象のオブジェクト位置を中心として
 X/Y/Z軸に対して
 指定した半径の円周上にオブジェクトを
 同じ大きさで複製する

 Duplicate the object with the same size on the circumference of
 the specified radius with respect to the X / Y / Z axis centering
 on the target object position.
"""
import math

import bpy
from bpy.props import (
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty
)
from bpy.types import Panel


bl_info = {
    "name": "TQ Circular Array",
    "description": "Make an array in a circular shape",
    "author": "Takashi Q. Hanamura",
    "version": (0, 1, 0, 0),
    "blender": (2, 80, 0),
    "category": "Object",
    "location": "View3D > Sidebar",
    "warning": "",
    "wiki_url": "",
    "tracker_url": ""
}


# Array対象オブジェクト
bpy.types.Scene.CircularArray_target = bpy.props.PointerProperty(
    name="Target object",
    description="Target object",
    type=bpy.types.Object
)
# 回転軸（デフォルト：X軸）
bpy.types.Scene.CircularArray_axis = bpy.props.EnumProperty(
    name="Axis of rotation",
    description="Axis of rotation",
    items=[("x", "X", "", 1), ("y", "Y", "", 2), ("z", "Z", "", 3)]
)
# 回転半径
bpy.types.Scene.CircularArray_radius = bpy.props.FloatProperty(
    name="Array radius",
    description="Array radius",
    default=5,
    min=0.001
)
# 複製する個数
bpy.types.Scene.CircularArray_count = bpy.props.IntProperty(
    name="Array count",
    description="Array count",
    default=2,
    min=1,
    max=50
)


# Operationクラス
class TQ_OT_CircularArray_Operator(bpy.types.Operator):
    bl_idname = "object.circular_array"
    bl_label = "Circular Array"
    bl_description = "Make an array in a circular shape"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "CircularArray_target")

    def execute(self, context):
        #
        # Want ToDo:
        # 2. パネルで半径やカウントを増減させたら都度反映させたい
        # 3. execute部分が長いのでクラス化して見やすく（？）したい
        #
        # Finish:
        # 1. 対象オブジェクトのスケールを維持する
        # 4. オブジェクトの有無チェックなどエラー処理
        #

        # Array対象オブジェクト
        target_ob = bpy.context.scene.CircularArray_target

        if target_ob is not None:
            # Array回転軸
            axis = bpy.context.scene.CircularArray_axis
            # Array半径
            radius = bpy.context.scene.CircularArray_radius
            # Array数
            count = bpy.context.scene.CircularArray_count

            # Array対象オブジェクトをアクティブ
            bpy.ops.object.select_all(action="DESELECT")
            target_ob.select_set(state=True)
            bpy.context.view_layer.objects.active = target_ob

            # Array対象オブジェクトが等倍で複製されるよう現在の変形状態を確定
            bpy.ops.object.transform_apply(
                location=False,
                rotation=True,
                scale=True)

            # Array対象オブジェクトをEDITモードで変形（移動）
            trans_x, trans_y, trans_z = 0, 0, 0
            if axis == 'x':
                trans_y = radius
                rotation_axis = 0  # X軸
            elif axis == 'y':
                trans_z = radius
                rotation_axis = 1  # Y軸
            else:
                trans_x = radius
                rotation_axis = 2  # Z軸

            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.transform.translate(
                value=(trans_x, trans_y, trans_z),
                orient_type="GLOBAL",
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                orient_matrix_type="GLOBAL",
                constraint_axis=(False, False, False),
                mirror=True,
                proportional="DISABLED",
                proportional_edit_falloff="SMOOTH",
                proportional_size=1
            )

            # Array対象オブジェクトをOBJECTモードで変形（回転）
            bpy.ops.object.mode_set(mode="OBJECT")
            rad = float(360 / count) * (math.pi / 180)
            bpy.context.object.rotation_euler[rotation_axis] = rad

            # Array Modifierを追加
            bpy.context.scene.cursor.location = bpy.context.object.location
            bpy.ops.object.origin_set(
                type="ORIGIN_CURSOR",
                center="MEDIAN"
            )
            array_mod = target_ob.modifiers.new(
                type="ARRAY",
                name="TQ_Circular_Array"
            )
            array_mod.use_relative_offset = False
            array_mod.use_object_offset = True
            array_mod.count = count

            # Emptyオブジェクトを追加
            circle_empty = bpy.data.objects.new("tq_circle_empty", None)
            bpy.context.scene.collection.objects.link(circle_empty)
            circle_empty.location = target_ob.location

            circle_empty.empty_display_size = 1
            circle_empty.empty_display_type = "ARROWS"
            array_mod.offset_object = circle_empty

            # 親子設定
            bpy.data.objects[circle_empty.name].select_set(state=True)
            bpy.ops.object.parent_set(type="OBJECT", keep_transform=False)
            bpy.data.objects[circle_empty.name].select_set(state=False)
        else:
            # エラー
            self.report({'WARNING'}, "Please select object.")

        return {'FINISHED'}


# Panelクラス
class TQ_PT_CircularArray_Panel(bpy.types.Panel):
    bl_label = "Circular Array"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Circular Array"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        # Array対象のオブジェクト
        row = layout.row()
        row.prop_search(context.scene, "CircularArray_target",
                        context.scene, "objects", text="Target")
        # Array回転軸
        row = layout.row()
        row.prop(context.scene, "CircularArray_axis",
                 text="Mirror Axis", expand=True)
        # Array半径
        row = layout.row()
        row.prop(context.scene, "CircularArray_radius",
                 text="Radius")
        # Array数
        row = layout.row()
        row.prop(context.scene, "CircularArray_count",
                 text="Count")
        # 実行ボタン
        layout.separator()
        row = layout.row()
        row.operator(TQ_OT_CircularArray_Operator.bl_idname,
                     text="Array")


# クラス一覧
classes = (
    TQ_OT_CircularArray_Operator,
    TQ_PT_CircularArray_Panel
)


# # 翻訳辞書
# TQ_translation_dict = {
#     "en_US": {
#     },
#     "ja_JP": {
#         ("*", "hoge"):
#         "ほげ",
#     }
# }


# 登録
def register():
    # クラスの登録
    for cls in classes:
        bpy.utils.register_class(cls)

    # # 辞書の登録
    # bpy.app.translations.register(__name__, TQ_translation_dict)


# 削除
def unregister():
    # クラスの削除
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # # 辞書の削除
    # bpy.app.translations.unregister(__name__)


# Add-On Entry
if __name__ == "__main__":
    register()
