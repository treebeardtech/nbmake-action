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
    await exec.exec(
      'pip install git+https://github.com/treebeardtech/treebeard.git@local-docker#subdirectory=treebeard-lib'
    )
    await exec.exec(
      `treebeard configure --api_key ${apiKey} --project_id "$GITHUB_REPOSITORY_OWNER"`
    )

    if (dockerUsername) {
      await exec.exec(`export DOCKER_USERNAME=${dockerUsername}`)
    }
    if (dockerPassword) {
      await exec.exec(`export DOCKER_PASSWORD=${dockerPassword}`)
    }
    if (dockerRegistry) {
      await exec.exec(`export DOCKER_REGISTRY=${dockerRegistry}`)
    }
    const envs = new Array()
    if (notebookEnv) {
      notebookEnv.split('\n').forEach(line => {
        envs.push(`--env ${line.replace(/=.*/, '')} `)
        exec.exec(`export ${line}`)
      })
    }
    await exec.exec(
      `treebeard run --confirm ${envs.join(' ')} --notebooks ${notebooks}`
    )
  } catch (error) {
    core.setFailed(error.message)
  }
}

run()
