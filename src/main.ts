import * as core from '@actions/core'
import * as exec from '@actions/exec'
import {treebeardRef} from './conf'

async function run(): Promise<void> {
  try {
    const apiKey = core.getInput('api-key')
    const notebooks = core.getInput('notebooks')
    const dockerUsername = core.getInput('docker-username')
    const dockerPassword = core.getInput('docker-password')
    const dockerImageName = core.getInput('docker-image-name')
    const dockerRegistryPrefix = core.getInput('docker-registry-prefix')
    const useDocker = core.getInput('use-docker').toLowerCase() === 'true'
    const debug = core.getInput('debug').toLowerCase() === 'true'
    const path = core.getInput('path')

    if (dockerUsername && dockerPassword === '') {
      throw new Error(
        'Docker username is supplied but password is an empty string, are you missing a secret?'
      )
    }

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

    const env: {[key: string]: string} = {
      TREEBEARD_REF: treebeardRef,
      ...process.env
    }

    const envsToFwd = []
    for (const key of Object.keys(env)) {
      if (key.startsWith('TB_')) {
        envsToFwd.push(` --env ${key} `)
      }
    }

    if (dockerUsername) {
      env.DOCKER_USERNAME = dockerUsername
    }
    if (dockerPassword) {
      env.DOCKER_PASSWORD = dockerPassword
    }
    if (dockerImageName) {
      env.TREEBEARD_IMAGE_NAME = dockerImageName
    }
    if (dockerRegistryPrefix) {
      env.DOCKER_REGISTRY_PREFIX = dockerRegistryPrefix
    }

    let tbRunCommand = `treebeard run --confirm `
    if (apiKey) {
      tbRunCommand += ' --upload '
    }

    tbRunCommand += envsToFwd.join(' ')

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

    if (debug) {
      console.log(`Treebeard submitting env:\n${Object.keys(env)}`)
    }

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
