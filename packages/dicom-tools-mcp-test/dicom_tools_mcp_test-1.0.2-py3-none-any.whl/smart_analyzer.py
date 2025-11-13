#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能分析和决策工具

实现思维链式的序列检测、决策和拆分流程
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path

from src.models import DICOMDirectory
from src.core import get_series_info

logger = logging.getLogger(__name__)

# 配置参数
DEFAULT_SERIES_THRESHOLD = 5  # 默认序列数阈值
DEFAULT_PATIENT_THRESHOLD = 2  # 默认患者数阈值


class ThinkingChain:
    """思维链决策记录"""
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, step: str, decision: str, reason: str):
        """添加决策步骤"""
        self.steps.append({
            "step": step,
            "decision": decision,
            "reason": reason
        })
    
    def to_dict(self):
        """转换为字典"""
        return {"thinking_chain": self.steps}


async def smart_analyze_directory_tool(
    directory_path: str,
    series_threshold: int = DEFAULT_SERIES_THRESHOLD,
    patient_threshold: int = DEFAULT_PATIENT_THRESHOLD
) -> Dict[str, Any]:
    """
    智能分析目录：检测序列数量，决策是否需要拆分
    
    Args:
        directory_path: 要分析的目录路径
        series_threshold: 序列数阈值（超过此值建议拆分）
        patient_threshold: 患者数阈值（超过此值建议按患者拆分）
    
    Returns:
        包含分析结果、决策建议和思维链的字典
    """
    try:
        # 初始化思维链
        thinking = ThinkingChain()
        
        # 步骤1: 扫描目录
        thinking.add_step(
            step="1. 扫描DICOM目录",
            decision="执行目录扫描",
            reason=f"检查目录 {directory_path} 中的DICOM文件"
        )
        
        dicom_directory = DICOMDirectory(directory_path)
        all_series = list(dicom_directory.get_dicom_series())
        total_series = len(all_series)
        
        # 按患者分组
        patient_series_map = {}
        for series in all_series:
            info = get_series_info(series)
            pid = info["PatientID"]
            patient_series_map.setdefault(pid, []).append({
                "series_uid": info.get("SeriesInstanceUID", "unknown"),
                "series_description": info.get("SeriesDescription", ""),
                "slice_count": info.get("SliceNum", 0)
            })
        
        total_patients = len(patient_series_map)
        
        thinking.add_step(
            step="2. 统计扫描结果",
            decision=f"发现 {total_patients} 个患者，{total_series} 个序列",
            reason="完成目录扫描和统计"
        )
        
        # 步骤3: 分析并决策
        needs_split = False
        split_by_patient = False
        recommendation = ""
        risk_level = "low"
        
        if total_series <= series_threshold:
            thinking.add_step(
                step="3. 评估序列数量",
                decision="序列数量适中，可直接上传",
                reason=f"序列数({total_series}) ≤ 阈值({series_threshold})，上传风险较低"
            )
            recommendation = "direct_upload"
            risk_level = "low"
            
        elif total_patients > patient_threshold:
            needs_split = True
            split_by_patient = True
            thinking.add_step(
                step="3. 评估序列数量和患者分布",
                decision="建议按患者拆分",
                reason=f"序列数({total_series}) > 阈值({series_threshold})，且包含多个患者({total_patients})，按患者拆分可避免超时"
            )
            recommendation = "split_by_patient"
            risk_level = "high"
            
        else:
            needs_split = True
            thinking.add_step(
                step="3. 评估序列数量",
                decision="建议手动选择部分序列上传",
                reason=f"序列数({total_series}) > 阈值({series_threshold})，但只有{total_patients}个患者，建议手动筛选或分批上传"
            )
            recommendation = "manual_select"
            risk_level = "medium"
        
        # 步骤4: 生成执行建议
        if needs_split and split_by_patient:
            thinking.add_step(
                step="4. 生成执行方案",
                decision="可调用 fileforsep 工具进行自动拆分",
                reason="系统将自动按患者和序列创建子目录，拆分后可选择单个患者目录上传"
            )
        elif needs_split:
            thinking.add_step(
                step="4. 生成执行方案",
                decision="建议用户手动筛选",
                reason="可以查看详细的患者和序列列表，选择需要上传的部分"
            )
        else:
            thinking.add_step(
                step="4. 生成执行方案",
                decision="可直接调用 Analysis_dicom_directory 工具上传",
                reason="序列数量适中，可以安全地一次性上传所有数据"
            )
        
        # 构建返回结果
        result = {
            "status": "success",
            "analysis": {
                "directory_path": directory_path,
                "total_patients": total_patients,
                "total_series": total_series,
                "series_threshold": series_threshold,
                "patient_threshold": patient_threshold
            },
            "decision": {
                "needs_split": needs_split,
                "split_by_patient": split_by_patient,
                "recommendation": recommendation,
                "risk_level": risk_level,
                "description": _get_risk_description(risk_level, total_series, series_threshold)
            },
            "patients_detail": [
                {
                    "patient_id": pid,
                    "series_count": len(series_list),
                    "series_details": series_list
                }
                for pid, series_list in patient_series_map.items()
            ],
            "next_steps": _get_next_steps(recommendation, directory_path),
            **thinking.to_dict()
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"智能分析失败: {str(e)}", exc_info=True)
        import traceback
        error_info = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(error_info, ensure_ascii=False, indent=2)
                }
            ]
        }


def _get_risk_description(risk_level: str, total_series: int, threshold: int) -> str:
    """获取风险等级描述"""
    if risk_level == "low":
        return f" 安全：序列数量({total_series})在安全范围内，建议直接上传"
    elif risk_level == "medium":
        return f"中等风险：序列数量({total_series})超过阈值({threshold})，可能需要较长时间，建议分批上传"
    else:  # high
        return f"高风险：序列数量({total_series})远超阈值({threshold})，强烈建议先拆分后再上传"


def _get_next_steps(recommendation: str, directory_path: str) -> List[Dict[str, str]]:
    """获取下一步操作建议"""
    if recommendation == "direct_upload":
        return [
            {
                "action": "call_tool",
                "tool": "Analysis_dicom_directory",
                "description": "直接上传所有序列",
                "parameters": {
                    "directory_path": directory_path,
                    "series_type": "1 或 9（根据实际类型选择）"
                }
            }
        ]
    elif recommendation == "split_by_patient":
        return [
            {
                "action": "call_tool",
                "tool": "fileforsep",
                "description": "第一步：按患者拆分目录",
                "parameters": {
                    "fileforsep": directory_path
                }
            },
            {
                "action": "manual",
                "description": "第二步：从拆分结果中选择单个患者目录"
            },
            {
                "action": "call_tool",
                "tool": "Analysis_dicom_directory",
                "description": "第三步：上传选定的患者目录",
                "parameters": {
                    "directory_path": "拆分后的子目录路径",
                    "series_type": "1 或 9（根据实际类型选择）"
                }
            }
        ]
    else:  # manual_select
        return [
            {
                "action": "manual",
                "description": "查看上面的患者详情，选择需要上传的患者"
            },
            {
                "action": "call_tool",
                "tool": "Analysis_dicom_directory",
                "description": "分批上传选定的序列",
                "parameters": {
                    "directory_path": directory_path,
                    "series_type": "1 或 9（根据实际类型选择）"
                }
            }
        ]


async def check_and_split_if_needed_tool(
    directory_path: str,
    series_threshold: int = DEFAULT_SERIES_THRESHOLD,
    auto_split: bool = True
) -> Dict[str, Any]:
    """
    一键检测并自动拆分（如果需要）
    
    Args:
        directory_path: 要分析的目录路径
        series_threshold: 序列数阈值
        auto_split: 是否自动执行拆分（如果需要）
    
    Returns:
        包含检测结果和拆分结果的字典
    """
    from upload import separate_series_by_patient
    
    try:
        # 第一步：智能分析
        analysis_result = await smart_analyze_directory_tool(directory_path, series_threshold)
        analysis_data = json.loads(analysis_result["content"][0]["text"])
        
        if analysis_data.get("status") != "success":
            return analysis_result
        
        decision = analysis_data["decision"]
        
        # 如果不需要拆分，直接返回分析结果
        if not decision.get("needs_split"):
            return analysis_result
        
        # 如果需要拆分但不自动执行，返回建议
        if not auto_split:
            return analysis_result
        
        # 如果建议按患者拆分且自动执行开启，则执行拆分
        if decision.get("split_by_patient"):
            logger.info("自动执行按患者拆分...")
            split_result = separate_series_by_patient(directory_path)
            split_data = json.loads(split_result["content"][0]["text"])
            
            # 合并分析和拆分结果
            combined_result = {
                **analysis_data,
                "auto_split_executed": True,
                "split_result": split_data
            }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(combined_result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        
        # 其他情况返回分析结果
        return analysis_result
        
    except Exception as e:
        logger.error(f"一键检测拆分失败: {str(e)}", exc_info=True)
        import traceback
        error_info = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(error_info, ensure_ascii=False, indent=2)
                }
            ]
        }
