"""
CostMatrix API 使用示例
演示如何在 Python 代码中调用 API
"""

import requests
import json
from pathlib import Path


# API 基础 URL
API_BASE_URL = "http://localhost:8000"


def example_1_health_check():
    """
    示例 1: 健康检查
    检查 API 服务是否正常运行
    """
    print("\n" + "="*60)
    print("示例 1: 健康检查")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def example_2_analyze_data(excel_file_path: str):
    """
    示例 2: 分析差旅数据
    上传 Excel 文件并获取分析结果
    """
    print("\n" + "="*60)
    print("示例 2: 分析差旅数据")
    print("="*60)
    
    # 打开文件并上传
    with open(excel_file_path, 'rb') as f:
        files = {
            'file': (
                Path(excel_file_path).name,
                f,
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        }
        response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
    
    if response.status_code == 200:
        data = response.json()
        
        # 提取 KPI 数据
        kpi = data['data']['kpi']
        print(f"\n📊 KPI 核心指标:")
        print(f"  - 总差旅成本: ¥{kpi['total_cost']:,.2f}")
        print(f"  - 总订单数: {kpi['total_orders']}")
        print(f"  - 异常记录数: {kpi['anomaly_count']}")
        print(f"  - 超标订单数: {kpi['over_standard_count']}")
        print(f"  - 紧急预订比例: {kpi['urgent_booking_ratio']}%")
        
        # 提取项目成本数据
        top_projects = data['data']['top_projects']
        print(f"\n💰 项目成本 Top 5:")
        for i, project in enumerate(top_projects[:5], 1):
            print(f"  {i}. {project['项目代码']}: ¥{project['总成本']:,.2f}")
        
        # 提取部门数据
        dept_metrics = data['data']['department_metrics']
        print(f"\n🏢 部门指标:")
        for dept in dept_metrics[:3]:
            print(f"  - {dept['一级部门']}: 成本 ¥{dept['总成本']:,.2f}, 饱和度 {dept['饱和度']}%")
        
        # 提取异常记录
        anomalies = data['data']['anomalies']
        if anomalies:
            print(f"\n⚠️  异常记录示例:")
            for i, anomaly in enumerate(anomalies[:3], 1):
                print(f"  {i}. [{anomaly['Type']}] {anomaly['姓名']} - {anomaly['日期']}")
                print(f"     {anomaly['描述']}")
        
        return data
    else:
        print(f"❌ 分析失败: {response.text}")
        return None


def example_3_export_with_analysis(excel_file_path: str, output_path: str = "output.xlsx"):
    """
    示例 3: 导出带分析结果的 Excel
    上传文件并下载包含分析结果的新 Excel
    """
    print("\n" + "="*60)
    print("示例 3: 导出带分析结果的 Excel")
    print("="*60)
    
    with open(excel_file_path, 'rb') as f:
        files = {
            'file': (
                Path(excel_file_path).name,
                f,
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        }
        response = requests.post(f"{API_BASE_URL}/api/export", files=files)
    
    if response.status_code == 200:
        # 保存文件
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 导出成功!")
        print(f"  输出文件: {output_path}")
        print(f"  文件大小: {len(response.content):,} bytes")
        print(f"\n新增 Sheet:")
        print(f"  - Dashboard_Data: KPI、项目成本、部门指标")
        print(f"  - Anomaly_Log: 异常记录明细")
        
        return output_path
    else:
        print(f"❌ 导出失败: {response.text}")
        return None


def example_4_preview_data(excel_file_path: str):
    """
    示例 4: 预览 Excel 数据结构
    查看文件的 Sheet 和列信息
    """
    print("\n" + "="*60)
    print("示例 4: 预览 Excel 数据结构")
    print("="*60)
    
    with open(excel_file_path, 'rb') as f:
        files = {
            'file': (
                Path(excel_file_path).name,
                f,
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        }
        response = requests.post(f"{API_BASE_URL}/api/preview", files=files)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n📋 数据预览:")
        for sheet_name, sheet_info in data['data'].items():
            print(f"\n  Sheet: {sheet_name}")
            print(f"    - 行数: {sheet_info['row_count']}")
            print(f"    - 列数: {len(sheet_info['columns'])}")
            print(f"    - 列名: {', '.join(sheet_info['columns'][:8])}...")
        
        return data
    else:
        print(f"❌ 预览失败: {response.text}")
        return None


def example_5_batch_analysis(file_list: list):
    """
    示例 5: 批量分析多个文件
    循环处理多个 Excel 文件
    """
    print("\n" + "="*60)
    print("示例 5: 批量分析多个文件")
    print("="*60)
    
    results = []
    
    for file_path in file_list:
        if not Path(file_path).exists():
            print(f"\n⚠️  文件不存在: {file_path}")
            continue
        
        print(f"\n正在分析: {Path(file_path).name}")
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
        
        if response.status_code == 200:
            data = response.json()
            kpi = data['data']['kpi']
            
            results.append({
                'file': Path(file_path).name,
                'total_cost': kpi['total_cost'],
                'total_orders': kpi['total_orders'],
                'anomaly_count': kpi['anomaly_count']
            })
            
            print(f"  ✅ 成功 - 成本: ¥{kpi['total_cost']:,.2f}, 订单: {kpi['total_orders']}")
        else:
            print(f"  ❌ 失败")
    
    # 汇总结果
    if results:
        print(f"\n📊 批量分析汇总:")
        total_cost = sum(r['total_cost'] for r in results)
        total_orders = sum(r['total_orders'] for r in results)
        total_anomalies = sum(r['anomaly_count'] for r in results)
        
        print(f"  - 文件数量: {len(results)}")
        print(f"  - 总成本: ¥{total_cost:,.2f}")
        print(f"  - 总订单数: {total_orders}")
        print(f"  - 总异常数: {total_anomalies}")
    
    return results


def example_6_filter_anomalies(excel_file_path: str, anomaly_type: str = "Conflict"):
    """
    示例 6: 筛选特定类型的异常
    从分析结果中提取特定类型的异常记录
    """
    print("\n" + "="*60)
    print(f"示例 6: 筛选异常类型 - {anomaly_type}")
    print("="*60)
    
    with open(excel_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
    
    if response.status_code == 200:
        data = response.json()
        anomalies = data['data']['anomalies']
        
        # 筛选特定类型
        filtered = [a for a in anomalies if a['Type'] == anomaly_type]
        
        print(f"\n找到 {len(filtered)} 条 {anomaly_type} 类型异常:")
        
        # 按部门分组统计
        dept_count = {}
        for anomaly in filtered:
            dept = anomaly['一级部门']
            dept_count[dept] = dept_count.get(dept, 0) + 1
        
        print(f"\n按部门分布:")
        for dept, count in sorted(dept_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {dept}: {count} 条")
        
        # 显示详细记录
        print(f"\n详细记录 (前5条):")
        for i, anomaly in enumerate(filtered[:5], 1):
            print(f"  {i}. {anomaly['姓名']} - {anomaly['日期']}")
            print(f"     部门: {anomaly['一级部门']}, 金额: ¥{anomaly['差旅金额']:.2f}")
            print(f"     {anomaly['描述']}")
        
        return filtered
    else:
        print(f"❌ 分析失败")
        return None


def example_7_department_ranking(excel_file_path: str):
    """
    示例 7: 部门成本排名
    分析各部门的差旅成本并排名
    """
    print("\n" + "="*60)
    print("示例 7: 部门成本排名")
    print("="*60)
    
    with open(excel_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
    
    if response.status_code == 200:
        data = response.json()
        dept_metrics = data['data']['department_metrics']
        
        print(f"\n🏆 部门成本排名:")
        for i, dept in enumerate(dept_metrics, 1):
            print(f"\n  第 {i} 名: {dept['一级部门']}")
            print(f"    - 总成本: ¥{dept['总成本']:,.2f}")
            print(f"    - 人员数: {dept['人员数量']} 人")
            print(f"    - 人均成本: ¥{dept['总成本']/dept['人员数量']:,.2f}")
            print(f"    - 饱和度: {dept['饱和度']}%")
        
        return dept_metrics
    else:
        print(f"❌ 分析失败")
        return None


# 主程序
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  python examples.py <excel_file_path>")
        print("\n示例:")
        print("  python examples.py data.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not Path(excel_file).exists():
        print(f"\n❌ 文件不存在: {excel_file}")
        sys.exit(1)
    
    print("\n" + "🚀 " + "="*58)
    print("   CostMatrix API 使用示例演示")
    print("="*60)
    
    # 运行所有示例
    example_1_health_check()
    example_4_preview_data(excel_file)
    example_2_analyze_data(excel_file)
    example_3_export_with_analysis(excel_file, "output_分析结果.xlsx")
    example_6_filter_anomalies(excel_file, "Conflict")
    example_7_department_ranking(excel_file)
    
    # 批量分析示例（如果有多个文件）
    # example_5_batch_analysis(['file1.xlsx', 'file2.xlsx'])
    
    print("\n" + "="*60)
    print("✅ 所有示例演示完成！")
    print("="*60 + "\n")


