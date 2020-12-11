import {Logger} from '../src/logging'

test('log test event', async () => {
  const logger = new Logger()
  process.env.GITHUB_REPOSITORY = 'treebeardtech/test'
  process.env.GITHUB_RUN_ID = 'test'
  process.env.GITHUB_SHA = ''
  process.env.GITHUB_REF = ''

  const success = await logger.logUsage('TEST')
  //   expect(success).toBe(true)
})
