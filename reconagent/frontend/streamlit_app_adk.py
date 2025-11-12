"""
Streamlit UI for Google ADK Orchestrator
Shows ADK agents, A2A messages, LangGraph execution, and comparisons
"""
import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator_adk.orchestrator import ADKReconciliationOrchestrator
from orchestrator.v2 import DynamicReconciliationOrchestrator

# Page config
st.set_page_config(
    page_title="ADK Orchestrator - Google ADK + A2A + LangGraph",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'adk_orchestrator' not in st.session_state:
    try:
        st.session_state.adk_orchestrator = ADKReconciliationOrchestrator()
        st.session_state.adk_initialized = True
    except Exception as e:
        st.session_state.adk_initialized = False
        st.session_state.adk_error = str(e)

if 'v2_orchestrator' not in st.session_state:
    try:
        st.session_state.v2_orchestrator = DynamicReconciliationOrchestrator()
    except:
        pass

if 'adk_results' not in st.session_state:
    st.session_state.adk_results = []

if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None

# Custom CSS with readable colors
st.markdown("""
<style>
    /* Main header with readable gradient */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #4285f4, #34a853, #fbbc04, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Badge styles with good contrast */
    .adk-badge {
        background-color: #4285f4;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* A2A message box with dark text */
    .a2a-message {
        background-color: #e8f4fd;
        border-left: 4px solid #4285f4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
        color: #1a1a1a;
    }
    
    /* Agent node with dark text */
    .agent-node-adk {
        background-color: #e8f5e9;
        border: 2px solid #4caf50;
        padding: 0.75rem;
        margin: 0.5rem;
        border-radius: 0.5rem;
        display: inline-block;
        color: #1a1a1a;
    }
    
    /* Tool badge with dark text */
    .tool-badge {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        border-radius: 0.25rem;
        display: inline-block;
        font-size: 0.85rem;
        color: #333;
    }
    
    /* LangGraph node with dark text */
    .langgraph-node {
        background-color: #e3f2fd;
        border: 2px solid #2196f3;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        color: #1a1a1a;
        font-weight: 500;
    }
    
    /* Success metric */
    .success-metric {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    
    /* Comparison box with dark text */
    .comparison-box {
        border: 2px solid #ddd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Ensure all custom divs have readable text */
    div[style*="background"] {
        color: #1a1a1a !important;
    }
    
    /* Fix for skipped agents */
    .skipped-agent {
        background-color: #f8f9fa;
        border: 2px dashed #ccc;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        color: #6c757d;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🤖 Google ADK Orchestrator</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Official Google ADK + A2A Protocol + LangGraph</p>', unsafe_allow_html=True)
st.markdown("---")

# Check initialization
if not st.session_state.adk_initialized:
    st.error(f"""
    ⚠️ **ADK Orchestrator Failed to Initialize**
    
    Error: {st.session_state.get('adk_error', 'Unknown error')}
    
    **Possible causes:**
    1. Google ADK SDK not installed: `pip install google-adk`
    2. A2A Protocol SDK not installed: `pip install a2a-python`
    3. LangGraph not installed: `pip install langgraph`
    4. Mock API server not running
    
    **To fix:**
    ```bash
    pip install google-adk a2a-python langgraph
    python main.py mock-api  # In separate terminal
    ```
    """)
    st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Navigation")
    
    page = st.radio(
        "Select View",
        [
            "🏠 Dashboard",
            "🤖 Process Break",
            "📦 Batch Processing",  # NEW!
            "📨 A2A Messages",
            "🔄 LangGraph Flow",
            "🛠️ Agent Tools",
            "🆚 ADK vs Custom",
            "📊 Performance"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.subheader("About ADK")
    st.info("""
    **Google ADK Features:**
    - ✅ Official Agent Development Kit
    - ✅ A2A Protocol standard
    - ✅ LangGraph orchestration
    - ✅ Conditional routing
    - ✅ State management
    """)
    
    # Agent status
    st.markdown("---")
    st.subheader("Agent Status")
    try:
        agents_info = st.session_state.adk_orchestrator.get_agent_info()
        st.success(f"✅ {len(agents_info)} ADK Agents Ready")
    except:
        st.warning("⚠️ Agents not loaded")

# Main content
if page == "🏠 Dashboard":
    st.header("Dashboard")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Breaks Processed", len(st.session_state.adk_results))
    
    with col2:
        if st.session_state.adk_results:
            successful = sum(1 for r in st.session_state.adk_results if r.get('success'))
            st.metric("Successful", successful, delta=f"{successful}/{len(st.session_state.adk_results)}")
        else:
            st.metric("Successful", 0)
    
    with col3:
        if st.session_state.adk_results:
            avg_time = sum(r.get('duration_ms', 0) for r in st.session_state.adk_results) / len(st.session_state.adk_results)
            st.metric("Avg Duration", f"{avg_time:.0f}ms")
        else:
            st.metric("Avg Duration", "N/A")
    
    with col4:
        if st.session_state.adk_results:
            avg_agents = sum(len(r.get('execution_path', [])) for r in st.session_state.adk_results) / len(st.session_state.adk_results)
            st.metric("Avg Agents Used", f"{avg_agents:.1f}")
        else:
            st.metric("Avg Agents Used", "N/A")
    
    st.markdown("---")
    
    # Recent results
    if st.session_state.adk_results:
        st.subheader("Recent Executions")
        
        for idx, result in enumerate(reversed(st.session_state.adk_results[-10:]), 1):
            with st.expander(f"Break {result['break_id']} - {result['decision'].get('action', 'N/A')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Execution:**")
                    st.write(f"- Success: {'✅' if result['success'] else '❌'}")
                    st.write(f"- Duration: {result['duration_ms']:.0f}ms")
                    st.write(f"- Agents: {len(result['execution_path'])}")
                    st.write(f"- A2A Messages: {len(result.get('a2a_messages', []))}")
                
                with col2:
                    st.write("**Decision:**")
                    st.write(f"- Action: {result['decision'].get('action', 'N/A')}")
                    st.write(f"- Path: {' → '.join(result['execution_path'])}")
                    
                    if result.get('errors'):
                        st.error(f"Errors: {result['errors']}")
                
                # Show orchestrator reasoning (NEW!)
                orchestrator_plan = result.get('orchestrator_plan', {})
                if orchestrator_plan and orchestrator_plan.get('reasoning'):
                    st.write("**🧠 Orchestrator:**")
                    st.write(f"- {orchestrator_plan.get('reasoning', 'N/A')[:80]}...")
                    if orchestrator_plan.get('skip_reasons'):
                        skipped = list(orchestrator_plan.get('skip_reasons', {}).keys())
                        st.write(f"- Skipped: {', '.join(skipped)}")
    else:
        st.info("No breaks processed yet. Go to 'Process Break' to get started!")
    
    # Agent Information
    st.markdown("---")
    st.subheader("Registered ADK Agents")
    
    try:
        agents_info = st.session_state.adk_orchestrator.get_agent_info()
        
        cols = st.columns(3)
        for idx, (name, info) in enumerate(agents_info.items()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="agent-node-adk">
                    <strong>{info['name']}</strong><br>
                    <small>{info['description'][:50]}...</small><br>
                    <span class="adk-badge">ADK Agent</span>
                    <span class="adk-badge">{len(info['tools'])} tools</span>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading agents: {e}")

elif page == "🤖 Process Break":
    st.header("Process Break with ADK")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Input")
        
        break_id = st.text_input("Break ID", value="BRK-001")
        
        if st.button("🚀 Process with ADK", type="primary"):
            with st.spinner("Processing with ADK + A2A + LangGraph..."):
                try:
                    start = time.time()
                    result = st.session_state.adk_orchestrator.process_break(break_id=break_id)
                    result['_ui_time'] = (time.time() - start) * 1000
                    
                    st.session_state.adk_results.append(result)
                    st.success("✅ Processing complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with col2:
        if st.session_state.adk_results:
            st.subheader("Latest Result")
            result = st.session_state.adk_results[-1]
            
            # Summary
            st.markdown("### Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Success", "✅" if result['success'] else "❌")
            with col2:
                st.metric("Duration", f"{result['duration_ms']:.0f}ms")
            with col3:
                st.metric("Agents", len(result['execution_path']))
            
            # Orchestrator Reasoning (NEW!)
            st.markdown("### 🧠 Orchestrator Agent Decision")
            orchestrator_plan = result.get('orchestrator_plan', {})
            if orchestrator_plan:
                st.info(f"**Reasoning:** {orchestrator_plan.get('reasoning', 'N/A')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**✅ Agents Invoked:**")
                    agents_invoked = orchestrator_plan.get('agents_to_invoke', [])
                    for agent in agents_invoked:
                        st.write(f"- {agent}")
                
                with col2:
                    skip_reasons = orchestrator_plan.get('skip_reasons', {})
                    if skip_reasons:
                        st.write("**⊘ Agents Skipped:**")
                        for agent, reason in skip_reasons.items():
                            st.write(f"- **{agent}**: {reason}")
            else:
                st.warning("Orchestrator plan not available")
            
            # Execution Path
            st.markdown("### LangGraph Execution Path")
            for stage in result['execution_path']:
                st.markdown(f'<div class="langgraph-node">📍 {stage.upper()}</div>', unsafe_allow_html=True)
            
            # Decision
            st.markdown("### Final Decision")
            decision = result['decision']
            action = decision.get('action', 'N/A')
            
            if action == 'AUTO_RESOLVE':
                st.success(f"✅ **{action}**")
            elif action == 'HIL_REVIEW':
                st.warning(f"📋 **{action}**")
            else:
                st.error(f"🚨 **{action}**")
            
            st.write(f"**Explanation:** {decision.get('explanation', 'N/A')}")
            
            # A2A Context
            st.markdown("### A2A Protocol")
            st.info(f"**Context ID:** {result.get('a2a_context', 'N/A')}")
            st.write(f"**Messages:** {len(result.get('a2a_messages', []))} A2A messages exchanged")
            
            # Errors
            if result.get('errors'):
                st.markdown("### Errors")
                for error in result['errors']:
                    st.error(error)

elif page == "📦 Batch Processing":
    st.header("Batch Processing - Process Multiple Breaks")
    
    st.info("""
    **Process multiple breaks at once** to see how the orchestrator handles different scenarios.
    15 sample breaks covering various types, complexities, and expected outcomes.
    """)
    
    # Import sample breaks
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from orchestrator_adk.sample_breaks import get_sample_breaks, get_break_statistics
    
    # Initialize batch results in session state
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = None
    if 'batch_processing' not in st.session_state:
        st.session_state.batch_processing = False
    
    # Sample break statistics
    stats = get_break_statistics()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Sample Breaks Overview")
        st.metric("Total Breaks", stats['total'])
        st.metric("Expected AUTO_RESOLVE", f"{stats['auto_resolve']} ({stats['auto_resolve_pct']:.0f}%)")
        st.metric("Expected HIL_REVIEW", f"{stats['hil_review']} ({stats['hil_review_pct']:.0f}%)")
        st.metric("Expected ESCALATE", f"{stats['escalate']} ({stats['escalate_pct']:.0f}%)")
        
        st.markdown("---")
        
        # Break types
        st.write("**Break Types:**")
        for break_type, count in stats['break_types'].items():
            st.write(f"- {break_type}: {count}")
        
        st.markdown("---")
        
        # Process button
        if st.button("🚀 Process All Breaks", type="primary", disabled=st.session_state.batch_processing):
            st.session_state.batch_processing = True
            st.rerun()
    
    with col2:
        if st.session_state.batch_processing and st.session_state.batch_results is None:
            st.subheader("Processing Breaks...")
            
            sample_breaks = get_sample_breaks()
            results = []
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, break_data in enumerate(sample_breaks):
                status_text.text(f"Processing {break_data['break_id']}... ({idx+1}/{len(sample_breaks)})")
                
                try:
                    result = st.session_state.adk_orchestrator.process_break(break_data=break_data)
                    result['expected_outcome'] = break_data.get('expected_outcome')
                    result['description'] = break_data.get('description')
                    results.append(result)
                except Exception as e:
                    results.append({
                        'break_id': break_data['break_id'],
                        'success': False,
                        'error': str(e),
                        'expected_outcome': break_data.get('expected_outcome')
                    })
                
                progress_bar.progress((idx + 1) / len(sample_breaks))
            
            st.session_state.batch_results = results
            st.session_state.batch_processing = False
            status_text.text("✅ All breaks processed!")
            st.rerun()
        
        elif st.session_state.batch_results:
            st.subheader("Batch Processing Results")
            
            results = st.session_state.batch_results
            
            # Summary metrics
            total = len(results)
            successful = sum(1 for r in results if r.get('success'))
            
            # Outcome distribution
            actual_outcomes = {}
            for r in results:
                if r.get('success'):
                    action = r.get('decision', {}).get('action', 'UNKNOWN')
                    actual_outcomes[action] = actual_outcomes.get(action, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Processed", total)
            with col2:
                st.metric("Successful", successful)
            with col3:
                auto_resolve = actual_outcomes.get('AUTO_RESOLVE', 0)
                st.metric("AUTO_RESOLVE", auto_resolve, delta=f"{(auto_resolve/total*100):.0f}%")
            with col4:
                hil = actual_outcomes.get('HIL_REVIEW', 0) + actual_outcomes.get('ESCALATE', 0)
                st.metric("HIL/ESCALATE", hil, delta=f"{(hil/total*100):.0f}%")
            
            st.markdown("---")
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📋 Results Table", "📊 Flow Diagram", "📈 Analysis"])
            
            with tab1:
                st.subheader("Detailed Results")
                
                # Results table
                for idx, result in enumerate(results, 1):
                    with st.expander(f"{idx}. {result['break_id']} - {result.get('decision', {}).get('action', 'ERROR')}"):
                        if result.get('success'):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Break Info:**")
                                st.write(f"- Description: {result.get('description', 'N/A')}")
                                st.write(f"- Expected: {result.get('expected_outcome', 'N/A')}")
                                st.write(f"- Actual: {result.get('decision', {}).get('action', 'N/A')}")
                                
                                # Match check
                                expected = result.get('expected_outcome')
                                actual = result.get('decision', {}).get('action')
                                if expected == actual:
                                    st.success("✅ Matches expectation")
                                else:
                                    st.warning(f"⚠️ Expected {expected}, got {actual}")
                            
                            with col2:
                                st.write("**Execution:**")
                                st.write(f"- Duration: {result.get('duration_ms', 0):.0f}ms")
                                st.write(f"- Agents: {len(result.get('execution_path', []))}")
                                st.write(f"- Path: {' → '.join(result.get('execution_path', []))}")
                                
                                # Orchestrator reasoning
                                plan = result.get('orchestrator_plan', {})
                                if plan.get('reasoning'):
                                    st.write(f"- Reasoning: {plan.get('reasoning', '')[:60]}...")
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            with tab2:
                st.subheader("Execution Flow Diagram")
                
                # Create Sankey diagram showing flow
                import plotly.graph_objects as go
                
                # Collect flow data
                flow_counts = {}
                for result in results:
                    if result.get('success'):
                        path = result.get('execution_path', [])
                        for i in range(len(path)-1):
                            edge = f"{path[i]}→{path[i+1]}"
                            flow_counts[edge] = flow_counts.get(edge, 0) + 1
                
                # Build Sankey
                nodes = list(set([p for r in results if r.get('success') for p in r.get('execution_path', [])]))
                node_dict = {node: idx for idx, node in enumerate(nodes)}
                
                sources = []
                targets = []
                values = []
                
                for result in results:
                    if result.get('success'):
                        path = result.get('execution_path', [])
                        for i in range(len(path)-1):
                            if path[i] in node_dict and path[i+1] in node_dict:
                                sources.append(node_dict[path[i]])
                                targets.append(node_dict[path[i+1]])
                                values.append(1)
                
                fig = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=nodes,
                        color="blue"
                    ),
                    link=dict(
                        source=sources,
                        target=targets,
                        value=values
                    )
                )])
                
                fig.update_layout(
                    title_text="Agent Execution Flow (All Breaks)",
                    font_size=10,
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Flow statistics
                st.markdown("---")
                st.subheader("Flow Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Most Common Paths:**")
                    path_counts = {}
                    for r in results:
                        if r.get('success'):
                            path = ' → '.join(r.get('execution_path', []))
                            path_counts[path] = path_counts.get(path, 0) + 1
                    
                    for path, count in sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"- ({count}x) {path}")
                
                with col2:
                    st.write("**Agent Usage:**")
                    agent_counts = {}
                    for r in results:
                        if r.get('success'):
                            for agent in r.get('execution_path', []):
                                agent_counts[agent] = agent_counts.get(agent, 0) + 1
                    
                    for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"- {agent}: {count}/{total} ({count/total*100:.0f}%)")
            
            with tab3:
                st.subheader("Analysis & Insights")
                
                # Expected vs Actual
                st.markdown("### Expected vs Actual Outcomes")
                
                matches = sum(1 for r in results if r.get('success') and 
                             r.get('expected_outcome') == r.get('decision', {}).get('action'))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Matches Expectation", matches, delta=f"{(matches/successful*100):.0f}%")
                with col2:
                    mismatches = successful - matches
                    st.metric("Mismatches", mismatches)
                with col3:
                    accuracy = (matches / successful * 100) if successful > 0 else 0
                    st.metric("Accuracy", f"{accuracy:.1f}%")
                
                # Performance analysis
                st.markdown("---")
                st.markdown("### Performance Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    durations = [r.get('duration_ms', 0) for r in results if r.get('success')]
                    if durations:
                        st.write("**Duration Statistics:**")
                        st.write(f"- Average: {sum(durations)/len(durations):.0f}ms")
                        st.write(f"- Min: {min(durations):.0f}ms")
                        st.write(f"- Max: {max(durations):.0f}ms")
                        st.write(f"- Total: {sum(durations):.0f}ms")
                
                with col2:
                    agents_used = [len(r.get('execution_path', [])) for r in results if r.get('success')]
                    if agents_used:
                        st.write("**Agent Usage Statistics:**")
                        st.write(f"- Average: {sum(agents_used)/len(agents_used):.1f} agents")
                        st.write(f"- Min: {min(agents_used)} agents")
                        st.write(f"- Max: {max(agents_used)} agents")
                
                # Orchestrator efficiency
                st.markdown("---")
                st.markdown("### Orchestrator Efficiency")
                
                skip_stats = {}
                for r in results:
                    if r.get('success'):
                        plan = r.get('orchestrator_plan', {})
                        skipped = plan.get('skip_reasons', {})
                        for agent in skipped.keys():
                            skip_stats[agent] = skip_stats.get(agent, 0) + 1
                
                if skip_stats:
                    st.write("**Agents Skipped (Efficiency Gains):**")
                    for agent, count in sorted(skip_stats.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"- {agent}: {count} times ({count/successful*100:.0f}%)")
                else:
                    st.info("No agents were skipped")
            
            # Reset button
            st.markdown("---")
            if st.button("🔄 Reset and Process Again"):
                st.session_state.batch_results = None
                st.session_state.batch_processing = False
                st.rerun()
        
        else:
            st.info("👈 Click 'Process All Breaks' to start batch processing")
            
            # Show sample breaks preview
            st.subheader("Sample Breaks Preview")
            sample_breaks = get_sample_breaks()
            
            for brk in sample_breaks[:5]:  # Show first 5
                with st.expander(f"{brk['break_id']} - {brk['break_type']}"):
                    st.write(f"**Description:** {brk['description']}")
                    st.write(f"**Expected Outcome:** {brk['expected_outcome']}")
                    st.write(f"**Expected Agents:** {', '.join(brk['expected_agents'])}")
            
            st.write(f"... and {len(sample_breaks) - 5} more breaks")

elif page == "📨 A2A Messages":
    st.header("A2A Protocol Messages")
    
    st.info("""
    **A2A (Agent2Agent) Protocol** is the official standard for agent communication.
    View all messages exchanged between agents during execution.
    """)
    
    if not st.session_state.adk_results:
        st.warning("No executions yet. Process a break first!")
    else:
        # Select execution
        break_ids = [r['break_id'] for r in st.session_state.adk_results]
        selected_break = st.selectbox("Select Break", break_ids, index=len(break_ids)-1)
        
        # Get result
        result = next((r for r in st.session_state.adk_results if r['break_id'] == selected_break), None)
        
        if result and result.get('a2a_messages'):
            st.subheader(f"A2A Messages for {selected_break}")
            st.write(f"**Context ID:** {result.get('a2a_context', 'N/A')}")
            st.write(f"**Total Messages:** {len(result['a2a_messages'])}")
            
            st.markdown("---")
            
            # Display each message
            for idx, msg in enumerate(result['a2a_messages'], 1):
                st.markdown(f"""
                <div class="a2a-message">
                    <strong>Message {idx}</strong> - {msg.get('type', 'UNKNOWN').upper()}<br>
                    <small>ID: {msg.get('id', 'N/A')}</small><br>
                    <br>
                    <strong>From:</strong> {msg.get('from_agent', 'N/A')}<br>
                    <strong>To:</strong> {msg.get('to_agent', 'N/A')}<br>
                    <strong>Timestamp:</strong> {msg.get('timestamp', 'N/A')}<br>
                </div>
                """, unsafe_allow_html=True)
                
                # Message content
                with st.expander("View Content"):
                    st.json(msg.get('content', {}))
                
                # Metadata
                if msg.get('metadata'):
                    with st.expander("View Metadata"):
                        st.json(msg['metadata'])
                
                # Context and threading
                if msg.get('context_id') or msg.get('reply_to'):
                    st.write(f"🔗 **Context:** {msg.get('context_id', 'N/A')}")
                    if msg.get('reply_to'):
                        st.write(f"↩️ **Reply to:** {msg.get('reply_to')}")
        else:
            st.warning("No A2A messages found for this execution")

elif page == "🔄 LangGraph Flow":
    st.header("LangGraph Execution Flow")
    
    st.info("""
    **LangGraph** provides dynamic DAG-based orchestration with conditional routing.
    See how the StateGraph executed agents based on conditions.
    """)
    
    if not st.session_state.adk_results:
        st.warning("No executions yet. Process a break first!")
    else:
        # Select execution
        break_ids = [r['break_id'] for r in st.session_state.adk_results]
        selected_break = st.selectbox("Select Break", break_ids, index=len(break_ids)-1)
        
        # Get result
        result = next((r for r in st.session_state.adk_results if r['break_id'] == selected_break), None)
        
        if result:
            st.subheader(f"Execution Flow for {selected_break}")
            
            # Execution path visualization
            st.markdown("### Agent Execution Sequence")
            
            execution_path = result.get('execution_path', [])
            completed_stages = result.get('completed_stages', execution_path)
            
            # All possible agents
            all_agents = [
                'ingestion',
                'enrichment',
                'matching',
                'rules',
                'pattern',
                'decision',
                'workflow'
            ]
            
            st.write("**Legend:** ✅ Executed | ⊘ Skipped")
            st.write("")
            
            for agent in all_agents:
                if agent in execution_path:
                    st.markdown(f"""
                    <div class="langgraph-node">
                        ✅ <strong>{agent.upper()}</strong> - Executed
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="skipped-agent">
                        ⊘ <strong>{agent.upper()}</strong> - Skipped
                    </div>
                    """, unsafe_allow_html=True)
            
            # Flow diagram
            st.markdown("---")
            st.markdown("### Flow Diagram")
            
            flow_text = " → ".join([stage.upper() for stage in execution_path])
            st.code(flow_text, language=None)
            
            # Conditional routing decisions
            st.markdown("---")
            st.markdown("### Conditional Routing Decisions")
            
            st.write("""
            LangGraph made these conditional routing decisions:
            """)
            
            # Check what was skipped
            if 'matching' not in execution_path:
                st.info("🔀 **Matching skipped** - Break type didn't require matching")
            else:
                st.success("✅ **Matching executed** - Break type required correlation")
            
            if 'pattern' not in execution_path:
                st.info("🔀 **Pattern skipped** - High confidence from rules, no ML needed")
            else:
                st.success("✅ **Pattern executed** - ML analysis needed for root cause")
            
            if 'workflow' not in execution_path:
                st.info("🔀 **Workflow skipped** - No ticket creation needed")
            else:
                st.success("✅ **Workflow executed** - Ticket created")
            
            # Performance
            st.markdown("---")
            st.markdown("### Performance")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Duration", f"{result['duration_ms']:.0f}ms")
            with col2:
                st.metric("Agents Executed", len(execution_path))
            with col3:
                st.metric("Agents Skipped", len(all_agents) - len(execution_path))

elif page == "🛠️ Agent Tools":
    st.header("ADK Agent Tools")
    
    st.info("""
    **ADK Agents** expose tools that LangGraph can invoke.
    View all registered tools for each agent.
    """)
    
    try:
        agents_info = st.session_state.adk_orchestrator.get_agent_info()
        
        for agent_name, info in agents_info.items():
            with st.expander(f"🤖 {info['name'].upper()}", expanded=False):
                st.write(f"**Description:** {info['description']}")
                st.write(f"**Model:** {info['model']}")
                
                st.markdown("---")
                st.markdown("### Available Tools")
                
                if info['tools']:
                    cols = st.columns(3)
                    for idx, tool in enumerate(info['tools']):
                        with cols[idx % 3]:
                            st.markdown(f'<span class="tool-badge">🔧 {tool}</span>', unsafe_allow_html=True)
                else:
                    st.write("No tools registered")
                
                # Show tool usage in latest execution
                if st.session_state.adk_results:
                    latest = st.session_state.adk_results[-1]
                    if agent_name.split('_')[-1] in latest.get('execution_path', []):
                        st.success(f"✅ Used in latest execution")
                    else:
                        st.info(f"⊘ Not used in latest execution")
    
    except Exception as e:
        st.error(f"Error loading agent tools: {e}")

elif page == "🆚 ADK vs Custom":
    st.header("ADK vs Custom Comparison")
    
    st.info("""
    **Compare** the official Google ADK implementation (Option A) with the custom v2 implementation.
    Run both and see the differences!
    """)
    
    # Input
    col1, col2 = st.columns(2)
    
    with col1:
        break_id = st.text_input("Break ID for Comparison", value="BRK-001")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔬 Run Both & Compare", type="primary"):
            with st.spinner("Running both implementations..."):
                comparison = {
                    'break_id': break_id,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Run ADK
                try:
                    adk_start = time.time()
                    adk_result = st.session_state.adk_orchestrator.process_break(break_id=break_id)
                    adk_time = (time.time() - adk_start) * 1000
                    
                    comparison['adk'] = {
                        'success': True,
                        'result': adk_result,
                        'duration_ms': adk_time
                    }
                except Exception as e:
                    comparison['adk'] = {
                        'success': False,
                        'error': str(e),
                        'duration_ms': 0
                    }
                
                # Run Custom v2
                try:
                    if hasattr(st.session_state, 'v2_orchestrator'):
                        v2_start = time.time()
                        v2_result = st.session_state.v2_orchestrator.process_break(break_id=break_id)
                        v2_time = (time.time() - v2_start) * 1000
                        
                        comparison['v2'] = {
                            'success': True,
                            'result': v2_result,
                            'duration_ms': v2_time
                        }
                    else:
                        comparison['v2'] = {
                            'success': False,
                            'error': 'v2 orchestrator not initialized',
                            'duration_ms': 0
                        }
                except Exception as e:
                    comparison['v2'] = {
                        'success': False,
                        'error': str(e),
                        'duration_ms': 0
                    }
                
                st.session_state.comparison_result = comparison
                st.success("✅ Comparison complete!")
                st.rerun()
    
    # Display comparison
    if st.session_state.comparison_result:
        comp = st.session_state.comparison_result
        
        st.markdown("---")
        st.subheader(f"Comparison Results: {comp['break_id']}")
        
        col1, col2 = st.columns(2)
        
        # ADK Results
        with col1:
            st.markdown("### 🤖 Google ADK (Option A)")
            st.markdown('<div class="comparison-box">', unsafe_allow_html=True)
            
            if comp['adk']['success']:
                result = comp['adk']['result']
                
                st.success("✅ Success")
                st.metric("Duration", f"{comp['adk']['duration_ms']:.0f}ms")
                st.write(f"**Decision:** {result['decision'].get('action', 'N/A')}")
                st.write(f"**Agents:** {len(result['execution_path'])}")
                st.write(f"**Path:** {' → '.join(result['execution_path'])}")
                st.write(f"**A2A Messages:** {len(result.get('a2a_messages', []))}")
                
                with st.expander("View Full Result"):
                    st.json(result)
            else:
                st.error(f"❌ Failed: {comp['adk']['error']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # v2 Results
        with col2:
            st.markdown("### ⚙️ Custom v2")
            st.markdown('<div class="comparison-box">', unsafe_allow_html=True)
            
            if comp['v2']['success']:
                result = comp['v2']['result']
                
                st.success("✅ Success")
                st.metric("Duration", f"{comp['v2']['duration_ms']:.0f}ms")
                st.write(f"**Decision:** {result.get('final_decision', {}).get('action', 'N/A')}")
                st.write(f"**Agents:** {len(result.get('agents_executed', []))}")
                st.write(f"**Stages:** {len(result.get('execution_stages', []))}")
                
                with st.expander("View Full Result"):
                    st.json(result)
            else:
                st.error(f"❌ Failed: {comp['v2']['error']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Comparison metrics
        st.markdown("---")
        st.subheader("📊 Comparison Metrics")
        
        if comp['adk']['success'] and comp['v2']['success']:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Performance")
                adk_time = comp['adk']['duration_ms']
                v2_time = comp['v2']['duration_ms']
                faster = "ADK" if adk_time < v2_time else "Custom v2"
                diff = abs(adk_time - v2_time)
                
                st.write(f"**Faster:** {faster}")
                st.write(f"**Difference:** {diff:.0f}ms")
                
                if adk_time < v2_time:
                    speedup = (v2_time / adk_time - 1) * 100
                    st.success(f"ADK is {speedup:.1f}% faster")
                else:
                    speedup = (adk_time / v2_time - 1) * 100
                    st.info(f"v2 is {speedup:.1f}% faster")
            
            with col2:
                st.markdown("### Agent Usage")
                adk_agents = len(comp['adk']['result']['execution_path'])
                v2_agents = len(comp['v2']['result'].get('agents_executed', []))
                
                st.write(f"**ADK:** {adk_agents} agents")
                st.write(f"**v2:** {v2_agents} agents")
                
                if adk_agents < v2_agents:
                    st.success(f"ADK used {v2_agents - adk_agents} fewer agents")
                elif adk_agents > v2_agents:
                    st.info(f"ADK used {adk_agents - v2_agents} more agents")
                else:
                    st.info("Same number of agents")
            
            with col3:
                st.markdown("### Decision")
                adk_decision = comp['adk']['result']['decision'].get('action', 'N/A')
                v2_decision = comp['v2']['result'].get('final_decision', {}).get('action', 'N/A')
                
                st.write(f"**ADK:** {adk_decision}")
                st.write(f"**v2:** {v2_decision}")
                
                if adk_decision == v2_decision:
                    st.success("✅ Same decision")
                else:
                    st.warning("⚠️ Different decisions")
        
        # Architecture comparison
        st.markdown("---")
        st.subheader("🏗️ Architecture Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ADK Architecture")
            st.code("""
            google.adk.Agent
            ├─ Official ADK pattern
            ├─ A2A Protocol (standard)
            ├─ LangGraph StateGraph
            ├─ Conditional routing
            └─ Tool-based execution
            """, language=None)
        
        with col2:
            st.markdown("### v2 Architecture")
            st.code("""
            Custom Agent
            ├─ Custom base class
            ├─ Custom orchestration
            ├─ Sequential DAG
            ├─ Policy-based routing
            └─ Direct function calls
            """, language=None)

elif page == "📊 Performance":
    st.header("Performance Metrics")
    
    if not st.session_state.adk_results:
        st.warning("No execution data yet. Process some breaks first!")
    else:
        # Overall stats
        st.subheader("Overall Statistics")
        
        results = st.session_state.adk_results
        total = len(results)
        successful = sum(1 for r in results if r.get('success'))
        failed = total - successful
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Processed", total)
        with col2:
            st.metric("Successful", successful, delta=f"{(successful/total*100):.1f}%")
        with col3:
            st.metric("Failed", failed)
        with col4:
            success_rate = (successful / total * 100) if total > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Performance metrics
        st.markdown("---")
        st.subheader("Performance Breakdown")
        
        durations = [r['duration_ms'] for r in results]
        agents_used = [len(r['execution_path']) for r in results]
        a2a_messages = [len(r.get('a2a_messages', [])) for r in results]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Duration (ms)")
            st.metric("Average", f"{sum(durations)/len(durations):.0f}ms")
            st.metric("Min", f"{min(durations):.0f}ms")
            st.metric("Max", f"{max(durations):.0f}ms")
        
        with col2:
            st.markdown("### Agents per Execution")
            st.metric("Average", f"{sum(agents_used)/len(agents_used):.1f}")
            st.metric("Min", min(agents_used))
            st.metric("Max", max(agents_used))
        
        with col3:
            st.markdown("### A2A Messages")
            st.metric("Average", f"{sum(a2a_messages)/len(a2a_messages):.1f}")
            st.metric("Min", min(a2a_messages))
            st.metric("Max", max(a2a_messages))
        
        # Execution paths
        st.markdown("---")
        st.subheader("Common Execution Paths")
        
        # Count path frequencies
        path_counts = {}
        for r in results:
            path = ' → '.join(r['execution_path'])
            path_counts[path] = path_counts.get(path, 0) + 1
        
        # Sort by frequency
        sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)
        
        for path, count in sorted_paths[:5]:
            percentage = (count / total * 100)
            st.write(f"**{count}x ({percentage:.1f}%):** `{path}`")
        
        # Decision distribution
        st.markdown("---")
        st.subheader("Decision Distribution")
        
        decisions = {}
        for r in results:
            action = r['decision'].get('action', 'UNKNOWN')
            decisions[action] = decisions.get(action, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for idx, (action, count) in enumerate(decisions.items()):
            with cols[idx % 3]:
                percentage = (count / total * 100)
                st.metric(action, count, delta=f"{percentage:.1f}%")
        
        # Recent history
        st.markdown("---")
        st.subheader("Recent Execution History")
        
        for idx, result in enumerate(reversed(results[-10:]), 1):
            with st.expander(f"{result['break_id']} - {result['decision'].get('action')} ({result['duration_ms']:.0f}ms)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Path:** {' → '.join(result['execution_path'])}")
                    st.write(f"**Agents:** {len(result['execution_path'])}")
                    st.write(f"**A2A Messages:** {len(result.get('a2a_messages', []))}")
                
                with col2:
                    st.write(f"**Success:** {'✅' if result['success'] else '❌'}")
                    st.write(f"**Duration:** {result['duration_ms']:.0f}ms")
                
                if result.get('errors'):
                    st.error(f"Errors: {', '.join(result['errors'])}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <strong>Google ADK Orchestrator</strong> • Official A2A Protocol • LangGraph StateGraph<br>
    Built with Streamlit • Powered by Google ADK
</div>
""", unsafe_allow_html=True)

