import argparse
import importlib
import inspect
import os
import sys

from spangle.api import Api


def urls_ts(args):
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
    http = api_instance._reverse_views
    views = [cls.__name__ for cls in http]
    paths = [path.replace("{", "${'").replace("}", "'}") for path in http.values()]
    reverse_views = [f"{cls}: tag`{path}`" for cls, path in zip(views, paths)]
    js = f"""
    const tag = (strings: TemplateStringsArray, ...keys: string[]) => {{
        const call = (p: {{ [key: string]: string }}) => {{
            if(keys.length === 0 ){{
                return strings.join();
            }}
            const parsed = keys.map(x=>p[x]).filter(x=>typeof x !=="undefined")
            if(Object.keys(parsed).length === 0){{
                return null;
            }}
            parsed.push("");
            return strings.map((x,index)=>x+parsed[index]).join("");
        }}
        return call;
    }}

    const reverse_views = {{{", ".join(reverse_views)}}}

    export const url_for = (name: string, params: {{ [key: string]: string }} = {{}}) => {{
        const path_func = reverse_views[name];
        return path_func?path_func(params):null;
    }}"""
    js = inspect.cleandoc(js)
    print(js)


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
