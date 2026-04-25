/**
 * OpenAI または Anthropic（環境変数で切替）
 */
import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";

export async function completeLlm(system: string, user: string): Promise<string> {
  const provider = (process.env.LLM_PROVIDER || "openai").toLowerCase();

  if (provider === "anthropic") {
    const key = process.env.ANTHROPIC_API_KEY;
    if (!key) throw new Error("ANTHROPIC_API_KEY が未設定です");
    const client = new Anthropic({ apiKey: key });
    // モデル ID は小文字（例: claude-opus-4-6）。省略時は Opus 4.6（要: docs の models-overview）
    const model = process.env.ANTHROPIC_MODEL || "claude-opus-4-6";
    const msg = await client.messages.create({
      model,
      max_tokens: 1024,
      system,
      messages: [{ role: "user", content: user }],
    });
    const block = msg.content[0];
    if (block && block.type === "text") return block.text;
    return "";
  }

  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error("OPENAI_API_KEY が未設定（LLM_PROVIDER=openai）");
  const openai = new OpenAI({ apiKey: key });
  const model = process.env.OPENAI_MODEL || "gpt-4o-mini";
  const res = await openai.chat.completions.create({
    model,
    messages: [
      { role: "system", content: system },
      { role: "user", content: user },
    ],
  });
  return res.choices[0]?.message?.content?.trim() ?? "";
}
