frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Export ZATCA XML"), () => {
				frappe.call({
					method: "communexus.communexus_erp_360_app.zatca_xml.export_zatca_xml",
					args: { name: frm.doc.name },
					freeze: true,
					freeze_message: __("Generating ZATCA XML..."),
					callback: (r) => {
						if (r.message) {
							const { file_url, uuid } = r.message;
							frappe.msgprint({
								title: __("ZATCA XML Exported"),
								message: __(
									"File: {0}<br>UUID: {1}",
									[
										`<a href="${file_url}" target="_blank">${file_url}</a>`,
										uuid,
									],
								),
								indicator: "green",
							});
							frm.reload_doc();
						}
					},
				});
			});
		}
	},
});
