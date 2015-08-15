from __future__ import absolute_import
# ---
import clay


def namespace(prefix=None):
    def config_wrapper(*args, **kwargs):
        if 'prefix' in kwargs:
            pfx = kwargs.pop('prefix')
            if pfx is not None:
                return namespace(prefix=pfx)(*args, **kwargs)
            else:
                return clay.config.get(*args, **kwargs)
        key = '{p}.{k}'.format(p=prefix, k=args[0]) if len(args) > 0 else prefix
        return clay.config.get(*((key,) + args[1:]), **kwargs)
    return config_wrapper
