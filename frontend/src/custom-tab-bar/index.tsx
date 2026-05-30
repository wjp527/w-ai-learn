import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { Component } from 'react'
import './index.scss'

const TAB_LIST = [
  { pagePath: '/pages/input/index', text: '闯关', icon: 'home' },
  { pagePath: '/pages/question-bank/index', text: '题库', icon: 'list' },
  { pagePath: '/pages/profile/index', text: '我的', icon: 'user' },
]

export default class CustomTabBar extends Component {
  state = {
    selected: 0,
  }

  setSelected(index: number) {
    this.setState({ selected: index })
  }

  switchTab(index: number, url: string) {
    this.setState({ selected: index })
    Taro.switchTab({ url })
  }

  render() {
    const { selected } = this.state

    return (
      <View className='comic-tab-bar'>
        {TAB_LIST.map((tab, index) => (
          <View
            key={tab.pagePath}
            className={`comic-tab-item ${selected === index ? 'comic-tab-item--active' : ''}`}
            onClick={() => this.switchTab(index, tab.pagePath)}
          >
            <View className={`comic-tab-icon comic-tab-icon--${tab.icon}`} />
            <Text className='comic-tab-text'>{tab.text}</Text>
          </View>
        ))}
      </View>
    )
  }
}
