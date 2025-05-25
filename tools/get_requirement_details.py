from database import get_db_connection
import json
from datetime import datetime
import argparse

def get_requirement_details(req_id):
    """
    Fetch requirement details based on req_id.

    Args:
        req_id (int): Requirement ID.

    Returns:
        str: JSON string of requirement details or error message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure req_id is an integer before passing it to the SQL query
        if not str(req_id).isdigit():
            return json.dumps({"error": f"Invalid req_id: {req_id}. Expected an integer."})

        query = """
        SELECT REQ_ID, REQ_TITLE, REQ_DESC, REQ_POSTED_ON, REQ_CATEGORY, REQ_URGENCY, 
               REQ_BUDGET, QUOTATION_PRICE_LIMIT, REQ_DELIVERY_LOC, REQ_TAXES, REQ_PAYMENT_TERMS
        FROM requirementdetails
        WHERE REQ_ID = ?
        """
        
        cursor.execute(query, (int(req_id),))  # Convert req_id to int before executing
        result = cursor.fetchone()
        
        if result:
            # Convert result to dictionary
            result_dict = dict(zip([column[0] for column in cursor.description], result))

            # Convert datetime fields to string
            if isinstance(result_dict.get("REQ_POSTED_ON"), datetime):
                result_dict["REQ_POSTED_ON"] = result_dict["REQ_POSTED_ON"].strftime('%Y-%m-%d %H:%M:%S')

            # Convert QUOTATION_PRICE_LIMIT (decimal) to float
            if "QUOTATION_PRICE_LIMIT" in result_dict and result_dict["QUOTATION_PRICE_LIMIT"] is not None:
                result_dict["QUOTATION_PRICE_LIMIT"] = float(result_dict["QUOTATION_PRICE_LIMIT"])

            return json.dumps(result_dict, indent=2)
        else:
            return json.dumps({"error": f"Requirement ID {req_id} not found."})

    except ValueError as ve:
        return json.dumps({"error": str(ve)})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        conn.close()

if __name__ == "__main__":
    # Set up argument parser to accept req_id as a command line argument
    parser = argparse.ArgumentParser(description="Fetch requirement details for a given requirement ID.")
    parser.add_argument("req_id", type=int, help="Requirement ID (REQ_ID) to fetch details for.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided req_id
    print(get_requirement_details(args.req_id))