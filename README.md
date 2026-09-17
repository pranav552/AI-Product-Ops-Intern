\# Composio AI Product Ops — 100-App Research Pipeline



Agentic research pipeline built for the \*\*AI Product Ops Intern take-home assignment\*\*.



The system researches a set of applications and produces structured, evidence-grounded findings on:



\- Authentication methods

\- Self-serve vs gated API access

\- REST / GraphQL API surface

\- MCP (Model Context Protocol) support

\- Buildability as an agent toolkit



The pipeline is designed so that claims must be supported by fetched evidence. Claims that cannot be grounded are downgraded to `UNKNOWN` rather than being silently accepted.



\## Live case study



\[link to be added after deployment]



\## Source repository



This repository contains the research agent, validation logic, batch runner, schemas, and generated research outputs.



\## Requirements



\- Python 3.11+

\- \[Ollama](https://ollama.com) running locally

\- `llama3.2:3b` pulled through Ollama

\- Internet access for web research



Pull the model:



```bash

ollama pull llama3.2:3b

Python dependencies are listed in:

requirements.txt

Setup

Install the Python dependencies:

pip install -r requirements.txt

Make sure Ollama is running and the required model is available before starting the research pipeline.

Running the research agent
Run a single app

Useful for debugging and development:

python test_pipeline.py
Run the full batch

The batch processes the applications listed in data/apps.csv.

Existing result files are treated as checkpoints and skipped automatically:

python run_batch.py
Force a re-run

To ignore existing checkpoints:

python run_batch.py --force
Run selected applications
python run_batch.py --app Salesforce --app Notion
Limit the batch

Useful for testing pipeline changes:

python run_batch.py --limit 10
