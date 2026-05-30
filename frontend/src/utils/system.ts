import Taro from '@tarojs/taro'

export interface NavLayout {
  statusBarHeight: number
  navContentHeight: number
}

let cachedLayout: NavLayout | null = null

/** 微信小程序 custom 导航栏布局（状态栏 + 导航内容区） */
export function getNavLayout(): NavLayout {
  if (cachedLayout && cachedLayout.statusBarHeight > 0) return cachedLayout

  try {
    const info = Taro.getWindowInfo?.() ?? Taro.getSystemInfoSync()
    const rawStatusBar = info.statusBarHeight ?? 0
    const statusBarHeight = rawStatusBar > 0 ? rawStatusBar : 20

    const menuButton = Taro.getMenuButtonBoundingClientRect?.()
    let navContentHeight = 44
    if (menuButton && menuButton.top > 0 && menuButton.height > 0) {
      navContentHeight = (menuButton.top - statusBarHeight) * 2 + menuButton.height
    }

    cachedLayout = { statusBarHeight, navContentHeight }
    return cachedLayout
  } catch {
    return { statusBarHeight: 20, navContentHeight: 44 }
  }
}

export function refreshNavLayout(): NavLayout {
  cachedLayout = null
  return getNavLayout()
}

export function getStatusBarHeight(): number {
  return getNavLayout().statusBarHeight
}
