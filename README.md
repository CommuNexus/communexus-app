# CommuNexus ERP-360 App

Branding, KSA, and ZATCA features for CommuNexus ERP-360 (delivered as a separate custom Frappe app).

## Install

```bash
cd ~/communexus-bench  # or your bench path
bench get-app https://github.com/CommuNexus/communexus-app.git
bench --site <yoursite> install-app communexus
```

## Assets

Branding assets live under `communexus/public/branding/` and include icons, stacked + horizontal logos, and favicons sized for app/UIs.

## ZATCA QR (Phase 1)

- Sales Invoice fields: `ZATCA QR (Base64 TLV)` and `ZATCA QR SVG` (auto-populated on validate/submit when Company VAT is present).
- Print format added: **CommuNexus Sales Invoice (ZATCA QR)** embeds the QR image; select it when printing.
- QR payload uses seller name, VAT number, invoice timestamp, grand total, and VAT amount per ZATCA Phase 1.

## Contributing

```bash
cd apps/communexus
pre-commit install
```

Pre-commit runs ruff, eslint, prettier, and pyupgrade.

## License

gpl-3.0
