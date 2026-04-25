/**
 * Slack Bolt: app_mention のみ。
 * - HTTP+Express: POST /slack/events, GET /health（本番・ngrok 向け）
 * - Socket Mode: SLACK_APP_TOKEN あり → 公開 URL 不要（ローカル向け）
 */
// カレントディレクトリの .env を読む（projects/slack-bot で npm start すること）
import "dotenv/config";
// @slack/bolt は CJS。Node ESM からは named import だと実行時に落ちるため default から取り出す
import bolt from "@slack/bolt";
import type { App as BoltApp } from "@slack/bolt";
const { App, ExpressReceiver } = bolt;

import { registerMentionHandler } from "./mentionHandler.js";

/** 届いているイベントをすべてターミナルに出す（反応しないときの切り分け用） */
function registerDebugEventLogger(app: BoltApp): void {
  app.use(async ({ body, next }) => {
    const b = body as { type?: string; event?: { type?: string } };
    if (b?.event?.type) {
      console.log("[slack-bot] Slack イベント:", b.event.type);
    } else if (b?.type) {
      console.log("[slack-bot] ペイロード:", b.type);
    }
    await next();
  });
}

function registerBoltErrorLogger(app: BoltApp): void {
  app.error(async (err) => {
    console.error("[slack-bot] Bolt エラー:", err);
  });
}

const signingSecret = process.env.SLACK_SIGNING_SECRET;
const token = process.env.SLACK_BOT_TOKEN;
if (!signingSecret || !token) {
  console.error("SLACK_SIGNING_SECRET と SLACK_BOT_TOKEN を設定してください。");
  process.exit(1);
}

const useSocket = Boolean(process.env.SLACK_APP_TOKEN?.trim());
const appToken = process.env.SLACK_APP_TOKEN;

if (useSocket) {
  const app = new App({
    token,
    signingSecret,
    socketMode: true,
    appToken: appToken!,
    processBeforeResponse: false,
  });
  registerDebugEventLogger(app);
  registerBoltErrorLogger(app);
  registerMentionHandler(app);
  (async () => {
    await app.start();
    console.log("Slack bot: Socket Mode 起動（公開URL不要）。app_mention のみ。");
  })().catch((err) => {
    console.error(err);
    process.exit(1);
  });
} else {
  const receiver = new ExpressReceiver({
    signingSecret,
    processBeforeResponse: false,
  });
  receiver.app.get("/health", (_req, res) => {
    res.status(200).type("text/plain").send("ok");
  });
  const app = new App({
    token,
    receiver,
    processBeforeResponse: false,
  });
  registerDebugEventLogger(app);
  registerBoltErrorLogger(app);
  registerMentionHandler(app);
  const port = Number(process.env.PORT) || 3000;
  (async () => {
    await app.start(port);
    console.log(
      `Slack bot: HTTP モード。port ${port} (POST /slack/events, GET /health)`,
    );
  })().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
