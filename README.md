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

## Contributing

```bash
cd apps/communexus
pre-commit install
```

Pre-commit runs ruff, eslint, prettier, and pyupgrade.

## License

gpl-3.0
