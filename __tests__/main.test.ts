import {wait} from '../src/wait'
import * as cp from 'child_process'
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
