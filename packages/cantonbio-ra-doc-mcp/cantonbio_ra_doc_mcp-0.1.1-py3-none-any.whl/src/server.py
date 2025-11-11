"""
RA Document MCP Server

Run:
    uv run src.server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
from src import extract_quality_standards
from src import fill_quality_standards
import os
import logging
import traceback
# Create an MCP server
mcp = FastMCP("ra-doc-mcp")


# Initialize LOG_FILE variable without assigning a value
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(ROOT_DIR, "ra-file-mcp.log")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize EXCEL_FILES_PATH variable without assigning a value
DOCX_FILES_PATH = None

def get_docx_path(filename: str) -> str:
    """Get full path to Excel file.
    
    Args:
        filename: Name of Excel file
        
    Returns:
        Full path to Excel file
    """
    # If filename is already an absolute path, return it
    if os.path.isabs(filename):
        return filename

    # Check if in SSE mode (EXCEL_FILES_PATH is not None)
    if DOCX_FILES_PATH is None:
        # Must use absolute path
        raise ValueError(f"Invalid filename: {filename}, must be an absolute path when not in SSE mode")

    # In SSE mode, if it's a relative path, resolve it based on EXCEL_FILES_PATH
    return os.path.join(DOCX_FILES_PATH, filename)


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b + 1


# Add an addition tool
@mcp.tool()
def extract_quality_standards_table(doc_path: str) -> str:
    """Extract quality standards table from docx file"""
    try:
        logger.info(f"Starting quality standards extraction for: {doc_path}")
        full_path = get_docx_path(doc_path)
        logger.debug(f"Resolved full path: {full_path}")

        result = extract_quality_standards.extract_quality_standards_table_from_docx(full_path)
        logger.info(f"Successfully extracted quality standards from: {full_path}")
        return result

    except Exception as e:
        error_msg = f"Error in extract_quality_standards_table: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"Error: {error_msg}"


@mcp.tool()
def fill_quality_standards_table(doc_path: str, markdown_content: str, table_index: int = None) -> str:
    """Fill Word document table with quality standards data from markdown format (modifies file in-place)

    Args:
        doc_path: Path to Word document to modify (absolute path or relative to DOCX_FILES_PATH)
        markdown_content: Markdown table content as string
        table_index: Specific table index to fill (None for auto-detection)

    Returns:
        Success message or error description
    """
    try:
        logger.info(f"Starting in-place table filling for: {doc_path}")

        # Resolve path
        full_doc_path = get_docx_path(doc_path)
        logger.debug(f"Resolved document path: {full_doc_path}")

        # Fill the document in-place
        result = fill_quality_standards.fill_quality_standards_inplace(
            full_doc_path, markdown_content, table_index, auto_merge=True
        )

        logger.info(f"Successfully filled quality standards table in-place: {result}")
        return result

    except Exception as e:
        error_msg = f"Error in fill_quality_standards_table: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"Error: {error_msg}"


# @mcp.tool()
# def extract_quality_standards_from_content(file_content_base64: str) -> str:
#     """
#     Extract quality standards table from Word document content (not file path)

#     Args:
#         file_content_base64: Base64 encoded Word document content

#     Returns:
#         Markdown formatted quality standards table
#     """
#     try:
#         file_bytes = base64.b64decode(file_content_base64)
#         return extract_quality_standards.extract_quality_standards_table_from_bytes(file_bytes)
#     except Exception as e:
#         return f"Error decoding or processing file content: {e}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

if __name__ == "__main__":
    mcp.run(transport='stdio')