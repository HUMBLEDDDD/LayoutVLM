#!/usr/bin/env python3
"""
测试Blender GPU渲染配置
在Colab中运行：blender --background --python test_gpu_render.py
"""

import sys
import os

# 确保在Blender环境中
try:
    import bpy
except ImportError:
    print("❌ 错误：此脚本需要在Blender中运行")
    print("使用: blender --background --python test_gpu_render.py")
    sys.exit(1)

def test_gpu_configuration():
    """测试GPU渲染配置"""
    print("="*60)
    print("🔍 检测GPU渲染配置")
    print("="*60)
    
    # 1. 检查Cycles插件
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        print("\n✅ Cycles渲染引擎已安装")
    except:
        print("\n❌ Cycles渲染引擎未安装")
        return False
    
    # 2. 测试不同GPU类型
    print("\n📊 可用GPU类型:")
    gpu_types = ['OPTIX', 'CUDA', 'OPENCL', 'METAL', 'HIP']
    available_types = []
    
    for gpu_type in gpu_types:
        try:
            prefs.compute_device_type = gpu_type
            prefs.get_devices()
            devices = [d for d in prefs.devices if d.type == gpu_type]
            if devices:
                available_types.append(gpu_type)
                print(f"   ✅ {gpu_type}: {len(devices)} 设备")
                for device in devices:
                    print(f"      - {device.name}")
            else:
                print(f"   ❌ {gpu_type}: 不可用")
        except Exception as e:
            print(f"   ❌ {gpu_type}: 错误 ({str(e)[:50]})")
    
    if not available_types:
        print("\n⚠️  警告：未找到任何GPU设备，将使用CPU渲染")
        return False
    
    # 3. 设置最佳GPU类型
    best_type = available_types[0]
    prefs.compute_device_type = best_type
    prefs.get_devices()
    
    print(f"\n🎯 选择最佳GPU类型: {best_type}")
    
    # 4. 启用所有GPU设备
    gpu_count = 0
    cpu_count = 0
    
    print("\n⚙️  设备配置:")
    for device in prefs.devices:
        if device.type in ['OPTIX', 'CUDA', 'OPENCL', 'METAL', 'HIP']:
            device.use = True
            gpu_count += 1
            print(f"   ✅ GPU {gpu_count}: {device.name} [{device.type}]")
        else:
            device.use = False
            cpu_count += 1
            print(f"   ⏸️  CPU {cpu_count}: {device.name} (已禁用)")
    
    # 5. 配置场景使用GPU
    bpy.context.scene.cycles.device = "GPU"
    
    print(f"\n📋 最终配置:")
    print(f"   渲染设备: {bpy.context.scene.cycles.device}")
    print(f"   GPU类型: {prefs.compute_device_type}")
    print(f"   启用GPU数: {gpu_count}")
    print(f"   渲染引擎: Cycles")
    
    # 6. 简单渲染测试
    print("\n🎨 执行简单渲染测试...")
    
    # 创建简单场景
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # 添加立方体
    bpy.ops.mesh.primitive_cube_add()
    
    # 添加光源
    bpy.ops.object.light_add(type='SUN')
    
    # 添加相机
    bpy.ops.object.camera_add(location=(5, -5, 5))
    cam = bpy.context.object
    cam.rotation_euler = (1.1, 0, 0.8)
    bpy.context.scene.camera = cam
    
    # 配置渲染
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 32
    bpy.context.scene.render.resolution_x = 256
    bpy.context.scene.render.resolution_y = 256
    
    # 渲染
    output_path = "/tmp/gpu_test.png"
    bpy.context.scene.render.filepath = output_path
    
    import time
    start_time = time.time()
    
    try:
        bpy.ops.render.render(write_still=True)
        render_time = time.time() - start_time
        
        print(f"✅ 渲染成功！")
        print(f"   耗时: {render_time:.2f}秒")
        print(f"   输出: {output_path}")
        
        # 检查文件大小
        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) / 1024
            print(f"   大小: {size_kb:.1f}KB")
        
        return True
        
    except Exception as e:
        print(f"❌ 渲染失败: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 开始GPU渲染测试\n")
    success = test_gpu_configuration()
    
    print("\n" + "="*60)
    if success:
        print("✅ GPU渲染配置成功！")
    else:
        print("⚠️  GPU渲染配置失败，将使用CPU渲染")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
