# Personal technology newsletter

The `tech-newsletter.yml` workflow replaces scheduled stock reports for this fork.
It runs weekdays at 10:00 UTC (7:00 PM Korea time), independently of the Mac.
GitHub may delay scheduled starts. A manual run is also available in Actions.

It reads recent Hugging Face blog, arXiv AI research, and GeekNews feeds, then uses
the existing Claude subscription token to select and explain up to four stories.
English and Korean summaries and source links are delivered in one Telegram message.
No new API subscription is required. Existing Claude usage limits still apply.
Research claims are preliminary; this is a curated digest, not a SOTA benchmark audit.
The four-day source window may repeat stories between editions. Feed failures are
tolerated if two sources remain fresh. Invalid generation or oversized output fails
without sending. Delivery errors are not retried to avoid duplicate messages.

Existing secrets are reused: `CLAUDE_CODE_OAUTH_TOKEN`, `TELEGRAM_BOT_TOKEN`,
`TELEGRAM_CHAT_ID`, and optional `TELEGRAM_MESSAGE_THREAD_ID`.
Rendered text is retained as an Actions artifact, including on delivery failure.
Restore the former service by disabling this workflow and re-enabling
`00-daily-analysis.yml`; the stock analysis code and saved settings are preserved.

Only this English operations guide is added because this is a personal fork
configuration, not a change to the upstream stock-analysis product documentation.
