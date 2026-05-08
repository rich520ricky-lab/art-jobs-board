Project: AICEO — Rich T's aistock100.org / Apex Claw Protocol. Goal: launch token on pump.fun, auto-post across Telegram/Twitter/Discord/TikTok/YouTube, auto-answer community questions via AICEO (AI CEO persona). 4 languages: EN, ZH-TW, ZH-CN, JA. Weekly 4-5 posts including Monday AI robot joke. Token holder vote for unknown questions. Stored as skill 'aiceo-project-plan'.
§
用戶希望記住 MLX 模型設定以快速切換：provider=custom, model.default=MLX-Qwen3.5-9B-DeepSeek-V4-Flash-6bit, base_url=http://127.0.0.1:8000/v1, api_key=1111, show_reasoning=hide, skin=light, compression.threshold=50, reasoning=off, saved to ~/hermes/mlx-model-config.yaml
§
HM MLX 配置設定流程（2026-05-01）：1) hermes config set model.base_url http://127.0.0.1:8000/v1, 2) hermes config set model.api_key 1111, 3) hermes config set display.show_reasoning hide, 4) hermes config set display.skin light, 5) hermes config set compression.threshold 50, 6) hermes /reset 生效。完整配置見 ~/hermes/mlx-model-config.yaml。可快速切換：複製 yaml 內容 → 貼 ~/.hermes/config.yaml → hermes /reset
§
AI Salesbot (sale.aiceox.com) — Taiwan market. Sellers upload products → auto-generate product copy, photos (downloadable), QR sales codes linked to Taiwan mobile payment, ad placement. GitHub: github.com/rich520ricky-lab/ai-sales-bot (private). Deployed on Oracle Cloud (129.146.1.87), PHP 8, Apache, MariaDB. Managed via aaPanel — do NOT touch Apache/httpd configs via SSH. DB: ai_salesbot / Ricky520!. Google OAuth from settings table. Code at /www/wwwroot/sale.aiceox.com/. SSH: ubuntu. Status as of 2026-05-05: deployed & working, OAuth configured.
§
AI Salesbot Google OAuth: credentials stored in `settings` table (`google_client_id`, `google_client_secret`). login.php reads from DB to build OAuth URL. Callback at /auth/google-callback.php. V1 at /www/wwwroot/sale.aiceox.com/ on Oracle Cloud.
§
Art & Design Jobs Board 網站已部署至 GitHub Pages: https://rich520ricky-lab.github.io/art-jobs-board/。Repo: github.com/rich520ricky-lab/art-jobs-board。靜態 HTML，中英雙語，收錄 28 個美術/設計職缺。本地源碼在 ~/hermes/art-jobs-site/。
§
GitHub CLI (gh) installed at ~/.local/bin/gh on macOS arm64. macOS releases are .zip (not .tar.gz). Extract to ~/.local/bin/. Must export PATH before use.