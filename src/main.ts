import * as core from '@actions/core'
import * as exec from '@actions/exec'
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
    script.push(
      'pip install git+https://github.com/treebeardtech/treebeard.git@local-docker#subdirectory=treebeard-lib'
    )

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

    await exec.exec(`bash -c ${script.join(' && ')}`)
  } catch (error) {
    core.setFailed(error.message)
  }
}

run()
