/**
 * コピーした .claude/skills/<名>/skill.md をシステムプロンプト用に読む。
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

/** フロントマタ（--- ... ---）を除いて本文だけ返す。無ければそのまま。 */
function stripYamlFrontmatter(md: string): string {
  if (!md.startsWith("---\n") && !md.startsWith("---\r\n")) return md;
  const end = md.indexOf("\n---\n", 3);
  if (end === -1) return md;
  return md.slice(end + 5).trimStart();
}

export function loadClaudeSkill(projectRoot: string, skillName: string | undefined): string {
  if (!skillName) return "";
  const path = join(projectRoot, ".claude", "skills", skillName, "skill.md");
  if (!existsSync(path)) {
    console.warn(`[skill] 見つかりません: ${path}`);
    return "";
  }
  let text = readFileSync(path, "utf8");
  text = stripYamlFrontmatter(text);
  const max = Number(process.env.SKILL_PROMPT_MAX_CHARS) || 12000;
  if (text.length > max) {
    return `${text.slice(0, max)}\n\n…(SKILL_PROMPT_MAX_CHARS により省略)`;
  }
  return text;
}
