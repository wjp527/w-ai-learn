import { View } from '@tarojs/components'

type MascotVariant = 'full' | 'mini' | 'sleep'

interface MascotProps {
  variant?: MascotVariant
  className?: string
}

export function Mascot({ variant = 'mini', className = '' }: MascotProps) {
  if (variant === 'full') {
    return (
      <View className={`mascot mascot--full ${className}`}>
        <View className='mascot-svg mascot-svg--full' />
      </View>
    )
  }

  if (variant === 'sleep') {
    return (
      <View className={`mascot mascot--sleep ${className}`}>
        <View className='mascot-svg mascot-svg--sleep' />
      </View>
    )
  }

  return (
    <View className={`mascot mascot--mini ${className}`}>
      <View className='mascot-svg mascot-svg--mini' />
    </View>
  )
}
