import * as core from '@actions/core'
import * as exec from '@actions/exec'
import axios from 'axios'

const TREEBEARD_TGZ = `${__dirname}/treebeard-lib.tgz`

async function isUsageLoggingEnabled(): Promise<boolean> {
  const loggingFlag = core.getInput('usage-logging')
  if (loggingFlag === 'false') {
    return false
  }

  if (loggingFlag === 'true') {
    return true
  }

  try {
    // Is repo public?
    await axios.get(`https://github.com/${process.env.GITHUB_REPOSITORY}`)
    return true
  } catch {
    return false
  }
}

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
    const reqFilePath = core.getInput('req-file-path')

    process.chdir(path)

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
    await exec.exec(`pip install -U ${TREEBEARD_TGZ}`)

    core.endGroup()

    if (apiKey) {
      await exec.exec(
        `treebeard configure --api_key ${apiKey} --user_name ${process.env.GITHUB_REPOSITORY_OWNER}`
      )
    }

    const env: {[key: string]: string | undefined} = {
      ...process.env
    }

    function setupDockerCreds(): void {
      if (dockerUsername && dockerPassword === '') {
        if (process.env.GITHUB_EVENT_NAME === 'pull_request') {
          console.log(
            '🐳❌ Not attempting to set up Docker registry as password is missing and this is a pull request'
          )
          return
        }
        throw new Error(
          'Docker username is supplied but password is an empty string, are you missing a secret?'
        )
      }

      if (dockerUsername) {
        env.DOCKER_USERNAME = dockerUsername
      }

      if (dockerPassword) {
        env.DOCKER_PASSWORD = dockerPassword
      }

      if (dockerRegistryPrefix) {
        env.DOCKER_REGISTRY_PREFIX = dockerRegistryPrefix
      }

      if (dockerImageName) {
        env.TREEBEARD_IMAGE_NAME = dockerImageName
      }

      return
    }

    setupDockerCreds()

    const tbArgs = ['run', '--confirm']
    if (apiKey) {
      tbArgs.push('--upload')
    }

    for (const key of Object.keys(env)) {
      if (key.startsWith('TB_')) {
        tbArgs.push('--env', key)
      }
    }

    if (notebooks) {
      tbArgs.push('--notebooks', notebooks)
    }

    tbArgs.push(useDocker ? '--use-docker' : '--no-use-docker')

    if (debug) {
      tbArgs.push('--debug')
    }

    const usageLogging = await isUsageLoggingEnabled()

    if (usageLogging) {
      tbArgs.push('--usagelogging')
    }

    if (reqFilePath) {
      tbArgs.push('--req-file-path', reqFilePath)
    }

    if (debug) {
      console.log(`Treebeard submitting env:\n${Object.keys(env)}`)
    }

    const status = await exec.exec('treebeard', tbArgs, {
      ignoreReturnCode: true,
      env
    })

    if (status > 0) {
      core.setFailed(`Treebeard CLI run failed with status code ${status}`)
    }
  } catch (error) {
    core.setFailed(error.message)
  }
}

run()
