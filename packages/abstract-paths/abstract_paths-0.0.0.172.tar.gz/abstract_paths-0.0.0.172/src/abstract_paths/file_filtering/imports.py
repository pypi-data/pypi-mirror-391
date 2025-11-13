from abstract_utilities.file_utils import *
def get_file_filters(*args,**kwargs):
    recursive = kwargs.get('recursive',True)
    include_files = kwargs.get('include_files',True)
    kwargs= get_safe_canonical_kwargs(*args,**kwargs)
    cfg = define_defaults(**kwargs)
    allowed = kwargs.get("allowed") or make_allowed_predicate(cfg)
    directories = [r for r in make_list(kwargs.get("directories")) if r]
    return directories,cfg,allowed,include_files,recursive
