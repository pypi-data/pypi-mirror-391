"""
Chatsee AI SDK
Production-grade tracker for LLM conversations, tool calls, and errors.
Sends each turn with full metadata to the Chatsee API.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import requests
import uuid
import logging
import warnings
import os

# Set up a logger for the library
logger = logging.getLogger(__name__)

@dataclass
class ToolCall:
    """Represents a tool/function call"""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class ConversationEntry:
    """Represents a single conversation turn"""
    user_message: str
    bot_message: str
    tool_call: int
    tool_calls_details: List[ToolCall]
    error_encountered: int
    exception: Optional[str]
    metadata: Dict[str, Any]
    timestamp: str
    agent_id: str
    user_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return asdict(self)

class ChatseeTracker:
    """
    Main SDK class for tracking LLM conversations and logging them
    to the Chatsee platform.
    """
    
    # The API endpoint is a private, non-configurable class constant.
    _API_ENDPOINT = "https://demo-api.chatsee.ai:8000/v1/api/process_interaction"
    
    def __init__(self, 
                 agent_id: str,
                 user_id: str,
                 tenant_id: str,
                 tenant_name: str,
                 chatsee_api_key: str,
                 session_id: Optional[str] = None,
                 timeout: int = 10,
                 verify_ssl: bool = False):
        """
        Initialize the Chatsee Tracker.
        
        Args:
            agent_id: Unique identifier for the agent (REQUIRED).
            user_id: Unique identifier for the user (REQUIRED).
            tenant_id: Unique identifier for the tenant - must be valid MongoDB ObjectId (REQUIRED).
            tenant_name: Name of the tenant (REQUIRED).
            chatsee_api_key: Your Chatsee API key for authentication (REQUIRED).
            session_id: Optional session identifier (auto-generated if not provided).
            timeout: Request timeout in seconds.
            verify_ssl: Whether to verify SSL certificates. Defaults to True.
        """
        # Validate required parameters
        if not agent_id:
            raise ValueError("agent_id must be provided.")
        if not user_id:
            raise ValueError("user_id must be provided.")
        if not tenant_id:
            raise ValueError("tenant_id must be provided.")
        if not tenant_name:
            raise ValueError("tenant_name must be provided.")
        if not chatsee_api_key:
            raise ValueError("chatsee_api_key must be provided.")
            
        self.agent_id = agent_id
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.chatsee_api_key = chatsee_api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        self.session_id = session_id or self._generate_session_id()
        self.conversation_history: List[ConversationEntry] = []
        self.current_entry: Optional[Dict[str, Any]] = None
        
        # Set up a requests Session for connection pooling and persistent headers
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        if not self.verify_ssl:
            logger.warning(
                "SSL verification is disabled. This is not recommended for production."
            )
            # Suppress InsecureRequestWarning from urllib3
            warnings.filterwarnings('ignore', 'Unverified HTTPS request')

        logger.info(f"ChatseeTracker initialized")
        logger.info(f"Tenant ID: {self.tenant_id}")
        logger.info(f"User ID: {self.user_id}")
        logger.info(f"Tenant Name: {self.tenant_name}")
        logger.info(f"Agent ID: {self.agent_id}")
        logger.info(f"Session ID: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def get_agent_id(self) -> str:
        """Return the agent_id for this tracker instance"""
        return self.agent_id
    
    def get_tenant_id(self) -> str:
        """Return the tenant_id for this tracker instance"""
        return self.tenant_id
    
    def get_tenant_name(self) -> str:
        """Return the tenant_name for this tracker instance"""
        return self.tenant_name
    
    def start_turn(self, 
                   user_message: str, 
                   metadata: Optional[Dict[str, Any]] = None):
        """
        Start tracking a new conversation turn.
        
        Args:
            user_message: The user's input message
            metadata: Optional metadata dictionary
        """
        if self.current_entry is not None:
            logger.warning("A new turn was started before the previous turn ended. "
                           "Call end_turn() to complete the previous turn. Overwriting.")
        
        self.current_entry = {
            'user_message': user_message,
            'bot_message': '',
            'tool_calls': [],
            'error_encountered': 0,
            'exception': None,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.agent_id,
            'user_id': self.user_id 
        }
        logger.debug(f"Turn started for agent: {self.agent_id}")
    
    def log_tool_call(self, tool_name: str, arguments: Dict[str, Any], 
                      result: Optional[Any] = None, error: Optional[str] = None):
        """
        Log a tool/function call that occurred within the current turn.
        
        Args:
            tool_name: Name of the function/tool called.
            arguments: Arguments passed to the tool.
            result: The successful result from the tool (if any).
            error: The error message from the tool (if any).
        """
        if self.current_entry is None:
            raise RuntimeError("Must call start_turn() before logging tool calls.")
        
        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            error=error
        )
        self.current_entry['tool_calls'].append(tool_call)
        logger.debug(f"Tool call logged: {tool_name}")
        
        if error:
            self.current_entry['error_encountered'] = 1
            if self.current_entry['exception'] is None:
                self.current_entry['exception'] = error
            logger.warning(f"Tool call error logged for {tool_name}: {error}")
    
    def log_exception(self, exception: Exception):
        """Log an exception that occurred during the turn."""
        if self.current_entry is None:
            raise RuntimeError("Must call start_turn() before logging exceptions.")
        
        self.current_entry['error_encountered'] = 1
        self.current_entry['exception'] = str(exception)
        logger.error(f"General turn exception logged: {exception}", exc_info=True)
    
    def end_turn(self, bot_message: str) -> Optional[ConversationEntry]:
        """
        Complete the current conversation turn and send it to the Chatsee API.
        
        Args:
            bot_message: The final response from the bot.
            
        Returns:
            The ConversationEntry object if logging was successful, else None.
        """
        if self.current_entry is None:
            raise RuntimeError("Must call end_turn() without first calling start_turn().")
        
        self.current_entry['bot_message'] = bot_message
        
        try:
            entry = ConversationEntry(
                user_message=self.current_entry['user_message'],
                bot_message=self.current_entry['bot_message'],
                tool_call=1 if self.current_entry['tool_calls'] else 0,
                tool_calls_details=self.current_entry['tool_calls'],
                error_encountered=self.current_entry['error_encountered'],
                exception=self.current_entry['exception'],
                metadata=self.current_entry['metadata'],
                timestamp=self.current_entry['timestamp'],
                agent_id=self.current_entry['agent_id'],
                user_id=self.current_entry['user_id']  
            )
            
            self.conversation_history.append(entry)
            
            # Send full data to API
            self._send_to_api(entry)
            
            return entry
            
        except Exception as e:
            logger.error(f"Failed to finalize and send turn: {e}", exc_info=True)
            return None
        finally:
            # Always reset the current turn, even if API send fails
            self.current_entry = None
            logger.debug("Turn ended and reset.")

    def _send_to_api(self, entry: ConversationEntry):
        """Internal method to send the completed turn data to the API."""
        
        try:
            # Convert tool calls to dict format for JSON serialization
            tool_calls_dicts = [asdict(tc) for tc in entry.tool_calls_details]
            
            payload = {
                'session_id': self.session_id,
                'user_id': self.user_id,
                'agent_id': entry.agent_id,
                'tenant_id': self.tenant_id,
                'tenant_name': self.tenant_name,
                'chatsee_api_key': self.chatsee_api_key,  # NEW: Include API key in payload
                'user_message': entry.user_message,
                'bot_message': entry.bot_message,
                'tool_call': entry.tool_call,
                'tool_calls_details': tool_calls_dicts,
                'error_encountered': entry.error_encountered,
                'exception': entry.exception,
                'metadata': entry.metadata
            }
            
            # Use the private class constant _API_ENDPOINT
            response = self.session.post(
                self._API_ENDPOINT, 
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # Raise an exception for bad status codes (4xx, 5xx)
            response.raise_for_status() 
            
            response_data = response.json()
            interaction_id = response_data.get('interaction_id', 'N/A')
            
            logger.info(f"Successfully sent turn to API. "
                        f"Status: {response.status_code}. "
                        f"Interaction ID: {interaction_id}")
            
        except requests.exceptions.HTTPError as e:
            # Handle 4xx/5xx errors with detailed error message
            error_detail = "Unknown error"
            try:
                error_response = e.response.json()
                error_detail = error_response.get('detail', e.response.text)
            except:
                error_detail = e.response.text
                
            logger.error(f"API Error: Failed to send turn data. "
                         f"Status Code: {e.response.status_code}. "
                         f"Error: {error_detail}", exc_info=True)
        except requests.exceptions.ConnectionError as e:
            # Handle DNS/Connection errors
            logger.error(f"Connection Error: Failed to connect to {self._API_ENDPOINT}. "
                         f"Check network/DNS. Error: {e}", exc_info=True)
        except requests.exceptions.Timeout as e:
            # Handle request timeout
            logger.error(f"Timeout Error: Request to {self._API_ENDPOINT} timed out "
                         f"after {self.timeout}s. Error: {e}", exc_info=True)
        except requests.exceptions.RequestException as e:
            # Handle other requests errors
            logger.error(f"API Log ERROR: Failed to send turn data to {self._API_ENDPOINT}. "
                         f"Error: {e}", exc_info=True)
        except json.JSONDecodeError as e:
            # Handle cases where API returns invalid JSON
            logger.error(f"API Response Error: Failed to decode JSON response from API. "
                         f"Error: {e}. Response Text: {response.text}", exc_info=True)

    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get all conversation entries as dictionaries"""
        return [entry.to_dict() for entry in self.conversation_history]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the current session"""
        total_turns = len(self.conversation_history)
        tool_calls_count = sum(1 for entry in self.conversation_history if entry.tool_call)
        errors_count = sum(1 for entry in self.conversation_history if entry.error_encountered)
        
        return {
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'tenant_name': self.tenant_name,
            'total_turns': total_turns,
            'tool_calls_count': tool_calls_count,
            'errors_count': errors_count,
            'conversation_history': self.get_conversation_history()
        }
    
    def export_json(self, filepath: Optional[str] = None) -> str:
        """Export conversation history summary to a JSON file or string"""
        data = self.get_summary()
        try:
            json_str = json.dumps(data, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to serialize summary to JSON: {e}", exc_info=True)
            return "{}"
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(json_str)
                logger.info(f"Summary successfully exported to {filepath}")
            except IOError as e:
                logger.error(f"Failed to write summary to file {filepath}: {e}", exc_info=True)
        
        return json_str
    
    def print_summary(self):
        """Print a formatted summary to the console"""
        summary = self.get_summary()
        print(f"\n{'='*60}")
        print(f"Tenant ID: {self.tenant_id}")
        print(f"Tenant Name: {self.tenant_name}")
        print(f"Agent ID: {self.agent_id}")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*60}")
        
        if not self.conversation_history:
            print("No turns have been logged in this session.")
        
        for idx, entry in enumerate(self.conversation_history, 1):
            print(f"\n--- Turn {idx} [{entry.timestamp}] ---")
            print(f"User: {entry.user_message}")
            print(f"Bot: {entry.bot_message}")
            print(f"Tool Call: {'Yes' if entry.tool_call else 'No'}")
            if entry.tool_calls_details:
                print(f"Tool Calls Details:")
                for tc in entry.tool_calls_details:
                    print(f"  - {tc.tool_name}")
                    print(f"    Args: {tc.arguments}")
                    if tc.result:
                        print(f"    Result: {tc.result}")
                    if tc.error:
                        print(f"    Error: {tc.error}")
            print(f"Error Encountered: {'Yes' if entry.error_encountered else 'No'}")
            if entry.exception:
                print(f"Exception: {entry.exception}")
            if entry.metadata:
                print(f"Metadata: {entry.metadata}")
        
        print(f"\n{'='*60}")
        print(f"Total Turns: {summary['total_turns']}")
        print(f"Tool Calls: {summary['tool_calls_count']}")
        print(f"Errors: {summary['errors_count']}")
        print(f"{'='*60}\n")