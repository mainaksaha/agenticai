"""
Streamlit UI for Reconciliation Agent System - HIL Interface
Human-in-the-Loop interface for reviewing agent decisions
"""
import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.workflow import ReconciliationOrchestrator
from shared.schemas import ActionType
from mcp.tools.workflow_tools import TICKETS, FEEDBACK_LOG, get_feedback_stats

# Page config
st.set_page_config(
    page_title="Reconciliation Review System (v1)",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = ReconciliationOrchestrator()
if 'processed_cases' not in st.session_state:
    st.session_state.processed_cases = []
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = None
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .status-auto {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .status-hil {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .status-escalate {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .agent-stage {
        background-color: #e7f3ff;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🔍 Recon System")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "📝 Review Queue", "📈 Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Process new breaks
    st.subheader("Process Breaks")
    num_breaks = st.number_input("Number of breaks", min_value=1, max_value=20, value=5)
    
    if st.button("🔄 Process Breaks", use_container_width=True):
        with st.spinner("Processing breaks..."):
            result = st.session_state.orchestrator.process_multiple_breaks(limit=num_breaks)
            st.session_state.processed_cases.extend(result.get('results', []))
            st.session_state.refresh_counter += 1
            st.success(f"Processed {result.get('total_processed', 0)} breaks!")
            st.rerun()

# Main content
if page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Reconciliation Dashboard</div>', unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    total_cases = len(st.session_state.processed_cases)
    auto_resolved = sum(1 for c in st.session_state.processed_cases 
                       if c.get('case', {}).get('decision', {}).get('action') == ActionType.AUTO_RESOLVE)
    hil_review = sum(1 for c in st.session_state.processed_cases 
                     if c.get('case', {}).get('decision', {}).get('action') == ActionType.HIL_REVIEW)
    escalated = sum(1 for c in st.session_state.processed_cases 
                    if c.get('case', {}).get('decision', {}).get('action') == ActionType.ESCALATE)
    
    with col1:
        st.metric("Total Cases", total_cases)
    with col2:
        st.metric("Auto-Resolved", auto_resolved, delta=f"{(auto_resolved/max(total_cases,1)*100):.0f}%")
    with col3:
        st.metric("Pending Review", hil_review, delta="Needs Action" if hil_review > 0 else "None")
    with col4:
        st.metric("Escalated", escalated, delta="High Priority" if escalated > 0 else "None")
    
    st.markdown("---")
    
    # Recent cases table
    st.subheader("Recent Cases")
    
    if total_cases == 0:
        st.info("👈 Use the sidebar to process breaks and populate the dashboard")
    else:
        # Create table data
        table_data = []
        for case in st.session_state.processed_cases[-20:]:  # Last 20 cases
            decision = case.get('case', {}).get('decision', {})
            break_data = case.get('case', {}).get('break_data', {})
            
            # Calculate amount difference
            system_a = break_data.get('system_a', {})
            system_b = break_data.get('system_b', {})
            amount_diff = abs(system_a.get('amount', 0) - system_b.get('amount', 0))
            
            table_data.append({
                'Break ID': break_data.get('break_id', 'N/A'),
                'Type': break_data.get('break_type', 'N/A'),
                'Instrument': break_data.get('entities', {}).get('instrument', 'N/A'),
                'Amount Diff': f"${amount_diff:,.2f}",
                'Risk Score': f"{decision.get('risk_score', 0):.2f}",
                'Confidence': f"{decision.get('confidence', 0):.0%}",
                'Decision': decision.get('action', 'N/A'),
                'Status': case.get('final_status', 'N/A')
            })
        
        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

elif page == "📝 Review Queue":
    st.markdown('<div class="main-header">📝 Human Review Queue</div>', unsafe_allow_html=True)
    
    # Filter for HIL cases
    hil_cases = [c for c in st.session_state.processed_cases 
                 if c.get('case', {}).get('decision', {}).get('action') == ActionType.HIL_REVIEW]
    
    if len(hil_cases) == 0:
        st.info("🎉 No cases pending review! All breaks are either auto-resolved or escalated.")
    else:
        st.success(f"📋 {len(hil_cases)} cases require your review")
        
        # Case selector
        case_options = [f"{c.get('break_id', 'Unknown')} - {c.get('case', {}).get('break_data', {}).get('entities', {}).get('instrument', 'N/A')}" 
                       for c in hil_cases]
        
        selected_idx = st.selectbox(
            "Select a case to review",
            range(len(case_options)),
            format_func=lambda i: case_options[i]
        )
        
        case = hil_cases[selected_idx]
        break_data = case.get('case', {}).get('break_data', {})
        decision = case.get('case', {}).get('decision', {})
        enriched = case.get('case', {}).get('enriched_data', {})
        rules = case.get('case', {}).get('rules_evaluation', {})
        ml_insights = case.get('case', {}).get('ml_insights', {})
        
        st.markdown("---")
        
        # Case details in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Overview", 
            "📊 Data Comparison", 
            "🤖 Agent Analysis", 
            "📈 Risk Assessment",
            "✅ Take Action"
        ])
        
        with tab1:
            st.subheader("Break Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Break Details**")
                st.write(f"**Break ID:** {break_data.get('break_id')}")
                st.write(f"**Type:** {break_data.get('break_type')}")
                st.write(f"**Instrument:** {break_data.get('entities', {}).get('instrument')}")
                st.write(f"**Account:** {break_data.get('entities', {}).get('account')}")
                st.write(f"**Broker:** {break_data.get('entities', {}).get('broker')}")
            
            with col2:
                st.write("**Agent Recommendation**")
                st.write(f"**Action:** {decision.get('action')}")
                st.write(f"**Confidence:** {decision.get('confidence', 0):.0%}")
                st.write(f"**Risk Score:** {decision.get('risk_score', 0):.2f}")
                st.write(f"**Requires HIL:** {'Yes' if decision.get('requires_hil') else 'No'}")
            
            st.markdown("---")
            st.write("**Explanation:**")
            st.info(decision.get('explanation', 'No explanation provided'))
        
        with tab2:
            st.subheader("System Data Comparison")
            
            col1, col2 = st.columns(2)
            
            system_a = break_data.get('system_a', {})
            system_b = break_data.get('system_b', {})
            
            with col1:
                st.write("**System A (OMS)**")
                st.json({
                    'system_name': system_a.get('system_name'),
                    'quantity': system_a.get('quantity'),
                    'amount': system_a.get('amount'),
                    'price': system_a.get('price'),
                    'currency': system_a.get('currency')
                })
            
            with col2:
                st.write("**System B (Trade Capture)**")
                st.json({
                    'system_name': system_b.get('system_name'),
                    'quantity': system_b.get('quantity'),
                    'amount': system_b.get('amount'),
                    'price': system_b.get('price'),
                    'currency': system_b.get('currency')
                })
            
            st.markdown("---")
            st.subheader("Differences")
            
            qty_diff = abs(system_a.get('quantity', 0) - system_b.get('quantity', 0))
            amt_diff = abs(system_a.get('amount', 0) - system_b.get('amount', 0))
            price_diff = abs(system_a.get('price', 0) - system_b.get('price', 0))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Quantity Difference", f"{qty_diff:.2f}")
            with col2:
                st.metric("Amount Difference", f"${amt_diff:,.2f}")
            with col3:
                st.metric("Price Difference", f"${price_diff:.2f}")
        
        with tab3:
            st.subheader("Agent Analysis Pipeline")
            
            # Stage 1: Ingestion
            with st.expander("✅ Stage 1: Break Ingestion", expanded=False):
                ingestion = case.get('stages', {}).get('ingestion', {})
                st.write(f"**Status:** {ingestion.get('status')}")
                if ingestion.get('validation'):
                    st.json(ingestion.get('validation'))
            
            # Stage 2: Enrichment
            with st.expander("✅ Stage 2: Data Enrichment", expanded=False):
                enrichment = case.get('stages', {}).get('enrichment', {})
                st.write(f"**Sources Fetched:** {enrichment.get('sources_fetched', 0)}")
                st.write(f"**Successful:** {enrichment.get('sources_successful', 0)}")
                
                if enriched:
                    for source, data in enriched.items():
                        if not isinstance(data, dict) or 'error' not in data:
                            st.write(f"✓ {source}")
            
            # Stage 3: Matching
            with st.expander("✅ Stage 3: Matching & Correlation", expanded=False):
                matching = case.get('stages', {}).get('matching', {})
                st.write(f"**Candidates Found:** {matching.get('num_candidates', 0)}")
                
                candidates = matching.get('match_candidates', [])
                if candidates:
                    for i, cand in enumerate(candidates, 1):
                        st.write(f"**Candidate {i}:** {cand.get('source')} - Similarity: {cand.get('similarity_score', 0):.2%}")
            
            # Stage 4: Rules
            with st.expander("✅ Stage 4: Rules & Tolerance", expanded=False):
                st.write(f"**Within Tolerance:** {rules.get('within_tolerance', False)}")
                st.write(f"**Rules Applied:** {len(rules.get('rules_applied', []))}")
                st.write(f"**Passed:** {len(rules.get('passed_rules', []))}")
                st.write(f"**Failed:** {len(rules.get('failed_rules', []))}")
                
                if rules.get('tolerance_checks'):
                    st.json(rules.get('tolerance_checks'))
            
            # Stage 5: Pattern
            with st.expander("✅ Stage 5: Pattern Intelligence", expanded=True):
                st.write(f"**Root Cause:** {ml_insights.get('probable_root_cause', 'Unknown')}")
                st.write(f"**Confidence:** {ml_insights.get('confidence', 0):.0%}")
                st.write(f"**Explanation:** {ml_insights.get('explanation', 'N/A')}")
                
                pattern_result = case.get('stages', {}).get('pattern', {})
                fix = pattern_result.get('fix_suggestion', {})
                if fix:
                    st.write(f"**Suggested Fix:** {fix.get('action')}")
                    st.write(f"**Description:** {fix.get('description')}")
            
            # Stage 6: Decision
            with st.expander("✅ Stage 6: Decision Making", expanded=True):
                st.write(f"**Final Action:** {decision.get('action')}")
                st.write(f"**Risk Score:** {decision.get('risk_score', 0):.2f}")
                st.write(f"**Auto Resolvable:** {decision.get('auto_resolvable', False)}")
                st.write(f"**Labels:** {', '.join(decision.get('labels', []))}")
        
        with tab4:
            st.subheader("Risk Assessment")
            
            risk_score = decision.get('risk_score', 0)
            
            # Risk gauge
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if risk_score < 0.3:
                    st.success(f"🟢 Low Risk: {risk_score:.2f}")
                elif risk_score < 0.75:
                    st.warning(f"🟡 Medium Risk: {risk_score:.2f}")
                else:
                    st.error(f"🔴 High Risk: {risk_score:.2f}")
            
            st.progress(risk_score)
            
            st.markdown("---")
            
            # Risk factors
            st.write("**Risk Factors:**")
            
            amount_diff = abs(
                break_data.get('system_a', {}).get('amount', 0) -
                break_data.get('system_b', {}).get('amount', 0)
            )
            
            factors = []
            if amount_diff > 100000:
                factors.append("⚠️ Large amount difference (>${:,.0f})".format(amount_diff))
            if len(rules.get('failed_rules', [])) > 0:
                factors.append(f"⚠️ Failed {len(rules.get('failed_rules', []))} business rules")
            if ml_insights.get('confidence', 1) < 0.7:
                factors.append(f"⚠️ Low ML confidence ({ml_insights.get('confidence', 0):.0%})")
            if break_data.get('break_type') in ['REGULATORY_DATA', 'PNL_RECONCILIATION']:
                factors.append("⚠️ High-risk break type")
            
            if factors:
                for factor in factors:
                    st.write(factor)
            else:
                st.success("✅ No significant risk factors identified")
        
        with tab5:
            st.subheader("Take Action")
            
            st.write("**Agent Recommendation:**")
            st.info(f"{decision.get('action')} - {decision.get('explanation')}")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Approve & Resolve", use_container_width=True, type="primary"):
                    # Log feedback
                    from mcp.tools.workflow_tools import log_feedback
                    log_feedback(
                        break_id=break_data.get('break_id'),
                        decision=decision,
                        human_action="AUTO_RESOLVE",
                        human_notes="Human approved agent recommendation"
                    )
                    st.success("✅ Case approved and resolved!")
                    # Remove from HIL queue
                    st.session_state.processed_cases = [
                        c for c in st.session_state.processed_cases 
                        if c.get('break_id') != case.get('break_id')
                    ]
                    st.rerun()
            
            with col2:
                if st.button("🔄 Override Decision", use_container_width=True):
                    st.session_state.override_mode = True
            
            with col3:
                if st.button("🚨 Escalate to Senior", use_container_width=True, type="secondary"):
                    from mcp.tools.workflow_tools import log_feedback
                    log_feedback(
                        break_id=break_data.get('break_id'),
                        decision=decision,
                        human_action="ESCALATE",
                        human_notes="Human escalated to senior team"
                    )
                    st.success("🚨 Case escalated to senior team!")
                    st.rerun()
            
            # Override mode
            if st.session_state.get('override_mode'):
                st.markdown("---")
                st.subheader("Override Decision")
                
                new_action = st.selectbox(
                    "New Action",
                    ["AUTO_RESOLVE", "ESCALATE", "REJECTED"]
                )
                
                notes = st.text_area("Notes (required)", placeholder="Explain why you're overriding...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Override", disabled=not notes):
                        from mcp.tools.workflow_tools import log_feedback
                        log_feedback(
                            break_id=break_data.get('break_id'),
                            decision=decision,
                            human_action=new_action,
                            human_notes=f"Override: {notes}"
                        )
                        st.success(f"✅ Decision overridden to {new_action}")
                        st.session_state.override_mode = False
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.override_mode = False
                        st.rerun()

elif page == "📈 Analytics":
    st.markdown('<div class="main-header">📈 Analytics & Insights</div>', unsafe_allow_html=True)
    
    if len(st.session_state.processed_cases) == 0:
        st.info("Process some breaks to see analytics")
    else:
        # Summary stats
        st.subheader("Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        total = len(st.session_state.processed_cases)
        auto_resolved = sum(1 for c in st.session_state.processed_cases 
                           if c.get('case', {}).get('decision', {}).get('action') == ActionType.AUTO_RESOLVE)
        avg_risk = sum(c.get('case', {}).get('decision', {}).get('risk_score', 0) 
                      for c in st.session_state.processed_cases) / max(total, 1)
        
        with col1:
            st.metric("Total Processed", total)
        with col2:
            st.metric("Auto-Resolve Rate", f"{(auto_resolved/total*100):.0f}%")
        with col3:
            st.metric("Avg Risk Score", f"{avg_risk:.2f}")
        
        st.markdown("---")
        
        # Feedback stats
        st.subheader("Feedback & Learning")
        
        stats = get_feedback_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Feedback", stats.get('total_feedback', 0))
        with col2:
            st.metric("Human Actions", stats.get('total_with_human_action', 0))
        with col3:
            st.metric("Agreement Rate", f"{stats.get('agreement_rate', 0):.0%}")
        with col4:
            st.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.0%}")
        
        st.markdown("---")
        
        # Break down by type
        st.subheader("Break Distribution")
        
        break_types = {}
        for case in st.session_state.processed_cases:
            bt = case.get('case', {}).get('break_data', {}).get('break_type', 'Unknown')
            break_types[bt] = break_types.get(bt, 0) + 1
        
        st.bar_chart(break_types)
        
        st.markdown("---")
        
        # Decision distribution
        st.subheader("Decision Distribution")
        
        decisions = {}
        for case in st.session_state.processed_cases:
            action = case.get('case', {}).get('decision', {}).get('action', 'Unknown')
            decisions[action] = decisions.get(action, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Auto-Resolved", decisions.get('AUTO_RESOLVE', 0))
        with col2:
            st.metric("HIL Review", decisions.get('HIL_REVIEW', 0))
        with col3:
            st.metric("Escalated", decisions.get('ESCALATE', 0))

else:  # Settings
    st.markdown('<div class="main-header">⚙️ System Settings</div>', unsafe_allow_html=True)
    
    st.subheader("Tolerance Settings")
    
    from shared.config import settings
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Amount Tolerance (bps)",
            value=settings.default_amount_tolerance_bps,
            help="Tolerance in basis points (0.01% = 1 bps)"
        )
        
        st.number_input(
            "Quantity Tolerance",
            value=settings.default_quantity_tolerance,
            help="Absolute quantity tolerance"
        )
        
        st.number_input(
            "FX Tolerance (bps)",
            value=settings.fx_tolerance_bps
        )
    
    with col2:
        st.number_input(
            "Auto-Resolve Confidence (%)",
            value=int(settings.auto_resolve_confidence_threshold * 100),
            min_value=50,
            max_value=100
        )
        
        st.number_input(
            "Auto-Resolve Max Amount ($)",
            value=int(settings.auto_resolve_max_amount),
            min_value=1000,
            max_value=100000
        )
        
        st.number_input(
            "Escalation Threshold ($)",
            value=int(settings.escalation_amount_threshold),
            min_value=10000,
            max_value=1000000
        )
    
    st.info("⚠️ Settings are read-only in this demo. Modify shared/config.py to change values.")
    
    st.markdown("---")
    
    st.subheader("System Information")
    
    st.write(f"**Mock API URL:** {settings.mock_api_base_url}")
    st.write(f"**Agent Timeout:** {settings.agent_timeout_seconds}s")
    st.write(f"**Environment:** {settings.environment}")
    
    st.markdown("---")
    
    # Clear data
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.processed_cases = []
        TICKETS.clear()
        FEEDBACK_LOG.clear()
        st.success("✅ All data cleared!")
        st.rerun()

# Footer
st.markdown("---")
st.caption("Reconciliation Agent System v1.0 | Powered by Google ADK & A2A Protocol")
