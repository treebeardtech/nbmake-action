import axios from 'axios'
import * as core from '@actions/core'

export async function isOpenUsageLoggingEnabled(): Promise<boolean> {
  const loggingFlag = core.getInput('open-usage-logging')
  if (loggingFlag !== 'true') {
    return false
  }

  try {
    // Is repo public?
    await axios.get(`https://github.com/${process.env.GITHUB_REPOSITORY}`)
    return true
  } catch {
    return false
  }
}

export class Logger {
  private startTime: Date = new Date()

  async logUsage(status: string): Promise<boolean> {
    try {
      const env = process.env
      const url = `https://api.treebeard.io/${env.GITHUB_REPOSITORY}/${env.GITHUB_RUN_ID}/log`
      const r = await axios.post(url, {
        status,
        start_time: this.startTime.toISOString(),
        end_time: new Date().toISOString(),
        sha: env.GITHUB_SHA,
        branch: env.GITHUB_REF
      })
      return r.status === 200 && r.data === ''
    } catch {
      return false
    }
  }
}
