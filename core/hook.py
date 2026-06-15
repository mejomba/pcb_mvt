from django.apps import apps


def tag_by_app(result, generator, **kwargs):
    for path, path_regex, method, view in generator._get_paths_and_endpoints():
        # view یک instance است، نه تابع as_view → باید __class__ بگیریم
        view_cls = view if isinstance(view, type) else view.__class__
        module = view_cls.__module__

        # view های داخلی خود spectacular (schema/swagger/redoc) را رد کن
        if module.startswith("drf_spectacular"):
            continue

        # گرفتن نام app به شکل تمیز و درست
        app_config = apps.get_containing_app_config(module)
        app_label = app_config.label if app_config else module.split(".")[0]

        operation = result["paths"].get(path, {}).get(method.lower())
        if operation:
            operation["tags"] = [app_label]

    return result