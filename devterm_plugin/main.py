"""DevTerm Plugin - Extensible plugin system for DevTerm."""

import os
import sys
import importlib
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path


class ToolPlugin(ABC):
    """Base class for DevTerm plugins."""
    
    name: str = "Plugin"
    description: str = "A DevTerm tool plugin"
    category: str = "Custom"
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin with input data."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the input schema for this plugin."""
        pass


class PluginManager:
    """Manages loading and execution of plugins."""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, ToolPlugin] = {}
        self._discovered_plugins: Dict[str, type] = {}
    
    def discover_plugins(self) -> List[str]:
        """Discover all plugins in the plugin directory."""
        discovered = []
        
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True)
            return discovered
        
        for file in self.plugin_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            
            module_name = file.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    # Find ToolPlugin subclasses
                    for name in dir(module):
                        obj = getattr(module, name)
                        if isinstance(obj, type) and issubclass(obj, ToolPlugin) and obj != ToolPlugin:
                            self._discovered_plugins[obj.name] = obj
                            discovered.append(obj.name)
            except Exception as e:
                print(f"Error loading plugin {module_name}: {e}")
        
        return discovered
    
    def load_plugin(self, name: str) -> bool:
        """Load a specific plugin by name."""
        if name in self.plugins:
            return True
        
        if name not in self._discovered_plugins:
            return False
        
        try:
            plugin_class = self._discovered_plugins[name]
            self.plugins[name] = plugin_class()
            return True
        except Exception as e:
            print(f"Error loading plugin {name}: {e}")
            return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self.plugins:
            del self.plugins[name]
            return True
        return False
    
    def execute_plugin(self, name: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a loaded plugin."""
        if name not in self.plugins:
            if not self.load_plugin(name):
                return None
        
        try:
            return self.plugins[name].execute(input_data)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_plugin_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a plugin."""
        if name not in self.plugins:
            if not self.load_plugin(name):
                return None
        
        return self.plugins[name].get_schema()
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all available plugins."""
        return [
            {"name": name, "description": plugin.description, "category": plugin.category}
            for name, plugin in self.plugins.items()
        ]


# === EXAMPLE PLUGINS ===

class UppercasePlugin(ToolPlugin):
    """Convert text to uppercase."""
    
    name = "uppercase"
    description = "Convert text to uppercase"
    category = "Text"
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        return {"success": True, "output": text.upper()}
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "inputs": [{"name": "text", "type": "string", "label": "Input Text"}],
            "outputs": [{"name": "output", "type": "string"}]
        }


class ReversePlugin(ToolPlugin):
    """Reverse text."""
    
    name = "reverse"
    description = "Reverse text"
    category = "Text"
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        return {"success": True, "output": text[::-1]}
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "inputs": [{"name": "text", "type": "string", "label": "Input Text"}],
            "outputs": [{"name": "output", "type": "string"}]
        }


class WordCountPlugin(ToolPlugin):
    """Count words in text."""
    
    name = "wordcount"
    description = "Count words, characters, and lines"
    category = "Text"
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        words = len(text.split())
        chars = len(text)
        lines = len(text.splitlines())
        return {
            "success": True,
            "output": f"Words: {words}\nCharacters: {chars}\nLines: {lines}"
        }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "inputs": [{"name": "text", "type": "string", "label": "Input Text"}],
            "outputs": [{"name": "output", "type": "string"}]
        }


# Built-in plugins
BUILTIN_PLUGINS = {
    "uppercase": UppercasePlugin,
    "reverse": ReversePlugin,
    "wordcount": WordCountPlugin,
}


def main():
    """Main entry point for the plugin system."""
    print("DevTerm Plugin System")
    print("=" * 40)
    
    # Create plugin manager
    manager = PluginManager()
    
    # Discover plugins
    print("\nDiscovering plugins...")
    discovered = manager.discover_plugins()
    print(f"Found {len(discovered)} external plugins")
    
    # Load built-in plugins
    for name, plugin_class in BUILTIN_PLUGINS.items():
        manager.plugins[name] = plugin_class()
    
    print(f"Total plugins: {len(manager.plugins)}")
    
    # List plugins
    print("\nAvailable plugins:")
    for plugin_info in manager.list_plugins():
        print(f"  - {plugin_info['name']}: {plugin_info['description']}")
    
    # Demo
    print("\nDemo - Running plugins:")
    
    result = manager.execute_plugin("uppercase", {"text": "hello world"})
    print(f"  uppercase: {result}")
    
    result = manager.execute_plugin("wordcount", {"text": "Hello world from DevTerm"})
    print(f"  wordcount: {result}")


if __name__ == "__main__":
    main()
