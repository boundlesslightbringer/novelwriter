# GRRM Novel Writer

A multi-agent novel-writing system inspired by George R.R. Martin's "gardener" methodology. The system uses a LangGraph-based orchestrator-worker architecture to manage the complex, multi-stage process of writing a novel, ensuring deep character consistency, logical consequences, and rich worldbuilding.

## Architecture

The system is built on an **Orchestrator-Worker** pattern using [LangGraph](https://langchain-ai.github.io/langgraph/). 

Instead of rigid, hardcoded workflows, the system relies on a central **Orchestrator Brain**. The user interacts *only* with the Brain through a terminal REPL. The Brain interprets the user's intent and dynamically delegates tasks to specialized domain workers.

### The Workers

- **`planning_subagent`**: Handles story foundation, initial seed generation, rough endpoints, worldbuilding, and research integration.
- **`character_subagent`**: Manages the full character lifecycle, including conception, psychological creation, voice differentiation, and plot integration.
- **`plotting_subagent`**: Drives the gardener plotting system, manages multiple POV structures, braided narratives, conflict layering, and plot thread tracking.
- **`writing_subagent`**: Generates draft prose, maintains POV consistency, calibrates pacing, layers history and legend, and applies professional writing techniques.
- **`consequence_subagent`**: Analyzes consequence cascades (immediate, short-term bombs, long-term implications) and audits the balance of realism and fantasy.
- **`worldbible_manager`**: The sole infrastructure worker with access to the MongoDB Knowledge Graph. Handles all reads, writes, and temporal versioning of the story state.

## Setup Instructions

### Prerequisites
- Python 3.12+
- A running MongoDB instance (local or remote)
- An Anthropic API key (the default model is `claude-3-5-sonnet-20240620` / `anthropic:claude-sonnet-4-20250514`)

### Installation

1. **Clone the repository and navigate to the directory:**
   ```bash
   git clone <repository-url>
   cd novelwriter
   ```

2. **Install dependencies:**
   We recommend using `uv` for dependency management:
   ```bash
   uv sync
   ```
   Or using standard pip:
   ```bash
   pip install -e .
   ```

3. **Set Environment Variables:**
   Create a `.env` file or export the following variables in your terminal:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   
   # Optional: Override default MongoDB connection (defaults to mongodb://localhost:27017/)
   export MONGODB_URI="mongodb://localhost:27017/"
   export MONGODB_DB_NAME="novelwriter_kg"
   ```

## Usage

Start the interactive terminal REPL by running:

```bash
python main.py
```

You will be dropped into a `User>` prompt. From here, you converse naturally with the Orchestrator Brain. 

### Example Interactions

**Bootstrapping a new story:**
> **User>** I want to start a new Dark Fantasy novel. The primary theme is the cost of ambition. Let's brainstorm some initial seeds.

The Brain will automatically delegate to the `planning_subagent` to generate seeds, present them to you, and then you can instruct it to persist the chosen seed to the World Bible.

**Planning a scene:**
> **User>** Let's plan the first scene for Chapter 1. The POV character is Jon.

The Brain will query the `worldbible_manager` for the current state, then delegate to the `plotting_subagent` to generate scene parameters (goal, obstacle, choice, consequence).

**Drafting a scene:**
> **User>** That plan looks good. Go ahead and draft the scene.

The Brain will pass the parameters to the `writing_subagent` to generate the prose and run a quality/POV consistency audit.

**Exiting:**
Type `exit` or `quit` to stop the REPL.

## How it Works Under the Hood

1. **User Input:** You type a request in the terminal.
2. **Brain Node:** The Orchestrator evaluates the conversation history and your request. It outputs a structured decision: either `respond` directly to you, or `delegate` to a specific worker.
3. **Worker Node:** If delegated, the selected worker (e.g., `writing_subagent`) receives the task, uses its specific tools (like `progressive_skill_loader` or `WORLD_BIBLE_TOOLS`), and returns a structured `WorkerResponse`.
4. **Loop:** The graph routes back to the Brain, which reads the worker's result and decides whether to delegate another task or present the final response to you.
