"""Minimal SAP2000 connection manager (single-software only)."""
from typing import Dict, Any, Optional


class SAP2000Connection:
    """Direct SAP2000 connection without generic adapter plumbing."""
    
    def __init__(self):
        self.connected = False
        self.sap_object = None
        self.sap_model = None
    
    def is_available(self) -> bool:
        try:
            import comtypes.client
            # Try existing instance
            try:
                comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
                return True
            except Exception:
                # Or create a new one
                comtypes.client.CreateObject("CSI.SAP2000.API.SapObject")
                return True
        except Exception:
            return False

    def connect(self, visible: bool = True) -> Dict[str, Any]:
        try:
            import comtypes.client

            try:
                self.sap_object = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
            except Exception:
                self.sap_object = comtypes.client.CreateObject("CSI.SAP2000.API.SapObject")
                # Start the application; visibility handled by SAP defaults
                self.sap_object.ApplicationStart()

            self.sap_model = self.sap_object.SapModel
            self.connected = True

            info = self.sap_model.GetProgramInfo()
            return {
                "status": "connected",
                "software": "SAP2000",
                "version": info[0],
                "build": info[1],
            }
        except Exception as e:
            self.connected = False
            return {"status": "failed", "error": str(e)}
    
    def execute(self, code: str) -> Dict[str, Any]:
        if not self.connected:
            return {"status": "error", "error": "Not connected. Call sap2000_connect first."}

        try:
            context = {"sap_object": self.sap_object, "sap_model": self.sap_model}
            exec(code, context)
            result = context.get("result", None)
            return {"status": "success", "result": result, "output": "Code executed successfully"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def status(self) -> Dict[str, Any]:
        return {"connected": self.connected, "software": "SAP2000" if self.connected else None}
    
    def disconnect(self) -> Dict[str, Any]:
        if not self.connected:
            return {"status": "info", "message": "No active connection"}
        try:
            if self.sap_object:
                try:
                    self.sap_object.ApplicationExit(False)
                except Exception:
                    pass
            self.sap_object = None
            self.sap_model = None
            self.connected = False
            return {"status": "disconnected", "software": "SAP2000"}
        except Exception as e:
            return {"status": "error", "error": f"Error during disconnect: {str(e)}"}

