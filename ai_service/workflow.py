"""
LangGraph workflow for AI service.

Defines the state machine that orchestrates the entire metadata generation process:
1. Input validation
2. Parallel data loading (modules, curriculum refs, examples, template)
3. Prompt construction
4. LLM generation
5. Output validation
6. Response formatting
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from common.models import FillWorkPlanResponse, ErrorResponse
from ai_service.nodes.validators import validate_input, validate_output, parse_llm_response
from ai_service.nodes.loaders import (
    load_modules,
    load_curriculum_refs,
    load_examples,
    load_prompt_template
)
from ai_service.nodes.prompt_builder import construct_prompt
from ai_service.nodes.llm_generator import generate_with_llm
from ai_service.nodes.formatters import format_success, format_error


class WorkflowState(TypedDict, total=False):
    """
    State for the LangGraph workflow.

    Contains all data flowing through the workflow nodes.
    """
    # Input (from API request)
    activity: str
    theme: str

    # Database Context (loaded in parallel)
    available_modules: List[Dict[str, Any]]
    major_curriculum_refs: List[Dict[str, Any]]
    curriculum_refs: List[Dict[str, Any]]
    example_entries: List[Dict[str, Any]]

    # Prompt Engineering
    prompt_template: str
    constructed_prompt: str

    # LLM Generation
    llm_raw_response: str
    llm_parsed_output: Dict[str, Any]
    reasoning: str  # Logged but not returned in API

    # Validation
    validation_passed: bool
    validation_errors: List[str]

    # Cost Tracking
    input_tokens: int
    output_tokens: int
    estimated_cost: float

    # Output
    final_response: Optional[FillWorkPlanResponse | ErrorResponse]


def should_continue_after_validation(state: WorkflowState) -> str:
    """
    Conditional routing function.

    Routes to success or error formatter based on validation result.

    Args:
        state: Current workflow state.

    Returns:
        "success" if validation passed, "error" otherwise.
    """
    if state.get("validation_passed", False):
        return "success"
    else:
        return "error"


def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow.

    Workflow structure:
        START
          ↓
        validate_input
          ↓
        ┌─────────────────┬──────────────────┬──────────────────┐
        ↓                 ↓                  ↓                  ↓
    load_modules   load_curriculum    load_examples    load_template
        │                 │                  │                  │
        └─────────────────┴──────────────────┴──────────────────┘
          ↓
        construct_prompt
          ↓
        generate_with_llm
          ↓
        parse_llm_response
          ↓
        validate_output
          ↓
        [conditional: validation_passed?]
          ↓                    ↓
        success              error
     format_success    format_error
          ↓                    ↓
        END                  END

    Returns:
        Compiled StateGraph ready for execution.
    """
    # Create workflow graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("load_modules", load_modules)
    workflow.add_node("load_curriculum_refs", load_curriculum_refs)
    workflow.add_node("load_examples", load_examples)
    workflow.add_node("load_template", load_prompt_template)
    workflow.add_node("construct_prompt", construct_prompt)
    workflow.add_node("generate_llm", generate_with_llm)
    workflow.add_node("parse_response", parse_llm_response)
    workflow.add_node("validate_output", validate_output)
    workflow.add_node("format_success", format_success)
    workflow.add_node("format_error", format_error)

    # Set entry point
    workflow.set_entry_point("validate_input")

    # Add edges from input validation to parallel loaders
    workflow.add_edge("validate_input", "load_modules")
    workflow.add_edge("validate_input", "load_curriculum_refs")
    workflow.add_edge("validate_input", "load_examples")
    workflow.add_edge("validate_input", "load_template")

    # Add edges from all loaders to prompt construction
    # Note: LangGraph automatically waits for all parallel branches to complete
    workflow.add_edge("load_modules", "construct_prompt")
    workflow.add_edge("load_curriculum_refs", "construct_prompt")
    workflow.add_edge("load_examples", "construct_prompt")
    workflow.add_edge("load_template", "construct_prompt")

    # Add sequential edges
    workflow.add_edge("construct_prompt", "generate_llm")
    workflow.add_edge("generate_llm", "parse_response")
    workflow.add_edge("parse_response", "validate_output")

    # Add conditional routing after validation
    workflow.add_conditional_edges(
        "validate_output",
        should_continue_after_validation,
        {
            "success": "format_success",
            "error": "format_error"
        }
    )

    # Add edges to END
    workflow.add_edge("format_success", END)
    workflow.add_edge("format_error", END)

    # Compile the graph
    return workflow.compile()


# Global compiled workflow instance
_compiled_workflow: Optional[StateGraph] = None


def get_workflow() -> StateGraph:
    """
    Get or create the compiled workflow instance.

    Returns:
        Compiled StateGraph ready for execution.
    """
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = create_workflow()
    return _compiled_workflow
