import base64
from datetime import datetime

from communexus.communexus_erp_360_app import zatca_qr


def test_build_zatca_payload_tlv_order_and_values():
	payload = zatca_qr.build_zatca_payload(
		"CommuNexus ERP-360",
		"123456789012345",
		datetime(2024, 1, 2, 3, 4, 5),
		115.0,
		15.0,
	)
	data = base64.b64decode(payload)
	# TLV: tag, length, value
	assert data[0] == 1
	seller_len = data[1]
	assert data[2 : 2 + seller_len] == b"CommuNexus ERP-360"

	vat_tag_index = 2 + seller_len
	assert data[vat_tag_index] == 2
	vat_len = data[vat_tag_index + 1]
	assert data[vat_tag_index + 2 : vat_tag_index + 2 + vat_len] == b"123456789012345"

	ts_tag_index = vat_tag_index + 2 + vat_len
	assert data[ts_tag_index] == 3
	ts_len = data[ts_tag_index + 1]
	assert data[ts_tag_index + 2 : ts_tag_index + 2 + ts_len] == b"2024-01-02T03:04:05"

	total_tag_index = ts_tag_index + 2 + ts_len
	assert data[total_tag_index] == 4
	total_len = data[total_tag_index + 1]
	assert data[total_tag_index + 2 : total_tag_index + 2 + total_len] == b"115.00"

	vat_total_index = total_tag_index + 2 + total_len
	assert data[vat_total_index] == 5
	vat_total_len = data[vat_total_index + 1]
	assert data[vat_total_index + 2 : vat_total_index + 2 + vat_total_len] == b"15.00"
