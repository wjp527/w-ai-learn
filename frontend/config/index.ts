import path from 'path'

const config = {
  projectName: 'frontend',
  date: '2026-5-27',
  designWidth: 375,
  deviceRatio: {
    640: 2.34 / 2,
    750: 1,
    375: 2,
    828: 1.81 / 2,
  },
  sourceRoot: 'src',
  outputRoot: 'dist',
  plugins: [],
  defineConstants: {},
  copy: {
    patterns: [
      {
        from: 'src/assets/fonts/',
        to: 'assets/fonts/',
      },
    ],
    options: {},
  },
  framework: 'react',
  compiler: 'webpack5',
  cache: {
    enable: false,
  },
  mini: {
    postcss: {
      pxtransform: {
        enable: true,
        config: {},
      },
      cssModules: {
        enable: false,
      },
    },
    webpackChain(chain) {
      chain.module
        .rule('font-files')
        .test(/\.(woff2?|ttf|eot|otf)(\?.*)?$/i)
        .type('asset/resource')
        .set('generator', {
          filename: 'assets/fonts/[name][ext][query]',
        })
    },
  },
  h5: {
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
      },
      cssModules: {
        enable: false,
      },
    },
  },
  alias: {
    '@': path.resolve(__dirname, '..', 'src'),
  },
}

export default function mergeConfig(merge) {
  if (process.env.NODE_ENV === 'development') {
    return merge({}, config, require('./dev'))
  }
  return merge({}, config, require('./prod'))
}
