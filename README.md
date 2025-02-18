# AI Agent Pattern Demos

This repository contains multiple **Jupyter notebooks** demonstrating various **AI agent patterns** for different use cases—from **ReAct** (Reason + Act) to **Chain-of-Thought (CoT)**, **Reflexion**, **Tool-Using**, **Auto-GPT** style agents, and even a **multi-agent** orchestrator approach.

Below is an overview of each notebook, along with instructions on how to run them.

---

## Contents

1. **ReAct Pattern**  
   - **Notebook**: `react_airline_demo.ipynb`  
   - **Description**: Shows a simple airline support agent that determines refund eligibility. Demonstrates the ReAct pattern’s loop: **Reason → Act → Observe → Reason → Conclude**.  
   - **Key Points**: 
     - Separates policy logic, LLM adapter, the agent’s ReAct flow, and a main script.  
     - Ideal for scenarios where the agent calls external “tools” or functions to gather data.

2. **Chain-of-Thought (CoT) Prompting**  
   - **Notebook**: `loan_cot_demo.ipynb`  
   - **Description**: Demonstrates CoT for deciding whether a loan application should be approved, showing step-by-step reasoning in a single LLM pass.  
   - **Key Points**: 
     - The agent explicitly “thinks aloud” (CoT) about the applicant’s credit score, debt-to-income ratio, etc.  
     - Integrates minimal domain checks plus LLM reasoning.

3. **Tool-Using Helpdesk Agent**  
   - **Notebook**: `tool_using_helpdesk_demo.ipynb`  
   - **Description**: A helpdesk agent that can call multiple tools (e.g., user directory, knowledge base, ticketing system) to resolve a user’s support request.  
   - **Key Points**: 
     - Focuses on how the agent chooses from different tools based on conversation context.  
     - Shows a mini ReAct-like loop of deciding whether to produce a final answer or call a tool next.

4. **Reflexion Pattern with CSV Analysis**  
   - **Notebook**: `reflexion_csv_demo.ipynb`  
   - **Description**: Demonstrates an agent that generates and executes Python code to analyze a CSV, then **self-corrects** if it encounters errors.  
   - **Key Points**: 
     - Illustrates the Reflexion pattern, where the LLM receives runtime errors as feedback, improves the code, and re-executes.  
     - Useful for iterative data analysis tasks.

5. **Auto-GPT Style Agent with Explicit CoT**  
   - **Notebook**: `auto_gpt_cot_demo.ipynb`  
   - **Description**: Shows how an Auto-GPT style agent can plan using a **Chain-of-Thought** approach, deciding which websites to visit and when to finalize an answer.  
   - **Key Points**: 
     - Emphasizes an iterative loop that calls “tools” (mock web search/scraping), and returns a final user-facing result.  
     - Makes the agent’s chain-of-thought visible in the output.

6. **Multi-Agent System**  
   - **Notebook**: `multi_agent_demo.ipynb`  
   - **Description**: Combines **three specialized agents**—Reflexion (local CSV analysis), Tool-Using (internal KB), and Auto-GPT (external research)—coordinated by a **master orchestrator**.  
   - **Key Points**: 
     - Demonstrates how you can break down tasks across multiple agent patterns.  
     - The master orchestrator merges sub-results into a final recommendation.

---

## How to Use

1. **Clone or Download** this repository to your local machine.
2. Ensure you have **Python 3** and **Jupyter** (or another environment like **VSCode** with Jupyter support).
3. **Install Dependencies**:  
   - Typically, you’ll need `pandas` for CSV demonstrations, plus any other libraries mentioned in the notebooks.  
   - Install via:
     ```bash
     pip install pandas
     ```
   - (If additional packages are required, each notebook’s first cell often indicates them.)
4. **Open** the notebook of interest in Jupyter (e.g., `jupyter notebook react_airline_demo.ipynb`).
5. **Run All Cells** in the notebook. Each notebook contains instructions at the bottom on what to expect from the output.

---

## Agent Patterns at a Glance

- **ReAct**: An agent that interleaves reasoning and tool-calling in multiple steps, capturing the pattern **Reason → Act → Observe → Reason → Conclude**.
- **Chain-of-Thought (CoT)**: Encourages the LLM to “think aloud” in a **single** pass, revealing how it arrives at an answer step-by-step.
- **Tool-Using**: The agent can dynamically choose which external or internal “tools” (APIs, knowledge bases, etc.) to query based on the conversation.
- **Reflexion**: An iterative approach where the agent detects errors or unsatisfactory results and uses them as feedback to **self-correct**.
- **Auto-GPT**: A more **autonomous** loop, often with mini-steps of planning, tool usage, and finalizing results, sometimes with explicit or implicit chain-of-thought.
- **Multi-Agent Orchestrator**: A master controller that delegates tasks to different specialized agents and merges their outputs.

---

## Contributing

Feel free to submit **issues** or **pull requests** if you:
- Encounter a bug in the sample code.
- Want to suggest improvements or additional agent patterns.
- Need clarifications or expanded examples.

---

## License

[MIT License](LICENSE) – You’re free to use, modify, and distribute this code for personal or commercial purposes. However, do keep in mind that the examples here are **conceptual**. For any production-grade system, you’d need additional **security, error handling,** and possibly **compliance** checks.

---

**Happy experimenting with AI agent patterns!** If you have any questions, open an issue or reach out. 
