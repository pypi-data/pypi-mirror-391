import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def serialize_to_dict(obj: Any) -> Any:
    """Convert objects to JSON-serializable format.

    Note:
        This function will never raise exceptions. If serialization fails, it returns a string representation.
    """
    try:
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj

        # Handle Pydantic models (OpenAI SDK uses these)
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            return obj.dict()

        # Handle lists recursively
        if isinstance(obj, list):
            return [serialize_to_dict(item) for item in obj]

        # Handle dicts recursively
        if isinstance(obj, dict):
            return {key: serialize_to_dict(value) for key, value in obj.items()}

        # Fallback: convert to string
        return str(obj)
    except Exception:
        # If all else fails, return a safe string representation
        try:
            return str(obj)
        except Exception:
            return "<unserializable object>"


# Valid span kinds for Playgent (now using OpenTelemetry)
SPAN_KIND_ENDPOINT = "endpoint"  # Root span for decorated functions
SPAN_KIND_GENERATION = "generation"  # LLM generation spans (replaces input/message/function_call)


@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    provider: str = "openai"
    event_type: str = ""
    user_id: Optional[str] = None
    person_id: Optional[str] = None
    trace_id: Optional[str] = None
    endpoint: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    is_output: bool = False
    input_event_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "provider": self.provider,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "person_id": self.person_id,
            "trace_id": self.trace_id,
            "endpoint": self.endpoint,
            "data": self.data,
            "is_output": self.is_output,
            "input_event_id": self.input_event_id
        }


def parse_endpoint_event(name: str, kwargs: Dict[str, Any], function_key: str = "") -> Event:
    """Create an endpoint event for function calls"""
    return Event(
        provider="",
        event_type="endpoint",
        data={
            "name": name,
            "kwargs": serialize_to_dict(kwargs),
            "function_key": function_key
        },
        is_output=False
    )


def parse_openai_input_item(inputs: Any, instructions: str) -> Event:
    event_id = str(uuid.uuid4())
    data = {
        "inputs": serialize_to_dict(inputs),
        "instructions": instructions
    }
    return Event(
        id=event_id,
        provider="openai",
        event_type="input",
        data=data,
        is_output=False
    )


def parse_openai_response_item(item: Any, input_event_id: Optional[str] = None) -> Optional[Event]:
    """Parse an OpenAI response item into an Event"""
    if not hasattr(item, 'type'):
        return None
    
    event_type = getattr(item, 'type', 'unknown')
    event_id = str(uuid.uuid4())
    
    data = {}
    
    # Handle different response types
    if event_type == 'output_text':
        # Handle output_text type - extract text content
        if hasattr(item, 'content') and isinstance(item.content, list):
            text_contents = []
            for content_item in item.content:
                if hasattr(content_item, 'text'):
                    text_contents.append(content_item.text)
            data['content'] = ' '.join(text_contents) if text_contents else ''
        elif hasattr(item, 'text'):
            data['content'] = item.text
        else:
            data['content'] = str(item)
            
    elif event_type == 'reasoning':
        # Handle reasoning type - extract text content from content array
        if hasattr(item, 'content') and isinstance(item.content, list):
            text_contents = []
            for content_item in item.content:
                if hasattr(content_item, 'text'):
                    text_contents.append(content_item.text)
            data['content'] = ' '.join(text_contents) if text_contents else ''
        else:
            data['content'] = ''
            
    elif event_type == 'custom_tool_call':
        # Handle custom tool call - store name and input
        data['name'] = getattr(item, 'name', '')
        data['input'] = getattr(item, 'input', '')
        
    elif event_type == 'function_call':
        # Handle function tool call - store name and arguments
        data['name'] = getattr(item, 'name', '')
        data['arguments'] = getattr(item, 'arguments', '')
        
    elif event_type == 'mcp_call':
        # Handle MCP tool call - store name, arguments, and output
        data['name'] = getattr(item, 'name', '')
        data['arguments'] = getattr(item, 'arguments', '')
        # Include output if available
        if hasattr(item, 'output'):
            data['output'] = getattr(item, 'output', '')

    elif event_type == 'web_search_call':
        # Handle web_search_call - map to function_call event type
        data['name'] = 'web_search'

        # Extract web search specific fields
        web_search_data = {}

        # Get the action (search, open_page, or find_in_page)
        if hasattr(item, 'action'):
            action = getattr(item, 'action', 'search')
            # Handle ActionSearch object or string
            if hasattr(action, '__class__') and action.__class__.__name__ == 'ActionSearch':
                # Extract the actual action value from the ActionSearch object
                if hasattr(action, 'value'):
                    web_search_data['action'] = action.value
                elif hasattr(action, 'name'):
                    web_search_data['action'] = action.name
                else:
                    web_search_data['action'] = str(action)
            elif isinstance(action, str):
                web_search_data['action'] = action
            elif hasattr(action, 'name') and isinstance(action.name, str):
                # Handle objects with a 'name' attribute that's a string
                web_search_data['action'] = action.name
            elif hasattr(action, 'value') and isinstance(action.value, str):
                # Handle objects with a 'value' attribute that's a string
                web_search_data['action'] = action.value
            else:
                # Serialize using the helper function for unknown types
                web_search_data['action'] = serialize_to_dict(action)
        else:
            web_search_data['action'] = 'search'  # Default action

        # Get search query if available (usually for 'search' action)
        if hasattr(item, 'search_query'):
            web_search_data['search_query'] = serialize_to_dict(getattr(item, 'search_query', ''))
        elif hasattr(item, 'query'):  # Alternative field name
            web_search_data['search_query'] = serialize_to_dict(getattr(item, 'query', ''))

        # Get domains if available (usually for 'search' action)
        if hasattr(item, 'domains'):
            web_search_data['domains'] = serialize_to_dict(getattr(item, 'domains', []))

        # Store as JSON string in arguments field
        data['arguments'] = json.dumps(web_search_data)

        # Store call_id if available
        if hasattr(item, 'call_id'):
            data['call_id'] = getattr(item, 'call_id', '')

        # Override event_type to be function_call
        event_type = 'function_call'

    elif hasattr(item, 'content'):
        # Fallback for other types with content
        if isinstance(item.content, list):
            text_contents = []
            for content_item in item.content:
                if hasattr(content_item, 'text'):
                    text_contents.append(content_item.text)
            data['content'] = ' '.join(text_contents) if text_contents else ''
        elif hasattr(item, 'text'):
            data['content'] = item.text
        else:
            data['content'] = str(item)
    else:
        # For other types, store minimal info
        data['type'] = event_type
    
    return Event(
        id=event_id,
        provider="openai",
        event_type=event_type,
        data=data,
        is_output=True,
        input_event_id=input_event_id
    )


# New data models based on actual database schema

@dataclass
class Trace:
    """Represents a trace (formerly session) from the database"""
    id: str
    status: str
    created_at: str
    test_case_id: Optional[str] = None
    person_id: Optional[str] = None
    eval_output: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trace':
        """Create Trace from API response"""
        # Parse eval_output if it's a string
        eval_output = data.get('eval_output')
        if isinstance(eval_output, str):
            try:
                eval_output = json.loads(eval_output)
            except (json.JSONDecodeError, ValueError):
                eval_output = None

        return cls(
            id=data['id'],
            status=data.get('status', 'pending'),
            created_at=data.get('created_at', ''),
            test_case_id=data.get('test_case_id'),
            person_id=data.get('person_id'),
            eval_output=eval_output
        )


@dataclass
class TestCase:
    """Represents a test case from the test_cases table"""
    id: str
    name: str
    description: str
    annotated_trace: Optional[str] = None
    rubric: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_run_at: Optional[str] = None
    run_summary: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        """Create TestCase from API response"""
        # Parse rubric if it's a string
        rubric = data.get('rubric')
        if isinstance(rubric, str):
            try:
                rubric = json.loads(rubric)
            except (json.JSONDecodeError, ValueError):
                rubric = None

        # Parse run_summary if it's a string
        run_summary = data.get('run_summary')
        if isinstance(run_summary, str):
            try:
                run_summary = json.loads(run_summary)
            except (json.JSONDecodeError, ValueError):
                run_summary = None

        return cls(
            id=data['id'],
            name=data.get('name', ''),
            description=data.get('description', ''),
            annotated_trace=data.get('annotated_trace'),
            rubric=rubric,
            user_id=data.get('user_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            last_run_at=data.get('last_run_at'),
            run_summary=run_summary
        )


@dataclass
class EndpointEvent:
    """Represents an endpoint event for replay"""
    name: str
    arguments: Dict[str, Any]
    function_key: str
    timestamp: str = ""
    id: str = ""

    def get(self, key: str, default=None):
        """Access event attributes for backward compatibility"""
        if key == "arguments":
            return self.arguments
        elif key == "name":
            return self.name
        elif key == "function_key":
            return self.function_key
        return default

    def __repr__(self):
        return f"EndpointEvent(name={self.name}, function_key={self.function_key})"


@dataclass
class EvaluationCriterion:
    """Represents a single evaluation criterion with score"""
    name: str
    category: str
    definition: str
    scale: Dict[str, str]
    score: Optional[float] = None
    reasoning: Optional[str] = None


@dataclass
class EvaluationResult:
    """Represents evaluation results for a trace"""
    score: float  # Average score (0-100 scale for compatibility)
    passed: bool
    average_score: float  # Raw average (1-5 scale)
    criteria: List[Dict[str, Any]]
    rubric_name: str = ""
    trace_id: str = ""
    test_case_id: str = ""

    @classmethod
    def from_eval_output(cls, eval_output: Dict[str, Any], trace_id: str = "", test_case_id: str = "") -> 'EvaluationResult':
        """Create EvaluationResult from eval_output dict"""
        avg_score = eval_output.get('average_score', 0.0)

        # Convert 1-5 scale to 0-100 for backward compatibility
        score_0_100 = (avg_score - 1) * 25 if avg_score > 0 else 0

        return cls(
            score=score_0_100,
            passed=eval_output.get('passed', False),
            average_score=avg_score,
            criteria=eval_output.get('criteria', []),
            rubric_name=eval_output.get('rubric_name', ''),
            trace_id=trace_id,
            test_case_id=test_case_id
        )

    def __repr__(self):
        return f"EvaluationResult(score={self.score:.1f}, passed={self.passed}, avg={self.average_score:.2f})"


class Judge:
    """Handles evaluation for a test case trace.

    The Judge class encapsulates the evaluation logic for a specific test case
    and trace, providing a clean interface for triggering and retrieving
    evaluation results.
    """

    def __init__(self, test_case_id: str, trace_id: str, client: Any, headers: Dict[str, str]):
        """Initialize the Judge with test case and trace information.

        Args:
            test_case_id: The ID of the test case being evaluated
            trace_id: The ID of the trace to evaluate
            client: HTTP client for API calls (httpx.Client)
            headers: Authorization headers for API calls
        """
        self.test_case_id = test_case_id
        self.trace_id = trace_id
        self._client = client
        self._headers = headers

    def evaluate(self, wait: bool = True, max_wait: int = 30) -> EvaluationResult:
        """Get or trigger evaluation for the trace.

        Args:
            wait: Whether to wait for evaluation to complete (default True)
            max_wait: Maximum seconds to wait for evaluation (default 30)

        Returns:
            EvaluationResult with score, passed status, and criteria details
        """
        import time
        import logging

        logger = logging.getLogger(__name__)

        # Import here to avoid circular dependency
        from . import state
        from .core import get_trace

        # First, check if evaluation already exists
        trace = get_trace(self.trace_id)

        if trace.eval_output:
            # Evaluation already exists, return it
            logger.info(f"Found existing evaluation for trace {self.trace_id}")
            return EvaluationResult.from_eval_output(
                trace.eval_output,
                trace_id=self.trace_id,
                test_case_id=self.test_case_id
            )

        # No evaluation yet, trigger it
        logger.info(f"Triggering evaluation for trace {self.trace_id}")

        # Update trace status to evaluating
        self._client.patch(
            f"{state.server_url}/traces/{self.trace_id}",
            json={"status": "evaluating"},
            headers=self._headers
        )

        # Trigger evaluation
        response = self._client.get(
            f"{state.server_url}/tests/{self.test_case_id}/traces/{self.trace_id}/evaluate",
            headers=self._headers
        )

        if response.status_code != 202:
            raise Exception(f"Failed to trigger evaluation (status {response.status_code})")

        if not wait:
            # Return empty result if not waiting
            return EvaluationResult(
                score=0,
                passed=False,
                average_score=0,
                criteria=[],
                trace_id=self.trace_id,
                test_case_id=self.test_case_id
            )

        # Wait for evaluation to complete
        start_time = time.time()
        while (time.time() - start_time) < max_wait:
            time.sleep(2)  # Poll every 2 seconds

            trace = get_trace(self.trace_id)
            if trace.eval_output:
                logger.info(f"Evaluation complete for trace {self.trace_id}")
                return EvaluationResult.from_eval_output(
                    trace.eval_output,
                    trace_id=self.trace_id,
                    test_case_id=self.test_case_id
                )

            if trace.status == "complete":
                # Trace is complete but no eval_output
                logger.warning(f"Trace {self.trace_id} complete but no evaluation found")
                break

        # Timeout or no evaluation
        logger.warning(f"Evaluation did not complete within {max_wait} seconds")
        return EvaluationResult(
            score=0,
            passed=False,
            average_score=0,
            criteria=[],
            session_id=self.session_id,
            test_case_id=self.test_case_id
        )