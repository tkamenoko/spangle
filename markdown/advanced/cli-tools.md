---
version: v0.10.0
---

# CLI Tools

`spangle` provides some tools for development.

## `spangle urls-ts`

This command generates a small script to map view names to paths like [`Api.url_for`](../api/api-py.md#Api.url_for) . Parameters of dynamic paths are supported.

### Usage

```shell
spangle urls-ts path.to.app:instance > urls.ts
```

Generated file looks like this:

```ts
// urls.ts
type ViewName = "path.to.app.Index" | "path.to.app.Store" | "path.to.app.Get";
type Params = {
  "path.to.app.Index": {};
  "path.to.app.Store": {};
  "path.to.app.Get": {
    key: string;
  };
};

const tag = (strings: TemplateStringsArray, ...keys: string[]) => {
  const call = (p: { [key: string]: string }) => {
    if (keys.length === 0) {
      return strings.join();
    }
    const parsed = keys
      .map((x) => p[x])
      .filter((x) => typeof x !== "undefined");
    if (Object.keys(parsed).length === 0) {
      return null;
    }
    parsed.push("");
    return strings.map((x, index) => x + parsed[index]).join("");
  };
  return call;
};

const taggedViews = {
  "path.to.app.Index": tag`/`,
  "path.to.app.Store": tag`/store`,
  "path.to.app.Get": tag`/dynamic/${"key"}`,
};

export const urlFor = <T extends ViewName>(
  name: T,
  params: Params[T]
): string => {
  const tagged = taggedViews[name];
  return tagged(params) as T;
};
```

To get a path, use a name of the view class instead of the class itself.
