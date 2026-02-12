# Fonts

To keep pull requests text-only and avoid binary-diff issues, this repository does **not** store `.ttf` binaries in Git.

Install the deterministic caption/watermark font locally:

```bash
bash bin/install_inter_font.sh
```

This downloads `fonts/Inter-Bold.ttf` from the official Inter font release URL and verifies SHA-256:

`5c1247acef7f2b8522a31742c76d6adcb5569bacc0be7ceaa4dc39dd252ce895`

`conf/app_config.json` is already configured to use:

- `watermark_config.font = "fonts/Inter-Bold.ttf"`
- `captions.font = "fonts/Inter-Bold.ttf"`
