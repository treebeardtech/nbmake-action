import * as core from '@actions/core'
import * as exec from '@actions/exec'
import {treebeardRef} from './conf'
import dotenv from 'dotenv'

async function run(): Promise<void> {
  try {
    const apiKey = core.getInput('api-key')
    const notebooks = core.getInput('notebooks')
    const dockerUsername = core.getInput('docker-username')
    const dockerPassword = core.getInput('docker-password')
    const dockerRegistry = core.getInput('docker-registry')
    const notebookEnv = core.getInput('notebook-env')
    const useDocker = core.getInput('use-docker').toLowerCase() === 'true'
    const debug = core.getInput('debug').toLowerCase() === 'true'
    const path = core.getInput('path')

    process.chdir(path)

    const script = []
    core.startGroup('Checking Python is Installed')
    const pythonSetupCheck = await exec.exec('python', [
      '-c',
      'from setuptools import find_namespace_packages'
    ])
    core.endGroup()

    if (pythonSetupCheck !== 0) {
      core.setFailed(
        'Python does not appear to be setup, please include "- uses: actions/setup-python@v2" in your workflow.'
      )
      return
    }

    core.startGroup('🌲 Install Treebeard')
    await exec.exec(
      `pip install git+https://github.com/treebeardtech/treebeard.git@${treebeardRef}#subdirectory=treebeard-lib`
    )

    core.endGroup()

    if (apiKey) {
      script.push(
        `treebeard configure --api_key ${apiKey} --user_name "$GITHUB_REPOSITORY_OWNER"`
      )
    }

    const notebookEnvObj = notebookEnv ? dotenv.parse(notebookEnv) : {}
    const envs = []
    if (notebookEnvObj) {
      for (const key of Object.keys(notebookEnvObj)) {
        if (debug) {
          console.log(`Treebeard forwarding ${key}`)
        }

        const value = notebookEnvObj[key]
        if (value.startsWith('"') || value.startsWith("'")) {
          console.log(
            `❗ Warning: ${key} starts with a quote. Check notebook-env is correct.`
          )
        }
        envs.push(`--env ${key} `)
      }
    }

    const env: {[key: string]: string} = {
      TREEBEARD_REF: treebeardRef,
      ...process.env,
      ...notebookEnvObj
    }

    if (dockerUsername) {
      env.DOCKER_USERNAME = dockerUsername
    }
    if (dockerPassword) {
      env.DOCKER_PASSWORD = dockerPassword
    }
    if (dockerRegistry) {
      env.DOCKER_REGISTRY = dockerRegistry
    }

    let tbRunCommand = `treebeard run --confirm `
    if (apiKey) {
      tbRunCommand += ' --upload '
    }

    tbRunCommand += envs.join(' ')

    if (notebooks) {
      tbRunCommand += ` --notebooks '${notebooks}' `
    }

    if (!useDocker) {
      tbRunCommand += ' --dockerless '
    }

    if (debug) {
      tbRunCommand += ' --debug '
    }

    script.push(tbRunCommand)

    const status = await exec.exec(
      `bash -c "${script.join(' && ')}"`,
      undefined,
      {
        ignoreReturnCode: true,
        env
      }
    )

    // Ignore status code 2 to allow other reporting mechanisms e.g. slack
    if (status === 2) {
      console.log(
        `Treebeard action ignoring Treebeard CLI failure status code ${status} to enable other notifications.\n\n`
      )
    } else if (status > 0) {
      core.setFailed(`Treebeard CLI run failed with status code ${status}`)
    }
  } catch (error) {
    core.setFailed(error.message)
  }
}

run()
