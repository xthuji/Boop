#!/usr/bin/env python3
"""
BoopPython Optimized Test Runner (Grouped Output Edition)
功能：自动扫描测试用例、按脚本分组并行执行、保证输出连续性。
"""

import sys
import json
import unittest
import time
import argparse
import importlib.util
import concurrent.futures
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple, NamedTuple

# --- 数据模型 ---

class TestResult(NamedTuple):
    name: str
    passed: bool
    message: str = ""
    duration: float = 0.0

class BoopState:
    def __init__(self, text: str):
        self.text = text
    
    def post_info(self, msg):
        pass # 生产环境通常重定向或忽略，避免干扰控制台
    
    def post_error(self, msg):
        pass

# --- 核心逻辑 ---

class TestRunner:
    def __init__(self, scripts_dir: Path):
        self.scripts_dir = scripts_dir

    def run_single(self, script_name: str, input_text: str, expected: str) -> TestResult:
        start_time = time.time()
        script_path = self.scripts_dir / f"{script_name}.py"
        
        if not script_path.exists():
            return TestResult(script_name, False, f"未找到脚本: {script_path}", time.time() - start_time)

        try:
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if not spec or not spec.loader:
                return TestResult(script_name, False, "无法加载模块", time.time() - start_time)
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            state = BoopState(input_text)
            module.main(state)

            duration = time.time() - start_time
            if state.text == expected:
                return TestResult(script_name, True, "OK", duration)
            else:
                return TestResult(script_name, False, f"FAIL: 期望 {repr(expected)} 但得到 {repr(state.text)}", duration)
        except Exception as e:
            return TestResult(script_name, False, f"ERROR: {str(e)}", time.time() - start_time)

# --- 辅助工具 ---

def load_all_test_cases(test_dir: Path) -> List[Dict]:
    all_categories = []
    for json_file in test_dir.glob("test_cases*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_categories.extend(data.get('testCases', []))
        except Exception as e:
            print(f"警告: 无法加载 {json_file.name}: {e}")
    return all_categories

def print_summary(results: List[TestResult], unit_results: Optional[unittest.TestResult]):
    """生成整洁的分组报告"""
    print("\n" + "=" * 60)
    print(f"测试报告 - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    # 按脚本名称分组打印结果
    grouped = defaultdict(list)
    for r in results:
        grouped[r.name].append(r)

    for script_name, res_list in sorted(grouped.items()):
        all_ok = all(r.passed for r in res_list)
        status_icon = "✅" if all_ok else "❌"
        print(f"{status_icon} 脚本: {script_name}")
        for i, r in enumerate(res_list):
            prefix = "  └─" if i == len(res_list)-1 else "  ├─"
            msg = f" Case {i+1}: {r.message}" if not r.passed else f" Case {i+1}: Pass"
            print(f"{prefix}{msg} ({r.duration:.3f}s)")
    
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print("-" * 60)
    print(f"统计概览: {passed}/{total} 通过")
    if unit_results and unit_results.testsRun > 0:
        print(f"单元测试: {unit_results.testsRun - len(unit_results.failures) - len(unit_results.errors)}/{unit_results.testsRun} 通过")
    print("=" * 60)

# --- 主程序 ---

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('script', nargs='?', help='指定脚本名')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()

    test_dir = Path(__file__).parent
    scripts_dir = test_dir.parent / 'boop' / 'scripts'
    
    # 1. 搜集并分组任务
    categories = load_all_test_cases(test_dir)
    tasks = [] # (script_name, input, expected)
    
    for cat in categories:
        for script_item in cat.get('scripts', []):
            s_name = script_item.get('name')
            if args.script and s_name != args.script: continue
            for test in script_item.get('tests', []):
                tasks.append((s_name, test.get('input', ''), test.get('expected', '')))

    # 2. 并行执行
    results = []
    if tasks:
        print(f"正在并行执行 {len(tasks)} 个用例...")
        runner = TestRunner(scripts_dir)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            # 提交所有任务
            future_to_task = [executor.submit(runner.run_single, *t) for t in tasks]
            # 按提交顺序收集结果（确保即使并发完成，列表顺序也是可控的）
            for future in future_to_task:
                results.append(future.result())

    # 3. 运行单元测试（仅当存在 test_*.py 文件时）
    suite = unittest.defaultTestLoader.discover(str(test_dir), pattern='test_*.py')
    unit_test_result = unittest.TextTestRunner(verbosity=0).run(suite)
    # 只有在实际运行了单元测试时才保留结果，否则设为 None
    if unit_test_result.testsRun == 0:
        unit_test_result = None

    # 4. 打印报告
    print_summary(results, unit_test_result)

    has_failed = any(not r.passed for r in results) or (unit_test_result and not unit_test_result.wasSuccessful())
    sys.exit(1 if has_failed else 0)

if __name__ == '__main__':
    main()