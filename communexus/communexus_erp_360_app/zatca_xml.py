import uuid
import xml.etree.ElementTree as ET

try:
	import frappe  # type: ignore
	from frappe import _  # type: ignore
except ImportError:  # pragma: no cover - used for tests without frappe
	class _DummyFrappe:
		@staticmethod
		def whitelist():
			def decorator(fn):
				return fn

			return decorator

	frappe = _DummyFrappe()  # type: ignore

	def _(msg):  # type: ignore
		return msg


def ensure_sales_invoice_fields():
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	create_custom_fields(
		{
			"Sales Invoice": [
				{
					"fieldname": "cn_zatca_uuid",
					"label": "ZATCA UUID",
					"fieldtype": "Data",
					"read_only": 1,
					"insert_after": "posting_time",
				},
				{
					"fieldname": "cn_zatca_xml_file",
					"label": "ZATCA XML File",
					"fieldtype": "Link",
					"options": "File",
					"read_only": 1,
					"insert_after": "cn_zatca_uuid",
				},
			]
		},
		update=True,
	)


def _ns(tag):
	return f"{{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}}{tag}"


def _cbc(tag):
	return f"{{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}}{tag}"


def _cac(tag):
	return f"{{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}}{tag}"


def _add_text(parent, tag, text):
	el = ET.SubElement(parent, tag)
	el.text = text
	return el


def build_xml(si, company_doc=None) -> tuple[bytes, str]:
	try:
		from frappe.utils import get_datetime
	except ImportError:  # pragma: no cover - requires frappe runtime
		class _Dummy:
			@staticmethod
			def throw(msg, exc_cls=Exception):
				raise exc_cls(msg)

			@staticmethod
			def get_doc(*_, **__):
				raise ImportError("frappe not available")

		def _(msg):  # type: ignore
			return msg

		frappe = _Dummy()  # type: ignore

		def get_datetime(value):  # type: ignore
			from datetime import datetime
			return datetime.fromisoformat(str(value))

	company = company_doc or frappe.get_doc("Company", si.company)
	company_vat = (
		getattr(company, "cn_vat_registration_no", None)
		or company.get("tax_id")
		or company.get("tax_id_number")
	)
	if not company_vat:
		frappe.throw(_("Company VAT registration is required for ZATCA XML."))

	customer_vat = si.tax_id or ""
	if not si.customer:
		frappe.throw(_("Customer is required for ZATCA XML."))

	posting_dt = get_datetime(f"{si.posting_date} {si.posting_time or '00:00:00'}")
	invoice = ET.Element(
		_ns("Invoice"),
		{
			"xmlns:cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
			"xmlns:cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
		},
	)

	uuid_value = getattr(si, "cn_zatca_uuid", None) or str(uuid.uuid4())

	_add_text(invoice, _cbc("CustomizationID"), "urn:zatca:sa:etr:invoice:xml")
	_add_text(invoice, _cbc("ProfileID"), "reporting:1.0")
	_add_text(invoice, _cbc("ID"), si.name)
	_add_text(invoice, _cbc("UUID"), uuid_value)
	_add_text(invoice, _cbc("IssueDate"), posting_dt.date().isoformat())
	_add_text(invoice, _cbc("IssueTime"), posting_dt.time().isoformat())
	_add_text(invoice, _cbc("InvoiceTypeCode"), "388")
	_add_text(invoice, _cbc("DocumentCurrencyCode"), si.currency)

	supplier = ET.SubElement(invoice, _cac("AccountingSupplierParty"))
	party = ET.SubElement(supplier, _cac("Party"))
	_add_text(ET.SubElement(party, _cac("PartyName")), _cbc("Name"), company.company_name or si.company)
	party_tax = ET.SubElement(party, _cac("PartyTaxScheme"))
	_add_text(party_tax, _cbc("CompanyID"), company_vat)
	_add_text(party_tax, _cbc("TaxScheme"), "VAT")

	customer_party = ET.SubElement(invoice, _cac("AccountingCustomerParty"))
	customer_entity = ET.SubElement(customer_party, _cac("Party"))
	_add_text(ET.SubElement(customer_entity, _cac("PartyName")), _cbc("Name"), si.customer_name or si.customer)
	if customer_vat:
		customer_tax = ET.SubElement(customer_entity, _cac("PartyTaxScheme"))
		_add_text(customer_tax, _cbc("CompanyID"), customer_vat)

	legal_total = ET.SubElement(invoice, _cac("LegalMonetaryTotal"))
	_add_text(legal_total, _cbc("TaxExclusiveAmount"), f"{float(si.net_total or 0):.2f}")
	_add_text(legal_total, _cbc("TaxInclusiveAmount"), f"{float(si.grand_total or 0):.2f}")
	_add_text(legal_total, _cbc("PayableAmount"), f"{float(si.grand_total or 0):.2f}")

	tax_total = ET.SubElement(invoice, _cac("TaxTotal"))
	_add_text(tax_total, _cbc("TaxAmount"), f"{float(si.total_taxes_and_charges or 0):.2f}")

	for item in si.items:
		line = ET.SubElement(invoice, _cac("InvoiceLine"))
		_add_text(line, _cbc("ID"), str(item.idx))
		_add_text(line, _cbc("InvoicedQuantity"), f"{float(item.qty or 0):.3f}")
		_add_text(line, _cbc("LineExtensionAmount"), f"{float(item.net_amount or 0):.2f}")
		price = ET.SubElement(line, _cac("Price"))
		_add_text(price, _cbc("PriceAmount"), f"{float(item.rate or 0):.2f}")

	xml_bytes = ET.tostring(invoice, encoding="utf-8", xml_declaration=True)
	return xml_bytes, uuid_value


@frappe.whitelist()
def export_zatca_xml(name: str):
	import frappe

	si = frappe.get_doc("Sales Invoice", name)
	if si.docstatus != 1:
		frappe.throw(_("Submit the Sales Invoice before exporting ZATCA XML."))

	ensure_sales_invoice_fields()
	xml_bytes, uuid_value = build_xml(si)

	file_name = f"{si.name}-zatca.xml"
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": file_name,
			"attached_to_doctype": "Sales Invoice",
			"attached_to_name": si.name,
			"is_private": 1,
			"content": xml_bytes,
		}
	).insert(ignore_permissions=True)

	si.db_set("cn_zatca_uuid", uuid_value)
	si.db_set("cn_zatca_xml_file", file_doc.name)
	return {"file_url": file_doc.file_url, "uuid": uuid_value}


def after_migrate():
	ensure_sales_invoice_fields()
