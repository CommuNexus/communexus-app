import base64
import io
from datetime import datetime

import pyqrcode


def ensure_sales_invoice_fields():
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	create_custom_fields(
		{
			"Sales Invoice": [
				{
					"fieldname": "cn_zatca_qr",
					"label": "ZATCA QR (Base64 TLV)",
					"fieldtype": "Small Text",
					"read_only": 1,
					"insert_after": "posting_time",
				},
				{
					"fieldname": "cn_zatca_qr_svg",
					"label": "ZATCA QR SVG",
					"fieldtype": "Long Text",
					"read_only": 1,
					"insert_after": "cn_zatca_qr",
				},
			]
		},
		update=True,
	)


def _tlv(tag: int, value: str) -> bytes:
	encoded = value.encode("utf-8")
	return bytes([tag, len(encoded)]) + encoded


def build_zatca_payload(seller_name: str, vat_number: str, timestamp: datetime, total: float, vat: float) -> str:
	payload = b"".join(
		[
			_tlv(1, seller_name),
			_tlv(2, vat_number),
			_tlv(3, timestamp.isoformat()),
			_tlv(4, f"{total:.2f}"),
			_tlv(5, f"{vat:.2f}"),
		]
	)
	return base64.b64encode(payload).decode()


def _qr_svg_data_uri(data: str) -> str:
	qr = pyqrcode.create(data, error="M")
	buffer = io.StringIO()
	qr.svg(buffer, scale=4)
	svg_text = buffer.getvalue()
	return "data:image/svg+xml;base64," + base64.b64encode(svg_text.encode()).decode()


def generate_for_sales_invoice(doc) -> tuple[str | None, str | None]:
	try:
		import frappe
		from frappe.utils import get_datetime
	except ImportError as exc:  # pragma: no cover - requires frappe runtime
		raise RuntimeError("frappe is required to generate ZATCA QR") from exc

	company = doc.company
	if not company:
		return (None, None)

	company_doc = frappe.get_doc("Company", company)
	vat_number = (
		getattr(company_doc, "cn_vat_registration_no", None)
		or company_doc.get("tax_id")
		or company_doc.get("tax_id_number")
	)
	if not vat_number:
		return (None, None)

	seller_name = company_doc.company_name or company
	posting_dt = get_datetime(f"{doc.posting_date} {doc.posting_time or '00:00:00'}")
	total = float(doc.grand_total or 0)
	vat_amount = float(doc.total_taxes_and_charges or 0)

	payload = build_zatca_payload(seller_name, vat_number, posting_dt, total, vat_amount)
	svg = _qr_svg_data_uri(payload)
	return payload, svg


def update_sales_invoice_qr(doc, _):
	payload, svg = generate_for_sales_invoice(doc)
	if payload:
		doc.cn_zatca_qr = payload
	if svg:
		doc.cn_zatca_qr_svg = svg


def ensure_print_format():
	import frappe

	name = "CommuNexus Sales Invoice (ZATCA QR)"
	if frappe.db.exists("Print Format", name):
		return

	html = """
<div class="cn-zatca-qr" style="padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px;">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
      <h3 style="margin: 0;">Sales Invoice {{ doc.name }}</h3>
      <p style="margin: 0;">Customer: {{ doc.customer_name or doc.customer }}</p>
      <p style="margin: 0;">Grand Total: {{ doc.grand_total }} {{ doc.currency }}</p>
    </div>
    <div>
      {% set qr_svg = doc.cn_zatca_qr_svg or communexus_zatca_qr_svg(doc) %}
      {% if qr_svg %}
        <img src="{{ qr_svg }}" width="180" alt="ZATCA QR" />
      {% else %}
        <div style="color: #b91c1c; font-size: 12px;">ZATCA QR not available (missing company VAT).</div>
      {% endif %}
    </div>
  </div>
</div>
"""
	fmt = frappe.new_doc("Print Format")
	fmt.doc_type = "Sales Invoice"
	fmt.name = name
	fmt.module = "Communexus"
	fmt.custom_format = 1
	fmt.print_format_type = "Jinja"
	fmt.raw_printing = 0
	fmt.disabled = 0
	fmt.html = html
	fmt.insert(ignore_if_duplicate=True, ignore_permissions=True)


def communexus_zatca_qr_payload(doc):
	payload, _ = generate_for_sales_invoice(doc)
	return payload


def communexus_zatca_qr_svg(doc):
	_, svg = generate_for_sales_invoice(doc)
	return svg


def after_migrate():
	ensure_sales_invoice_fields()
	ensure_print_format()
