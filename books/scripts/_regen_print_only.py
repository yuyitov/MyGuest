#!/usr/bin/env python3
"""Regenerates print.html for all 4 demos without touching web pages."""
import sys
import os
import json
import importlib

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

DEMO_SCRIPTS = [
    "_generate_demo",
    "_generate_demo_classic",
    "_generate_demo_cozy",
    "_generate_demo_city",
]

for demo_name in DEMO_SCRIPTS:
    print(f"\n=== {demo_name} ===")
    # Load PAYLOAD from demo script without executing it
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        demo_name, os.path.join(script_dir, demo_name + ".py")
    )
    mod = importlib.util.module_from_spec(spec)
    # Stub out side-effect modules before exec
    sys.modules.setdefault("generate_villa", type(sys)("generate_villa"))
    sys.modules.setdefault("build_print_pdf", type(sys)("build_print_pdf"))

    # Read PAYLOAD directly using exec in isolated namespace
    src = open(os.path.join(script_dir, demo_name + ".py"), encoding="utf-8").read()
    ns = {"__file__": os.path.join(script_dir, demo_name + ".py")}
    # Only exec up to the point where imports start executing
    lines = src.splitlines()
    payload_lines = []
    in_payload = False
    for line in lines:
        if line.strip().startswith("PAYLOAD"):
            in_payload = True
        if in_payload:
            payload_lines.append(line)
            # Stop after the closing brace of PAYLOAD
            if line.strip() == "}" and not line.startswith(" ") and not line.startswith("\t"):
                break
    exec("\n".join(payload_lines), ns)
    payload = ns["PAYLOAD"]

    json_str = json.dumps(payload)
    sys.argv = ["", json_str]

    # Remove cached build_print_pdf so it reloads fresh
    if "build_print_pdf" in sys.modules:
        del sys.modules["build_print_pdf"]

    import build_print_pdf
    build_print_pdf.main()

print("\nAll print.html files regenerated.")
