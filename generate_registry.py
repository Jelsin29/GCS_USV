#!/usr/bin/env python3
import os, re, yaml, sys


def extract_frontmatter(content):
    """Extract YAML frontmatter from SKILL.md"""
    if content.startswith("---"):
        try:
            end = content.index("---", 3)
            fm = content[3:end].strip()
            data = yaml.safe_load(fm)
            return data
        except:
            pass
    return {}


def extract_trigger(frontmatter):
    desc = frontmatter.get("description", "")
    # Trigger: ... pattern
    match = re.search(r"Trigger:\s*(.+)", desc)
    if match:
        return match.group(1).strip()
    # fallback: first sentence
    return desc.split(".")[0].strip()


def extract_compact_rules(content, frontmatter):
    """Generate 1-5 line compact rules from content"""
    rules = []
    name = frontmatter.get("name", "")
    # Look for a "Rules" or "Critical Patterns" section
    lines = content.split("\n")
    in_section = False
    for line in lines:
        if line.startswith("## ") and (
            "Rules" in line or "Critical" in line or "Patterns" in line
        ):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            rules.append(line.strip())
        if in_section and line.strip().startswith("* "):
            rules.append(line.strip())
    if rules:
        return rules[:5]  # limit
    # fallback: extract first few non-empty lines after frontmatter
    after_front = False
    count = 0
    for line in lines:
        if line.startswith("---") and after_front:
            after_front = False
            continue
        if line.startswith("---") and not after_front:
            after_front = True
            continue
        if after_front and line.strip() and not line.startswith("#"):
            # skip code blocks
            if line.strip().startswith("```"):
                continue
            rules.append(line.strip())
            count += 1
            if count >= 3:
                break
    return rules


def main():
    skills = []
    for root in ["/home/jelsin/.claude/skills", "/home/jelsin/.config/opencode/skills"]:
        for dirpath, dirnames, filenames in os.walk(root):
            for f in filenames:
                if f == "SKILL.md":
                    full = os.path.join(dirpath, f)
                    if "sdd-" in full or "_shared" in full or "skill-registry" in full:
                        continue
                    skills.append(full)
    # deduplicate by name
    seen = {}
    for path in skills:
        with open(path, "r") as fp:
            content = fp.read()
        front = extract_frontmatter(content)
        name = front.get("name", os.path.basename(os.path.dirname(path)))
        if name in seen:
            # keep first
            continue
        seen[name] = (path, front, content)

    # Build registry
    lines = []
    lines.append("# Skill Registry")
    lines.append("")
    lines.append(
        "**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files."
    )
    lines.append("")
    lines.append("## User Skills")
    lines.append("")
    lines.append("| Trigger | Skill | Path |")
    lines.append("|---------|-------|------|")
    for name, (path, front, content) in sorted(seen.items()):
        trigger = extract_trigger(front)
        lines.append(f"| {trigger} | {name} | `{path}` |")
    lines.append("")
    lines.append("## Compact Rules")
    lines.append("")
    lines.append(
        "Pre-digested rules per skill. Delegators copy matching blocks into sub-agent prompts as `## Project Standards (auto-resolved)`."
    )
    lines.append("")
    for name, (path, front, content) in sorted(seen.items()):
        rules = extract_compact_rules(content, front)
        lines.append(f"### {name}")
        if rules:
            for rule in rules:
                lines.append(f"- {rule}")
        else:
            lines.append("- No specific rules extracted")
        lines.append("")
    lines.append("## Project Conventions")
    lines.append("")
    lines.append(
        "None detected (no project-level CLAUDE.md, .cursorrules, AGENTS.md, or GEMINI.md)."
    )
    lines.append("")
    registry = "\n".join(lines)
    # Write to .atl/skill-registry.md
    os.makedirs(".atl", exist_ok=True)
    with open(".atl/skill-registry.md", "w") as fp:
        fp.write(registry)
    print("Registry written to .atl/skill-registry.md")
    print(f"Total skills: {len(seen)}")


if __name__ == "__main__":
    main()
