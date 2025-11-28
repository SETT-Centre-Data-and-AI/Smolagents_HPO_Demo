from smolagents import CodeAgent, WebSearchTool, TransformersModel, BaseTool
import os
import json

# --- Custom tool to read hpo.json on demand ---
class HPOFileTool(BaseTool):
    name = "hpo_lookup"
    description = (
        "Given a clinical string, look up all HPO mappings from hpo.json. "
        "Always use this tool for HPO lookups."
    )

    inputs = {
        "query": {
            "type": "string",
            "description": "The clinical string to parse and look up in hpo.json"
        }
    }
    outputs = {
        "mapping": {
            "type": "object",
            "description": "Dictionary of clinical terms and their HPO mappings"
        }
    }
    output_type = "object"

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def forward(self, query: str) -> dict:
        with open(self.file_path, "r") as f:
            hpo_data = json.load(f)

        # Normalize and split the query into candidate terms
        terms = [t.strip().lower() for t in query.replace(";", ",").split(",") if t.strip()]

        # Recursive helper to walk the JSON tree
        def search_entry(entry, query_norm):
            if isinstance(entry, dict):
                if "lbl" in entry and isinstance(entry["lbl"], str):
                    if entry["lbl"].lower() == query_norm:
                        return entry.get("id")
                if "meta" in entry and "synonyms" in entry["meta"]:
                    for syn in entry["meta"]["synonyms"]:
                        if syn.get("val", "").lower() == query_norm:
                            return entry.get("id")
                for v in entry.values():
                    result = search_entry(v, query_norm)
                    if result:
                        return result
            elif isinstance(entry, list):
                for item in entry:
                    result = search_entry(item, query_norm)
                    if result:
                        return result
            return None

        results = {}
        for term in terms:
            match = search_entry(hpo_data, term)
            results[term] = match if match else "No mapping found"

        # --- NEW: save results to file automatically ---
        output_path = os.path.join(os.path.dirname(__file__), "output_mappings.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to {output_path}")
        return results

    # Implement the abstract __call__ method required by BaseTool
    def __call__(self, query: str) -> dict:
        return self.forward(query)

    # Implement to_code_prompt so smolagents can render it in the system prompt
    def to_code_prompt(self) -> str:
        return (
            f"Tool name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Inputs: {self.inputs}\n"
            f"Outputs: {self.outputs}\n"
        )


# --- Load your model ---
model = TransformersModel(
    model_id="openai/gpt-oss-20b",
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

# --- Direct test of the tool itself with a long clinical string ---
clinical_string = "the patient has probably got iron deficiency anaemia, they don't however have short stature, but they do have a congenital heart defect and developmental delay. The person is very fat and has type 2 diabetes. He also has diarrhoea. He has vomited. He has eaten a lot of pizza with extra pepperoni and this has made him gassy. He also drank too much pineapple juice and tomato juice as well as liquorice. This has given him high blood pressure. He is very lonely and depressed. He did not respond to treatment with SSRI's. He is also very sleepy. He also has a bald head. Lack of vitamin D. He has a painful tongue and has scurvy and Crohn's as well as lead poisoning."
hpo_terms = hpo_tool.forward(clinical_string)
print("Direct lookup results:", hpo_terms)

# --- Example usage via the agent ---
agent.run(
    "Use the hpo_lookup tool to map the following clinical string to the correct HPO terms but please do NOT map any negations only positively asserted terms and do not include any non-clinical terms. Please format the terms you wish to check as a list before sending the queries and don't try to import the json module or it won't work: "
    "'the patient has probably got iron deficiency anaemia, they don't however have short stature, but they do have a congenital heart defect and developmental delay. The person is very fat and has diabetes. He also has diarrhoea. He has vomited. He has eaten a lot of pizza with extra pepperoni and this has made him gassy. He also drank too much pineapple juice and tomato juice as well as liquorice. This has given him high blood pressure. He is very lonely and depressed. He did not respond to treatment with SSRI's. He is also very sleepy. He also has a bald head. Lack of vitamin D. He has a painful tongue and has scurvy and Crohn's as well as lead poisoning'. "
    "Save the results as a JSON object."
)