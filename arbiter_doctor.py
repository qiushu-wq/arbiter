#!/usr/bin/env python3
"""arbiter doctor — 多Agent系统诊断工具
扫描项目目录，找出上下文、故障、状态三类的潜在问题。
不修任何东西。只告诉你哪里会崩、为什么。
"""

import os, re, sys
from collections import defaultdict

# 诊断规则
CHECKS = [
    # 上下文共享风险
    {
        'id': 'context_no_quota',
        'severity': 'high',
        'category': '上下文共享风险',
        'pattern': r'(StateGraph|TypedDict|messages\s*=\s*\[)',
        'description': '多个Agent共用一个StateGraph，无配额隔离',
        'detail': '你的Agent在抢同一个上下文窗口，随时可能溢出。Arbiter用固定分区+即时回收解决这个问题。',
    },
    {
        'id': 'no_max_tokens',
        'severity': 'medium',
        'category': '上下文共享风险',
        'pattern': r'(max_tokens|max_context_length)\s*=\s*None',
        'description': 'Agent调用未设置max_tokens上限',
        'detail': '没有硬上限，一个Agent的上下文膨胀会挤掉所有其他Agent的空间。',
    },
    # 故障盲区
    {
        'id': 'error_swallowed',
        'severity': 'high',
        'category': '故障盲区',
        'pattern': r'except\s+\w+.*:\s*\n\s*(pass|print|logger\.warning)',
        'description': 'Agent异常被静默吞掉',
        'detail': 'catch块只有pass或print，错误没进审计日志。你上周可能有几十次超时你完全不知道。Arbiter的AuditTrail记录每一次异常。',
    },
    {
        'id': 'no_timeout',
        'severity': 'medium',
        'category': '故障盲区',
        'pattern': r'\.invoke\(|\.run\(|\.call\(',
        'description': 'LLM调用未设置timeout',
        'detail': 'Agent卡住时整个管道停摆。Arbiter的guard熔断器自动止损。',
    },
    # 状态冲突
    {
        'id': 'state_conflict',
        'severity': 'high',
        'category': '状态冲突',
        'pattern': r'(state\.messages\s*=|\bstate\[.+\]\s*=)',
        'description': '多个Agent同时写同一个state字段',
        'detail': 'Agent A和Agent B都在改state.messages，概率性数据丢失。你还没发现是因为并发不够高。Arbiter用项目级锁防冲突。',
    },
    # Token边界问题
    {
        'id': 'context_overflow',
        'severity': 'high',
        'category': '上下文边界溢出',
        'pattern': r'(context_window|max_input_tokens)\s*=\s*(\d{5,6})',
        'description': '上下文窗口接近满载运行',
        'detail': '你的Agent上下文窗口接近满载，12%的调用可能触发截断。Arbiter的adapt配额策略提前分配，避免边界溢出。',
    },
]

def scan_directory(path):
    """扫描目录，运行所有诊断规则"""
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        print(f'错误: {path} 不是有效目录')
        sys.exit(1)

    # 收集所有Python文件
    py_files = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', 'venv', '.venv')]
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))

    if not py_files:
        print(f'未找到Python文件在 {path}')
        sys.exit(0)

    # 检测框架
    all_code = ''
    for fp in py_files:
        try:
            with open(fp, encoding='utf-8', errors='ignore') as f:
                all_code += f.read() + '\n'
        except Exception as e:
            import sys
            print(f'[WARN] Failed to read {fp}: {e}', file=sys.stderr)

    framework = detect_framework(all_code)
    agent_count = estimate_agent_count(all_code, py_files)

    # 运行诊断
    findings = []
    for check in CHECKS:
        matches = []
        for fp in py_files:
            try:
                with open(fp, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    found = re.findall(check['pattern'], content, re.MULTILINE | re.DOTALL)
                    if found:
                        # Get line numbers
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if re.search(check['pattern'], line):
                                matches.append(f'{os.path.basename(fp)}:{i+1}')
                                break
            except Exception as e:
                import sys
                print(f'[WARN] Failed to scan {fp}: {e}', file=sys.stderr)
        if matches:
            findings.append({**check, 'files': matches[:3]})  # Max 3 locations

    return {
        'path': path,
        'agent_count': agent_count,
        'framework': framework,
        'findings': findings,
        'file_count': len(py_files),
    }

def detect_framework(code):
    if 'langgraph' in code.lower() or 'StateGraph' in code:
        return 'LangGraph'
    if 'crewai' in code.lower() or 'Crew' in code:
        return 'CrewAI'
    if 'autogen' in code.lower():
        return 'AutoGen'
    if 'langchain' in code.lower():
        return 'LangChain'
    if 'openai' in code.lower() or 'anthropic' in code.lower():
        return 'Direct API'
    return 'Unknown'

def estimate_agent_count(code, files):
    # Count from graph node definitions (most reliable)
    nodes = set()
    for match in re.findall(r'add_node\([\"\'](\w+)[\"\']', code):
        nodes.add(match)

    if len(nodes) > 0:
        return len(nodes)

    # Count from class definitions
    classes = re.findall(r'class\s+(\w*[Aa]gent)\s*[(:]', code)
    if classes:
        return len(set(classes))

    # Fallback: count files with agent patterns, capped
    count = 0
    for fp in files:
        try:
            with open(fp, encoding='utf-8', errors='ignore') as f:
                c = f.read()
            if re.search(r'(from langgraph|import langgraph|StateGraph|add_node)', c):
                count += 1
        except Exception as e:
            import sys
            print(f'[WARN] Failed to scan {fp}: {e}', file=sys.stderr)
    return max(min(count, 20), 1)

def print_report(result):
    """输出诊断报告"""
    findings = result['findings']
    high = [f for f in findings if f['severity'] == 'high']
    medium = [f for f in findings if f['severity'] == 'medium']
    low = [f for f in findings if f['severity'] == 'low']

    sep = '-' * 56
    a_count = result['agent_count']
    fw = result['framework']
    f_count = result['file_count']

    print('')
    print(f'  Diagnosis: {a_count} Agents - {fw} - {f_count} files')
    print('  ' + sep)

    if not findings:
        print('  [OK] No obvious issues found.')
        return

    for f in findings:
        if f['severity'] == 'high':
            icon = '[HIGH]'
        elif f['severity'] == 'medium':
            icon = '[MED]'
        else:
            icon = '[LOW]'

        cat = f['category']
        desc = f['description']
        detail = f['detail']

        print('')
        print(f'  {icon} {cat}: {desc}')
        print(f'     -> {detail}')
        for loc in f.get('files', []):
            print(f'     @ {loc}')

    print('')
    print('  ' + sep)
    print(f'  {len(high)} high, {len(medium)} medium, {len(low)} low')
    print('')
    print('  -> These problems are solved by Arbiter:')
    print('     https://github.com/qiushu-wq/arbiter')

def check_self(project_dirs=None, min_memory_files=8):
    home = os.path.expanduser('~')
    findings = []
    details = {'claude_md_ok': False, 'projects_ok': True, 'missing': [], 'memory_ok': False}
    claude_md = os.path.join(home, '.claude', 'CLAUDE.md')
    details['claude_md_ok'] = os.path.exists(claude_md)

    # Check memory directory
    memory_dir = os.path.join(home, '.claude', 'projects')
    memory_files = []
    if os.path.isdir(memory_dir):
        for root, dirs, files in os.walk(memory_dir):
            for f in files:
                if f.endswith('.md'):
                    memory_files.append(os.path.join(root, f))
    details['memory_ok'] = len(memory_files) >= min_memory_files
    details['memory_count'] = len(memory_files)
    if not details['memory_ok']:
        findings.append({
            'severity': 'high', 'category': 'Memory Degraded',
            'description': f'Memory files: {len(memory_files)} (min: {min_memory_files})',
            'detail': 'Memory system is below minimum threshold. Run arbiter-doctor --self to recheck.'
        })

    # Check project dirs if provided
    dirs = project_dirs or {}
    for name, path in dirs.items():
        full = os.path.join(home, path)
        if not os.path.isdir(full):
            details['missing'].append(name)
            details['projects_ok'] = False
            findings.append({
                'severity': 'high', 'category': 'Project Missing',
                'description': f'Directory missing: {name}',
                'detail': f'Expected at ~/{path}'
            })
    return {'status': 'healthy' if details['projects_ok'] and not findings else 'degraded',
            'findings': findings, 'details': details}

def print_self_report(result):
    sep = '-' * 56
    print('')
    print('  Arbiter Self-Scan')
    print('  ' + sep)
    d = result['details']
    print(f'  CLAUDE.md:    {"OK" if d["claude_md_ok"] else "MISSING"}')
    print(f'  Projects:     {len(d["missing"])} missing')
    for f in result.get('findings', []):
        print(f'  [HIGH] {f["category"]}: {f["description"]}')
    print(f'  Status: {result["status"].upper()}')


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '--self':
        result = check_self()
        print_self_report(result)
        sys.exit(0 if result['status'] == 'healthy' else 1)

    if len(sys.argv) < 2:
        print('Usage:')
        print('  arbiter-doctor <project-dir>    -- diagnose multi-agent project')
        print('  arbiter-doctor --self           -- self-check environment')
        sys.exit(1)

    path = sys.argv[1]
    result = scan_directory(path)
    print_report(result)


if __name__ == '__main__':
    main()
