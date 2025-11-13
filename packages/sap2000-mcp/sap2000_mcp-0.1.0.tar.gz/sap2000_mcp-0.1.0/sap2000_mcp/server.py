from mcp.server.fastmcp import FastMCP
from sap2000_mcp.manager import SAP2000Connection

mcp = FastMCP("sap2000-mcp")

# Module-level state: persists across tool calls
sap = SAP2000Connection()

@mcp.tool()
def sap2000_connect(visible: bool = True) -> dict:
    """Connect to SAP2000.
    
    Args:
        visible: Whether to show the software window (default: True)
    
    Returns:
        dict: Connection status and information
    
    Examples:
        sap2000_connect(visible=True)
    """
    return sap.connect(visible=visible)


@mcp.tool()
def sap2000_execute(code: str) -> dict:
    """Execute Python code against the connected software.
    
    The code has access to software API objects. For SAP2000:
    - sap_object: Main SAP2000 API object
    - sap_model: SAP2000 model interface (SapModel)
    
    Args:
        code: Python code to execute
    
    Returns:
        dict: Execution results including status, output, and any errors
    
    Examples:
        sap2000_execute("result = sap_model.GetModelFilename()")
    """
    return sap.execute(code)


@mcp.tool()
def sap2000_status() -> dict:
    """Get current connection status.
    
    Returns:
        dict: Connection status including software name and connection state
    """
    return sap.status()


@mcp.tool()
def sap2000_disconnect() -> dict:
    """Close the current software connection.
    
    Returns:
        dict: Disconnection status
    """
    return sap.disconnect()


@mcp.tool()
def sap2000_is_available() -> bool:
    """Return True if SAP2000 is installed and accessible."""
    return bool(sap.is_available())


def main():
    mcp.run()


if __name__ == "__main__":
    main()
