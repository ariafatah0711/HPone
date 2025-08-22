import argparse

def build_arg_parser() -> argparse.ArgumentParser:
	"""Build the argument parser for the application."""
	parser = argparse.ArgumentParser(
		description="HPone Docker template manager - Modular Version",
		formatter_class=argparse.RawTextHelpFormatter,
	)
	sub = parser.add_subparsers(dest="command", required=True, title="Commands", metavar="COMMAND")

	# Check dependencies command
	p_check = sub.add_parser("check", help="Check dependencies")

	# Import command (only show when ALWAYS_IMPORT=false)
	try:
		from config import ALWAYS_IMPORT
		show_import_commands = not ALWAYS_IMPORT
	except ImportError:
		show_import_commands = False

	if show_import_commands:
		# Import command
		p_import = sub.add_parser("import", help="Import template and generate .env for the tool")
		p_import.add_argument("tool", nargs="?", help="Tool name (matches YAML filename in tools/)")
		p_import.add_argument("--all", action="store_true", help="Import all enabled tools")
		p_import.add_argument("--force", action="store_true", help="Overwrite docker/<tool> if it already exists")

		# Update command
		p_update = sub.add_parser("update", help="Update all imported tools (equivalent to import --force)")

	# List command
	p_list = sub.add_parser("list", help="List tools based on YAML files in tools/")
	p_list.add_argument("-a", action="store_true", help="Show full details (description and ports)")

	# Status command (running only)
	p_status = sub.add_parser("status", help="Show port mappings of running tools (HOST -> CONTAINER)")

	# Inspect command
	p_inspect = sub.add_parser("inspect", help="Show detailed configuration information for one tool")
	p_inspect.add_argument("tool", help="Tool name to inspect")

	# Enable command
	p_enable = sub.add_parser("enable", help="Enable tool in tools/<tool>.yml (set enabled: true)")
	p_enable.add_argument("tool", help="Tool name to enable")

	# Disable command
	p_disable = sub.add_parser("disable", help="Disable tool in tools/<tool>.yml (set enabled: false)")
	p_disable.add_argument("tool", help="Tool name to disable")

	# Up command
	p_up = sub.add_parser("up", help="docker compose up -d for one tool or all enabled tools")
	group_up = p_up.add_mutually_exclusive_group(required=True)
	group_up.add_argument("tool", nargs="?", help="Tool name. If omitted, use --all")
	group_up.add_argument("--all", action="store_true", help="Run for all enabled and imported tools")

	# Only show --update option when ALWAYS_IMPORT=false
	if show_import_commands:
		p_up.add_argument("--update", action="store_true", help="Update templates before starting")

	p_up.add_argument("--force", action="store_true", help="Force start even if not enabled (single tool only)")

	# Down command
	p_down = sub.add_parser("down", help="docker compose down for one tool or all imported tools")
	group_down = p_down.add_mutually_exclusive_group(required=True)
	group_down.add_argument("tool", nargs="?", help="Tool name. If omitted, use --all")
	group_down.add_argument("--all", action="store_true", help="Run for all imported tools")

	# Shell command
	p_shell = sub.add_parser("shell", help="Open shell (bash/sh) in running container")
	p_shell.add_argument("tool", help="Tool name to open shell in")

	# Logs command
	p_logs = sub.add_parser("logs", help="Interactive logs viewer for containers and mounted data")
	p_logs.add_argument("tool", help="Tool name to view logs for")

	# Clean command
	p_clean = sub.add_parser("clean", help="Stop (down) then delete directory docker/<tool>")
	p_clean.add_argument("tool", nargs="?", help="Tool name to clean")
	p_clean.add_argument("--all", action="store_true", help="Clean all imported tools")
	p_clean.add_argument("--data", action="store_true", help="Also remove mounted data under data/<tool>")
	# Extra docker compose down options
	p_clean.add_argument("--image", action="store_true", help="Also remove images (docker compose down --rmi local)")
	p_clean.add_argument("--volume", action="store_true", help="Also remove volumes (docker compose down -v)")

	return parser


def format_full_help(parser: argparse.ArgumentParser) -> str:
	"""Generate comprehensive help output with a compact layout."""
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
		"inspect", "enable", "disable", "up", "down", "shell", "logs", "clean"
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
