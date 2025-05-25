import json
import os
import openai  # Ensure OpenAI is installed and configured

# Import necessary functions
from get_requirement_details import get_requirement_details
from get_items import get_items
from get_quotations import get_quotations

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_vendors(req_id):
    """
    Use an LLM to evaluate vendor quotations based on contextual semantic similarity.
    The model determines which vendors should be accepted or rejected.
    """

    # 🔹 Fetch procurement details
    requirement_details = get_requirement_details(req_id)
    items = get_items(req_id)
    quotations = get_quotations(req_id)

    # 🔹 Ensure JSON is properly parsed
    try:
        requirement_details = json.loads(requirement_details) if isinstance(requirement_details, str) else requirement_details
        items_dict = json.loads(items).get("data", []) if isinstance(items, str) else items.get("data", [])
        quotations_dict = json.loads(quotations) if isinstance(quotations, str) else quotations
    except json.JSONDecodeError as e:
        return f"❌ Error decoding JSON data: {str(e)}"

    # 🔹 Prepare LLM prompt
    prompt = f"""
    You are a procurement evaluation assistant. Given a set of buyer requirements, item details, and vendor quotations,
    determine which vendors should be accepted or rejected. Provide a contextual semantic similarity score for each vendor.

    ## Buyer Requirements:
    {json.dumps(requirement_details, indent=2)}

    ## Items:
    {json.dumps(items_dict, indent=2)}

    ## Vendor Quotations:
    {json.dumps(quotations_dict, indent=2)}

    Evaluate vendors based on overall suitability, price, delivery time, brand relevance, warranty, and other contextual factors.
    Provide a list of vendors with:
    - Vendor ID
    - Acceptance Status ("ACCEPT" or "REJECT")
    - Contextual Similarity Score (0-100)
    - Justification for the decision
    All the above mentioned details must be displayed. The ID, Score, Status and Reason.
    """

    # 🔹 Call LLM to process evaluation
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": "You are an expert in procurement analysis."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        evaluation_results = response.choices[0].message.content.strip()
        return evaluation_results
    except Exception as e:
        return f"❌ Error in LLM processing: {str(e)}"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate vendors for a given requirement ID.")
    parser.add_argument("req_id", type=int, help="Requirement ID (REQ_ID) to evaluate vendors for.")
    args = parser.parse_args()

    print(evaluate_vendors(args.req_id))