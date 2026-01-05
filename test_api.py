"""
API 测试脚本
用于快速测试 CorpPilot API 功能
"""

import requests
import json
import sys
from pathlib import Path


API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查接口"""
    print("\n" + "="*50)
    print("测试 1: 健康检查")
    print("="*50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_analyze(file_path: str):
    """测试数据分析接口"""
    print("\n" + "="*50)
    print("测试 2: 数据分析")
    print("="*50)
    
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 分析成功!")
            print(f"\n--- KPI 指标 ---")
            kpi = data['data']['kpi']
            print(f"总差旅成本: ¥{kpi['total_cost']:,.2f}")
            print(f"总订单数: {kpi['total_orders']}")
            print(f"异常记录数: {kpi['anomaly_count']}")
            print(f"超标订单数: {kpi['over_standard_count']}")
            print(f"紧急预订比例: {kpi['urgent_booking_ratio']}%")
            
            print(f"\n--- 项目成本 Top 5 ---")
            for i, project in enumerate(data['data']['top_projects'][:5], 1):
                print(f"{i}. {project['项目代码']}: ¥{project['总成本']:,.2f}")
            
            print(f"\n--- 异常记录示例 (前3条) ---")
            for i, anomaly in enumerate(data['data']['anomalies'][:3], 1):
                print(f"{i}. [{anomaly['Type']}] {anomaly['姓名']} - {anomaly['日期']}")
                print(f"   {anomaly['描述']}")
            
            return True
        else:
            print(f"❌ 分析失败: {response.json()}")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_export(file_path: str, output_path: str = "output_分析结果.xlsx"):
    """测试导出接口"""
    print("\n" + "="*50)
    print("测试 3: Excel 导出")
    print("="*50)
    
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{API_BASE_URL}/api/export", files=files)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ 导出成功!")
            print(f"输出文件: {output_path}")
            print(f"文件大小: {len(response.content):,} bytes")
            return True
        else:
            print(f"❌ 导出失败: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_preview(file_path: str):
    """测试数据预览接口"""
    print("\n" + "="*50)
    print("测试 4: 数据预览")
    print("="*50)
    
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{API_BASE_URL}/api/preview", files=files)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 预览成功!")
            
            for sheet_name, sheet_info in data['data'].items():
                print(f"\n--- Sheet: {sheet_name} ---")
                print(f"列数: {len(sheet_info['columns'])}")
                print(f"行数: {sheet_info['row_count']}")
                print(f"列名: {', '.join(sheet_info['columns'][:5])}...")
            
            return True
        else:
            print(f"❌ 预览失败: {response.json()}")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def main():
    """主测试流程"""
    print("\n" + "🚀 " + "="*48)
    print("   CorpPilot API 测试工具")
    print("="*50)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print(f"  python test_api.py <excel_file_path>")
        print(f"\n示例:")
        print(f"  python test_api.py data.xlsx")
        return
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not Path(file_path).exists():
        print(f"\n❌ 错误: 文件不存在 - {file_path}")
        return
    
    print(f"\n测试文件: {file_path}")
    
    # 运行测试
    results = []
    
    # 1. 健康检查
    results.append(("健康检查", test_health_check()))
    
    # 2. 数据预览
    results.append(("数据预览", test_preview(file_path)))
    
    # 3. 数据分析
    results.append(("数据分析", test_analyze(file_path)))
    
    # 4. Excel 导出
    results.append(("Excel导出", test_export(file_path)))
    
    # 总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查服务状态")


if __name__ == "__main__":
    main()


