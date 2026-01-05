import { Button, Card, Space, Typography, Alert } from 'antd'
import { useNavigate } from 'react-router-dom'
import { ThunderboltOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { loadMockData, clearMockData } from '@/utils/mockData'

const { Title, Paragraph } = Typography

/**
 * 演示页面 - 加载模拟数据用于测试
 */
const Demo = () => {
  const navigate = useNavigate()

  const handleLoadMockData = () => {
    loadMockData()
    navigate('/')
  }

  const handleClearData = () => {
    clearMockData()
    window.location.reload()
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2}>
              <ThunderboltOutlined /> 演示模式
            </Title>
            <Paragraph type="secondary">
              使用模拟数据快速体验 CorpPilot 管理驾驶舱的功能
            </Paragraph>
          </div>

          <Alert
            message="提示"
            description="后端服务未运行时，可以使用模拟数据来测试前端功能。模拟数据包含完整的分析结果示例。"
            type="info"
            showIcon
          />

          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Card type="inner" title="模拟数据内容">
              <ul>
                <li>总成本: ¥1,250,000</li>
                <li>平均工时: 9.5 小时</li>
                <li>异常记录: 42 条</li>
                <li>部门统计: 8 个部门</li>
                <li>项目 Top 10: 10 个项目</li>
              </ul>
            </Card>

            <Space style={{ width: '100%', justifyContent: 'center' }}>
              <Button
                type="primary"
                size="large"
                icon={<EyeOutlined />}
                onClick={handleLoadMockData}
              >
                加载模拟数据并查看
              </Button>
              <Button
                danger
                size="large"
                icon={<DeleteOutlined />}
                onClick={handleClearData}
              >
                清除所有数据
              </Button>
            </Space>
          </Space>

          <Alert
            message="注意事项"
            description={
              <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                <li>模拟数据仅用于开发和测试</li>
                <li>导出功能需要后端服务支持</li>
                <li>生产环境请使用真实数据</li>
              </ul>
            }
            type="warning"
            showIcon
          />
        </Space>
      </Card>
    </div>
  )
}

export default Demo


