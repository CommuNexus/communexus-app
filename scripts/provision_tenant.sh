#!/usr/bin/env bash
set -euo pipefail

# Usage:
# SITE_NAME=my.erp360.local ADMIN_PASSWORD=admin bench_path=~/communexus-bench ./scripts/provision_tenant.sh

SITE_NAME="${SITE_NAME:-}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"
BENCH_PATH="${BENCH_PATH:-~/communexus-bench}"

if [ -z "$SITE_NAME" ]; then
  echo "SITE_NAME is required" >&2
  exit 1
fi

cd "$BENCH_PATH"
bench new-site "$SITE_NAME" ${ADMIN_PASSWORD:+--admin-password "$ADMIN_PASSWORD"}
bench --site "$SITE_NAME" install-app erpnext
bench --site "$SITE_NAME" install-app communexus
bench --site "$SITE_NAME" execute communexus.communexus_erp_360_app.setup.apply_ksa_defaults

echo "Provisioned $SITE_NAME with ERPNext + CommuNexus ERP-360"
