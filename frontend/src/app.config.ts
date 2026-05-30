export default {
  pages: [
    'pages/welcome/index',
    'pages/input/index',
    'pages/generating/index',
    'pages/quiz/index',
    'pages/report/index',
    'pages/question-bank/index',
    'pages/profile/index',
    'pages/record-detail/index',
    'pages/record-list/index',
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#FFF6E0',
    navigationBarTitleText: 'AI闯关学习',
    navigationBarTextStyle: 'black',
    backgroundColor: '#FFF6E0',
  },
  tabBar: {
    custom: true,
    color: '#141414',
    selectedColor: '#FF5C1A',
    backgroundColor: '#ffffff',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/input/index',
        text: '闯关',
      },
      {
        pagePath: 'pages/question-bank/index',
        text: '题库',
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的',
      },
    ],
  },
}
