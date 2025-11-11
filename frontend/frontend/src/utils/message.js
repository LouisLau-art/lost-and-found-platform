import { ElMessage } from 'element-plus'

const DEFAULT_DURATION = 4000

function withDuration(input) {
  if (typeof input === 'string') {
    return { message: input, duration: DEFAULT_DURATION }
  }
  const opts = input || {}
  if (opts.duration == null) opts.duration = DEFAULT_DURATION
  return opts
}

export const message = {
  success: (input) => ElMessage.success(withDuration(input)),
  error: (input) => ElMessage.error(withDuration(input)),
  info: (input) => ElMessage.info(withDuration(input)),
  warning: (input) => ElMessage.warning(withDuration(input)),
}

export default message
