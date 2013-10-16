import sys
import os
import inspect
import logging
import flask
import werkzeug.exceptions

class DynamicAttributeError(AttributeError):
    pass

class Cyborg(object):
    def __init__(self, module, import_path=[]):
        self.module = module
        self.import_path = import_path

    def __getattr__(self, attr):
        attrs = attr.split('.')
        attr_root = attrs.pop(0)
        import_path = self.import_path + [attr_root]

        try:
            if hasattr(self.module, "__getattr__"):
                try:
                    cyborg = self.module.__getattr__(attr_root)
                except DynamicAttributeError:
                    cyborg = getattr(self.module, attr_root)
            else:
                cyborg = getattr(self.module, attr_root)
        except AttributeError:
            module_path = os.path.dirname(self.module.__file__)

            if not (os.path.exists(module_path + '/' + attr_root + ".py")
            or os.path.exists(module_path + '/' + attr_root + "/__init__.py")):
                raise
        
            __import__('.'.join(import_path))

            cyborg = Cyborg(sys.modules['.'.join(import_path)
                ], import_path = import_path)
                
        if attrs:
            if not isinstance(cyborg, Cyborg):
                cyborg = Cyborg(cyborg, import_path = import_path)

            return cyborg.__getattr__('.'.join(attrs))
        return cyborg

    # Internal helper function.
    def _fetch_response(self, consumer, module, request):
        http_method = request.method.lower()

        if not hasattr(module, http_method):
            valid_methods = [func[0].upper()
                for func in inspect.getmembers(
                module, predicate = inspect.isfunction)
            ]

            raise werkzeug.exceptions.MethodNotAllowed(
                valid_methods = valid_methods)

        return getattr(
            getattr(module, http_method), consumer
        )(request)

    # Sets up the default Cyborg routes.
    # Should only ever get called on the root Cyborg object.
    def setup(self, app, human_ext='', machine_ext='.json'):

        # Cyborg foundational routes.
        @app.route('/<path:path>%s' % human_ext, methods=["POST","PUT","DELETE","GET"])
        def human_readable(path):
            return self._fetch_response('human',
                getattr(self, path.replace('/', '.')), flask.request)
    
        @app.route('/<path:path>%s' % machine_ext, methods=["POST","PUT","DELETE","GET"])
        def machine_readable(path):
            return flask.json.jsonify(self._fetch_response('machine',
                getattr(self, path.replace('/', '.')), flask.request)
            )


class DefaultGet(object):
    def __init__(self, obj):
        self.obj_dict = dict(obj)

    def human(self, request):
        return flask.render_template(
            "_human.html", 
            _dict = super(HtmlGet, self).get(request)
        )

    def machine(self, request):
        return self.obj_dict
