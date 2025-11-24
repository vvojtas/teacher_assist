"""
Data formatting utilities for prompt construction.

Formats database data into strings suitable for LLM prompts.
"""

from typing import List, Dict, Any


def format_curriculum_refs(
    major_refs: List[Dict[str, Any]],
    curriculum_refs: List[Dict[str, Any]]
) -> str:
    """
    Format curriculum references grouped by major curriculum area.

    Output format per requirement:
        [Major curriculum text]
        [code] - [text]
        [code] - [text]
        ...

    Example output:
        Fizyczny obszar rozwoju dziecka. Dziecko przygotowane do podjęcia nauki w szkole
        1.1 - zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne
        1.2 - wykonuje czynności samoobsługowe: ubieranie się i rozbieranie, w tym czynności precyzyjne, np. zapinanie guzików, wiązanie sznurowadeł [...]

    Args:
        major_refs: List of major curriculum references with 'id' and 'full_text'.
        curriculum_refs: List of curriculum references with 'reference_code',
                        'full_text', and 'major_reference_id'.

    Returns:
        Formatted string with curriculum references organized by major area.
    """
    # Group curriculum refs by major_reference_id
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for ref in curriculum_refs:
        major_id: int = ref['major_reference_id']
        if major_id not in grouped:
            grouped[major_id] = []
        grouped[major_id].append(ref)

    # Build formatted string
    output_lines: List[str] = []

    for major_ref in major_refs:
        major_id: int = major_ref['id']

        # Only include major sections that have curriculum refs
        if major_id in grouped:
            # Add major curriculum section header
            output_lines.append(major_ref['full_text'])

            # Add all curriculum refs under this major section
            for ref in grouped[major_id]:
                output_lines.append(
                    f"{ref['reference_code']} - {ref['full_text']}"
                )

            # Add blank line between major sections
            output_lines.append("")

    # Join with newlines, remove trailing blank line
    return "\n".join(output_lines).rstrip()


def format_modules_list(modules: List[Dict[str, Any]]) -> str:
    """
    Format educational modules list for prompt.

    Args:
        modules: List of modules with 'module_name' field.

    Returns:
        Comma-separated list of module names.

    Example:
        "MATEMATYKA, JĘZYK, MOTORYKA MAŁA, FORMY PLASTYCZNE"
    """
    module_names: List[str] = [m['module_name'] for m in modules]
    return ", ".join(sorted(module_names))


def format_examples(examples: List[Dict[str, Any]]) -> str:
    """
    Format LLM training examples for prompt.

    Each example shows input (theme, activity) followed by 'Odpowiedź:' with
    correctly formatted JSON output. This trains the LLM on the expected output format.

    Args:
        examples: List of example work plan entries with theme, activity,
                 modules, objectives, and curriculum_references.

    Returns:
        Formatted string with numbered examples showing input and JSON response.

    Example output:
        Przykład 1:
        Temat: Jesień - zbiory
        Aktywność: Zabawa w sklep z owocami

        Odpowiedź:
        {
          "modules": ["MATEMATYKA"],
          "curriculum_refs": ["4.15", "4.18"],
          "objectives": [
            "Dziecko potrafi przeliczać w zakresie 5",
            "Rozpoznaje poznane wcześniej cyfry"
          ]
        }
    """
    import json

    formatted_examples: List[str] = []

    for i, example in enumerate(examples, start=1):
        # Format objectives as list
        # Handle both string (newline-separated) and list formats
        objectives = example['objectives']
        if isinstance(objectives, str):
            objectives_list = [obj.strip() for obj in objectives.split('\n') if obj.strip()]
        else:
            objectives_list = objectives

        # Create JSON response object
        response_json = {
            "modules": example['modules'],
            "curriculum_refs": example['curriculum_references'],
            "objectives": objectives_list
        }

        # Format with proper indentation
        json_str = json.dumps(response_json, ensure_ascii=False, indent=2)

        lines: List[str] = [
            f"Przykład {i}:",
            f"Temat: {example['theme']}",
            f"Aktywność: {example['activity']}",
            "",
            "Odpowiedź:",
            json_str
        ]
        formatted_examples.append("\n".join(lines))

    return "\n\n".join(formatted_examples)
