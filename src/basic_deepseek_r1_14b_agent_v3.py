from smolagents import CodeAgent, WebSearchTool, TransformersModel, Tool
import os
import json

# Custom tool to read hpo.json on demand
class HPOFileTool(Tool):
    name = "hpo_lookup"
    description = (
        "Given a clinical term, look up its HPO mapping from hpo.json. "
        "Always use this tool for HPO lookups."
    )

    inputs = {
        "query": {
            "type": "string",
            "description": "The clinical term to look up in hpo.json"
        }
    }
    outputs = {
        "mapping": {
            "type": "string",
            "description": "The HPO mapping for the given clinical term"
        }
    }
    output_type = "string"

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def forward(self, query: str) -> str:
        with open(self.file_path, "r") as f:
            hpo_data = json.load(f)

        query_norm = query.strip().lower()

        # Recursive helper to walk the JSON tree
        def search_entry(entry):
            if isinstance(entry, dict):
                # Check label
                if "lbl" in entry and isinstance(entry["lbl"], str):
                    if entry["lbl"].lower() == query_norm:
                        return entry.get("id")

                # Check synonyms
                if "meta" in entry and "synonyms" in entry["meta"]:
                    for syn in entry["meta"]["synonyms"]:
                        if syn.get("val", "").lower() == query_norm:
                            return entry.get("id")

                # Recurse into all values
                for v in entry.values():
                    result = search_entry(v)
                    if result:
                        return result

            elif isinstance(entry, list):
                for item in entry:
                    result = search_entry(item)
                    if result:
                        return result

            return None

        result = search_entry(hpo_data)
        return result if result else "No mapping found"


# Load your model
model = TransformersModel(
    model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    max_new_tokens=4096,
    device_map="auto"
)

file_path = os.path.join(os.path.dirname(__file__), "hpo.json")
hpo_tool = HPOFileTool(file_path)

agent = CodeAgent(
    tools=[WebSearchTool(), hpo_tool],
    model=model,
    stream_outputs=True
)

# --- Direct test of the tool itself ---
hpo_term = hpo_tool.forward("iron deficiency anaemia")
print("Direct lookup result:", hpo_term)

# --- Example usage via the agent ---
agent.run("Use the hpo_lookup tool to map 'iron deficiency anaemia' to the correct HPO term.")