
import { computed, type MaybeRefOrGetter, toValue } from 'vue'

interface ProgressData {
  status?: 'in_progress' | 'completed' | 'failed'
  progress?: number
}

interface ProgressMessages {
  processing: string
  completed: string
  failed: string
  processingDescription: string
  completedDescription: string
  failedDescription: string
}

export const useProgress = (
  progress: MaybeRefOrGetter<ProgressData | null | undefined>,
  isProgressError: MaybeRefOrGetter<boolean>,
  messages: ProgressMessages
) => {
  const status = computed(() => {
    if (toValue(isProgressError)) return 'failed'
    return toValue(progress)?.status || 'in_progress'
  })

  const progressColors = computed(() => {
    switch (status.value) {
      case 'completed':
        return {
          background: 'bg-green-50',
          border: 'border-green-200',
          text: 'text-green-900',
          description: 'text-green-700',
          bar: 'bg-green-600'
        }
      case 'failed':
        return {
          background: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-900',
          description: 'text-red-700',
          bar: 'bg-red-600'
        }
      case 'in_progress':
      default:
        return {
          background: 'bg-blue-50',
          border: 'border-blue-200',
          text: 'text-blue-900',
          description: 'text-blue-700',
          bar: 'bg-blue-600'
        }
    }
  })

  const progressTitle = computed(() => {
    if (toValue(isProgressError) || toValue(progress)?.status === 'failed') return messages.failed
    if (toValue(progress)?.status === 'completed') return messages.completed
    return messages.processing
  })

  const progressDescription = computed(() => {
    if (toValue(isProgressError)) return messages.failedDescription
    if (toValue(progress)?.status === 'completed') return messages.completedDescription
    return messages.processingDescription
  })

  const progressPercentage = computed(() => {
    return toValue(progress)?.progress ?? 0
  })

  return {
    status,
    progressColors,
    progressTitle,
    progressDescription,
    progressPercentage
  }
}
