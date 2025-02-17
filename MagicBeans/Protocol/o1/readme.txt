# O1ProtocolBean

## Overview
This Magic Bean enforces the [o1] test type protocol by:
- Ensuring minimal references to other test types (e.g., [4o] or [o3-mini-high]).
- Maintaining strict adherence to Giants Framework axioms.
- Providing structured prompts and checks to keep answers concise and methodical.

## Key Features
1. **Test Type Validation**: Analyzes the context of the conversation to ensure [o1] compliance.
2. **Response Structuring**: Suggests a methodical format for answers based on [o1] guidelines.
3. **Data Integration**: Offers placeholders or sample logic for referencing external datasets (e.g., Anthropic’s newly released data) in an [o1]-compliant manner.

## Usage
1. **Import** this bean in your AI test environment or script.
2. **Initialize** the O1ProtocolBean to wrap or filter user requests/responses.
3. **Leverage** the provided `validate_o1_compliance(...)` function in `script.py` to confirm each response is within [o1] scope.

## Examples
See [examples/example_o1_usage.py](examples/example_o1_usage.py) for a quick demonstration.

## Contributing
1. Make sure to reference the Giants axioms in all expansions or modifications.
2. Adhere to the [CONTRIBUTING.md](../../CONTRIBUTING.md) guidelines.
3. Tag changes with `o1-protocol` for clarity in commits and pull requests.
