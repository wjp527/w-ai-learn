import Taro from '@tarojs/taro'

const PKG_FONT_DIR = 'assets/fonts'

const FONTS = [
  { family: 'ZCOOL KuaiLe', file: 'zcool-kuaile.woff2' },
  { family: 'ZCOOL QingKe HuangYou', file: 'zcool-qingke-huangyou.woff2' },
  { family: 'Ma Shan Zheng', file: 'ma-shan-zheng.woff2' },
] as const

function localFontPath(file: string) {
  return `${Taro.env.USER_DATA_PATH}/${file}`
}

function fileExists(path: string): Promise<boolean> {
  const fs = Taro.getFileSystemManager()
  return new Promise((resolve) => {
    fs.access({
      path,
      success: () => resolve(true),
      fail: () => resolve(false),
    })
  })
}

function copyPkgFontToLocal(pkgPath: string, destPath: string): Promise<void> {
  const fs = Taro.getFileSystemManager()
  return new Promise((resolve, reject) => {
    fs.copyFile({
      srcPath: pkgPath,
      destPath,
      success: () => resolve(),
      fail: (err) => reject(err),
    })
  })
}

function registerFont(family: string, destPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    Taro.loadFontFace({
      family,
      source: `url("${destPath}")`,
      global: true,
      success: () => resolve(),
      fail: (err) => reject(err),
    })
  })
}

async function ensureLocalFont(file: string): Promise<string | null> {
  const destPath = localFontPath(file)
  if (await fileExists(destPath)) {
    return destPath
  }

  const pkgPath = `${PKG_FONT_DIR}/${file}`
  try {
    await copyPkgFontToLocal(pkgPath, destPath)
    return destPath
  } catch {
    return null
  }
}

async function loadOneFont(family: string, file: string) {
  const destPath = await ensureLocalFont(file)
  if (!destPath) return
  await registerFont(family, destPath)
}

/** 后台加载字体，失败静默降级为 PingFang；不阻塞页面渲染 */
export function loadAppFonts() {
  if (Taro.getEnv() !== Taro.ENV_TYPE.WEAPP) {
    return
  }

  void (async () => {
    for (const { family, file } of FONTS) {
      try {
        await loadOneFont(family, file)
      } catch {
        // 使用 font-family 里的 PingFang SC 回退
      }
    }
  })()
}
