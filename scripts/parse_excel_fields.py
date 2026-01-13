#!/usr/bin/env python3
"""
Excel 字段解析脚本

用于解析 Excel 文件中的所有 Sheet 和字段信息，输出结构化的数据字典。
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any
import sys


def parse_excel_file(file_path: str) -> Dict[str, Any]:
    """
    解析 Excel 文件，提取所有 Sheet 的字段信息

    Args:
        file_path: Excel 文件路径

    Returns:
        包含所有 Sheet 字段信息的字典
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 获取所有 Sheet 名称
    xl = pd.ExcelFile(file_path)
    sheet_names = xl.sheet_names

    result = {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "total_sheets": len(sheet_names),
        "sheets": {}
    }

    for sheet_name in sheet_names:
        # 读取 Sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # 获取字段信息
        columns = list(df.columns)
        row_count = len(df)

        # 获取每列的数据类型和示例值
        column_info = {}
        for col in columns:
            col_data = df[col]
            dtype = str(col_data.dtype)

            # 获取非空样本值（最多3个）
            non_null_values = col_data.dropna().head(3).tolist()
            sample_values = [str(v) for v in non_null_values]

            # 统计空值数量
            null_count = col_data.isna().sum()
            null_percentage = (null_count / row_count) * 100 if row_count > 0 else 0

            # 对于唯一值较少的字段，获取所有唯一值
            unique_count = col_data.nunique()
            unique_values = []
            if unique_count <= 20 and unique_count > 0:
                unique_values = [str(v) for v in col_data.dropna().unique()]

            column_info[col] = {
                "data_type": dtype,
                "sample_values": sample_values,
                "null_count": int(null_count),
                "null_percentage": round(null_percentage, 2),
                "unique_count": int(unique_count),
                "unique_values": unique_values if unique_values else None
            }

        result["sheets"][sheet_name] = {
            "column_count": len(columns),
            "row_count": row_count,
            "columns": columns,
            "column_details": column_info
        }

    return result


def print_markdown_dictionary(data: Dict[str, Any]):
    """
    将解析结果以 Markdown 格式输出

    Args:
        data: 解析结果数据
    """
    print(f"\n# 📋 数据字典 - {data['file_name']}\n")
    print(f"**文件路径**: `{data['file_path']}`  \n")
    print(f"**Sheet 数量**: {data['total_sheets']}\n")

    for sheet_name, sheet_info in data["sheets"].items():
        print(f"## {sheet_name}\n")
        print(f"- **行数**: {sheet_info['row_count']:,}")
        print(f"- **列数**: {sheet_info['column_count']}\n")

        print("| 字段名 | 数据类型 | 示例值 | 唯一值数 | 空值率 | 备注 |")
        print("|--------|----------|--------|----------|--------|------|")

        for col, details in sheet_info["column_details"].items():
            # 格式化示例值
            samples = ", ".join([f"`{v}`" for v in details["sample_values"]])
            if len(samples) > 50:
                samples = samples[:50] + "..."

            # 数据类型映射
            dtype_map = {
                "object": "string",
                "int64": "integer",
                "float64": "float",
                "datetime64[ns]": "datetime",
                "bool": "boolean"
            }
            dtype = dtype_map.get(details["data_type"], details["data_type"])

            # 唯一值显示
            unique_count = details["unique_count"]
            unique_display = unique_count
            if details["unique_values"]:
                unique_str = ", ".join([f"`{v}`" for v in details["unique_values"]])
                if len(unique_str) <= 30:
                    unique_display = f"{unique_count} ({unique_str})"
                else:
                    unique_display = f"{unique_count}"

            # 空值率显示
            null_pct = details["null_percentage"]
            null_display = f"{null_pct:.1f}%"

            print(f"| `{col}` | {dtype} | {samples} | {unique_display} | {null_display} | |")

        print()


def save_json_result(data: Dict[str, Any], output_path: str = None):
    """
    将解析结果保存为 JSON 文件

    Args:
        data: 解析结果数据
        output_path: 输出文件路径，默认为当前目录下的 excel_fields.json
    """
    if output_path is None:
        output_path = "excel_fields.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n📁 JSON 结果已保存到: {output_path}")


def main():
    """主函数"""
    # 默认文件路径
    default_file = "/Users/guoliang/Desktop/workspace/code/GalaxySpace/GalaxySpaceAI/CostMatrix/testdata/8月份考勤数据统计与分析1.xlsx"

    # 支持命令行参数
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = default_file

    print(f"🔍 正在解析 Excel 文件: {file_path}")

    try:
        data = parse_excel_file(file_path)

        # 打印 Markdown 格式的数据字典
        print_markdown_dictionary(data)

        # 保存 JSON 结果
        save_json_result(data)

        print("✅ 解析完成！")

    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
