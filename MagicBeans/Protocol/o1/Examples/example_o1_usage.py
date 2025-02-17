from O1ProtocolBean.script import validate_o1_compliance, structure_o1_response

def demo():
    # Sample query about the new Anthropic dataset
    user_query = "How does the newly released data inform large language model safety research?"
    
    # Build a structured [o1] response
    response = structure_o1_response(query=user_query, dataset_info="Anthropic 2023 Data Release")
    
    # Validate compliance
    is_compliant = validate_o1_compliance(response)
    
    if is_compliant:
        print("[INFO] Compliant Response:\n", response)
    else:
        print("[WARNING] Response Not O1-Compliant.\n", response)

if __name__ == "__main__":
    demo()
