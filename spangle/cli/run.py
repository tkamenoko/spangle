import argparse
import importlib
import inspect
import os
import sys

from parse import compile
from spangle.api import Api


def urls_ts(args: argparse.Namespace) -> None:
    """
    Print `url_for` function written in TypeScript.

    API is a place of your spangle app, like "path.to.file:instance".
    """

    api: str = args.api
    cwd = os.getcwd()
    sys.path.append(cwd)
    try:
        modulename, api_name = api.rsplit(":", 1)
    except ValueError:
        sys.exit(f"`{api}` is invalid form.")
    module = importlib.import_module(modulename)
    api_instance: Api = getattr(module, api_name)
    reverse_views = {
        f"'{view.__module__}.{view.__name__}'": path
        for view, path in api_instance._reverse_views.items()
    }
    tagged_views = {
        view: "tag`" + path.replace("{", "${'").replace("}", "'}") + "`"
        for view, path in reverse_views.items()
    }
    view_to_tags = (
        "{\n    "
        + ",\n    ".join([f"    {view}: {path}" for view, path in tagged_views.items()])
        + "\n    }"
    )
    view_to_params = {
        view: "{\n"
        + "\n".join(
            [f"         {name}: string;" for name in compile(path).named_fields]
        )
        + "\n        }"
        for view, path in reverse_views.items()
    }
    view_name = " | ".join([f"{name}" for name in reverse_views.keys()])
    params = ";\n    ".join(
        [f"    {view}: {params}" for view, params in view_to_params.items()]
    )
    tag = """
    const tag = (strings: TemplateStringsArray, ...keys: string[]) => {
        const call = (p: { [key: string]: string }) => {
            if(keys.length === 0 ){
                return strings.join();
            }
            const parsed = keys.map(x=>p[x]).filter(x=>typeof x !=="undefined")
            if(Object.keys(parsed).length === 0){
                return null;
            }
            parsed.push("");
            return strings.map((x,index)=>x+parsed[index]).join("");
        }
        return call;
    }
    """
    ts = f"""
    type ViewName = {view_name};
    type Params = {{
    {params}
    }}
    {tag}

    const taggedViews = {view_to_tags};

    export const urlFor = <T extends ViewName>(name: T, params: Params[T]): string => {{
        const tagged = taggedViews[name];
        return tagged(params) as T;
    }}

    """
    ts = inspect.cleandoc(ts)
    print(ts)


parser = argparse.ArgumentParser(description="spangle utility commands.")
subparser = parser.add_subparsers()
urls = subparser.add_parser(name="urls-ts", help=inspect.getdoc(urls_ts))
urls.add_argument("api")
urls.set_defaults(func=urls_ts)


def main():
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
