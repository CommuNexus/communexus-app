import xml.etree.ElementTree as ET

from communexus.communexus_erp_360_app import zatca_xml


class StubCompany:
	def __init__(self):
		self.cn_vat_registration_no = "123456789012345"
		self.tax_id = None
		self.tax_id_number = None
		self.company_name = "CommuNexus ERP-360"

	def get(self, key):
		return getattr(self, key, None)


class StubItem:
	def __init__(self, idx, qty, net_amount, rate):
		self.idx = idx
		self.qty = qty
		self.net_amount = net_amount
		self.rate = rate


class StubSalesInvoice:
	def __init__(self):
		self.company = "CommuNexus"
		self.customer = "Customer A"
		self.customer_name = "Customer A"
		self.tax_id = "987654321000003"
		self.posting_date = "2024-01-02"
		self.posting_time = "03:04:05"
		self.currency = "SAR"
		self.net_total = 100.0
		self.grand_total = 115.0
		self.total_taxes_and_charges = 15.0
		self.name = "SINV-0001"
		self.items = [StubItem(1, 2, 100.0, 50.0)]


def test_build_xml_produces_basic_ubl():
	si = StubSalesInvoice()
	company = StubCompany()
	xml_bytes, uuid_value = zatca_xml.build_xml(si, company_doc=company)
	root = ET.fromstring(xml_bytes)
	assert "Invoice" in root.tag
	ids = [el.text for el in root.findall(".//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")]
	assert "SINV-0001" in ids
	assert uuid_value
