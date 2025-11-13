# DICOM MCP 工具 - 智能分析和闭环上传功能

## 新增功能概述

为了解决大型DICOM文件夹上传超时问题，新增了**智能分析和自动拆分闭环功能**，结合**思维链决策过程**，让AI助手能够智能地判断是否需要拆分目录。

---

## 🎯 核心功能

### 1. **smart_analyze_directory** - 智能分析工具
智能扫描并分析DICOM目录，提供风险评估和操作建议。

**功能特点：**
- ✅ 统计患者数量和序列数量
- ✅ 基于阈值评估上传风险（低/中/高）
- ✅ 展示完整的思维链决策过程
- ✅ 提供患者和序列的详细信息
- ✅ 给出下一步操作建议

**参数：**
```json
{
  "directory_path": "C:\\DICOM数据\\患者文件夹",
  "series_threshold": 5,      // 序列数阈值（可选，默认5）
  "patient_threshold": 2      // 患者数阈值（可选，默认2）
}
```

**返回结果示例：**
```json
{
  "status": "success",
  "analysis": {
    "directory_path": "C:\\DICOM数据\\患者文件夹",
    "total_patients": 3,
    "total_series": 12,
    "series_threshold": 5,
    "patient_threshold": 2
  },
  "decision": {
    "needs_split": true,
    "split_by_patient": true,
    "recommendation": "split_by_patient",
    "risk_level": "high",
    "description": "❌ 高风险：序列数量(12)远超阈值(5)，强烈建议先拆分后再上传"
  },
  "thinking_chain": [
    {
      "step": "1. 扫描DICOM目录",
      "decision": "执行目录扫描",
      "reason": "检查目录 C:\\DICOM数据\\患者文件夹 中的DICOM文件"
    },
    {
      "step": "2. 统计扫描结果",
      "decision": "发现 3 个患者，12 个序列",
      "reason": "完成目录扫描和统计"
    },
    {
      "step": "3. 评估序列数量和患者分布",
      "decision": "建议按患者拆分",
      "reason": "序列数(12) > 阈值(5)，且包含多个患者(3)，按患者拆分可避免超时"
    },
    {
      "step": "4. 生成执行方案",
      "decision": "可调用 fileforsep 工具进行自动拆分",
      "reason": "系统将自动按患者和序列创建子目录，拆分后可选择单个患者目录上传"
    }
  ],
  "patients_detail": [
    {
      "patient_id": "P001",
      "series_count": 4,
      "series_details": [...]
    }
  ],
  "next_steps": [
    {
      "action": "call_tool",
      "tool": "fileforsep",
      "description": "第一步：按患者拆分目录",
      "parameters": {
        "fileforsep": "C:\\DICOM数据\\患者文件夹"
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
}
```

---

### 2. **check_and_split_if_needed** - 一键智能处理工具
自动检测并在需要时执行拆分，实现完全自动化的闭环流程。

**功能特点：**
- ✅ 自动分析目录
- ✅ 智能判断是否需要拆分
- ✅ 自动执行拆分操作（可选）
- ✅ 返回分析+拆分的完整结果

**参数：**
```json
{
  "directory_path": "C:\\DICOM数据\\患者文件夹",
  "series_threshold": 5,    // 序列数阈值（可选，默认5）
  "auto_split": true        // 是否自动拆分（可选，默认true）
}
```

**返回结果示例（已自动拆分）：**
```json
{
  "status": "success",
  "analysis": {...},         // 与 smart_analyze_directory 相同
  "decision": {...},
  "thinking_chain": [...],
  "auto_split_executed": true,
  "split_result": {
    "status": "success",
    "summary": {
      "totalPatients": 3,
      "totalSeries": 12,
      "totalFilesCopied": 480,
      "outputDirectory": "C:\\DICOM数据\\患者文件夹"
    },
    "patient_directories": {
      "P001": {
        "directory": "C:\\DICOM数据\\患者文件夹\\P001",
        "series_count": 4,
        "series_details": [...]
      }
    }
  }
}
```

---

### 3. **fileforsep** - 按患者拆分工具（已优化）
按患者和序列拆分DICOM文件，现在返回更详细的结果。

**优化内容：**
- ✅ 返回每个患者的目录路径
- ✅ 显示每个序列的详细信息
- ✅ 提供文件复制统计
- ✅ 给出下一步操作指引

---

## 🔄 闭环工作流程

### 场景1：AI助手自动处理（推荐）

```
用户: "我想上传这个DICOM文件夹，里面有很多序列"
     └─ 文件夹路径: C:\DICOM数据\大型研究

AI助手:
  ┌─> 步骤1: 调用 check_and_split_if_needed
  │   参数: {"directory_path": "C:\\DICOM数据\\大型研究", "auto_split": true}
  │
  ├─> 系统自动:
  │   - 扫描目录 (发现15个序列，4个患者)
  │   - 思维链决策: 序列过多 → 需要拆分 → 自动执行拆分
  │   - 按患者拆分完成
  │
  └─> 返回结果:
      ├─ 拆分统计: 4个患者目录已创建
      ├─ 患者列表: P001, P002, P003, P004
      └─ 每个患者的目录路径和序列信息

AI助手: "已检测到15个序列，已自动按患者拆分为4个目录。
         您希望上传哪个患者的数据？例如：
         - P001 (4个序列) 位于 C:\DICOM数据\大型研究\P001"

用户: "上传P001的数据，类型是主动脉"

AI助手:
  └─> 调用 Analysis_dicom_directory
      参数: {
        "directory_path": "C:\\DICOM数据\\大型研究\\P001",
        "series_type": "1"
      }
      
  └─> 上传成功！
```

### 场景2：仅分析不自动拆分

```
用户: "先帮我看看这个文件夹的情况"

AI助手:
  └─> 调用 smart_analyze_directory
      参数: {"directory_path": "C:\\DICOM数据\\患者A"}

  └─> 返回分析结果:
      - ✅ 安全：3个序列，1个患者
      - 风险等级: 低
      - 建议: 可直接上传
      - 思维链: [扫描 → 统计 → 评估 → 建议直接上传]

AI助手: "这个文件夹包含3个序列，数量适中，可以安全地直接上传。
         是否现在上传？"
```

### 场景3：手动控制拆分

```
用户: "检查文件夹但先不要自动拆分"

AI助手:
  └─> 调用 check_and_split_if_needed
      参数: {
        "directory_path": "C:\\DICOM数据\\混合数据",
        "auto_split": false
      }

  └─> 返回分析结果（未执行拆分）:
      - ⚠️ 中等风险：8个序列
      - 建议: 手动筛选或分批上传
      - 患者详情: [P001: 5序列, P002: 3序列]

AI助手: "检测到8个序列（P001有5个，P002有3个）。
         您可以：
         1. 调用拆分工具分开处理
         2. 直接上传但可能耗时较长
         请选择处理方式。"
```

---

## 📊 决策规则

系统使用以下规则进行智能决策：

| 条件 | 风险等级 | 建议操作 | 工具推荐 |
|-----|---------|---------|---------|
| 序列数 ≤ 阈值 | 🟢 低 | 直接上传 | `Analysis_dicom_directory` |
| 序列数 > 阈值 且 患者数 ≤ 阈值 | 🟡 中 | 手动筛选或分批 | 查看详情后决定 |
| 序列数 > 阈值 且 患者数 > 阈值 | 🔴 高 | 按患者拆分 | `fileforsep` + 分批上传 |

**默认阈值：**
- 序列数阈值：5
- 患者数阈值：2

**可自定义阈值：** 根据网络状况和服务器性能调整

---

## 💡 使用建议

### 对于AI助手：
1. **首次遇到上传请求**：优先调用 `check_and_split_if_needed` 进行智能分析
2. **大型数据集**：设置 `auto_split=true` 让系统自动处理
3. **不确定情况**：先用 `smart_analyze_directory` 查看详情再决定
4. **已知小数据集**：直接调用 `Analysis_dicom_directory` 上传

### 对于用户：
1. **快速处理**：直接说"上传这个文件夹"，AI会自动处理
2. **谨慎处理**：要求"先分析再上传"，AI会先评估风险
3. **自定义阈值**：告诉AI你的网络状况，调整判断标准

---

## 🔧 技术实现

### 思维链（Thinking Chain）
每个决策步骤都被记录：
```python
thinking_chain: [
  {
    "step": "步骤编号和描述",
    "decision": "做出的决策",
    "reason": "决策理由"
  }
]
```

### 闭环机制
```
输入目录 → 扫描分析 → 智能决策 → 自动拆分（可选）→ 返回结果 → 用户选择 → 上传执行
     ↑                                                              |
     └──────────────────── 如需重新处理 ────────────────────────────┘
```

---

## ⚙️ 配置说明

### 环境变量（.env）
```env
name=你的用户名
password=你的密码
tel=手机号
base_url=https://your-api-server.com
```

### 阈值调整
在调用工具时传入自定义参数：
```json
{
  "directory_path": "路径",
  "series_threshold": 10,      // 根据网络调整
  "patient_threshold": 3       // 根据需求调整
}
```

---

## 🎉 优势总结

1. **智能化**：自动评估风险，无需人工判断
2. **透明化**：思维链展示完整决策过程
3. **自动化**：可选的自动拆分功能
4. **灵活性**：支持手动控制每个步骤
5. **安全性**：避免大文件上传超时
6. **用户友好**：清晰的下一步操作指引

---

## 📝 常见问题

**Q: 什么时候会自动拆分？**
A: 当序列数超过阈值且患者数大于阈值，并且设置了 `auto_split=true` 时。

**Q: 拆分后文件存储在哪里？**
A: 在原目录下创建以患者ID命名的子目录，每个序列再创建独立子目录。

**Q: 如果不想自动拆分怎么办？**
A: 设置 `auto_split=false` 或直接使用 `smart_analyze_directory` 工具。

**Q: 阈值如何设置？**
A: 根据经验：
- 网络好：series_threshold=10
- 网络一般：series_threshold=5（默认）
- 网络差：series_threshold=3

---

## 示例对话

**示例1：完全自动化**
```
👤 用户: "帮我上传 C:\Data\DICOM_20250113 这个文件夹的主动脉数据"

🤖 AI: [调用 check_and_split_if_needed]
      "检测到该文件夹包含15个序列，分属3个患者。已自动拆分为：
       - 患者001: 6个序列 (C:\Data\DICOM_20250113\患者001)
       - 患者002: 5个序列 (C:\Data\DICOM_20250113\患者002)
       - 患者003: 4个序列 (C:\Data\DICOM_20250113\患者003)
       
       您想上传哪个患者的数据？"

👤 用户: "上传患者001"

🤖 AI: [调用 Analysis_dicom_directory]
      "患者001的6个序列已成功上传！
       查看地址: https://your-server.com/study/studylist"
```

**示例2：先分析再决定**
```
👤 用户: "先看看 D:\Medical\CT_Scans 里有什么"

🤖 AI: [调用 smart_analyze_directory]
      "分析结果：
       📊 总计: 2个患者，4个序列
       ✅ 风险等级: 低
       💡 建议: 序列数量适中，可以安全地直接上传
       
       决策思维链：
       1. 扫描目录 → 发现4个序列
       2. 评估风险 → 序列数(4) ≤ 阈值(5)
       3. 决策 → 可直接上传
       4. 执行方案 → 调用 Analysis_dicom_directory
       
       是否现在上传？"
```

---

**文档版本**: v1.0  
**最后更新**: 2025-11-13  
**作者**: GitHub Copilot
