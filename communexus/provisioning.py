import subprocess
from collections.abc import Iterable


def _run(cmd: Iterable[str]):
	subprocess.check_call(list(cmd))


def create_site(site: str, admin_password: str | None = None):
	cmd = ["bench", "new-site", site]
	if admin_password:
		cmd += ["--admin-password", admin_password]
	_run(cmd)


def install_apps(site: str):
	_run(["bench", "--site", site, "install-app", "frappe"])
	_run(["bench", "--site", site, "install-app", "erpnext"])
	_run(["bench", "--site", site, "install-app", "communexus"])


def apply_ksa_defaults(site: str):
	_run(
		[
			"bench",
			"--site",
			site,
			"execute",
			"communexus.communexus_erp_360_app.setup.apply_ksa_defaults",
		]
	)


def provision(site: str, admin_password: str | None = None):
	create_site(site, admin_password=admin_password)
	install_apps(site)
	apply_ksa_defaults(site)
