import re
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def ensure_defaults():
	"""Set KSA defaults if not already configured."""
	global_defaults = frappe.get_single("Global Defaults")
	system_settings = frappe.get_single("System Settings")

	if not global_defaults.default_country:
		global_defaults.default_country = "Saudi Arabia"
	if not global_defaults.default_currency:
		global_defaults.default_currency = "SAR"
	global_defaults.save()

	if not system_settings.time_zone:
		system_settings.time_zone = "Asia/Riyadh"
	# keep English as primary but enable Arabic for bilingual use
	if not system_settings.language:
		system_settings.language = "en"
	if not system_settings.get("enabled_system_languages"):
		system_settings.enabled_system_languages = ["en", "ar"]
	system_settings.flags.ignore_mandatory = True
	system_settings.save()


def ensure_company_fields():
	"""Add Company custom fields needed for KSA compliance."""
	fields = {
		"Company": [
			{
				"fieldname": "cn_vat_registration_no",
				"label": "VAT Registration Number",
				"fieldtype": "Data",
				"insert_after": "tax_id",
				"description": "15-digit VAT registration number",
			},
			{
				"fieldname": "cn_commercial_registration_no",
				"label": "Commercial Registration (CR)",
				"fieldtype": "Data",
				"insert_after": "cn_vat_registration_no",
			},
			{
				"fieldname": "cn_national_address_section",
				"fieldtype": "Section Break",
				"label": "National Address",
				"insert_after": "cn_commercial_registration_no",
			},
			{
				"fieldname": "cn_building_no",
				"label": "Building No",
				"fieldtype": "Data",
				"insert_after": "cn_national_address_section",
			},
			{
				"fieldname": "cn_street_name",
				"label": "Street Name",
				"fieldtype": "Data",
				"insert_after": "cn_building_no",
			},
			{
				"fieldname": "cn_district",
				"label": "District",
				"fieldtype": "Data",
				"insert_after": "cn_street_name",
			},
			{
				"fieldname": "cn_city",
				"label": "City",
				"fieldtype": "Data",
				"insert_after": "cn_district",
			},
			{
				"fieldname": "cn_postal_code",
				"label": "Postal Code",
				"fieldtype": "Data",
				"insert_after": "cn_city",
			},
			{
				"fieldname": "cn_additional_no",
				"label": "Additional No",
				"fieldtype": "Data",
				"insert_after": "cn_postal_code",
			},
		]
	}
	create_custom_fields(fields, update=True)


def ensure_vat_template(company: str | None = None):
	"""Create a 15% VAT sales template for KSA."""
	company = company or frappe.defaults.get_global_default("company")
	if not company:
		return

	template_name = f"KSA VAT 15% - {company}"
	if frappe.db.exists("Sales Taxes and Charges Template", template_name):
		return

	doc = frappe.new_doc("Sales Taxes and Charges Template")
	doc.title = template_name
	doc.company = company
	doc.is_default = 1
	doc.disabled = 0
	doc.append(
		"taxes",
		{
			"charge_type": "On Net Total",
			"account_head": _("VAT - {0}").format(company),
			"description": "VAT 15%",
			"rate": 15,
		},
	)
	doc.insert(ignore_if_duplicate=True)


def validate_company(doc, _):
	"""Validate Company KSA fields."""
	vat_no = (doc.get("cn_vat_registration_no") or "").strip()
	if vat_no and not re.fullmatch(r"\\d{15}", vat_no):
		frappe.throw(_("VAT Registration Number must be 15 digits."))

	postcode = (doc.get("cn_postal_code") or "").strip()
	if postcode and not re.fullmatch(r"\\d{5}", postcode):
		frappe.throw(_("Postal Code must be 5 digits."))


def bootstrap(company: str | None = None):
	"""Idempotent helper to apply KSA defaults."""
	ensure_defaults()
	ensure_company_fields()
	ensure_vat_template(company=company)


def after_migrate():
	bootstrap()
