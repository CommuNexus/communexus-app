(() => {
	const brandTitle = "CommuNexus ERP-360";

	const setDocumentTitle = () => {
		if (!document.title.includes(brandTitle)) {
			document.title = `${brandTitle} | ${document.title}`;
		}
	};

	const addHelpLink = () => {
		const $menu = $(".dropdown-help #help-links");
		if (!$menu.length || $menu.find("[data-communexus-legal]").length) return;

		$(
			"<a>",
			{
				href: "/legal",
				class: "dropdown-item",
				text: __("Legal / Open Source Notices"),
				target: "_blank",
				"data-communexus-legal": 1,
			},
		).prependTo($menu);
	};

	const init = () => {
		setDocumentTitle();
		addHelpLink();
	};

	if (window.frappe) {
		frappe.after_app_boot = () => {
			init();
			$(document).on("page-change", init);
		};
	}
})();
