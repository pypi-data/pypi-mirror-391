from xl_router.router import Router
from flask import Flask, request
from flask.json import JSONEncoder
from importlib import import_module
from typing import Optional
import decimal
import os
import glob


class JsonEncoder(JSONEncoder):
    """Custom JSON encoder that handles Decimal objects"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return JSONEncoder.default(self, obj)


class App(Flask):
    """Extended Flask application with resource registration capabilities"""
    resources = []

    def __init__(self, config, *args, **kwargs):
        """Initialize app with custom JSON encoder and config"""
        super().__init__('', *args, **kwargs)
        self._configure_json()
        self._load_config(config)

    def _configure_json(self):
        """Configure JSON settings"""
        self.json_provider_class = JsonEncoder
        self.json.ensure_ascii = False

    def _load_config(self, config):
        """Load configuration from dict or file"""
        if isinstance(config, dict):
            self.config.from_mapping(config)
        elif isinstance(config, str) and config.endswith('.py'):
            self.config.from_pyfile(config)

    def register_extensions(self):
        """Register Flask extensions"""
        pass

    def register_resources(self):
        """Register blueprints for all resources"""
        print(f"register_resources called on {type(self).__name__} with root_path: {self.root_path}")
        # Get the app directory path (inside the flask app root path)
        app_dir = os.path.join(self.root_path, 'app')

        if not os.path.exists(app_dir):
            # If still not found, skip auto-discovery
            return

        # Find all directories in app that contain resource*.py files
        for item in os.listdir(app_dir):
            module_dir = os.path.join(app_dir, item)
            if not os.path.isdir(module_dir) or item.startswith('__'):
                continue

            # Check if this directory contains any resource*.py files
            resource_pattern = os.path.join(module_dir, 'resource*.py')
            resource_files = glob.glob(resource_pattern)

            if resource_files:
                # Import all resource files first (this will make resource classes available)
                imported_modules = []
                for resource_file in resource_files:
                    filename = os.path.basename(resource_file)[:-3]  # remove .py extension
                    try:
                        module = import_module(f'app.{item}.{filename}')
                        imported_modules.append((module, resource_file))
                    except (ImportError, AttributeError, Exception):
                        # Ignore import errors (some modules may not be ready yet)
                        pass

                # Create router for this module
                router = Router(item)

                # Manually add resources from the imported modules
                from xl_router.router import ResourceLoader
                resource_classes = []
                for module, file_path in imported_modules:
                    resource_classes.extend(ResourceLoader.get_resource_classes_from_module(module, file_path))
                router.add_resources(resource_classes)

                # Register the router
                self.register_blueprint(router)


class RequestUtils:
    """Utility class for handling request-related operations"""
    
    @staticmethod
    def get_user_agent() -> str:
        """Get lowercase user agent string"""
        return request.user_agent.string.lower()

    @staticmethod
    def get_ip() -> str:
        """Get client IP address"""
        nodes = request.headers.getlist("X-Forwarded-For")
        return nodes[0] if nodes else request.remote_addr

    @staticmethod
    def get_rule():
        """Get current URL rule"""
        return request.url_rule

    @classmethod
    def get_platform(cls) -> int:
        """
        Get platform identifier
        Returns:
            1: Desktop (Windows/Mac)
            2: Mobile/Other
        """
        user_agent = cls.get_user_agent()
        if 'windows' in user_agent:
            return 1
        if 'mac os' in user_agent and 'iphone' not in user_agent:
            return 1
        return 2