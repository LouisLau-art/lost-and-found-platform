import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import utc from 'dayjs/plugin/utc'
import localizedFormat from 'dayjs/plugin/localizedFormat'

// Extend plugins
dayjs.extend(utc)
dayjs.extend(relativeTime)
dayjs.extend(localizedFormat)

// Optionally set locale based on browser
// dayjs.locale(navigator.language?.toLowerCase().startsWith('zh') ? 'zh-cn' : 'en')

export const formatRelative = (dateString) => {
  if (!dateString) return ''
  return dayjs.utc(dateString).local().fromNow()
}

export const formatLocal = (dateString, format = 'LLL') => {
  if (!dateString) return ''
  return dayjs.utc(dateString).local().format(format)
}

export default {
  formatRelative,
  formatLocal
}
