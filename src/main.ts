import * as core from '@actions/core'
import * as exec from '@actions/exec'
import * as fs from 'fs'
import axios from 'axios'
import {DONT_FORWARD} from './envs_to_not_forward'

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

function getTbRef(): string {
  const repoName = process.env.GITHUB_REPOSITORY

  // enable internal PRs to run successfully
  if (
    repoName === 'treebeardtech/treebeard' &&
    process.env.GITHUB_EVENT_NAME === 'pull_request'
  ) {
    const ev = JSON.parse(
      fs.readFileSync(process.env.GITHUB_EVENT_PATH as string).toString()
    )
    return `refs/pull/${ev.number}/merge`
  }

  return fs
    .readFileSync(`${process.env.JKASDFLKJSA || __dirname}/../.git/HEAD`) // sorry webpack
    .toString()
    .replace('ref: ', '')
    .replace('\n', '')
}

async function run(): Promise<void> {
  await exec.exec(`ls -l ${__dirname}`)
  await exec.exec(`ls -l ../${__dirname}`)
  await exec.exec(`ls -l ../../${__dirname}`)
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
    await exec.exec(`pip install -U ${__dirname}/../treebeard-lib`)

    core.endGroup()

    if (apiKey) {
      await exec.exec(
        `treebeard configure --api_key ${apiKey} --user_name ${process.env.GITHUB_REPOSITORY_OWNER}`
      )
    }

    const TREEBEARD_REF = getTbRef()

    if (debug) {
      console.log(`TREEBEARD_REF is ${TREEBEARD_REF}.`)
    }

    const env: {[key: string]: string} = {
      TREEBEARD_REF,
      ...(process.env as {[key: string]: string})
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
      if (DONT_FORWARD.includes(key)) {
        continue
      }
      tbArgs.push('--env', key)
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

    // const status = await exec.exec('treebeard', tbArgs, {
    //   ignoreReturnCode: true,
    //   env
    // })

    // if (status > 0) {
    //   core.setFailed(`Treebeard CLI run failed with status code ${status}`)
    // }
  } catch (error) {
    core.setFailed(error.message)
  }
}

run()
