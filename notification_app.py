"""notification_app.py – Prompt Subscription App (single‑pane)

Streamlit UI where users subscribe prompts that run on a schedule.
• Main pane lists each prompt and its next run time (runs every 30 seconds in
  this demo).  Users can add new prompts via an input at the bottom.
• A 🔔 bell lights up when unseen notifications arrive; click it to view them.
• Prompts auto‑"run" every 30 s and generate dummy notifications referencing
  the prompt text.

Run with:

    streamlit run notification_app.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, List

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

RUN_INTERVAL: timedelta = timedelta(seconds=30)  # how often prompts fire

PRE_SAVED_PROMPTS: List[str] = [
    "Notify me if any of my client having more than 10k in cash.",
    "Notify me if any of my client selling NVDA and age less than 40.",
    "Notify me if any portfolio lost more than 5% today.",
]

# ─────────────────────────────────────────────────────────────────────────────
# Rerun shim (handles Streamlit version differences)
# ─────────────────────────────────────────────────────────────────────────────

if hasattr(st, "experimental_rerun"):
    _trigger_rerun: Callable[[], None] = st.experimental_rerun  # type: ignore[attr-defined]
elif hasattr(st, "rerun"):
    _trigger_rerun = st.rerun  # type: ignore[attr-defined]
else:  # pragma: no cover
    def _trigger_rerun() -> None:  # noqa: D401 – noop fallback
        st.warning("Installed Streamlit lacks programmatic rerun support; auto‑refresh disabled.")

# ─────────────────────────────────────────────────────────────────────────────
# Session‑state helpers
# ─────────────────────────────────────────────────────────────────────────────

def _initialise_state() -> None:
    """Populate *st.session_state* with default keys."""

    defaults = {
        "prompts": [],
        "notifications": [],
        "new_notif": False,
        "show_panel": False,
        "prompt_input": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    if not st.session_state.prompts:
        now = datetime.utcnow() - RUN_INTERVAL  # ensure immediate first run
        for text in PRE_SAVED_PROMPTS:
            st.session_state.prompts.append({"text": text, "last_run": now})


# ─────────────────────────────────────────────────────────────────────────────
# Prompt scheduler / runner
# ─────────────────────────────────────────────────────────────────────────────

def _maybe_run_prompts() -> None:
    """Simulate prompt execution on schedule, append notifications."""

    now = datetime.utcnow()
    ran_any = False
    for p in st.session_state.prompts:
        if now - p["last_run"] >= RUN_INTERVAL:
            p["last_run"] = now
            timestamp = now.strftime("%H:%M:%S")
            st.session_state.notifications.append(
                f"Prompt triggered: '{p['text']}' @ {timestamp}"
            )
            ran_any = True
    if ran_any:
        st.session_state.new_notif = True
        _trigger_rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────────────────────────────────────

def _add_prompt() -> None:
    text = st.session_state.prompt_input.strip()
    if text:
        st.session_state.prompts.append({"text": text, "last_run": datetime.utcnow()})
        st.session_state.prompt_input = ""


def _toggle_bell() -> None:
    st.session_state.show_panel = not st.session_state.show_panel
    st.session_state.new_notif = False


# ─────────────────────────────────────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────────────────────────────────────

def _top_bar() -> None:
    col_title, col_bell = st.columns([0.94, 0.06])
    with col_title:
        st.markdown("## 📝 Prompt Subscription App")
    with col_bell:
        bell_label = "🔔" if not st.session_state.new_notif else "🔔 (new)"
        st.button(bell_label, key="bell", on_click=_toggle_bell)

    if st.session_state.show_panel:
        with st.container(border=True):
            st.markdown("### Notifications")
            if st.session_state.notifications:
                for idx, note in enumerate(reversed(st.session_state.notifications), 1):
                    st.write(f"{idx}. {note}")
            else:
                st.write("No notifications yet …")


def _main_pane() -> None:
    st.subheader("🗓️ Prompt Schedule")
    if st.session_state.prompts:
        for p in st.session_state.prompts:
            next_run = p["last_run"] + RUN_INTERVAL
            st.write(f"• **{p['text']}**\n  ↳ next check: {next_run.strftime('%H:%M:%S')} UTC")
    else:
        st.write("No prompts yet.")

    st.divider()
    st.text_input(
        "Add a new prompt", key="prompt_input", on_change=_add_prompt, placeholder="Describe the condition to monitor …"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def _build_ui() -> None:
    st.set_page_config(page_title="Prompt Subscription App", layout="wide")
    _initialise_state()
    _maybe_run_prompts()

    _top_bar()
    st.divider()
    _main_pane()


def main() -> None:  # pragma: no cover
    _build_ui()


if __name__ == "__main__":
    main()
