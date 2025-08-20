import argparse

def build_arg_parser() -> argparse.ArgumentParser:
	"""Buat argument parser untuk aplikasi."""
	parser = argparse.ArgumentParser(
		description="HPone Docker template manager - Modular Version",
		formatter_class=argparse.RawTextHelpFormatter,
	)
	sub = parser.add_subparsers(dest="command", required=True, title="Commands", metavar="COMMAND")

	# Check dependencies command
	p_check = sub.add_parser("check", help="Check dependencies")

	# Import command
	p_import = sub.add_parser("import", help="Import template dan generate .env untuk tool")
	p_import.add_argument("tool", nargs="?", help="Nama tool (sesuai nama file YAML di folder tools/)")
	p_import.add_argument("--all", action="store_true", help="Import semua tool yang enabled")
	p_import.add_argument("--force", action="store_true", help="Overwrite folder docker/<tool> jika sudah ada")
	
	# Update command
	p_update = sub.add_parser("update", help="Update semua tool yang sudah diimport (setara import --force)")

	# List command
	p_list = sub.add_parser("list", help="List tools berdasarkan YAML di folder tools/")
	p_list.add_argument("-a", action="store_true", help="Tampilkan detail lengkap (deskripsi dan ports)")

	# Status command (running only)
	p_status = sub.add_parser("status", help="Tampilkan port mapping tools yang sedang running (HOST -> CONTAINER)")
	
	# Remove command
	p_remove = sub.add_parser("remove", help="Hapus folder docker/<tool>")
	p_remove.add_argument("tool", nargs="?", help="Nama tool yang akan dihapus")
	p_remove.add_argument("--all", action="store_true", help="Hapus semua tool yang sudah diimport")

	# Inspect command
	p_inspect = sub.add_parser("inspect", help="Tampilkan informasi detail config dari satu tool")
	p_inspect.add_argument("tool", help="Nama tool yang akan diinspect")

	# Enable command
	p_enable = sub.add_parser("enable", help="Enable tool pada tools/<tool>.yml (set enabled: true)")
	p_enable.add_argument("tool", help="Nama tool yang akan di-enable")

	# Disable command
	p_disable = sub.add_parser("disable", help="Disable tool pada tools/<tool>.yml (set enabled: false)")
	p_disable.add_argument("tool", help="Nama tool yang akan di-disable")

	# Up command
	p_up = sub.add_parser("up", help="docker compose up -d untuk satu tool atau semua tool yang enabled")
	group_up = p_up.add_mutually_exclusive_group(required=True)
	group_up.add_argument("tool", nargs="?", help="Nama tool. Jika tidak diberikan, gunakan --all")
	group_up.add_argument("--all", action="store_true", help="Jalankan untuk semua tool yang enabled dan sudah diimport")
	p_up.add_argument("--force", action="store_true", help="Force up tool meskipun tidak enabled (hanya untuk single tool)")

	# Down command
	p_down = sub.add_parser("down", help="docker compose down untuk satu tool atau semua tool yang diimport")
	group_down = p_down.add_mutually_exclusive_group(required=True)
	group_down.add_argument("tool", nargs="?", help="Nama tool. Jika tidak diberikan, gunakan --all")
	group_down.add_argument("--all", action="store_true", help="Jalankan untuk semua tool yang diimport")

	return parser


def format_full_help(parser: argparse.ArgumentParser) -> str:
	"""Cetak help komprehensif dengan layout ringkas. Menghindari copy panjang."""
	prog = parser.prog
	desc = parser.description or ""

	# Kumpulkan subparsers
	subparsers_actions = [
		action for action in getattr(parser, "_actions", [])
		if isinstance(action, argparse._SubParsersAction)
	]
	if not subparsers_actions:
		# Fallback standar
		return parser.format_help()

	sub_action = subparsers_actions[0]

	# Peta nama -> subparser
	choices = sub_action.choices  # preserves insertion order in modern Python

	# Peta nama -> short help (mengambil dari help subparser)
	short_help_map = {
		choice: (sub_action.choices[choice].description or act.help or "")
		for act in sub_action._get_subactions()
		for choice in [act.dest]
	}

	# Urutan tampilan yang diinginkan; sisanya mengikuti urutan asli
	desired_order = [
		"check", "import", "update", "list", "status",
		"remove", "inspect", "enable", "disable", "up", "down",
	]
	names_in_choice = list(choices.keys())
	ordered_names = [n for n in desired_order if n in names_in_choice] + [
		n for n in names_in_choice if n not in desired_order
	]

	# Bangun bagian Commands dengan alignment
	name_width = max((len(n) for n in ordered_names), default=0)
	cmd_lines = []
	for name in ordered_names:
		summary = short_help_map.get(name) or (choices[name].description or "")
		cmd_lines.append(f"  {name.ljust(name_width)}  {summary}".rstrip())

	# Helper: generate ringkas usage dan opsi per subparser
	def format_detail_for(name: str) -> str:
		sp = choices[name]
		# Ringkas usage dari objek subparser
		tokens = []
		option_entries = []  # (label, help)
		max_label_len = 0
		for act in getattr(sp, "_actions", []):
			# Skip builtin help action
			if isinstance(act, argparse._HelpAction):
				continue
			label = None
			help_text = (act.help or "").strip()
			if getattr(act, "option_strings", None):
				# Pilih long option jika ada, kalau tidak pakai yang pertama
				longs = [opt for opt in act.option_strings if opt.startswith("--")]
				label = longs[0] if longs else act.option_strings[0]
				# Flag optional
				token = f"[{label}]"
				tokens.append(token)
			else:
				# Positional
				metavar = act.metavar or act.dest
				display = f"<{metavar}>"
				# Optional jika nargs mengizinkan kosong
				optional = str(getattr(act, "nargs", "")) in ("?", "*", None)
				token = f"[{display}]" if optional else f"{display}"
				tokens.append(token)
				label = display
			if label:
				max_label_len = max(max_label_len, len(label))
				if help_text:
					option_entries.append((label, help_text))

		# Susun bagian detail
		lines = []
		if tokens:
			# Hilangkan duplikasi token sambil mempertahankan urutan
			seen = set()
			uniq_tokens = []
			for t in tokens:
				if t in seen:
					continue
				seen.add(t)
				uniq_tokens.append(t)
			lines.append(f"  {name} " + " ".join(uniq_tokens))
		else:
			lines.append(f"  {name}")

		if not option_entries:
			lines.append("    No options.")
		else:
			pad = max_label_len
			for label, help_text in option_entries:
				lines.append(f"    {label.ljust(pad)}  {help_text}")

		return "\n".join(lines)

	# Bangun bagian Detailed Commands
	details_sections = [format_detail_for(n) for n in ordered_names]

	# Rangkai semua bagian
	out_lines = []
	out_lines.append("Usage:\n  {} [COMMAND] [OPTIONS]".format(prog))
	if desc:
		out_lines.append("\n{}".format(desc))
	out_lines.append("\nCommands:")
	out_lines.extend(cmd_lines)
	out_lines.append("\nDetailed Commands:")
	out_lines.extend(details_sections)

	return "\n".join(out_lines) + "\n"
