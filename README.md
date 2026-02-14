# DevTerm Plugin

Extensible plugin system for DevTerm - build and share custom tools.

## Installation

```bash
pip install devterm-plugin
```

## Usage

```bash
# Run the plugin demo
devterm-plugin
```

## Creating Custom Plugins

Create a Python file in the `plugins/` directory:

```python
from devterm_plugin.main import ToolPlugin

class MyPlugin(ToolPlugin):
    name = "my_plugin"
    description = "My custom tool"
    category = "Custom"
    
    def execute(self, input_data):
        text = input_data.get("text", "")
        return {"success": True, "output": text[::-1]}
    
    def get_schema(self):
        return {
            "inputs": [{"name": "text", "type": "string", "label": "Input"}],
            "outputs": [{"name": "output", "type": "string"}]
        }
```

## Built-in Plugins

- **uppercase** - Convert to uppercase
- **reverse** - Reverse text
- **wordcount** - Count words, characters, lines

## Plugin API

- `ToolPlugin` - Base class for plugins
- `PluginManager` - Load and manage plugins
- `discover_plugins()` - Find plugins in directory
- `execute_plugin()` - Run a plugin
