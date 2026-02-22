#!/usr/bin/env python3
"""Save kitty session layout (tabs, splits, cwds) for restoration on next launch."""
import json
import os
import subprocess
import sys

SESSION = os.path.expanduser("~/.config/kitty/last-session.kitty")


def kitty_ls():
    r = subprocess.run(["kitty", "@", "ls"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def get_cwd(win):
    for p in reversed(win.get("foreground_processes", [])):
        c = p.get("cwd")
        if c and os.path.isdir(c):
            return c
    return win.get("cwd") or os.path.expanduser("~")


def infer_split(prev, curr):
    """Same height = side by side (vsplit), same width = stacked (hsplit)."""
    if abs(prev.get("lines", 0) - curr.get("lines", 0)) <= 2:
        return "vsplit"
    if abs(prev.get("columns", 0) - curr.get("columns", 0)) <= 2:
        return "hsplit"
    return "vsplit"


def build(state):
    out = []
    first = True
    for ow in state:
        for tab in ow.get("tabs", []):
            wins = tab.get("windows", [])
            if not wins:
                continue
            if not first:
                out.append("")
            first = False
            layout = tab.get("layout", "splits")
            out.append(f"new_tab {tab.get('title', '')}")
            out.append(f"layout {layout}")
            for i, w in enumerate(wins):
                out.append(f"cd {get_cwd(w)}")
                if i == 0:
                    out.append("launch --cwd=current")
                elif layout == "splits":
                    out.append(f"launch --cwd=current --location={infer_split(wins[i - 1], w)}")
                else:
                    out.append("launch --cwd=current")
                if w.get("is_focused"):
                    out.append("focus")
    return "\n".join(out) + "\n" if out else None


if __name__ == "__main__":
    state = kitty_ls()
    if not state:
        sys.exit(1)
    content = build(state)
    if content:
        os.makedirs(os.path.dirname(SESSION), exist_ok=True)
        with open(SESSION, "w") as f:
            f.write(content)
