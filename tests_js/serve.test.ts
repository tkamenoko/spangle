import { ChildProcess } from 'child_process';
import got from 'got';
import WebSocket from 'isomorphic-ws';
import * as tests from 'testyts';

import { runServer } from './fixtures';
import { url_for } from './src/urls';

// TODO: improve!

@tests.TestSuite()
export class ServeTests {
    server: ChildProcess | null = null
    host = "http://localhost"
    port = 3000
    origin = `${this.host}:${this.port}`


    @tests.BeforeAll()
    async serve() {
        await new Promise((resolve, reject) => {
            this.server = runServer({ port: this.port })
            setTimeout(resolve, 1000)
        })
    }

    @tests.Test()
    async testGet() {
        const resp = await got(`${this.origin}${url_for("Index", {})}`)
        tests.expect.toBeEqual(resp.statusCode, 200)
        tests.expect.toBeEqual(JSON.parse(resp.body).hello, "world")
    }

    @tests.Test()
    async testPost() {
        let resp = await got(`${this.origin}${url_for("Store", {})}`, { throwHttpErrors: false })
        tests.expect.toBeEqual(resp.statusCode, 404)
        resp = await got.post(`${this.origin}${url_for("Store", {})}`, {
            body: JSON.stringify({ hello: "world" }), headers: { "content-type": "application/json" }
        })
        tests.expect.toBeEqual(resp.statusCode, 200)
        tests.expect.toBeTrue(JSON.parse(resp.body).accepted)
        resp = await got(`${this.origin}${url_for("Store", {})}?key=hello`)
        tests.expect.toBeEqual(JSON.parse(resp.body).result, "world")
    }

    @tests.Test()
    async testDynamic() {
        let resp = await got(`${this.origin}${url_for("GetStored", { key: "dynamic" })}`, { throwHttpErrors: false })
        tests.expect.toBeEqual(resp.statusCode, 404)
        resp = await got.post(`${this.origin}${url_for("Store", {})}`, {
            body: JSON.stringify({ dynamic: "value" }), headers: { "content-type": "application/json" }
        })
        tests.expect.toBeEqual(resp.statusCode, 200)
        tests.expect.toBeTrue(JSON.parse(resp.body).accepted)
        resp = await got(`${this.origin}${url_for("GetStored", { key: "dynamic" })}`)
        tests.expect.toBeEqual(JSON.parse(resp.body).result, "value")
    }

    @tests.Test()
    async testWebSocket() {
        const ws = new WebSocket("ws://localhost:3000/websocket", { origin: this.origin })
        let sent = false
        ws.onmessage = (event) => {
            tests.expect.toBeEqual(event.data, "you said `hello` .")
            sent = true
        }
        ws.onopen = (event) => {
            ws.send("hello")
        }

        await new Promise((resolve, reject) => {
            setTimeout(() => {
                resolve()
            }, 1000)
        }).then(() => { tests.expect.toBeTrue(sent) })

    }


    @tests.afterAll()
    close() {
        if (this.server) {
            process.kill(-this.server.pid, "SIGINT")
        } else {
            throw "No Server!";
        }
    }
}