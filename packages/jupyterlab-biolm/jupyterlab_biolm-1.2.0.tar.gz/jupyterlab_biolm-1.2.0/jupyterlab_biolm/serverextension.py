"""
JupyterLab Server Extension for BioLM API Proxy
This server extension provides API endpoints to proxy requests to the BioLM API,
avoiding CORS issues by making requests from the server side.
"""
import json
import os
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from jupyter_server.base.handlers import JupyterHandler
import tornado


class BioLMModelsHandler(APIHandler):
    """Handler for fetching BioLM models"""
    
    # Disable XSRF for API endpoints
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self):
        """Fetch models from BioLM API"""
        try:
            # Get API key from Authorization header or query parameter
            api_key = None
            auth_header = self.request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
            else:
                api_key = self.get_query_argument('api_key', None)
            
            # Build request to BioLM API
            url = 'https://biolm.ai/api/ui/community-api-models/'
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'JupyterLab-BioLM-Extension/0.1.0',
            }
            
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            # Make request
            req = Request(url, headers=headers)
            
            try:
                with urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    self.set_status(200)
                    self.set_header('Content-Type', 'application/json')
                    self.finish(json.dumps(data))
            except HTTPError as e:
                error_data = {
                    'error': True,
                    'message': f'API request failed: {e.code} {e.reason}',
                    'status': e.code,
                }
                self.set_status(e.code)
                self.set_header('Content-Type', 'application/json')
                self.finish(json.dumps(error_data))
            except URLError as e:
                error_data = {
                    'error': True,
                    'message': f'Network error: {str(e)}',
                }
                self.set_status(500)
                self.set_header('Content-Type', 'application/json')
                self.finish(json.dumps(error_data))
                
        except Exception as e:
            error_data = {
                'error': True,
                'message': f'Server error: {str(e)}',
            }
            self.set_status(500)
            self.set_header('Content-Type', 'application/json')
            self.finish(json.dumps(error_data))


class BioLMModelDetailsHandler(APIHandler):
    """Handler for fetching individual model details with code examples"""
    
    # Disable XSRF for API endpoints
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def get(self, model_slug):
        """Fetch model details from BioLM API"""
        try:
            # Get API key from Authorization header or query parameter
            api_key = None
            auth_header = self.request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
            else:
                api_key = self.get_query_argument('api_key', None)
            
            # Build request to BioLM API with code_examples and exclude_docs_html
            url = f'https://biolm.ai/api/ui/community-api-models/{model_slug}/?code_examples=true&exclude_docs_html=true'
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'JupyterLab-BioLM-Extension/0.1.0',
            }
            
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            # Make request
            req = Request(url, headers=headers)
            
            try:
                with urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Transform example_payload fields into code_examples format
                    code_examples = []
                    model_slug_from_data = data.get('model_slug', model_slug)
                    
                    # Map action types to their example payload fields
                    action_mapping = {
                        'predict': 'predictor_example_payload',
                        'encode': 'encoder_example_payload',
                        'generate': 'generator_example_payload',
                        'classify': 'classifier_example_payload',
                        'similarity': 'similarity_example_payload',
                        'explain': 'explainer_example_payload',
                        'transform': 'transformer_example_payload',
                    }
                    
                    for action, payload_key in action_mapping.items():
                        payload = data.get(payload_key)
                        if payload and payload.get('items'):
                            items = payload['items']
                            
                            # Determine item type and format
                            if isinstance(items, list) and len(items) > 0:
                                # Check if items are objects with 'sequence' field
                                if isinstance(items[0], dict) and 'sequence' in items[0]:
                                    sequences = [item['sequence'] for item in items]
                                    if len(sequences) == 1:
                                        code = f'result = biolm(entity="{model_slug_from_data}", action="{action}", type="sequence", items="{sequences[0]}")\n\nprint(result)'
                                    else:
                                        seq_list = ', '.join([f'"{seq}"' for seq in sequences])
                                        code = f'result = biolm(entity="{model_slug_from_data}", action="{action}", type="sequence", items=[{seq_list}])\n\nprint(result)'
                                else:
                                    # Handle other item formats
                                    if len(items) == 1:
                                        code = f'result = biolm(entity="{model_slug_from_data}", action="{action}", type="sequence", items={json.dumps(items[0])})\n\nprint(result)'
                                    else:
                                        code = f'result = biolm(entity="{model_slug_from_data}", action="{action}", type="sequence", items={json.dumps(items)})\n\nprint(result)'
                                    
                                code_examples.append({
                                    'action': action,
                                    'code': code
                                })
                    
                    # Add setup example for environment variable (if API key is provided)
                    api_key = None
                    auth_header = self.request.headers.get('Authorization', '')
                    if auth_header.startswith('Bearer '):
                        api_key = auth_header[7:]
                    else:
                        api_key = self.get_query_argument('api_key', None)
                    
                    if api_key:
                        # Add setup example as the first example
                        setup_code = f"import os\nos.environ['BIOLMAI_TOKEN'] = 'YOUR_API_KEY_HERE'  # Replace with your actual API key"
                        code_examples.insert(0, {
                            'action': 'setup',
                            'code': setup_code
                        })
                    
                    # Add code_examples to the response
                    if code_examples:
                        data['code_examples'] = code_examples
                    
                    self.set_status(200)
                    self.set_header('Content-Type', 'application/json')
                    self.finish(json.dumps(data))
            except HTTPError as e:
                error_data = {
                    'error': True,
                    'message': f'API request failed: {e.code} {e.reason}',
                    'status': e.code,
                }
                self.set_status(e.code)
                self.set_header('Content-Type', 'application/json')
                self.finish(json.dumps(error_data))
            except URLError as e:
                error_data = {
                    'error': True,
                    'message': f'Network error: {str(e)}',
                }
                self.set_status(500)
                self.set_header('Content-Type', 'application/json')
                self.finish(json.dumps(error_data))
                
        except Exception as e:
            error_data = {
                'error': True,
                'message': f'Server error: {str(e)}',
            }
            self.set_status(500)
            self.set_header('Content-Type', 'application/json')
            self.finish(json.dumps(error_data))


class BioLMTestConnectionHandler(APIHandler):
    """Handler for testing API connection"""
    
    # Disable XSRF for API endpoints
    def check_xsrf_cookie(self):
        pass
    
    @tornado.web.authenticated
    def post(self):
        """Test connection with API key"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            api_key = data.get('api_key')
            
            if not api_key:
                self.set_status(400)
                self.finish(json.dumps({
                    'error': True,
                    'message': 'API key is required',
                }))
                return
            
            # Test connection by making a request
            url = 'https://biolm.ai/api/ui/community-api-models/'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'JupyterLab-BioLM-Extension/0.1.0',
            }
            
            req = Request(url, headers=headers)
            
            try:
                with urlopen(req, timeout=10) as response:
                    result = {
                        'valid': response.status == 200,
                        'message': 'Connection successful' if response.status == 200 else f'HTTP {response.status}',
                    }
                    self.set_status(200)
                    self.set_header('Content-Type', 'application/json')
                    self.finish(json.dumps(result))
            except HTTPError as e:
                result = {
                    'valid': False,
                    'message': f'Authentication failed: {e.code} {e.reason}',
                }
                self.set_status(200)  # Return 200 with error in body
                self.set_header('Content-Type', 'application/json')
                self.finish(json.dumps(result))
            except URLError as e:
                result = {
                    'valid': False,
                    'message': f'Connection failed: {str(e)}',
                }
                self.set_status(200)
                self.set_header('Content-Type', 'application/json')
                self.finish(json.dumps(result))
                
        except Exception as e:
            error_data = {
                'error': True,
                'message': f'Server error: {str(e)}',
            }
            self.set_status(500)
            self.set_header('Content-Type', 'application/json')
            self.finish(json.dumps(error_data))


def _jupyter_server_extension_points():
    """Return server extension points - this enables auto-discovery in Jupyter Server 2.x"""
    return [{
        'module': 'jupyterlab_biolm.serverextension',
    }]


def _load_jupyter_server_extension(server_app):
    """Load the server extension"""
    web_app = server_app.web_app
    base_url = web_app.settings['base_url']
    
    # Register handlers
    handlers = [
        (url_path_join(base_url, 'biolm', 'api', 'models'), BioLMModelsHandler),
        (url_path_join(base_url, 'biolm', 'api', 'models', r'([^/]+)'), BioLMModelDetailsHandler),
        (url_path_join(base_url, 'biolm', 'api', 'test-connection'), BioLMTestConnectionHandler),
    ]
    
    web_app.add_handlers('.*$', handlers)
    
    server_app.log.info('BioLM server extension loaded')


# For JupyterLab 4.x compatibility
def _jupyter_server_extension_paths():
    """Return server extension paths"""
    return [{
        'module': 'jupyterlab_biolm.serverextension',
    }]


# For JupyterLab 4.x / Jupyter Server 2.x
load_jupyter_server_extension = _load_jupyter_server_extension

# Also register as a function that can be called directly
__all__ = ['_load_jupyter_server_extension', 'load_jupyter_server_extension']

