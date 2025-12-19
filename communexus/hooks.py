app_name = "communexus"
app_title = "CommuNexus ERP-360"
app_publisher = "CommuNexus"
app_description = "Branding, KSA, and ZATCA features for CommuNexus ERP-360"
app_email = "ops@communexus.com"
app_license = "gpl-3.0"
app_logo_url = "/assets/communexus/branding/logo-horizontal.png"
brand_html = "CommuNexus ERP-360"
website_context = {
	"brand_html": "CommuNexus ERP-360",
	"favicon": "/assets/communexus/branding/favicon-32.png",
	"splash_image": "/assets/communexus/branding/logo-stacked.png",
}
after_migrate = "communexus.communexus_erp_360_app.setup.after_migrate"

# Includes in <head>
# ------------------
app_include_css = "/assets/communexus/css/branding.css"
app_include_js = "/assets/communexus/js/branding.js"

# include js in doctype views
doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}

# Jinja
# ----------
jinja = {
	"methods": [
		"communexus.communexus_erp_360_app.zatca_qr.communexus_zatca_qr_payload",
		"communexus.communexus_erp_360_app.zatca_qr.communexus_zatca_qr_svg",
	],
}

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
	"Company": {
		"validate": "communexus.communexus_erp_360_app.ksa.validate_company",
	},
	"Sales Invoice": {
		"validate": "communexus.communexus_erp_360_app.zatca_qr.update_sales_invoice_qr",
		"on_submit": "communexus.communexus_erp_360_app.zatca_qr.update_sales_invoice_qr",
	},
}
