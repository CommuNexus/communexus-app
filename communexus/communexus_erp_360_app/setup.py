import frappe

from communexus.communexus_erp_360_app import ksa, zatca_qr, zatca_xml


def after_migrate():
	"""Run all post-migrate hooks for CommuNexus ERP-360."""
	# KSA defaults and company fields
	ksa.after_migrate()
	# ZATCA QR fields/print format
	zatca_qr.after_migrate()
	# ZATCA XML fields
	zatca_xml.after_migrate()


@frappe.whitelist()
def apply_ksa_defaults(company: str | None = None):
	"""Idempotent helper to apply KSA defaults (for manual execution)."""
	ksa.bootstrap(company=company)
