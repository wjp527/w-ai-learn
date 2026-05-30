import Taro from '@tarojs/taro'

export function setTabBarIndex(index: number) {
  const page = Taro.getCurrentInstance().page as
    | (Taro.PageInstance & { getTabBar?: () => { setSelected?: (i: number) => void } })
    | undefined
  page?.getTabBar?.()?.setSelected?.(index)
}
