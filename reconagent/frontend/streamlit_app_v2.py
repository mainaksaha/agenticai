"""
Streamlit UI for Dynamic Orchestrator v2
Shows execution graphs, efficiency metrics, and performance comparison
"""
import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.v2 import DynamicReconciliationOrchestrator
from orchestrator.workflow import ReconciliationOrchestrator

# Page config
st.set_page_config(
    page_title="Reconciliation v2 - Dynamic Orchestrator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'orch_v2' not in st.session_state:
    st.session_state.orch_v2 = DynamicReconciliationOrchestrator()
if 'orch_v1' not in st.session_state:
    st.session_state.orch_v1 = ReconciliationOrchestrator()
if 'v2_results' not in st.session_state:
    st.session_state.v2_results = []
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = None

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
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .agent-node {
        padding: 0.5rem;
        margin: 0.25rem;
        border-radius: 0.25rem;
        display: inline-block;
    }
    .agent-completed {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .agent-skipped {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .agent-failed {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">⚡ Dynamic Orchestrator v2</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    
    page = st.radio(
        "Select View",
        ["🏠 Dashboard", "🔬 Single Break Analysis", "📊 Batch Processing", "⚖️ v1 vs v2 Comparison", "📖 Policy Viewer"]
    )
    
    st.markdown("---")
    
    st.subheader("About v2")
    st.info("""
    **Dynamic Orchestrator v2** features:
    - ⚡ 30-70% faster
    - 🎯 Selective agent invocation
    - 🔀 Parallel execution
    - 🚪 Early exit on decision
    - 📜 Policy-driven routing
    """)

# Main content based on page selection
if page == "🏠 Dashboard":
    st.header("Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Breaks Processed (v2)", len(st.session_state.v2_results))
    
    with col2:
        if st.session_state.v2_results:
            avg_efficiency = sum(r['performance']['efficiency'].rstrip('%') for r in st.session_state.v2_results if 'performance' in r) / len(st.session_state.v2_results)
            st.metric("Avg Efficiency", f"{avg_efficiency:.0f}%", delta="vs 100% in v1")
        else:
            st.metric("Avg Efficiency", "N/A")
    
    with col3:
        if st.session_state.v2_results:
            avg_time = sum(r['performance']['total_duration_ms'] for r in st.session_state.v2_results if 'performance' in r) / len(st.session_state.v2_results)
            st.metric("Avg Time", f"{avg_time:.0f}ms")
        else:
            st.metric("Avg Time", "N/A")
    
    with col4:
        if st.session_state.v2_results:
            early_exits = sum(1 for r in st.session_state.v2_results if r.get('performance', {}).get('early_exit'))
            st.metric("Early Exits", f"{early_exits}/{len(st.session_state.v2_results)}")
        else:
            st.metric("Early Exits", "N/A")
    
    st.markdown("---")
    
    # Recent results
    if st.session_state.v2_results:
        st.subheader("Recent Breaks")
        
        for idx, result in enumerate(st.session_state.v2_results[-10:]):
            with st.expander(f"Break {result['break_id']} - {result['break_profile']['break_type']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Profile:**")
                    st.write(f"- Type: {result['break_profile']['break_type']}")
                    st.write(f"- Risk: {result['break_profile']['risk_tier']}")
                    st.write(f"- Exposure: ${result['break_profile']['exposure']:,.2f}")
                
                with col2:
                    st.write("**Execution:**")
                    st.write(f"- Agents: {result['execution_plan']['agents_invoked']}/{result['execution_plan']['agents_planned']}")
                    st.write(f"- Time: {result['performance']['total_duration_ms']:.0f}ms")
                    st.write(f"- Decision: {result['decision']['action']}")
    else:
        st.info("No breaks processed yet. Go to 'Single Break Analysis' or 'Batch Processing' to get started!")

elif page == "🔬 Single Break Analysis":
    st.header("Single Break Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Process Break")
        
        break_id = st.text_input("Break ID", value="BRK-001")
        
        if st.button("🚀 Process Break", type="primary"):
            with st.spinner("Processing break with v2..."):
                try:
                    result = st.session_state.orch_v2.process_break(break_id=break_id)
                    st.session_state.v2_results.append(result)
                    st.success(f"✅ Break processed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.session_state.v2_results:
            st.subheader("Latest Result")
            result = st.session_state.v2_results[-1]
            
            # Break Profile
            st.markdown("### Break Profile")
            profile = result['break_profile']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Type", profile['break_type'])
            with col2:
                st.metric("Risk Tier", profile['risk_tier'])
            with col3:
                st.metric("Exposure", f"${profile['exposure']:,.2f}")
            
            # Execution Summary
            st.markdown("### Execution Summary")
            perf = result['performance']
            exec_plan = result['execution_plan']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Agents Planned", exec_plan['agents_planned'])
            with col2:
                st.metric("Agents Invoked", exec_plan['agents_invoked'], 
                         delta=f"-{exec_plan['agents_skipped']}", delta_color="normal")
            with col3:
                st.metric("Duration", f"{perf['total_duration_ms']:.0f}ms")
            with col4:
                st.metric("Efficiency", perf['efficiency'])
            
            # Orchestration Reasoning - WHY these agents were selected
            if 'orchestration_reasoning' in result:
                st.markdown("### 🧠 Orchestration Reasoning")
                
                reasoning = result['orchestration_reasoning']
                
                # Create tabs for different types of reasoning
                reason_tabs = st.tabs([
                    "🎯 Why These Agents?",
                    "📋 Classification Logic", 
                    "🔄 Execution Strategy",
                    "⚡ What Was Skipped?"
                ])
                
                with reason_tabs[0]:
                    # Agent Selection Reasoning
                    agent_selection = reasoning.get('agent_selection_reasoning', {})
                    
                    st.write(f"**{agent_selection.get('summary', '')}**")
                    st.write("")
                    
                    for reason in agent_selection.get('reasons', []):
                        if reason.startswith('✅'):
                            st.success(reason)
                        elif reason.startswith('⊘'):
                            st.info(reason)
                        else:
                            st.write(reason)
                
                with reason_tabs[1]:
                    # Classification Reasoning
                    classification = reasoning.get('classification_reasoning', {})
                    
                    st.write(f"**{classification.get('summary', '')}**")
                    st.write("")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Break Type", classification.get('break_type', 'N/A'))
                        st.metric("Exposure", f"${classification.get('exposure', 0):,.2f}")
                    with col2:
                        st.metric("Risk Tier", classification.get('risk_tier', 'N/A'))
                        st.metric("Asset Class", classification.get('asset_class', 'N/A'))
                    
                    st.write("**Classification Reasons:**")
                    for reason in classification.get('reasons', []):
                        st.write(f"• {reason}")
                
                with reason_tabs[2]:
                    # Execution Strategy
                    strategy = reasoning.get('execution_strategy', {})
                    
                    st.write(f"**{strategy.get('summary', '')}**")
                    st.write("")
                    
                    # Show execution stages
                    st.write("**Execution Stages:**")
                    for stage in strategy.get('stages', []):
                        if stage.get('parallel'):
                            st.write(f"**Stage {stage['stage']}:** {' || '.join(stage['agents'])} (parallel)")
                        else:
                            st.write(f"**Stage {stage['stage']}:** {stage['agents'][0]}")
                    
                    st.write("")
                    st.write("**Strategy Details:**")
                    for reason in strategy.get('reasons', []):
                        st.write(f"• {reason}")
                
                with reason_tabs[3]:
                    # Skip Reasoning
                    skip_info = reasoning.get('skip_reasoning', {})
                    
                    st.write(f"**{skip_info.get('summary', '')}**")
                    
                    if skip_info.get('skipped_count', 0) > 0:
                        st.write("")
                        st.write("**Why Agents Were Skipped:**")
                        for reason in skip_info.get('reasons', []):
                            st.warning(reason)
                    
                    # Checkpoint reasoning
                    checkpoint_info = reasoning.get('checkpoint_reasoning', {})
                    if checkpoint_info.get('checkpoint_count', 0) > 0:
                        st.write("")
                        st.write("**Decision Checkpoints:**")
                        for reason in checkpoint_info.get('reasons', []):
                            if reason.startswith('✓'):
                                st.success(reason)
                            else:
                                st.write(f"• {reason}")
            
            # Execution Graph
            st.markdown("### 📊 Execution Timeline")
            
            exec_graph = result['execution_graph']
            executions = exec_graph['executions']
            
            st.write("**Agent Execution Order:**")
            for execution in executions:
                status = execution['status']
                agent_name = execution['agent_name']
                
                if status == 'COMPLETED':
                    duration = execution.get('duration_ms', 0)
                    st.markdown(f'<div class="agent-node agent-completed">✅ {agent_name} ({duration:.0f}ms)</div>', unsafe_allow_html=True)
                elif status == 'SKIPPED':
                    skip_reason = execution.get('skip_reason', 'Unknown')
                    st.markdown(f'<div class="agent-node agent-skipped">⊘ {agent_name} (Skipped: {skip_reason})</div>', unsafe_allow_html=True)
                elif status == 'FAILED':
                    error = execution.get('error', 'Unknown error')
                    st.markdown(f'<div class="agent-node agent-failed">❌ {agent_name} (Failed: {error})</div>', unsafe_allow_html=True)
            
            # Early Exit
            if exec_graph.get('early_exit'):
                st.success(f"🚪 Early Exit: {exec_graph.get('early_exit_reason', 'Decision reached')}")
            
            # Decision
            st.markdown("### Final Decision")
            decision = result['decision']
            
            action = decision['action']
            if action == 'AUTO_RESOLVE':
                st.success(f"✅ **{action}**")
            elif action == 'HIL_REVIEW':
                st.warning(f"📋 **{action}**")
            else:
                st.error(f"🚨 **{action}**")
            
            st.write(f"**Explanation:** {decision.get('explanation', 'N/A')}")
            st.write(f"**Confidence:** {decision.get('confidence', 0):.2%}")

elif page == "📊 Batch Processing":
    st.header("Batch Processing")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Process Multiple Breaks")
        
        num_breaks = st.slider("Number of breaks to process", 1, 20, 5)
        
        if st.button("🚀 Process Batch", type="primary"):
            with st.spinner(f"Processing {num_breaks} breaks..."):
                try:
                    results = st.session_state.orch_v2.process_multiple_breaks(limit=num_breaks)
                    
                    # Add to session state
                    st.session_state.v2_results.extend(results['results'])
                    
                    st.success(f"✅ Processed {results['breaks_processed']} breaks!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.session_state.v2_results:
            st.subheader("Batch Statistics")
            
            # Calculate stats
            total_planned = sum(r['execution_plan']['agents_planned'] for r in st.session_state.v2_results)
            total_invoked = sum(r['execution_plan']['agents_invoked'] for r in st.session_state.v2_results)
            total_skipped = sum(r['execution_plan']['agents_skipped'] for r in st.session_state.v2_results)
            total_time = sum(r['performance']['total_duration_ms'] for r in st.session_state.v2_results)
            early_exits = sum(1 for r in st.session_state.v2_results if r['performance']['early_exit'])
            
            efficiency = (total_invoked / total_planned * 100) if total_planned > 0 else 0
            avg_time = total_time / len(st.session_state.v2_results)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Breaks", len(st.session_state.v2_results))
                st.metric("Total Agents Invoked", total_invoked)
            with col2:
                st.metric("Total Agents Skipped", total_skipped)
                st.metric("Overall Efficiency", f"{efficiency:.0f}%")
            with col3:
                st.metric("Early Exits", early_exits)
                st.metric("Avg Time/Break", f"{avg_time:.0f}ms")
            
            # Decision Distribution
            st.markdown("### Decision Distribution")
            decisions = {}
            for r in st.session_state.v2_results:
                action = r['decision']['action']
                decisions[action] = decisions.get(action, 0) + 1
            
            decision_data = [{"Decision": k, "Count": v} for k, v in decisions.items()]
            st.bar_chart(decision_data, x="Decision", y="Count")
            
            # Risk Tier Distribution
            st.markdown("### Risk Tier Distribution")
            risk_tiers = {}
            for r in st.session_state.v2_results:
                tier = r['break_profile']['risk_tier']
                risk_tiers[tier] = risk_tiers.get(tier, 0) + 1
            
            risk_data = [{"Risk Tier": k, "Count": v} for k, v in risk_tiers.items()]
            st.bar_chart(risk_data, x="Risk Tier", y="Count")

elif page == "⚖️ v1 vs v2 Comparison":
    st.header("v1 vs v2 Performance Comparison")
    
    st.info("Compare the sequential v1 orchestrator with the dynamic v2 orchestrator on the same break.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Run Comparison")
        
        break_id = st.text_input("Break ID for comparison", value="BRK-001")
        
        if st.button("⚔️ Run Comparison", type="primary"):
            with st.spinner("Running both orchestrators..."):
                try:
                    # Run v1
                    st.write("Running v1 (Sequential)...")
                    start = time.time()
                    result_v1 = st.session_state.orch_v1.process_break(break_id=break_id)
                    v1_time = (time.time() - start) * 1000
                    
                    # Run v2
                    st.write("Running v2 (Dynamic)...")
                    start = time.time()
                    result_v2 = st.session_state.orch_v2.process_break(break_id=break_id)
                    v2_time = (time.time() - start) * 1000
                    
                    st.session_state.comparison_results = {
                        'v1': {'result': result_v1, 'time': v1_time},
                        'v2': {'result': result_v2, 'time': v2_time}
                    }
                    
                    st.success("✅ Comparison complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.session_state.comparison_results:
            st.subheader("Comparison Results")
            
            v1_data = st.session_state.comparison_results['v1']
            v2_data = st.session_state.comparison_results['v2']
            
            # Time Comparison
            st.markdown("### ⏱️ Time Comparison")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("v1 Time", f"{v1_data['time']:.0f}ms")
            with col2:
                st.metric("v2 Time", f"{v2_data['time']:.0f}ms")
            with col3:
                improvement = ((v1_data['time'] - v2_data['time']) / v1_data['time'] * 100)
                st.metric("Improvement", f"{improvement:.1f}%", delta=f"{improvement:.1f}%")
            
            # Agent Comparison
            st.markdown("### 🤖 Agent Invocation")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**v1 (Sequential)**")
                st.write("- Agents: 7 (all)")
                st.write("- Execution: Sequential")
                st.write("- Early Exit: No")
            
            with col2:
                st.write("**v2 (Dynamic)**")
                v2_result = v2_data['result']
                st.write(f"- Agents: {v2_result['execution_plan']['agents_invoked']}/{v2_result['execution_plan']['agents_planned']}")
                st.write(f"- Efficiency: {v2_result['performance']['efficiency']}")
                st.write(f"- Early Exit: {'Yes' if v2_result['performance']['early_exit'] else 'No'}")
            
            # Visual Comparison
            st.markdown("### 📊 Visual Comparison")
            
            comparison_data = [
                {"Version": "v1", "Metric": "Time (ms)", "Value": v1_data['time']},
                {"Version": "v2", "Metric": "Time (ms)", "Value": v2_data['time']},
                {"Version": "v1", "Metric": "Agents", "Value": 7},
                {"Version": "v2", "Metric": "Agents", "Value": v2_data['result']['execution_plan']['agents_invoked']},
            ]
            
            import pandas as pd
            df = pd.DataFrame(comparison_data)
            
            col1, col2 = st.columns(2)
            with col1:
                time_df = df[df['Metric'] == 'Time (ms)']
                st.bar_chart(time_df, x="Version", y="Value")
                st.caption("Lower is better")
            
            with col2:
                agents_df = df[df['Metric'] == 'Agents']
                st.bar_chart(agents_df, x="Version", y="Value")
                st.caption("Fewer agents = more efficient")
            
            # Winner
            st.markdown("### 🏆 Winner")
            if improvement > 0:
                st.success(f"✨ **v2 is {improvement:.1f}% faster** with {v2_data['result']['execution_plan']['agents_skipped']} fewer agents!")
            else:
                st.info("Results are similar for this break type.")

elif page == "📖 Policy Viewer":
    st.header("Policy Viewer")
    
    st.info("View the routing policies that determine which agents run for different break types.")
    
    # Get policy info
    policy_info = st.session_state.orch_v2.get_policy_info()
    
    st.subheader("Available Policies")
    st.write(f"**Total Break Types:** {len(policy_info['break_types'])}")
    
    # Policy selector
    break_type = st.selectbox("Select Break Type", policy_info['break_types'])
    
    if break_type:
        risk_tiers = policy_info['policies'].get(break_type, [])
        
        st.markdown(f"### {break_type}")
        
        for tier in risk_tiers:
            with st.expander(f"Risk Tier: {tier}"):
                # Load the actual policy
                policy = st.session_state.orch_v2.policy_engine.policy_loader.get_policy(break_type, tier)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Mandatory Agents:**")
                    for agent in policy.get('mandatory_agents', []):
                        st.write(f"- {agent}")
                    
                    st.write("**Optional Agents:**")
                    optional = policy.get('optional_agents', [])
                    if optional:
                        for agent in optional:
                            st.write(f"- {agent}")
                    else:
                        st.write("- None")
                
                with col2:
                    st.write("**Configuration:**")
                    st.write(f"- Max Parallel: {policy.get('max_parallel', 3)}")
                    st.write(f"- Early Exit: {'Enabled' if policy.get('early_exit_enabled') else 'Disabled'}")
                    st.write(f"- Checkpoints: {len(policy.get('decision_checkpoints', []))}")
                
                # Show parallel groups
                st.write("**Execution Order:**")
                parallel_groups = policy.get('parallel_groups', [])
                for idx, group in enumerate(parallel_groups, 1):
                    if len(group) > 1:
                        st.write(f"Stage {idx}: {' || '.join(group)} (parallel)")
                    else:
                        st.write(f"Stage {idx}: {group[0]}")
                
                # Show checkpoints
                checkpoints = policy.get('decision_checkpoints', [])
                if checkpoints:
                    st.write("**Decision Checkpoints:**")
                    for cp in checkpoints:
                        st.write(f"- After {cp.get('after_nodes', [])}: {cp.get('condition')} → {cp.get('action')}")

# Footer
st.markdown("---")
st.markdown("**Dynamic Orchestrator v2** | Policy-driven, parallel execution, early exit")
