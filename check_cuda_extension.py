#!/usr/bin/env python3
"""
快速诊断CUDA扩展编译状态
可以在Colab或本地运行
"""

import sys
import os

def check_cuda_extension():
    print("="*60)
    print("🔍 诊断CUDA扩展编译状态")
    print("="*60)
    
    # 1. 检查sort_vertices模块
    print("\n1️⃣ 检查 sort_vertices 模块:")
    try:
        import sort_vertices
        print(f"   ✅ 模块已加载")
        print(f"   📍 位置: {sort_vertices.__file__}")
        print(f"   📦 包含函数: {dir(sort_vertices)}")
        sort_vertices_ok = True
    except ImportError as e:
        print(f"   ❌ 模块未找到: {e}")
        print(f"   💡 需要重新编译 CUDA 扩展")
        sort_vertices_ok = False
    
    # 2. 检查编译产物
    print("\n2️⃣ 检查编译产物 (.so 文件):")
    
    search_paths = [
        "/usr/local/lib/python*/dist-packages/sort_vertices*.so",
        "~/.local/lib/python*/site-packages/sort_vertices*.so",
        "./third_party/Rotated_IoU/cuda_op/build/**/sort_vertices*.so",
        "./build/**/sort_vertices*.so"
    ]
    
    import glob
    found_files = []
    for pattern in search_paths:
        matches = glob.glob(os.path.expanduser(pattern), recursive=True)
        found_files.extend(matches)
    
    if found_files:
        print(f"   ✅ 找到 {len(found_files)} 个编译产物:")
        for f in found_files:
            size = os.path.getsize(f) / 1024
            print(f"      - {f} ({size:.1f}KB)")
    else:
        print(f"   ❌ 未找到任何 .so 文件")
        print(f"   💡 CUDA扩展未编译成功")
    
    # 3. 检查oriented_iou_loss
    print("\n3️⃣ 检查 oriented_iou_loss 模块:")
    
    # 添加项目路径
    project_paths = [
        os.path.dirname(os.path.abspath(__file__)),
        "/content/LayoutVLM",
        os.getcwd()
    ]
    
    for path in project_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
    
    try:
        from third_party.Rotated_IoU import oriented_iou_loss
        print(f"   ✅ oriented_iou_loss 导入成功")
        print(f"   📍 位置: {oriented_iou_loss.__file__}")
        oriented_iou_ok = True
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}")
        oriented_iou_ok = False
    
    # 4. 检查constraints.py中的状态
    print("\n4️⃣ 检查 constraints.ORIENTED_IOU_AVAILABLE:")
    
    try:
        from src.layoutvlm import constraints
        if constraints.ORIENTED_IOU_AVAILABLE:
            print(f"   ✅ ORIENTED_IOU_AVAILABLE = True")
            print(f"   🚀 将使用CUDA加速的IoU计算")
        else:
            print(f"   ❌ ORIENTED_IOU_AVAILABLE = False")
            print(f"   ⚠️  将使用Shapely CPU fallback（慢5-10倍）")
        constraints_ok = constraints.ORIENTED_IOU_AVAILABLE
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        constraints_ok = False
    
    # 5. 功能测试
    print("\n5️⃣ 功能测试 (CUDA IoU计算):")
    
    if sort_vertices_ok and oriented_iou_ok:
        try:
            import torch
            
            # 检查CUDA
            if not torch.cuda.is_available():
                print(f"   ⚠️  CUDA不可用，跳过测试")
            else:
                print(f"   🎮 CUDA设备: {torch.cuda.get_device_name(0)}")
                
                # 创建测试数据
                corners1 = torch.randn(1, 2, 4, 2).cuda()
                corners2 = torch.randn(1, 2, 4, 2).cuda()
                area1 = torch.ones(1, 2).cuda()
                area2 = torch.ones(1, 2).cuda()
                
                # 测试计算
                import time
                start = time.time()
                giou_loss, iou = oriented_iou_loss.cal_giou(corners1, corners2, area1, area2)
                elapsed = (time.time() - start) * 1000
                
                print(f"   ✅ CUDA IoU计算成功")
                print(f"   📊 结果: GIoU={giou_loss[0,0].item():.4f}, IoU={iou[0,0].item():.4f}")
                print(f"   ⏱️  耗时: {elapsed:.2f}ms")
                
                functional_ok = True
        except Exception as e:
            print(f"   ❌ 功能测试失败: {e}")
            import traceback
            traceback.print_exc()
            functional_ok = False
    else:
        print(f"   ⏭️  跳过（模块未加载）")
        functional_ok = False
    
    # 6. 总结
    print("\n" + "="*60)
    print("📋 诊断总结:")
    print("="*60)
    
    checks = {
        "sort_vertices 模块": sort_vertices_ok,
        "编译产物 .so 文件": len(found_files) > 0,
        "oriented_iou_loss 导入": oriented_iou_ok,
        "ORIENTED_IOU_AVAILABLE": constraints_ok if 'constraints_ok' in locals() else False,
        "功能测试": functional_ok if 'functional_ok' in locals() else False
    }
    
    all_ok = all(checks.values())
    
    for check_name, status in checks.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {check_name}")
    
    print("="*60)
    
    if all_ok:
        print("\n🎉 CUDA扩展配置完美！")
        print("🚀 优化性能将提升 5-10倍")
        return 0
    else:
        print("\n⚠️  CUDA扩展存在问题")
        print("\n💡 修复建议:")
        
        if not sort_vertices_ok:
            print("   1. 重新编译CUDA扩展:")
            print("      cd third_party/Rotated_IoU/cuda_op")
            print("      python3 setup.py install --user")
        
        if not constraints_ok:
            print("   2. 检查导入路径:")
            print("      import sys")
            print("      sys.path.insert(0, '/path/to/LayoutVLM')")
        
        print("\n📚 详细文档: CUDA_EXTENSION_FIX.md")
        return 1

if __name__ == "__main__":
    exit_code = check_cuda_extension()
    sys.exit(exit_code)
