import * as core from '@actions/core'
import * as exec from '@actions/exec'
import * as io from '@actions/io'
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
    const pythonSetupCheck = await exec.exec('python', [
      '-c',
      'from setuptools import find_namespace_packages'
    ])

    if (pythonSetupCheck !== 0) {
      core.setFailed(
        'Python does not appear to be setup, please include "- uses: actions/setup-python@v2" in your workflow.'
      )
      return
    }

    core.startGroup('🌲 Install Treebeard')
    script.push(
      'pip install git+https://github.com/treebeardtech/treebeard.git@local-docker#subdirectory=treebeard-lib'
    )
    core.endGroup()

    if (apiKey) {
      script.push(
        `treebeard configure --api_key ${apiKey} --project_id "$GITHUB_REPOSITORY_OWNER"`
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
    const envs = new Array()
    if (notebookEnv) {
      notebookEnv.split('\n').forEach(line => {
        console.log(`Treebeard forwarding ${line}`)
        envs.push(`--env ${line.replace(/=.*/, '')} `)
        script.push(`export ${line}`)
      })
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

    await exec.exec(`bash -c "${script.join(' && ')}"`)
  } catch (error) {
    core.setFailed(error.message)
  }
}

run()
