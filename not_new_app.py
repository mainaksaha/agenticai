"""prompt_pulse.py – PromptPulse (multi-channel + tool-tips)

Streamlit UI where users subscribe prompts, pick **multiple** notification
channels (Web, Teams, Email), and see icon + label pairs with tool-tips on the
schedule board.

• Top-left title now reads **📈 PromptPulse** (pulse graph icon).
• Internal `page_title` set to *PromptPulse* so the browser tab matches.

Run with:

    streamlit run prompt_pulse.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, List, Dict

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

RUN_INTERVAL: timedelta = timedelta(seconds=30)  # how often prompts fire

CHANNEL_OPTIONS: List[str] = ["Web", "Teams", "Email"]
CHANNEL_ICONS: Dict[str, str] = {"Web": "🌐", "Teams": "💬", "Email": "📧"}

# HTML snippet with tooltip + label (e.g. <span title="Web">🌐 Web</span>)
CHANNEL_HTML: Dict[str, str] = {
    ch: f"<span title='{ch}'>{icon} {ch}</span>" for ch, icon in CHANNEL_ICONS.items()
}

PRE_SAVED_PROMPTS: List[dict] = [
    {
        "text": "Notify me if any of my client having more than 10k in cash.",
        "channels": ["Web"],
    },
    {
        "text": "Notify me if any of my client selling NVDA and age less than 40.",
        "channels": ["Email", "Web"],
    },
    {
        "text": "Notify me if any portfolio lost more than 5% today.",
        "channels": ["Teams"],
    },
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
        st.warning("Installed Streamlit lacks programmatic rerun support; auto-refresh disabled.")

# ─────────────────────────────────────────────────────────────────────────────
# State initialisation
# ─────────────────────────────────────────────────────────────────────────────

def _initialise_state() -> None:
    defaults = {
        "prompts": [],  # each: {text:str, channels:List[str], last_run:datetime}
        "notifications": [],
        "new_notif": False,
        "show_panel": False,
        "prompt_input": "",
        "notif_channels_selected": [CHANNEL_OPTIONS[0]],
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    if not st.session_state.prompts:
        now = datetime.utcnow() - RUN_INTERVAL
        for item in PRE_SAVED_PROMPTS:
            st.session_state.prompts.append({
                "text": item["text"],
                "channels": item["channels"],
                "last_run": now,
            })

# ─────────────────────────────────────────────────────────────────────────────
# Scheduler simulation
# ─────────────────────────────────────────────────────────────────────────────

def _maybe_run_prompts() -> None:
    now = datetime.utcnow()
    ran_any = False
    for p in st.session_state.prompts:
        if now - p["last_run"] >= RUN_INTERVAL:
            p["last_run"] = now
            ts = now.strftime("%H:%M:%S")
            chan_disp = ", ".join(CHANNEL_ICONS[c] + " " + c for c in p["channels"])
            st.session_state.notifications.append(
                f"[{chan_disp}] Prompt triggered: '{p['text']}' @ {ts}"
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
    channels = st.session_state.notif_channels_selected
    if text and channels:
        st.session_state.prompts.append({
            "text": text,
            "channels": channels,
            "last_run": datetime.utcnow(),
        })
        st.session_state.prompt_input = ""


def _toggle_bell() -> None:
    st.session_state.show_panel = not st.session_state.show_panel
    st.session_state.new_notif = False

# ─────────────────────────────────────────────────────────────────────────────
# UI builders
# ─────────────────────────────────────────────────────────────────────────────

def _top_bar() -> None:
    col_title, col_bell = st.columns([0.94, 0.06])
    with col_title:
        st.markdown("## 📈 PromptPulse")
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
                st.write("No notifications yet …")


def _main_pane() -> None:
    st.subheader("🗓️ Prompt Schedule")
    if st.session_state.prompts:
        for p in st.session_state.prompts:
            next_run = p["last_run"] + RUN_INTERVAL
            icons_html = " ".join(CHANNEL_HTML[c] for c in p["channels"])
            st.markdown(
                f"• **{p['text']}** {icons_html}  \n"
                f"  ↳ next check: {next_run.strftime('%H:%M:%S')} UTC",
                unsafe_allow_html=True,
            )
    else:
        st.write("No prompts yet.")

    st.divider()

    st.multiselect(
        "Notification channels",
        options=CHANNEL_OPTIONS,
        default=st.session_state.notif_channels_selected,
        key="notif_channels_selected",
    )
    st.text_input(
        "Add a new prompt",
        key="prompt_input",
        on_change=_add_prompt,
        placeholder="Describe the condition to monitor …",
    )

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def _build_ui() -> None:
    st.set_page_config(page_title="PromptPulse", layout="wide")
    _initialise_state()
    _maybe_run_prompts()

    _top_bar()
    st.divider()
    _main_pane()


def main() -> None:  # pragma: no cover
    _build_ui()


if __name__ == "__main__":
    main()
