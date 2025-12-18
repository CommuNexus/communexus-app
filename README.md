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

## KSA defaults

- Defaults applied (idempotently) on migrate: country = Saudi Arabia, currency = SAR, timezone = Asia/Riyadh, English + Arabic enabled.
- Company custom fields: VAT Registration Number (15 digits), Commercial Registration, National Address fields.
- VAT helper: creates a `KSA VAT 15% - <Company>` template when a default company exists.
- Run manually if needed:

```bash
bench --site <yoursite> execute communexus.communexus_erp_360_app.ksa.bootstrap
```

## Contributing

```bash
cd apps/communexus
pre-commit install
```

Pre-commit runs ruff, eslint, prettier, and pyupgrade.

## License

gpl-3.0
