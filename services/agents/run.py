import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.crew import run_agent_pipeline

if __name__ == "__main__":
    run_agent_pipeline(limit=3)