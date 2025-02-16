from flask import Flask, request, jsonify
import pprint

# 1) Create your Flask app
api = Flask(__name__)

# 2) Suppose your pipeline is something like:
#    pipeline_app = SomePipelineClass(...)
#    and it has a method pipeline_app.stream({ "question": ... })

@api.route("/api/generate_lease", methods=["POST"])
def generate_call():
    """
    Accepts a JSON body like:
    {
      "question": "How do I get a lease for a public housing apartment in NY?"
    }
    and returns a JSON response with the pipeline's final generation and intermediate steps.
    """

    # 1) Parse JSON input
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Missing or empty 'question' field."}), 400

    # 2) Prepare the input for your pipeline
    pipeline_inputs = {"question": question}

    # 3) Run the pipeline in streaming mode
    #    We'll collect each "node" and any relevant info in a list
    trace_outputs = []
    final_generation = None

    for output in pipeline_app.stream(pipeline_inputs):
        # 'output' is typically a dict with keys = node names, values = state/data
        # e.g. { "node1": {...}, "node2": {...} } 
        for node_key, node_value in output.items():
            # capture or log any relevant info
            trace_outputs.append({
                "node": node_key,
                # you might store partial generations or any other keys
                # "partial": node_value.get("some_intermediate_data", None)
            })
            # last node_value typically has "generation"
            final_generation = node_value.get("generation", None)

    # 4) Return a JSON response
    #    For example, we include both the final generation
    #    and the "trace" of intermediate nodes
    return jsonify({
        "question": question,
        "final_generation": final_generation,
        "trace": trace_outputs
    }), 200


if __name__ == "__main__":
    # For local testing
    api.run(debug=True, port=5000)

