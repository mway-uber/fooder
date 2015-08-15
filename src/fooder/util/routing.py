import re


DEFAULT_VERBS   = ['GET']
REGEX_NULLABLE  = r'\(.+\)'
REGEX_PARENS    = r'[()]'


"""
A basic clay/flask route factory for reusable decorators and optional named parameters.
A less flexible, more verbose option would be to attach numerous decorators to view functions, i.e.
    @clay.app.route('/users', methods=['GET'])
    @clay.app.route('/users.<format>', methods=['GET'])
    def get_users(**kwargs):
        ...
"""
def RouteFactory(fn, **factoryopts):
    nullable = bool(factoryopts.pop('nullable', False))

    def wrapper(pattern, **wrapperopts):
        patterns = []

        if nullable: # and matches pattern
            patterns.append(re.sub(REGEX_PARENS, '', pattern))
            patterns.append(re.sub(REGEX_NULLABLE, '', pattern))
        else:
            patterns = [pattern]

        def decorator(wrapped):
            # decorator options are lower priority, so we can't do silly things like
            # overwrite the allowed methods of an explicitly-gettable decorator, etc
            opts = wrapperopts.copy()
            opts.update(**factoryopts)
            map(lambda pat: fn(pat, **opts)(wrapped), patterns)
            return wrapped

        return decorator

    return wrapper


def compose(fn, pattern, **kwargs):
    opts = kwargs.copy()
    opts.update({ 'methods': opts.pop('methods', DEFAULT_VERBS) })

    wrapper = RouteFactory(fn, **opts)
    opts.pop('nullable', None)
    return wrapper(pattern, **opts)


RouteFactory.gettable = lambda *args, **kwargs: compose(*args, **dict(kwargs, methods=['GET']))
RouteFactory.postable = lambda *args, **kwargs: compose(*args, **dict(kwargs, methods=['POST']))
RouteFactory.puttable = lambda *args, **kwargs: compose(*args, **dict(kwargs, methods=['PUT']))
RouteFactory.deletable = lambda *args, **kwargs: compose(*args, **dict(kwargs, methods=['DELETE']))
