#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试套件运行脚本
使用 pytest 统一运行所有测试，支持多线程执行
"""
import sys
import os
import subprocess
import argparse
import concurrent.futures
import time
from typing import List

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_all_tests(parallel: bool = False):
    """运行所有测试"""
    print("🚀 开始运行 Python SDK 测试套件 (pytest)")
    print("=" * 60)
    
    if parallel:
        return run_all_tests_parallel()
    else:
        # 使用 pytest 运行所有测试
        result = subprocess.run([sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"])
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("🎉 所有测试通过！Python SDK 测试套件执行完成")
            return True
        else:
            print(f"❌ 测试失败: 退出码 {result.returncode}")
            return False


def run_all_tests_parallel():
    """并行运行所有测试模块"""
    print("🔄 使用多线程并行运行所有测试模块")
    
    modules = ['goods', 'color', 'size', 'brand', 'material', 'user', 'supplier', 
               'season', 'storehouse', 'ranges', 'produce', 'report', 'oss', 'token']
    
    start_time = time.time()
    
    # 使用线程池并行执行测试
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 提交所有测试任务
        future_to_module = {
            executor.submit(run_module_test_single, module): module 
            for module in modules
        }
        
        # 收集结果
        results = []
        for future in concurrent.futures.as_completed(future_to_module):
            module = future_to_module[future]
            try:
                success = future.result()
                results.append((module, success))
            except Exception as exc:
                print(f'模块 {module} 产生异常: {exc}')
                results.append((module, False))
    
    end_time = time.time()
    
    # 统计结果
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print("\n" + "=" * 60)
    print(f"📊 并行测试执行完成 (耗时: {end_time - start_time:.2f}秒)")
    print(f"✅ 通过模块: {passed}")
    print(f"❌ 失败模块: {failed}")
    
    if failed == 0:
        print("🎉 所有测试模块通过！Python SDK 测试套件执行完成")
        return True
    else:
        print("❌ 部分测试模块失败:")
        for module, success in results:
            if not success:
                print(f"  - {module}")
        return False


def run_module_test_single(module_name: str) -> bool:
    """运行单个模块测试（用于并行执行）"""
    print(f"🧪 开始运行 {module_name} 模块测试")
    
    try:
        # 使用 -k 参数按文件名匹配
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "-k", module_name, 
            "-v", "--tb=short", 
            "--disable-warnings"
        ], capture_output=True, text=True, timeout=300)  # 5分钟超时
        
        if result.returncode == 0:
            print(f"✅ {module_name} 模块测试通过")
            return True
        else:
            print(f"❌ {module_name} 模块测试失败")
            print(f"   错误输出: {result.stderr[:200]}...")  # 只显示前200个字符
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {module_name} 模块测试超时")
        return False
    except Exception as e:
        print(f"💥 {module_name} 模块测试异常: {e}")
        return False


def run_module_tests(module_name: str, parallel: bool = False):
    """运行指定模块的测试"""
    print(f"🧪 运行 {module_name} 模块测试")
    
    if parallel:
        # 并行运行单个模块（如果有子测试的话）
        return run_module_test_single(module_name)
    else:
        # 使用 -k 参数按文件名匹配
        result = subprocess.run([sys.executable, "-m", "pytest", "-k", module_name, "-v", "--tb=short"])
        
        if result.returncode == 0:
            print(f"✅ {module_name} 模块测试通过")
            return True
        else:
            print(f"❌ {module_name} 模块测试失败: 退出码 {result.returncode}")
            return False


def list_test_modules():
    """列出所有可用的测试模块"""
    modules = ['goods', 'color', 'size', 'brand', 'material', 'user', 'supplier', 
               'season', 'storehouse', 'ranges', 'produce', 'report', 'oss', 'token']
    print("📋 可用的测试模块:")
    for module in modules:
        print(f"  - {module}")


def main():
    parser = argparse.ArgumentParser(description="Python SDK 测试套件运行器")
    parser.add_argument("command", nargs="?", default="all", 
                        choices=["list", "all", "goods", "color", "size", "brand", "material", 
                                "user", "supplier", "season", "storehouse", "ranges", "produce", 
                                "report", "oss", "token"],
                        help="要执行的命令: list, all, 或特定模块名")
    parser.add_argument("--parallel", "-p", action="store_true", 
                        help="启用并行测试执行")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_test_modules()
    elif args.command == "all":
        run_all_tests(parallel=args.parallel)
    else:
        run_module_tests(args.command, parallel=args.parallel)


if __name__ == "__main__":
    main()