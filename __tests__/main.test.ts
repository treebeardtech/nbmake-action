import {wait} from '../src/wait'
import * as cp from 'child_process'
import {treebeardRef} from '../src/conf'
import yaml from 'yaml'

import fs from 'fs'
import dotenv from 'dotenv'

test('throws invalid number', async () => {
  const input = parseInt('foo', 10)
  await expect(wait(input)).rejects.toThrow('milliseconds not a number')
})

test('wait 500 ms', async () => {
  const start = new Date()
  await wait(500)
  const end = new Date()
  var delta = Math.abs(end.getTime() - start.getTime())
  expect(delta).toBeGreaterThan(450)
})

test('parse notebook-env', async () => {
  const file = fs.readFileSync('./__tests__/test.yml', 'utf8')
  const obj = yaml.parse(file)
  const parsed = dotenv.parse(obj['notebook-env'])
  console.log(parsed)
  expect(parsed).toStrictEqual({FOO: 'bar', baz: '42'})
})

test('ref is correct', async () => {
  const branch = cp
    .execSync('git rev-parse --abbrev-ref HEAD')
    .toString()
    .replace('\n', '')
  expect(treebeardRef).toBe(branch)
})

// shows how the runner will run a javascript action with env / stdout protocol
// test('test runs', () => {
//   process.env['INPUT_MILLISECONDS'] = '500'
//   const ip = path.join(__dirname, '..', 'lib', 'main.js')
//   const options: cp.ExecSyncOptions = {
//     env: process.env
//   }
//   console.log(cp.execSync(`node ${ip}`, options).toString())
// })
