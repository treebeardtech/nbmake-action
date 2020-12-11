import * as core from '@actions/core'
import * as exec from '@actions/exec'
import * as fg from 'fast-glob'
import {isOpenUsageLoggingEnabled, Logger} from './logging'
import * as path from 'path'
const isLoggingEnabled = isOpenUsageLoggingEnabled()

async function run(): Promise<void> {
  const logger = isLoggingEnabled ? new Logger() : null
  try {
    const notebooks = core.getInput('notebooks')
    const ignore = core.getInput('ignore')
    const workdir = core.getInput('workdir')
    const pathOutput =
      core.getInput('path-output') && path.resolve(core.getInput('path-output'))
    const verbose = core.getInput('verbose').toLowerCase() === 'true'
    const overwrite = core.getInput('overwrite').toLowerCase() === 'true'
    const extraPytestArgs = core.getInput('extra-pytest-args')

    process.chdir(workdir)

    if (verbose) {
      await exec.exec('bash', ['-c', 'pwd && ls -la'])
    }

    core.startGroup('Install test packages')
    const pkg = `git+https://github.com/treebeardtech/nbmake.git@main${
      pathOutput ? '#egg=nbmake[html]' : ''
    }`
    await exec.exec(`pip install ${pkg}`)
    core.endGroup()

    const paths = notebooks.split('\n').filter(n => n)
    const ignores = ignore.split('\n').filter(i => i)

    const nbs = fg.sync(paths, {ignore: ignores}).map(nb => `'${nb}'`)
    const args = ['pytest', '--nbmake']

    if (pathOutput) {
      args.push(`--path-output=${pathOutput}`)
    }

    args.push(...nbs)
    args.push(...extraPytestArgs.split('\n').filter(i => i))

    const command = args.join(' ')
    if (verbose) {
      args.push('-v')
      console.log(`cmd: ${command}`)
    }

    if (overwrite) {
      args.push('--overwrite')
    }

    await exec.exec('bash', ['-c', command])

    if (logger) {
      logger.logUsage('SUCCESS')
    }
  } catch (error) {
    if (logger) {
      logger.logUsage('FAILURE')
    }
    core.setFailed(error.message)
  }
}

run()
