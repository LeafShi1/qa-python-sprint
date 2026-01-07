
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI Agent：读取测试/构建日志，识别常见失败模式，输出分析报告（analysis.md）。

用法：
    python agent/ci_agent.py --log pytest_output.txt --out analysis.md

你可以根据自己的项目，将规则扩展为更强的领域知识：
- WinForms 设计时异常（PropertyDescriptor/UITypeEditor/Font family 等）
- Playwright 选择器策略（iframe/shadow DOM/data-testid）
- .NET 构建/打包管线中的路径/包管理问题
"""

import argparse
import os
import re
from datetime import datetime


def read_text(path: str) -> str:
    if not os.path.exists(path):
        return ''
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def detect_patterns(log: str):
    """返回 (label, details) 列表，描述识别到的失败模式。"""
    patterns = []

    # Playwright：TimeoutError / 选择器等待失败
    if re.search(r'TimeoutError', log, re.IGNORECASE) or \
       re.search(r'waiting for locator\(', log):
        details = []
        if '#username' in log or 'locator("#' in log:
            details.append('疑似选择器为 ID（如 `#username`）未出现或在 iframe/shadow DOM 内。')
        details.append("""
建议：
- 在操作前等待页面就绪：`page.wait_for_load_state("networkidle")`
- 检查是否在 iframe：先 `frame = page.frame(name="...")`，再在 frame 内操作
- 使用更稳健的选择器（如 `data-testid`），避免易变的 CSS/文本
"""
        )
        patterns.append(('PlaywrightTimeout', '\n'.join(details)))

    # Playwright：浏览器未安装/找不到可执行文件
    if re.search(r"Executable doesn't exist", log) or re.search(r'playwright\.install', log, re.IGNORECASE):
        patterns.append(('PlaywrightInstall', '浏览器未安装或环境缺依赖。建议在 CI 中执行：\n`playwright install --with-deps`（Linux）或 `playwright install`（Windows/macOS）。'))

    # .NET：非法路径字符
    if re.search(r'Illegal characters in path', log, re.IGNORECASE):
        patterns.append(('DotNetPath', '检测到路径包含非法字符。建议：\n- 使用 `Path.Combine` 构造路径\n- 在赋值前用 `Path.GetInvalidPathChars()` 进行校验\n- 确认输入来自 UI/配置文件时是否包含意外的冒号/问号等字符'))

    # NuGet/网络问题导致的临时失败（示例）
    if re.search(r'(NU1\d{3}|connection timed out|temporary failure|network error)', log, re.IGNORECASE):
        patterns.append(('TransientNetwork', '疑似网络/镜像不稳定导致的临时失败。建议：\n- 增加重试策略（最多 3 次，指数退避）\n- 切换镜像源或开启缓存\n- 对只读任务采用离线缓存以降低波动'))

    return patterns


def summarize(log: str, patterns):
    """生成中文 Markdown 分析报告。"""
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ UTC')
    header = f"""# CI Agent 分析报告

生成时间：{now}

"""

    if not log.strip():
        return header + "未找到日志内容，请检查工作流步骤是否正确保存了输出文件。"

    summary = []
    if patterns:
        summary.append("## 结论摘要\n")
        for i, (label, _) in enumerate(patterns, 1):
            summary.append(f"- 问题 {i}: **{label}**")
    else:
        summary.append("## 结论摘要\n- 未识别到常见失败模式，建议人工进一步查看完整日志。")

    body = ["\n## 详细分析\n"]
    for i, (label, details) in enumerate(patterns, 1):
        body.append(f"### 问题 {i}: {label}\n{details}\n")

    next_steps = """
## 建议的下一步
- 如为 Playwright 选择器问题：优先改用稳定的 `data-testid`，并在关键页面加载后等待 `networkidle`。
- 如为 .NET 路径问题：统一通过 `Path.Combine` 构造路径，并在输入入口加入校验逻辑。
- 如为临时网络问题：为易波动步骤增加重试与缓存；区分“可重试失败”与“必须人工处理”的失败类型。
- 将以上策略沉淀为测试/构建规范，并在 Pipeline 中强制执行。
"""

    return header + '\n'.join(summary) + '\n' + '\n'.join(body) + '\n' + next_steps


def main():
    parser = argparse.ArgumentParser(description='CI Agent：分析日志并生成报告')
    parser.add_argument('--log', required=True, help='日志文件路径，如 pytest_output.txt')
    parser.add_argument('--out', default='analysis.md', help='输出报告路径，默认 analysis.md')
    args = parser.parse_args()

    log = read_text(args.log)
    patterns = detect_patterns(log)
    report = summarize(log, patterns)

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[CI Agent] 已生成报告：{args.out}")


if __name__ == '__main__':
    main()
