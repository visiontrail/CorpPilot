"""
数据加载和清洗模块
负责从 Excel 读取数据并进行预处理
"""

import pandas as pd
import re
from typing import Dict, Tuple
from datetime import datetime
from logger_config import get_logger


class DataLoader:
    """Excel 数据加载器"""
    
    def __init__(self, file_path: str):
        """
        初始化数据加载器
        
        Args:
            file_path: Excel 文件路径
        """
        self.file_path = file_path
        self.attendance_df = None
        self.flight_df = None
        self.hotel_df = None
        self.train_df = None
        self.logger = get_logger("data_loader")
        
        self.logger.info(f"初始化数据加载器，文件路径: {file_path}")
    
    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        """
        加载所有 Sheet 数据
        
        Returns:
            包含所有 DataFrame 的字典
        """
        try:
            self.logger.info("开始加载所有工作表")
            
            # 读取考勤数据
            self.logger.debug("正在读取考勤数据（状态明细）")
            self.attendance_df = pd.read_excel(
                self.file_path, 
                sheet_name="状态明细"
            )
            self.logger.info(f"考勤数据加载完成，行数: {len(self.attendance_df)}, 列数: {len(self.attendance_df.columns)}")
            self._clean_attendance_data()
            
            # 读取差旅数据
            self.logger.debug("正在读取机票数据")
            self.flight_df = pd.read_excel(
                self.file_path, 
                sheet_name="机票"
            )
            self.logger.info(f"机票数据加载完成，行数: {len(self.flight_df)}, 列数: {len(self.flight_df.columns)}")
            self._clean_travel_data(self.flight_df, "出发日期")
            
            self.logger.debug("正在读取酒店数据")
            self.hotel_df = pd.read_excel(
                self.file_path, 
                sheet_name="酒店"
            )
            self.logger.info(f"酒店数据加载完成，行数: {len(self.hotel_df)}, 列数: {len(self.hotel_df.columns)}")
            self._clean_travel_data(self.hotel_df, "入住日期")
            
            self.logger.debug("正在读取火车票数据")
            self.train_df = pd.read_excel(
                self.file_path, 
                sheet_name="火车票"
            )
            self.logger.info(f"火车票数据加载完成，行数: {len(self.train_df)}, 列数: {len(self.train_df.columns)}")
            self._clean_travel_data(self.train_df, "出发日期")
            
            self.logger.info("所有工作表加载并清洗完成")
            
            return {
                "attendance": self.attendance_df,
                "flight": self.flight_df,
                "hotel": self.hotel_df,
                "train": self.train_df
            }
        
        except Exception as e:
            self.logger.error(f"数据加载失败: {str(e)}", exc_info=True)
            raise ValueError(f"数据加载失败: {str(e)}")
    
    def _clean_attendance_data(self):
        """清洗考勤数据"""
        if self.attendance_df is None:
            self.logger.warning("考勤数据为空，跳过清洗")
            return
        
        self.logger.debug("开始清洗考勤数据")
        
        # 转换日期格式
        self.attendance_df['日期'] = pd.to_datetime(
            self.attendance_df['日期'], 
            errors='coerce'
        )
        invalid_dates = self.attendance_df['日期'].isna().sum()
        if invalid_dates > 0:
            self.logger.warning(f"发现 {invalid_dates} 条无效日期记录")
        
        # 确保工时为数值类型
        if '工时' in self.attendance_df.columns:
            self.attendance_df['工时'] = pd.to_numeric(
                self.attendance_df['工时'], 
                errors='coerce'
            ).fillna(0)
            invalid_hours = (self.attendance_df['工时'] == 0).sum()
            if invalid_hours > 0:
                self.logger.warning(f"发现 {invalid_hours} 条无效或空工时记录")
        
        # 填充空值
        self.attendance_df['姓名'] = self.attendance_df['姓名'].fillna('未知')
        self.attendance_df['一级部门'] = self.attendance_df['一级部门'].fillna('未知')
        self.attendance_df['当日状态判断'] = self.attendance_df['当日状态判断'].fillna('未知')
        
        self.logger.info("考勤数据清洗完成")
    
    def _clean_travel_data(self, df: pd.DataFrame, date_column: str):
        """
        清洗差旅数据
        
        Args:
            df: 差旅数据 DataFrame
            date_column: 日期列名称
        """
        if df is None:
            self.logger.warning(f"差旅数据为空，跳过清洗（日期列: {date_column}）")
            return
        
        self.logger.info(f"=" * 60)
        self.logger.info(f"开始清洗差旅数据（日期列: {date_column}）- 详细模式")
        self.logger.info(f"=" * 60)
        self.logger.info(f"原始数据行数: {len(df)}")
        
        # 清洗授信金额
        if '授信金额' in df.columns:
            self.logger.info(f"🔧 开始清洗'授信金额'字段...")
            
            # 记录清洗前的统计
            original_values = df['授信金额'].copy()
            null_count = original_values.isna().sum()
            self.logger.info(f"   - 空值数量: {null_count}")
            
            # 显示前5个原始值示例
            self.logger.debug(f"   - 原始值示例（前5条）:")
            for i, val in enumerate(original_values.head(5), 1):
                self.logger.debug(f"      {i}. {repr(val)} (类型: {type(val).__name__})")
            
            # 执行清洗
            df['授信金额'] = df['授信金额'].apply(self._clean_amount)
            
            # 统计清洗结果
            zero_count = (df['授信金额'] == 0).sum()
            total_amount = df['授信金额'].sum()
            valid_count = len(df) - zero_count
            
            self.logger.info(f"   ✅ 授信金额清洗完成:")
            self.logger.info(f"      - 总记录数: {len(df)}")
            self.logger.info(f"      - 有效金额记录: {valid_count}")
            self.logger.info(f"      - 零值/无效记录: {zero_count}")
            self.logger.info(f"      - 金额总和: ¥{total_amount:,.2f}")
            
            if zero_count > 0:
                self.logger.warning(f"   ⚠️  发现 {zero_count} 条金额为0的记录（可能是空值或转换失败）")
            
            # 显示清洗后的示例
            self.logger.debug(f"   - 清洗后值示例（前5条）:")
            for i, val in enumerate(df['授信金额'].head(5), 1):
                self.logger.debug(f"      {i}. ¥{val:,.2f}")
        else:
            self.logger.warning(f"   ⚠️  未找到'授信金额'列")
        
        # 转换日期
        if date_column in df.columns:
            self.logger.info(f"📅 处理日期字段: {date_column}")
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            invalid_dates = df[date_column].isna().sum()
            if invalid_dates > 0:
                self.logger.warning(f"   发现 {invalid_dates} 条无效日期记录")
            else:
                self.logger.info(f"   日期字段处理完成，全部有效")
        
        # 提取项目代码
        if '项目' in df.columns:
            self.logger.info(f"🏷️  开始提取项目代码...")
            
            # 显示原始项目字段示例
            self.logger.debug(f"   - 原始'项目'字段示例（前5条）:")
            for i, val in enumerate(df['项目'].head(5), 1):
                self.logger.debug(f"      {i}. {repr(val)}")
            
            # 执行提取
            df['项目代码'] = df['项目'].apply(self._extract_project_code)
            
            # 统计提取结果
            unique_projects = df['项目代码'].nunique()
            unknown_count = (df['项目代码'] == '未知').sum()
            valid_count = len(df) - unknown_count
            
            self.logger.info(f"   ✅ 项目代码提取完成:")
            self.logger.info(f"      - 总记录数: {len(df)}")
            self.logger.info(f"      - 唯一项目数: {unique_projects}")
            self.logger.info(f"      - 有效项目记录: {valid_count}")
            self.logger.info(f"      - '未知'项目记录: {unknown_count}")
            
            if unknown_count > 0:
                unknown_amount = df[df['项目代码'] == '未知']['授信金额'].sum() if '授信金额' in df.columns else 0
                self.logger.warning(f"   ⚠️  {unknown_count}条记录的项目代码为'未知'，金额: ¥{unknown_amount:,.2f}")
                
                # 显示部分未知项目的原始值
                unknown_samples = df[df['项目代码'] == '未知']['项目'].head(5)
                if not unknown_samples.empty:
                    self.logger.warning(f"   未能提取的'项目'字段示例:")
                    for i, val in enumerate(unknown_samples, 1):
                        self.logger.warning(f"      {i}. {repr(val)}")
            
            # 显示提取的项目代码示例
            project_code_counts = df['项目代码'].value_counts()
            self.logger.debug(f"   - 项目代码分布（Top 5）:")
            for project_code, count in project_code_counts.head(5).items():
                project_amount = df[df['项目代码'] == project_code]['授信金额'].sum() if '授信金额' in df.columns else 0
                self.logger.debug(f"      {project_code}: {count}单, ¥{project_amount:,.2f}")
        else:
            self.logger.warning(f"   ⚠️  未找到'项目'列")
        
        # 填充基础字段
        self.logger.debug(f"🔄 填充空值字段...")
        if '预订人姓名' in df.columns:
            df['预订人姓名'] = df['预订人姓名'].fillna('未知')
        if '差旅人员姓名' in df.columns:
            df['差旅人员姓名'] = df['差旅人员姓名'].fillna('未知')
        if '一级部门' in df.columns:
            df['一级部门'] = df['一级部门'].fillna('未知')
        
        # 确保提前预定天数为数值
        if '提前预定天数' in df.columns:
            df['提前预定天数'] = pd.to_numeric(
                df['提前预定天数'], 
                errors='coerce'
            ).fillna(0)
            avg_advance_days = df['提前预定天数'].mean()
            self.logger.debug(f"   平均提前预订天数: {avg_advance_days:.2f} 天")
        
        self.logger.info(f"✅ 差旅数据清洗完成（日期列: {date_column}）")
        self.logger.info(f"=" * 60 + "\n")
    
    @staticmethod
    def _clean_amount(amount_str) -> float:
        """
        清洗金额字段，去除货币符号和逗号
        
        Args:
            amount_str: 原始金额字符串
            
        Returns:
            清洗后的浮点数
        """
        logger = get_logger("data_loader")
        
        if pd.isna(amount_str):
            logger.debug(f"金额清洗: NaN 或 None -> 0.0")
            return 0.0
        
        # 记录原始值
        original = amount_str
        
        # 转为字符串
        amount_str = str(amount_str)
        
        # 去除 ¥ 符号、逗号、空格
        cleaned = re.sub(r'[¥,\s]', '', amount_str)
        
        try:
            result = float(cleaned)
            if result == 0.0:
                logger.debug(f"金额清洗: {repr(original)} -> {result}")
            return result
        except ValueError:
            logger.warning(f"⚠️  金额转换失败: {repr(original)} -> 清洗后: {repr(cleaned)} -> 返回 0.0")
            return 0.0
    
    @staticmethod
    def _extract_project_code(project_str) -> str:
        """
        从项目字段提取项目代码
        格式: "05010013 市场-整星..." -> "05010013"
        
        Args:
            project_str: 原始项目字符串
            
        Returns:
            项目代码
        """
        logger = get_logger("data_loader")
        
        if pd.isna(project_str):
            logger.debug(f"项目代码提取: NaN 或 None -> '未知'")
            return "未知"
        
        original = project_str
        project_str = str(project_str).strip()
        
        # 提取空格前的数字
        match = re.match(r'^(\d+)', project_str)
        if match:
            code = match.group(1)
            logger.debug(f"项目代码提取成功: {repr(original)} -> {code}")
            return code
        
        logger.warning(f"⚠️  项目代码提取失败: {repr(original)} -> '未知' (不符合格式: 以数字开头)")
        return "未知"
    
    def get_merged_travel_data(self) -> pd.DataFrame:
        """
        合并所有差旅数据（机票、酒店、火车票）
        
        Returns:
            合并后的差旅数据 DataFrame
        """
        travel_dfs = []
        
        # 机票数据
        if self.flight_df is not None and not self.flight_df.empty:
            flight_copy = self.flight_df.copy()
            flight_copy['差旅类型'] = '机票'
            if '出发日期' in flight_copy.columns:
                flight_copy['消费日期'] = flight_copy['出发日期']
            travel_dfs.append(flight_copy)
        
        # 酒店数据
        if self.hotel_df is not None and not self.hotel_df.empty:
            hotel_copy = self.hotel_df.copy()
            hotel_copy['差旅类型'] = '酒店'
            if '入住日期' in hotel_copy.columns:
                hotel_copy['消费日期'] = hotel_copy['入住日期']
            travel_dfs.append(hotel_copy)
        
        # 火车票数据
        if self.train_df is not None and not self.train_df.empty:
            train_copy = self.train_df.copy()
            train_copy['差旅类型'] = '火车票'
            if '出发日期' in train_copy.columns:
                train_copy['消费日期'] = train_copy['出发日期']
            travel_dfs.append(train_copy)
        
        if not travel_dfs:
            return pd.DataFrame()
        
        # 合并所有差旅数据
        merged_df = pd.concat(travel_dfs, ignore_index=True, sort=False)
        
        return merged_df


