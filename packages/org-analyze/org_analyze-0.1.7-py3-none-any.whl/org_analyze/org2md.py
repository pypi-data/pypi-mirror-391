from .ParserOrg import ParserOrg, OrgHeader, OrgClock, OrgTable, OrgSourceBlock, OrgText, OrgMath, OrgProperties
from typing import List, Sequence, Tuple, Union, Optional

def link_converter(link: str, name: str) -> str:
    if link.startswith("id:"):
        return f"[[{name}]]"
    return f"[{name}]({link})"

def export_markdown(orgfile: str) -> List[str]:
    result: List[str] = []
    with ParserOrg(orgfile, link_converter) as p:
        for item in p.parse():
            if isinstance(item, OrgHeader):
                result.append("#" * item.level + " " + item.name)
            elif isinstance(item, OrgProperties):
                print(item.values)
            elif isinstance(item, OrgClock):
                pass # do nothing for now
            elif isinstance(item, OrgTable):
                for row in item.rows:
                    result.append("| " + " | ".join(row) + " |")
                result.append("")  # add an empty line after the table
            elif isinstance(item, OrgSourceBlock):
                result.append("```" + (item.language or ""))
                result.extend(item.lines)
                result.append("```")
                # result.append("")  # add an empty line after the code block
            elif isinstance(item, OrgText):
                result.append(item.line)
            elif isinstance(item, OrgMath):
                result.append("```math")
                result.extend(item.lines)
                result.append("```")

    return result
