import { spawn } from 'child_process';


export const runServer = ({ app = "app:api", port = 3000 } = {}) => {
    const importStr = "tests_js.src." + app
    return spawn("poetry", ["run", "hypercorn", "-b", `127.0.0.1:${port}`, importStr], { detached: true })
}
