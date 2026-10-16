#!/usr/bin/env python3
"""Render both README catalog blocks from the reviewed resource records."""
import argparse
import html
import sys
from collections import defaultdict

from catalog import ROOT, load_resources


BEGIN = '<!-- BEGIN GENERATED CATALOG -->'
END = '<!-- END GENERATED CATALOG -->'
CATEGORIES = {
    'core': ('Official REA: core and setup', 'REA 官方：核心与配置'),
    'workflow-guides': ('Official REA: investigation guides', 'REA 官方：调查指南'),
    'official-case-studies': ('Official REA: case studies', 'REA 官方：案例'),
    'community-integrations': ('Community REA integrations', 'REA 社区集成'),
    'community-labs': ('Community REA labs', 'REA 社区练习'),
    'community-case-studies': ('Community REA investigations', 'REA 社区调查案例'),
    'agent-mcp': ('Independent MCP integrations', '独立 MCP 集成'),
    'agent-workflows': ('Independent agent workflows', '独立 Agent 工作流'),
    'game-analysis': ('Game analysis tools', '游戏分析工具'),
    'web-analysis': ('Website analysis tools', '网站分析工具'),
    'native-analysis': ('Native analysis tools', '原生分析工具'),
    'dynamic-analysis': ('Debugging and dynamic analysis', '调试与动态分析'),
    'android': ('Android tools', 'Android 工具'),
    'dotnet': ('.NET tools', '.NET 工具'),
    'javascript-electron': ('JavaScript and Electron tools', 'JavaScript 与 Electron 工具'),
    'webassembly': ('WebAssembly tools', 'WebAssembly 工具'),
    'firmware': ('Firmware tools', '固件工具'),
    'binary-libraries': ('Binary analysis libraries', '二进制分析库'),
    'binary-diffing': ('Binary comparison tools', '二进制对比工具'),
    'learning': ('Learning resources', '学习资源'),
    'related-lists': ('Related resource lists', '相关资源目录'),
}
RELATIONSHIPS = {
    'official-core': ('Official REA project', 'REA 官方项目'),
    'official-skill': ('Official REA skill', 'REA 官方技能'),
    'official-documentation': ('Official REA documentation', 'REA 官方文档'),
    'official-guide': ('Official REA guide', 'REA 官方指南'),
    'official-case-study': ('Official REA case study', 'REA 官方案例'),
    'community-integration': ('Community REA integration', 'REA 社区集成'),
    'community-learning-resource': ('Community REA learning resource', 'REA 社区学习资源'),
    'community-reported-mixed-workflow': ('Author-reported mixed workflow', '作者报告的混合工具流程'),
    'upstream-maintainer-companion-list': ('REA maintainer companion list', 'REA 维护者的相关目录'),
    'independent-agent-integration': ('Independent agent integration', '独立 Agent 集成'),
    'foundation': ('Foundation tool', '基础工具'),
    'learning': ('Learning resource', '学习资源'),
}
TARGETS = {
    'website': ('Website', '网站'),
    'game': ('Game', '游戏'),
    'app': ('App', '应用'),
    'binary': ('Binary', '二进制'),
    'firmware': ('Firmware', '固件'),
}


def plain_text(value):
    """Keep contributed text on one line and avoid HTML or link-label markup."""
    text = html.escape(' '.join(value.split()), quote=False)
    return text.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')


def requirements_text(value):
    """Both supported source formats render as ordinary prose."""
    if isinstance(value, str):
        return plain_text(value)
    return plain_text(' '.join(value))


def render_catalog(records, language):
    index = 0 if language == 'en' else 1
    groups = defaultdict(list)
    for record in records:
        groups[record['category']].append(record)
    unknown = set(groups) - set(CATEGORIES)
    if unknown:
        raise ValueError('Add category labels before generating: ' + ', '.join(sorted(unknown)))
    if language == 'en':
        lines = [
            f'{len(records)} resources, grouped by task. These are resource entries, not a count of independent projects.',
            '',
            'Each entry links its primary evidence and source-review date. Source review is not runtime verification; full records are in the [JSON catalog](data/README.md).',
            '',
            'REA resources are open below. Expand an independent tool family for its entries, prerequisites, and sources, or [search every record](#search-the-catalog).',
        ]
    else:
        lines = [
            f'按任务整理的 {len(records)} 条资源；条目数不代表独立项目数。',
            '',
            '每条附一手证据与来源审阅日期。来源审阅不等于运行验证；完整记录见 [JSON 目录](data/README.md)。',
            '',
            'REA 资源直接展开；独立工具按类别折叠，展开可见条目、依赖与来源，也可[搜索全部记录](#搜索目录)。',
        ]
    for category, titles in CATEGORIES.items():
        if category not in groups:
            continue
        lines.extend(['', f'### {titles[index]}', ''])
        collapsed = category not in {
            'core', 'workflow-guides', 'official-case-studies',
            'community-integrations', 'community-labs',
            'community-case-studies', 'related-lists',
        }
        if collapsed:
            summary = f'Browse {len(groups[category])} resources' if language == 'en' else f'展开 {len(groups[category])} 条资源'
            lines.extend(['<details>', f'<summary>{summary}</summary>', ''])
        for record in groups[category]:
            relation = RELATIONSHIPS.get(record['relationship'])
            if relation is None:
                raise ValueError(f"Unknown relationship: {record['relationship']}")
            name = plain_text(record['name'])
            description = plain_text(record[f'description_{language}'])
            date = plain_text(record['verified_at'])
            requirement = requirements_text(record['requirements'])
            targets = ' / '.join(TARGETS[target][index] for target in record['targets'])
            lines.append(f"- **[{name}]({record['url']})** — {description}")
            lines.append('')
            if language == 'en':
                lines.append(f"  {relation[index]} · {targets} · [Source]({record['evidence_url']}) · Source reviewed {date}.")
                lines.append(f'  Requirements and limits: {requirement}')
            else:
                lines.append(f"  {relation[index]} · {targets} · [一手来源]({record['evidence_url']}) · 来源审阅：{date}。")
                lines.append(f'  前提与范围：{requirement}')
            lines.append('')
        if collapsed:
            lines.extend(['</details>', ''])
    return '\n'.join(lines).rstrip() + '\n'


def replace_catalog(content, rendered):
    if content.count(BEGIN) != 1 or content.count(END) != 1:
        raise ValueError('Each README must contain exactly one BEGIN/END catalog marker pair')
    before, rest = content.split(BEGIN, 1)
    if END not in rest:
        raise ValueError('Catalog END marker must follow BEGIN')
    _, after = rest.split(END, 1)
    return before + BEGIN + '\n' + rendered + END + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report stale generated blocks without writing files')
    args = parser.parse_args()
    try:
        records = load_resources()
        stale = []
        for name, language in [('README.md', 'en'), ('README.zh-CN.md', 'zh')]:
            path = ROOT / name
            current = path.read_text(encoding='utf-8')
            expected = replace_catalog(current, render_catalog(records, language))
            if current != expected:
                stale.append(name)
                if not args.check:
                    path.write_text(expected, encoding='utf-8')
        if args.check and stale:
            print('Stale generated catalog: ' + ', '.join(stale), file=sys.stderr)
            print('Run python3 scripts/build_readme.py', file=sys.stderr)
            return 1
        if args.check:
            print(f'Both README catalogs match {len(records)} source records.')
        else:
            print(f"Rendered {len(records)} resources into both READMEs; updated {len(stale)} files.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Catalog generation failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
