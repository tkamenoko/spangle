# CLI Tools

`spangle` provides some tools for development.

## `spangle urls-ts`

This command generates a small script to map view names to paths like [`Api.url_for`](/api/api-py#Api.url_for) . Parameters of dynamic paths are supported.

### Usage

```shell
spangle urls-ts path.to.app:instance > urls.ts
```

Generated file looks like this:

```ts
// urls.ts
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

const reverse_views = {Index: tag`/`, Store: tag`/store/`, Get: tag`/dynamic/${'key'}/`}

export const url_for = (name: string, params: { [key: string]: string } = {}) => {
    const path_func = reverse_views[name];
    return path_func?path_func(params):null;
}

```

To get a path, use a name of the view class instead of the class itself.
