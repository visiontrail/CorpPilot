"""
核心分析逻辑模块
实现项目成本归集、交叉验证、预订行为分析等业务逻辑
"""

import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import json
from logger_config import get_logger


class TravelAnalyzer:
    """差旅数据分析器"""
    
    def __init__(
        self, 
        attendance_df: pd.DataFrame,
        flight_df: pd.DataFrame,
        hotel_df: pd.DataFrame,
        train_df: pd.DataFrame
    ):
        """
        初始化分析器
        
        Args:
            attendance_df: 考勤数据
            flight_df: 机票数据
            hotel_df: 酒店数据
            train_df: 火车票数据
        """
        self.attendance_df = attendance_df
        self.flight_df = flight_df
        self.hotel_df = hotel_df
        self.train_df = train_df
        self.logger = get_logger("analysis_service")
        
        self.logger.info("初始化差旅数据分析器")
        self.logger.debug(f"考勤数据行数: {len(attendance_df)}")
        self.logger.debug(f"机票数据行数: {len(flight_df)}")
        self.logger.debug(f"酒店数据行数: {len(hotel_df)}")
        self.logger.debug(f"火车票数据行数: {len(train_df)}")
        
        # 合并所有差旅数据
        self.travel_df = self._merge_travel_data()
        self.logger.info(f"差旅数据合并完成，总行数: {len(self.travel_df)}")
    
    def _merge_travel_data(self) -> pd.DataFrame:
        """合并所有差旅数据"""
        self.logger.info("=" * 80)
        self.logger.info("开始合并差旅数据（机票、酒店、火车票）")
        self.logger.info("=" * 80)
        
        travel_dfs = []
        total_amount = 0
        
        # 机票
        if self.flight_df is not None and not self.flight_df.empty:
            flight_copy = self.flight_df.copy()
            flight_copy['差旅类型'] = '机票'
            if '出发日期' in flight_copy.columns:
                flight_copy['消费日期'] = flight_copy['出发日期']
            flight_amount = flight_copy['授信金额'].sum() if '授信金额' in flight_copy.columns else 0
            self.logger.info(f"✈️  机票数据: {len(flight_copy)}条, 总金额: ¥{flight_amount:,.2f}")
            travel_dfs.append(flight_copy)
            total_amount += flight_amount
        else:
            self.logger.warning("⚠️  机票数据为空")
        
        # 酒店
        if self.hotel_df is not None and not self.hotel_df.empty:
            hotel_copy = self.hotel_df.copy()
            hotel_copy['差旅类型'] = '酒店'
            if '入住日期' in hotel_copy.columns:
                hotel_copy['消费日期'] = hotel_copy['入住日期']
            hotel_amount = hotel_copy['授信金额'].sum() if '授信金额' in hotel_copy.columns else 0
            self.logger.info(f"🏨 酒店数据: {len(hotel_copy)}条, 总金额: ¥{hotel_amount:,.2f}")
            travel_dfs.append(hotel_copy)
            total_amount += hotel_amount
        else:
            self.logger.warning("⚠️  酒店数据为空")
        
        # 火车票
        if self.train_df is not None and not self.train_df.empty:
            train_copy = self.train_df.copy()
            train_copy['差旅类型'] = '火车票'
            if '出发日期' in train_copy.columns:
                train_copy['消费日期'] = train_copy['出发日期']
            train_amount = train_copy['授信金额'].sum() if '授信金额' in train_copy.columns else 0
            self.logger.info(f"🚄 火车票数据: {len(train_copy)}条, 总金额: ¥{train_amount:,.2f}")
            travel_dfs.append(train_copy)
            total_amount += train_amount
        else:
            self.logger.warning("⚠️  火车票数据为空")
        
        if not travel_dfs:
            self.logger.error("❌ 所有差旅数据均为空，无法合并")
            return pd.DataFrame()
        
        merged_df = pd.concat(travel_dfs, ignore_index=True, sort=False)
        
        self.logger.info(f"\n✅ 差旅数据合并完成:")
        self.logger.info(f"   - 总记录数: {len(merged_df)}")
        self.logger.info(f"   - 总金额: ¥{total_amount:,.2f}")
        
        # 验证合并后的数据
        if '授信金额' in merged_df.columns:
            merged_total = merged_df['授信金额'].sum()
            if abs(merged_total - total_amount) > 0.01:
                self.logger.error(f"⚠️  金额验证失败！")
                self.logger.error(f"   分类汇总: ¥{total_amount:,.2f}")
                self.logger.error(f"   合并后总计: ¥{merged_total:,.2f}")
        
        self.logger.info("=" * 80 + "\n")
        
        return merged_df
    
    def aggregate_project_cost(self) -> pd.DataFrame:
        """
        项目成本归集
        提取项目代码，聚合所有差旅的授信金额
        
        Returns:
            项目成本汇总 DataFrame
        """
        self.logger.info("=" * 80)
        self.logger.info("开始执行项目成本归集 - 详细模式")
        self.logger.info("=" * 80)
        
        if self.travel_df.empty:
            self.logger.warning("差旅数据为空，无法进行项目成本归集")
            return pd.DataFrame(columns=['项目代码', '项目名称', '总成本', '机票成本', '酒店成本', '火车票成本', '订单数量'])
        
        # 输出数据总览
        total_records = len(self.travel_df)
        total_amount_all = self.travel_df['授信金额'].sum() if '授信金额' in self.travel_df.columns else 0
        self.logger.info(f"📊 差旅数据总览:")
        self.logger.info(f"   - 总记录数: {total_records}")
        self.logger.info(f"   - 授信金额总和: ¥{total_amount_all:,.2f}")
        
        # 确保必要的列存在
        required_cols = ['项目代码', '授信金额', '差旅类型']
        for col in required_cols:
            if col not in self.travel_df.columns:
                self.logger.error(f"缺少必要列: {col}")
                return pd.DataFrame(columns=['项目代码', '项目名称', '总成本', '机票成本', '酒店成本', '火车票成本', '订单数量'])
        
        # 统计各差旅类型数量
        travel_type_counts = self.travel_df['差旅类型'].value_counts().to_dict()
        self.logger.info(f"📋 差旅类型分布:")
        for travel_type, count in travel_type_counts.items():
            type_amount = self.travel_df[self.travel_df['差旅类型'] == travel_type]['授信金额'].sum()
            self.logger.info(f"   - {travel_type}: {count}条, 总金额 ¥{type_amount:,.2f}")
        
        # 统计项目代码分布
        project_counts = self.travel_df['项目代码'].value_counts()
        unknown_count = project_counts.get('未知', 0)
        unknown_amount = self.travel_df[self.travel_df['项目代码'] == '未知']['授信金额'].sum() if unknown_count > 0 else 0
        
        self.logger.info(f"🏷️  项目代码统计:")
        self.logger.info(f"   - 唯一项目数: {len(project_counts)}")
        self.logger.info(f"   - '未知'项目记录数: {unknown_count}, 金额: ¥{unknown_amount:,.2f}")
        if unknown_count > 0:
            self.logger.warning(f"⚠️  发现 {unknown_count} 条'未知'项目记录，将被排除在项目成本统计外！")
        
        # 按项目代码和差旅类型分组
        project_stats = []
        valid_project_codes = [code for code in self.travel_df['项目代码'].unique() if code != "未知"]
        
        self.logger.info(f"\n🔍 开始逐项目分析（共 {len(valid_project_codes)} 个有效项目）:")
        self.logger.info("=" * 80)
        
        for idx, project_code in enumerate(valid_project_codes, 1):
            project_data = self.travel_df[self.travel_df['项目代码'] == project_code]
            
            # 获取项目名称（从"项目"字段提取）
            project_name = "未命名"
            if '项目' in project_data.columns:
                first_project = project_data['项目'].iloc[0] if not project_data.empty else ""
                if pd.notna(first_project) and str(first_project) != "未知":
                    # 提取项目代码后面的名称部分
                    project_str = str(first_project).strip()
                    # 格式: "05010013 市场-整星..." -> "市场-整星..."
                    parts = project_str.split(maxsplit=1)
                    if len(parts) > 1:
                        project_name = parts[1][:50]  # 限制长度
            
            # 计算各类成本
            total_cost = project_data['授信金额'].sum()
            flight_cost = project_data[project_data['差旅类型'] == '机票']['授信金额'].sum()
            hotel_cost = project_data[project_data['差旅类型'] == '酒店']['授信金额'].sum()
            train_cost = project_data[project_data['差旅类型'] == '火车票']['授信金额'].sum()
            order_count = len(project_data)
            
            # 输出项目汇总信息
            self.logger.info(f"\n📁 项目 #{idx}: {project_code} - {project_name}")
            self.logger.info(f"   订单总数: {order_count}")
            self.logger.info(f"   总成本: ¥{total_cost:,.2f}")
            self.logger.info(f"   ├─ 机票: ¥{flight_cost:,.2f} ({len(project_data[project_data['差旅类型'] == '机票'])}单)")
            self.logger.info(f"   ├─ 酒店: ¥{hotel_cost:,.2f} ({len(project_data[project_data['差旅类型'] == '酒店'])}单)")
            self.logger.info(f"   └─ 火车票: ¥{train_cost:,.2f} ({len(project_data[project_data['差旅类型'] == '火车票'])}单)")
            
            # 输出每条记录的明细（前10条，避免日志过大）
            self.logger.debug(f"   📝 明细记录（前10条）:")
            for i, (_, row) in enumerate(project_data.head(10).iterrows(), 1):
                name = row.get('差旅人员姓名', '未知')
                travel_type = row.get('差旅类型', '未知')
                amount = row.get('授信金额', 0)
                date = row.get('消费日期', '未知')
                date_str = date.strftime('%Y-%m-%d') if pd.notna(date) else '未知'
                self.logger.debug(f"      {i}. {travel_type} | {name} | ¥{amount:,.2f} | {date_str}")
            
            if order_count > 10:
                self.logger.debug(f"      ... 还有 {order_count - 10} 条记录未显示")
            
            # 验证成本计算
            calculated_sum = flight_cost + hotel_cost + train_cost
            if abs(calculated_sum - total_cost) > 0.01:  # 允许0.01的浮点误差
                self.logger.error(f"   ⚠️  成本计算不一致！")
                self.logger.error(f"      直接求和: ¥{total_cost:,.2f}")
                self.logger.error(f"      分类求和: ¥{calculated_sum:,.2f}")
                self.logger.error(f"      差异: ¥{abs(calculated_sum - total_cost):,.2f}")
            
            project_stats.append({
                '项目代码': project_code,
                '项目名称': project_name,
                '总成本': round(total_cost, 2),
                '机票成本': round(flight_cost, 2),
                '酒店成本': round(hotel_cost, 2),
                '火车票成本': round(train_cost, 2),
                '订单数量': order_count
            })
        
        result_df = pd.DataFrame(project_stats)
        
        # 按总成本降序排序
        if not result_df.empty:
            result_df = result_df.sort_values('总成本', ascending=False).reset_index(drop=True)
            
            # 输出最终统计
            self.logger.info("\n" + "=" * 80)
            self.logger.info("✅ 项目成本归集完成")
            self.logger.info("=" * 80)
            self.logger.info(f"📊 统计结果:")
            self.logger.info(f"   - 有效项目数: {len(result_df)}")
            self.logger.info(f"   - 总订单数: {result_df['订单数量'].sum()}")
            self.logger.info(f"   - 总成本: ¥{result_df['总成本'].sum():,.2f}")
            self.logger.info(f"   - 机票成本: ¥{result_df['机票成本'].sum():,.2f}")
            self.logger.info(f"   - 酒店成本: ¥{result_df['酒店成本'].sum():,.2f}")
            self.logger.info(f"   - 火车票成本: ¥{result_df['火车票成本'].sum():,.2f}")
            
            # 验证总成本
            result_total = result_df['总成本'].sum()
            original_valid_total = self.travel_df[self.travel_df['项目代码'] != '未知']['授信金额'].sum()
            if abs(result_total - original_valid_total) > 0.01:
                self.logger.error(f"⚠️  总成本验证失败！")
                self.logger.error(f"   汇总结果: ¥{result_total:,.2f}")
                self.logger.error(f"   原始数据: ¥{original_valid_total:,.2f}")
            
            # 输出Top 5项目
            self.logger.info(f"\n🏆 成本Top 5项目:")
            for i, row in result_df.head(5).iterrows():
                self.logger.info(f"   {i+1}. {row['项目代码']} - {row['项目名称']}")
                self.logger.info(f"      成本: ¥{row['总成本']:,.2f} | 订单: {row['订单数量']}单")
            
            # 如果有未知项目，再次提醒
            if unknown_count > 0:
                self.logger.warning(f"\n⚠️  提醒: {unknown_count}条'未知'项目记录（¥{unknown_amount:,.2f}）未计入以上统计")
                self.logger.warning(f"   实际差旅总金额: ¥{total_amount_all:,.2f}")
                self.logger.warning(f"   已统计金额: ¥{result_total:,.2f}")
                self.logger.warning(f"   未统计金额: ¥{unknown_amount:,.2f}")
        else:
            self.logger.warning("项目成本归集结果为空")
        
        self.logger.info("=" * 80 + "\n")
        
        return result_df
    
    def cross_check_anomalies(self) -> List[Dict]:
        """
        交叉验证异常记录
        
        Returns:
            异常记录列表
        """
        self.logger.debug("开始执行交叉验证异常检测")
        anomalies = []
        
        if self.attendance_df.empty or self.travel_df.empty:
            self.logger.warning("考勤数据或差旅数据为空，无法进行异常检测")
            return anomalies
        
        # 确保必要列存在
        if '日期' not in self.attendance_df.columns or '姓名' not in self.attendance_df.columns:
            self.logger.warning("考勤数据缺少必要列（日期、姓名），无法进行异常检测")
            return anomalies
        
        if '消费日期' not in self.travel_df.columns or '差旅人员姓名' not in self.travel_df.columns:
            self.logger.warning("差旅数据缺少必要列（消费日期、差旅人员姓名），无法进行异常检测")
            return anomalies
        
        # 类型1: 考勤显示上班，但有异地差旅消费
        self.logger.debug("检测类型1异常：考勤显示上班但有异地差旅消费")
        work_records = self.attendance_df[
            self.attendance_df['当日状态判断'].str.contains('上班', na=False)
        ].copy()
        self.logger.debug(f"上班考勤记录数: {len(work_records)}")
        
        for _, record in work_records.iterrows():
            date = record['日期']
            name = record['姓名']
            
            # 查找同日差旅消费
            same_day_travel = self.travel_df[
                (self.travel_df['消费日期'] == date) & 
                (self.travel_df['差旅人员姓名'] == name)
            ]
            
            if not same_day_travel.empty:
                for _, travel in same_day_travel.iterrows():
                    anomalies.append({
                        'Type': 'Conflict',
                        '姓名': name,
                        '日期': date.strftime('%Y-%m-%d') if pd.notna(date) else '',
                        '考勤状态': record.get('当日状态判断', ''),
                        '差旅类型': travel.get('差旅类型', ''),
                        '差旅金额': float(travel.get('授信金额', 0)),
                        '一级部门': record.get('一级部门', ''),
                        '描述': '考勤显示上班但同日有异地差旅消费'
                    })
        
        # 类型2: 考勤显示出差，但无任何差旅消费
        # 注意：根据业务需求，此类异常已被标记为"可忽略"，不纳入异常统计
        # 原因：出差不一定产生差旅消费（例如：客户提供交通/住宿、本地出差等）
        # 如需启用此检测，请取消以下注释
        """
        self.logger.debug("检测类型2异常：考勤显示出差但无任何差旅消费")
        business_trip_records = self.attendance_df[
            self.attendance_df['当日状态判断'].str.contains('出差', na=False)
        ].copy()
        self.logger.debug(f"出差考勤记录数: {len(business_trip_records)}")
        
        for _, record in business_trip_records.iterrows():
            date = record['日期']
            name = record['姓名']
            
            # 查找差旅消费
            travel_expenses = self.travel_df[
                (self.travel_df['差旅人员姓名'] == name)
            ]
            
            # 检查该日期前后3天内是否有差旅记录
            if pd.notna(date) and not travel_expenses.empty:
                date_range = pd.date_range(
                    start=date - pd.Timedelta(days=3),
                    end=date + pd.Timedelta(days=3)
                )
                
                travel_in_range = travel_expenses[
                    travel_expenses['消费日期'].isin(date_range)
                ]
                
                if travel_in_range.empty:
                    anomalies.append({
                        'Type': 'NoExpense',
                        '姓名': name,
                        '日期': date.strftime('%Y-%m-%d') if pd.notna(date) else '',
                        '考勤状态': record.get('当日状态判断', ''),
                        '差旅类型': '',
                        '差旅金额': 0.0,
                        '一级部门': record.get('一级部门', ''),
                        '描述': '考勤显示出差但无任何差旅消费记录'
                    })
        """
        
        self.logger.info(f"异常检测完成，发现 {len(anomalies)} 条异常记录")
        conflict_count = len([a for a in anomalies if a['Type'] == 'Conflict'])
        no_expense_count = len([a for a in anomalies if a['Type'] == 'NoExpense'])
        self.logger.debug(f"其中冲突类型: {conflict_count}, 无消费类型: {no_expense_count}")
        
        return anomalies
    
    def analyze_booking_behavior(self) -> Dict:
        """
        预订行为分析
        统计提前预定天数 <= 2 的订单比例
        
        Returns:
            预订行为统计字典
        """
        self.logger.debug("开始执行预订行为分析")
        
        if self.travel_df.empty or '提前预定天数' not in self.travel_df.columns:
            self.logger.warning("差旅数据为空或缺少'提前预定天数'列，无法进行预订行为分析")
            return {
                'total_orders': 0,
                'urgent_orders': 0,
                'urgent_ratio': 0.0,
                'avg_advance_days': 0.0
            }
        
        total_orders = len(self.travel_df)
        urgent_orders = len(self.travel_df[self.travel_df['提前预定天数'] <= 2])
        urgent_ratio = (urgent_orders / total_orders * 100) if total_orders > 0 else 0
        avg_advance_days = self.travel_df['提前预定天数'].mean()
        
        self.logger.info(f"预订行为分析完成: 总订单={total_orders}, 紧急订单={urgent_orders}, "
                        f"紧急比例={urgent_ratio:.2f}%, 平均提前天数={avg_advance_days:.2f}")
        
        return {
            'total_orders': int(total_orders),
            'urgent_orders': int(urgent_orders),
            'urgent_ratio': round(urgent_ratio, 2),
            'avg_advance_days': round(avg_advance_days, 2)
        }

    def _calculate_over_standard_stats(self) -> Dict[str, int]:
        """
        统计各差旅类型的超标订单数量

        规则：
        - 机票：超标类型包含“超折扣”或“超时间”
        - 酒店：是否超标为“是”
        - 火车票：是否超标为“是”
        """
        def _count_yes(df: pd.DataFrame, column: str) -> int:
            if df is None or df.empty or column not in df.columns:
                return 0
            return int(df[df[column].astype(str).str.contains('是', na=False)].shape[0])

        flight_over = 0
        if self.flight_df is not None and not self.flight_df.empty:
            if '超标类型' in self.flight_df.columns:
                flight_over = int(
                    self.flight_df[
                        self.flight_df['超标类型']
                        .astype(str)
                        .str.contains('超折扣|超时间', na=False)
                    ].shape[0]
                )
            elif '是否超标' in self.flight_df.columns:
                flight_over = _count_yes(self.flight_df, '是否超标')

        hotel_over = _count_yes(self.hotel_df, '是否超标')
        train_over = _count_yes(self.train_df, '是否超标')

        total = flight_over + hotel_over + train_over

        return {
            'total': int(total),
            'flight': int(flight_over),
            'hotel': int(hotel_over),
            'train': int(train_over)
        }
    
    def calculate_department_metrics(self) -> pd.DataFrame:
        """
        计算部门级指标（用于散点图）
        包括：部门总成本、总工时、饱和度
        
        Returns:
            部门指标 DataFrame
        """
        dept_metrics = []
        
        # 计算部门差旅成本
        if not self.travel_df.empty and '一级部门' in self.travel_df.columns:
            dept_cost = self.travel_df.groupby('一级部门')['授信金额'].sum().to_dict()
        else:
            dept_cost = {}
        
        # 计算部门工时
        if not self.attendance_df.empty and '一级部门' in self.attendance_df.columns:
            dept_hours = self.attendance_df.groupby('一级部门')['工时'].sum().to_dict()
        else:
            dept_hours = {}
        
        # 合并所有部门
        all_depts = set(list(dept_cost.keys()) + list(dept_hours.keys()))
        
        for dept in all_depts:
            if dept == "未知" or dept == "":
                continue
            
            total_cost = dept_cost.get(dept, 0)
            total_hours = dept_hours.get(dept, 0)
            
            # 饱和度 = 工时 / (人数 * 标准工时)
            # 简化计算：假设标准工时为 8小时/天 * 22天/月
            standard_hours = 176
            employee_count = self.attendance_df[
                self.attendance_df['一级部门'] == dept
            ]['姓名'].nunique() if not self.attendance_df.empty else 1
            
            saturation = (total_hours / (employee_count * standard_hours) * 100) if employee_count > 0 else 0
            
            dept_metrics.append({
                '一级部门': dept,
                '总成本': round(total_cost, 2),
                '总工时': round(total_hours, 2),
                '人员数量': int(employee_count),
                '饱和度': round(saturation, 2)
            })
        
        result_df = pd.DataFrame(dept_metrics)
        
        if not result_df.empty:
            result_df = result_df.sort_values('总成本', ascending=False).reset_index(drop=True)
        
        return result_df
    
    def generate_dashboard_data(self) -> Dict:
        """
        生成 Dashboard 所需的完整 JSON 数据
        
        Returns:
            包含所有分析结果的字典
        """
        self.logger.info("开始生成Dashboard数据")
        
        # 项目成本 Top 20（如果超过20条，其余汇总到"其他"）
        project_cost = self.aggregate_project_cost()
        top_projects = self._prepare_top_items_with_others(
            project_cost, 
            top_n=20, 
            name_column='项目代码',
            sum_columns=['总成本', '机票成本', '酒店成本', '火车票成本', '订单数量']
        ) if not project_cost.empty else []
        
        # 部门指标 Top 15（如果超过15条，其余汇总到"其他"）
        dept_metrics = self.calculate_department_metrics()
        dept_data = self._prepare_top_items_with_others(
            dept_metrics,
            top_n=15,
            name_column='一级部门',
            sum_columns=['总成本', '总工时', '人员数量'],
            avg_columns=['饱和度']
        ) if not dept_metrics.empty else []
        
        # 异常记录
        anomalies = self.cross_check_anomalies()
        
        # 预订行为
        booking_behavior = self.analyze_booking_behavior()
        
        # KPI 统计
        total_cost = self.travel_df['授信金额'].sum() if not self.travel_df.empty else 0
        total_orders = len(self.travel_df) if not self.travel_df.empty else 0
        anomaly_count = len(anomalies)
        
        # 超标统计（按业务规则拆分）
        over_standard_stats = self._calculate_over_standard_stats()
        over_standard_count = over_standard_stats.get('total', 0)
        
        self.logger.info(f"Dashboard数据生成完成: 总成本=¥{total_cost:,.2f}, 订单数={total_orders}, "
                        f"异常数={anomaly_count}, 超标数={over_standard_count}")
        
        return {
            'kpi': {
                'total_cost': round(float(total_cost), 2),
                'total_orders': int(total_orders),
                'anomaly_count': int(anomaly_count),
                'over_standard_count': int(over_standard_count),
                'urgent_booking_ratio': booking_behavior['urgent_ratio']
            },
            'department_metrics': dept_data,
            'top_projects': top_projects,
            'anomalies': anomalies[:100],  # 限制返回前100条异常
            'booking_behavior': booking_behavior,
            'over_standard_breakdown': over_standard_stats,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _prepare_top_items_with_others(
        self, 
        df: pd.DataFrame, 
        top_n: int, 
        name_column: str,
        sum_columns: List[str],
        avg_columns: List[str] = None
    ) -> List[Dict]:
        """
        准备 Top N 数据，如果超过 N 条，将其余数据汇总到"其他"
        
        Args:
            df: 数据 DataFrame
            top_n: 保留的前 N 条记录数
            name_column: 名称列（如"项目代码"、"一级部门"）
            sum_columns: 需要求和的列
            avg_columns: 需要求平均的列（可选）
        
        Returns:
            处理后的记录列表
        """
        if df.empty:
            return []
        
        total_count = len(df)
        
        # 如果记录数不超过 top_n，直接返回全部
        if total_count <= top_n:
            self.logger.debug(f"{name_column}记录数({total_count}) <= {top_n}，返回全部数据")
            return df.to_dict('records')
        
        # 取前 top_n 条
        top_items = df.head(top_n).to_dict('records')
        
        # 计算"其他"条目
        others_df = df.iloc[top_n:]
        others_record = {name_column: '其他'}
        
        # 对需要求和的列进行求和
        for col in sum_columns:
            if col in others_df.columns:
                others_record[col] = round(others_df[col].sum(), 2)
        
        # 对需要求平均的列进行平均
        if avg_columns:
            for col in avg_columns:
                if col in others_df.columns:
                    others_record[col] = round(others_df[col].mean(), 2)
        
        # 将"其他"条目添加到列表末尾
        top_items.append(others_record)
        
        self.logger.info(f"{name_column}: 总计{total_count}条，展示前{top_n}条 + \"其他\"({total_count - top_n}条汇总)")
        
        return top_items
