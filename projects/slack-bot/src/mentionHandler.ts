import type { App } from "@slack/bolt";
import type { AppMentionEvent } from "@slack/types";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

import { completeLlm } from "./llm.js";
import { loadClaudeSkill } from "./skillLoader.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
export const projectRoot = join(__dirname, "..");

type PersonaRow = { key: string; label: string; skill?: string };
type PersonaMap = Record<string, PersonaRow> & { _default?: PersonaRow };

let channelPersona: PersonaMap;

export function loadChannelPersonaMap(): void {
  const p = join(projectRoot, "config", "channel-persona.json");
  const raw = readFileSync(p, "utf8");
  channelPersona = JSON.parse(raw) as PersonaMap;
}

function resolvePersonaRow(channelId: string): PersonaRow {
  const row = channelPersona[channelId];
  if (row && typeof row === "object" && "key" in row && "label" in row) {
    return row;
  }
  const def = channelPersona._default;
  if (def && typeof def === "object" && "key" in def) {
    return def;
  }
  return { key: "_default", label: "default" };
}

function loadPersonaMarkdown(personaKey: string): string {
  const direct = join(projectRoot, "personas", `${personaKey}.md`);
  if (existsSync(direct)) {
    return readFileSync(direct, "utf8");
  }
  return readFileSync(join(projectRoot, "personas", "_default.md"), "utf8");
}

function stripMentions(text: string): string {
  return text.replace(/<@[^>]+>/g, "").trim();
}

function truncateForSlack(s: string, max = 3900): string {
  if (s.length <= max) return s;
  return `${s.slice(0, max - 20)}\n\n…(省略)`;
}

/** 初回importでpersonaを読み込み */
loadChannelPersonaMap();

export function registerMentionHandler(app: App): void {
  app.event("app_mention", async ({ event, client, logger }) => {
    const e = event as AppMentionEvent;
    // デバッグ: メンションが届いているかターミナルで確認（値は先頭だけ）
    console.log(
      "[slack-bot] app_mention 受信",
      "channel=",
      e.channel,
      "text=",
      (e.text || "").slice(0, 120),
    );
    const userText = stripMentions(e.text || "");
    const { key, label, skill } = resolvePersonaRow(e.channel);
    const skillBlock = loadClaudeSkill(projectRoot, skill);
    const parts = [
      "あなたは ai-company の「役職担当 AI」として回答します。",
      "ユーザーは **Slack だけ**で依頼している。リポジトリ・Cursor は使えない前提で、ここで完結する答え方をする。",
      `役職ラベル: ${label}（key=${key}）`,
      "Slack 用に簡潔に。箇条書き可。日本語。",
      "--- 役割定義（ペルソナ）---",
      loadPersonaMarkdown(key),
    ];
    if (skillBlock) {
      parts.push("--- 参照スキル（.claude/skills）---");
      parts.push(skillBlock);
    }
    const system = parts.join("\n\n");

    let reply: string;
    try {
      reply = await completeLlm(
        system,
        userText || "（空のメンション）何ができますか？短く教えて。",
      );
    } catch (err) {
      logger.error("LLM error", err);
      reply =
        "（エラー）LLM 呼び出しに失敗しました。LOG と API キー・プロバイダを確認してください。";
    }

    const threadTs = e.thread_ts || e.ts;
    try {
      await client.chat.postMessage({
        channel: e.channel,
        thread_ts: threadTs,
        text: truncateForSlack(`【${label}】\n${reply}`),
      });
      console.log("[slack-bot] chat.postMessage 成功 channel=", e.channel);
    } catch (postErr) {
      // 例: not_in_channel（チャンネル未招待）, missing_scope（chat:write なし）
      logger.error("chat.postMessage 失敗", postErr);
      console.error("[slack-bot] chat.postMessage 失敗:", postErr);
    }
  });
}
