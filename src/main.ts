import * as core from '@actions/core'
import * as exec from '@actions/exec'
import {branch} from './conf'

async function run(): Promise<void> {
  try {
    const apiKey = core.getInput('api-key')
    const notebooks = core.getInput('notebooks')
    const dockerUsername = core.getInput('docker-username')
    const dockerPassword = core.getInput('docker-password')
    const dockerRegistry = core.getInput('docker-registry')
    const notebookEnv = core.getInput('notebook-env')
    const useDocker = core.getInput('use-docker').toLowerCase() === 'true'

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
      `pip install git+https://github.com/treebeardtech/treebeard.git@${branch}#subdirectory=treebeard-lib`
    )

    core.endGroup()

    if (apiKey) {
      script.push(
        `treebeard configure --api_key ${apiKey} --user_name "$GITHUB_REPOSITORY_OWNER"`
      )
    }

    if (dockerUsername) {
      script.push(`export DOCKER_USERNAME='${dockerUsername}'`)
    }
    if (dockerPassword) {
      script.push(`export DOCKER_PASSWORD='${dockerPassword}'`)
    }
    if (dockerRegistry) {
      script.push(`export DOCKER_REGISTRY='${dockerRegistry}'`)
    }
    const envs = []
    if (notebookEnv) {
      for (const line of notebookEnv.split('\n')) {
        console.log(`Treebeard forwarding ${line}`)
        envs.push(`--env ${line.replace(/=.*/, '')} `)
        script.push(`export ${line}`)
      }
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

    script.push(tbRunCommand)

    const status = await exec.exec(
      `bash -c "${script.join(' && ')}"`,
      undefined,
      {
        ignoreReturnCode: true
      }
    )

    if (status === 1) {
      // Ignore status code > 1 to allow other reporting mechanisms e.g. slack
      core.setFailed(`Treebeard CLI run failed with status code ${status}`)
    } else if (status > 1) {
      console.log(
        `Treebeard action ignoring Treebeard CLI failure status code ${status} to enable other notifications.\n\n`
      )
    }
  } catch (error) {
    core.setFailed(error.message)
  }
}

run()
