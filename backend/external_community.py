#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
外部社区数据获取模块
支持从 Dify、Coze 等平台获取热门Agent和工作流
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict, Optional
import time

class ExternalCommunityFetcher:
    """外部社区数据获取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_dify_agents(self, limit: int = 20) -> List[Dict]:
        """
        从 Dify Explore 获取热门应用
        
        Args:
            limit: 获取数量
            
        Returns:
            Agent列表
        """
        try:
            print(f"[外部数据] 正在从 Dify Explore 获取数据...")
            
            # 这里需要根据实际的 Dify API 或网页结构调整
            url = "https://api.dify.ai/v1/explore/apps"  # 示例URL，需要确认
            
            # 如果没有公开API，可以爬取网页
            # response = requests.get("https://dify.ai/explore", headers=self.headers)
            # soup = BeautifulSoup(response.text, 'html.parser')
            
            # 示例返回数据（需要根据实际情况调整）
            agents = []
            
            # TODO: 实现实际的爬取逻辑
            
            print(f"[外部数据] ✅ 从 Dify 获取 {len(agents)} 个应用")
            return agents
            
        except Exception as e:
            print(f"[外部数据] ❌ 从 Dify 获取失败: {e}")
            return []
    
    def fetch_coze_agents(self, limit: int = 20) -> List[Dict]:
        """
        从 Coze 广场获取热门Bot
        
        Args:
            limit: 获取数量
            
        Returns:
            Agent列表
        """
        try:
            print(f"[外部数据] 正在从 Coze 广场获取数据...")
            
            # 示例数据（需要根据实际Coze API调整）
            agents = []
            
            # TODO: 实现实际的爬取逻辑
            
            print(f"[外部数据] ✅ 从 Coze 获取 {len(agents)} 个Bot")
            return agents
            
        except Exception as e:
            print(f"[外部数据] ❌ 从 Coze 获取失败: {e}")
            return []
    
    def get_mock_external_data(self) -> Dict[str, List[Dict]]:
        """
        获取模拟的外部数据（用于演示）
        
        Returns:
            包含agents和workflows的字典
        """
        return {
            'agents': [
                # Dify 平台 Agents
                {
                    'id': 'ext_1',
                    'name': 'AI写作助手',
                    'icon': '✍️',
                    'description': '智能生成各类文章，支持多种文体风格和SEO优化，一键生成高质量内容',
                    'author': 'Dify社区',
                    'rating': 4.8,
                    'usageCount': 15234,
                    'likeCount': 3456,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'agent',
                    'tags': ['写作', 'SEO', '内容创作']
                },
                {
                    'id': 'ext_2',
                    'name': '智能客服机器人',
                    'icon': '💬',
                    'description': '24小时在线客服，智能理解用户意图，快速响应常见问题，提升服务质量',
                    'author': 'Coze用户',
                    'rating': 4.9,
                    'usageCount': 28976,
                    'likeCount': 5678,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Coze',
                    'type': 'agent',
                    'tags': ['客服', '对话', '企业服务']
                },
                {
                    'id': 'ext_3',
                    'name': '数据分析专家',
                    'icon': '📊',
                    'description': '自动分析Excel/CSV数据，生成可视化图表和专业分析报告',
                    'author': 'FlowiseAI',
                    'rating': 4.7,
                    'usageCount': 12543,
                    'likeCount': 2890,
                    'isHot': True,
                    'isNew': False,
                    'source': 'FlowiseAI',
                    'type': 'agent',
                    'tags': ['数据分析', '可视化', 'Excel']
                },
                {
                    'id': 'ext_4',
                    'name': '代码审查助手',
                    'icon': '💻',
                    'description': '自动审查代码质量，发现潜在bug，提供优化建议和最佳实践',
                    'author': 'LangFlow',
                    'rating': 4.8,
                    'usageCount': 9876,
                    'likeCount': 2134,
                    'isHot': False,
                    'isNew': True,
                    'source': 'LangFlow',
                    'type': 'agent',
                    'tags': ['代码', '编程', '质量检查']
                },
                {
                    'id': 'ext_5',
                    'name': '简历优化师',
                    'icon': '📄',
                    'description': '智能分析简历短板，匹配岗位JD，生成优化建议，提升求职成功率',
                    'author': 'Dify社区',
                    'rating': 4.6,
                    'usageCount': 18765,
                    'likeCount': 4321,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'agent',
                    'tags': ['简历', '求职', 'HR']
                },
                {
                    'id': 'ext_6',
                    'name': '翻译专家',
                    'icon': '🌍',
                    'description': '支持100+语言互译，保持语境准确，专业术语精准翻译',
                    'author': 'Coze用户',
                    'rating': 4.9,
                    'usageCount': 34567,
                    'likeCount': 7890,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Coze',
                    'type': 'agent',
                    'tags': ['翻译', '多语言', '国际化']
                },
                # 新增更多Agents
                {
                    'id': 'ext_7',
                    'name': '社交媒体运营',
                    'icon': '📱',
                    'description': '智能生成社交媒体文案，分析热点话题，自动发布和互动管理',
                    'author': 'Dify社区',
                    'rating': 4.7,
                    'usageCount': 11234,
                    'likeCount': 2789,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'agent',
                    'tags': ['社交媒体', '运营', '营销']
                },
                {
                    'id': 'ext_8',
                    'name': '法律文书助手',
                    'icon': '⚖️',
                    'description': '智能起草合同、协议等法律文书，提供法律风险分析和建议',
                    'author': 'LangFlow',
                    'rating': 4.8,
                    'usageCount': 8765,
                    'likeCount': 1956,
                    'isHot': False,
                    'isNew': True,
                    'source': 'LangFlow',
                    'type': 'agent',
                    'tags': ['法律', '合同', '文书']
                },
                {
                    'id': 'ext_9',
                    'name': 'PPT设计师',
                    'icon': '🎨',
                    'description': '根据内容自动生成精美PPT，提供多种模板和配色方案',
                    'author': 'Coze用户',
                    'rating': 4.6,
                    'usageCount': 16543,
                    'likeCount': 3876,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Coze',
                    'type': 'agent',
                    'tags': ['PPT', '设计', '演示']
                },
                {
                    'id': 'ext_10',
                    'name': '邮件管理助手',
                    'icon': '📧',
                    'description': '智能分类邮件，自动回复常见问题，邮件优先级排序',
                    'author': 'FlowiseAI',
                    'rating': 4.5,
                    'usageCount': 14321,
                    'likeCount': 2654,
                    'isHot': True,
                    'isNew': False,
                    'source': 'FlowiseAI',
                    'type': 'agent',
                    'tags': ['邮件', '效率', '办公']
                },
                {
                    'id': 'ext_11',
                    'name': '视频脚本创作',
                    'icon': '🎬',
                    'description': '为短视频、Vlog生成创意脚本，包含分镜、台词、画面描述',
                    'author': 'Dify社区',
                    'rating': 4.7,
                    'usageCount': 13456,
                    'likeCount': 3124,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'agent',
                    'tags': ['视频', '脚本', '创作']
                },
                {
                    'id': 'ext_12',
                    'name': '健康饮食顾问',
                    'icon': '🥗',
                    'description': '根据个人体质和需求，定制健康饮食方案和食谱推荐',
                    'author': 'Coze用户',
                    'rating': 4.8,
                    'usageCount': 9876,
                    'likeCount': 2345,
                    'isHot': False,
                    'isNew': True,
                    'source': 'Coze',
                    'type': 'agent',
                    'tags': ['健康', '饮食', '营养']
                },
                {
                    'id': 'ext_13',
                    'name': '财务报表分析',
                    'icon': '💰',
                    'description': '自动分析企业财务报表，生成财务健康度报告和投资建议',
                    'author': 'LangFlow',
                    'rating': 4.9,
                    'usageCount': 7654,
                    'likeCount': 1987,
                    'isHot': False,
                    'isNew': True,
                    'source': 'LangFlow',
                    'type': 'agent',
                    'tags': ['财务', '分析', '投资']
                },
                {
                    'id': 'ext_14',
                    'name': '会议纪要生成',
                    'icon': '📝',
                    'description': '根据会议录音/文字，自动生成结构化会议纪要和待办事项',
                    'author': 'FlowiseAI',
                    'rating': 4.7,
                    'usageCount': 11234,
                    'likeCount': 2567,
                    'isHot': True,
                    'isNew': False,
                    'source': 'FlowiseAI',
                    'type': 'agent',
                    'tags': ['会议', '纪要', '办公']
                },
                {
                    'id': 'ext_15',
                    'name': '品牌命名大师',
                    'icon': '🏷️',
                    'description': '为品牌、产品生成创意名称，提供商标查询和注册建议',
                    'author': 'Dify社区',
                    'rating': 4.6,
                    'usageCount': 8765,
                    'likeCount': 2134,
                    'isHot': False,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'agent',
                    'tags': ['品牌', '命名', '创意']
                },
                {
                    'id': 'ext_16',
                    'name': '学习路径规划',
                    'icon': '📚',
                    'description': '根据目标和基础，制定个性化学习计划和资源推荐',
                    'author': 'Coze用户',
                    'rating': 4.8,
                    'usageCount': 15678,
                    'likeCount': 3890,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Coze',
                    'type': 'agent',
                    'tags': ['学习', '教育', '规划']
                },
                {
                    'id': 'ext_17',
                    'name': '产品需求文档',
                    'icon': '📋',
                    'description': '智能生成PRD文档，包含功能描述、用例图、原型建议',
                    'author': 'LangFlow',
                    'rating': 4.7,
                    'usageCount': 9876,
                    'likeCount': 2345,
                    'isHot': False,
                    'isNew': True,
                    'source': 'LangFlow',
                    'type': 'agent',
                    'tags': ['产品', 'PRD', '需求']
                },
                {
                    'id': 'ext_18',
                    'name': '情感咨询师',
                    'icon': '❤️',
                    'description': '提供情感问题分析和建议，帮助改善人际关系和心理健康',
                    'author': 'FlowiseAI',
                    'rating': 4.9,
                    'usageCount': 21345,
                    'likeCount': 5432,
                    'isHot': True,
                    'isNew': False,
                    'source': 'FlowiseAI',
                    'type': 'agent',
                    'tags': ['情感', '咨询', '心理']
                },
                {
                    'id': 'ext_19',
                    'name': '装修方案设计',
                    'icon': '🏠',
                    'description': '根据户型和预算，提供装修风格建议和材料清单',
                    'author': 'Dify社区',
                    'rating': 4.6,
                    'usageCount': 7654,
                    'likeCount': 1876,
                    'isHot': False,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'agent',
                    'tags': ['装修', '设计', '家居']
                },
                {
                    'id': 'ext_20',
                    'name': '股票投资顾问',
                    'icon': '📈',
                    'description': '分析股票市场趋势，提供投资组合建议和风险评估',
                    'author': 'Coze用户',
                    'rating': 4.7,
                    'usageCount': 13456,
                    'likeCount': 3234,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Coze',
                    'type': 'agent',
                    'tags': ['股票', '投资', '金融']
                }
            ],
            'workflows': [
                # 原有工作流
                {
                    'id': 'ext_wf_1',
                    'name': '全栈内容创作流程',
                    'description': '从主题策划到SEO优化，一键生成高质量文章',
                    'agents': ['主题生成', '大纲撰写', '内容创作', 'SEO优化'],
                    'executionCount': 8765,
                    'successRate': 96.5,
                    'likeCount': 3456,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'workflow',
                    'tags': ['内容创作', 'SEO', '写作']
                },
                {
                    'id': 'ext_wf_2',
                    'name': '电商选品分析',
                    'description': '自动抓取竞品数据，分析趋势，生成选品报告',
                    'agents': ['数据爬取', '趋势分析', '报告生成'],
                    'executionCount': 5432,
                    'successRate': 94.2,
                    'likeCount': 1876,
                    'isHot': False,
                    'isNew': True,
                    'source': 'Coze',
                    'type': 'workflow',
                    'tags': ['电商', '数据分析', '选品']
                },
                {
                    'id': 'ext_wf_3',
                    'name': '智能招聘流程',
                    'description': '简历筛选→面试安排→候选人评估→Offer生成',
                    'agents': ['简历解析', '智能筛选', '面试助手', '报告生成'],
                    'executionCount': 3210,
                    'successRate': 97.8,
                    'likeCount': 987,
                    'isHot': False,
                    'isNew': True,
                    'source': 'FlowiseAI',
                    'type': 'workflow',
                    'tags': ['招聘', 'HR', '人力资源']
                },
                # 新增工作流
                {
                    'id': 'ext_wf_4',
                    'name': '自媒体运营全流程',
                    'description': '热点监控→内容创作→多平台发布→数据分析',
                    'agents': ['热点监控', '内容生成', '平台发布', '数据分析'],
                    'executionCount': 6789,
                    'successRate': 95.3,
                    'likeCount': 2456,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Dify',
                    'type': 'workflow',
                    'tags': ['自媒体', '运营', '内容']
                },
                {
                    'id': 'ext_wf_5',
                    'name': '客户服务自动化',
                    'description': '问题分类→智能回复→工单生成→满意度调查',
                    'agents': ['问题分类', '智能回复', '工单系统', '满意度调查'],
                    'executionCount': 9876,
                    'successRate': 98.1,
                    'likeCount': 3567,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Coze',
                    'type': 'workflow',
                    'tags': ['客服', '自动化', '服务']
                },
                {
                    'id': 'ext_wf_6',
                    'name': '市场调研分析',
                    'description': '数据采集→竞品分析→用户调研→报告生成',
                    'agents': ['数据采集', '竞品分析', '用户调研', '报告生成'],
                    'executionCount': 4321,
                    'successRate': 93.7,
                    'likeCount': 1654,
                    'isHot': False,
                    'isNew': True,
                    'source': 'LangFlow',
                    'type': 'workflow',
                    'tags': ['市场调研', '分析', '报告']
                },
                {
                    'id': 'ext_wf_7',
                    'name': '项目管理流程',
                    'description': '需求分析→任务分解→进度追踪→风险预警',
                    'agents': ['需求分析', '任务管理', '进度监控', '风险评估'],
                    'executionCount': 5678,
                    'successRate': 96.8,
                    'likeCount': 2134,
                    'isHot': True,
                    'isNew': False,
                    'source': 'FlowiseAI',
                    'type': 'workflow',
                    'tags': ['项目管理', '协作', '效率']
                },
                {
                    'id': 'ext_wf_8',
                    'name': '教育培训方案',
                    'description': '需求评估→课程设计→教学实施→效果评估',
                    'agents': ['需求评估', '课程设计', '教学助手', '效果评估'],
                    'executionCount': 3456,
                    'successRate': 94.5,
                    'likeCount': 1345,
                    'isHot': False,
                    'isNew': True,
                    'source': 'Dify',
                    'type': 'workflow',
                    'tags': ['教育', '培训', '学习']
                },
                {
                    'id': 'ext_wf_9',
                    'name': '财务报销审批',
                    'description': '发票识别→合规检查→自动审批→记账归档',
                    'agents': ['发票OCR', '合规检查', '审批流程', '财务记账'],
                    'executionCount': 7890,
                    'successRate': 99.2,
                    'likeCount': 2987,
                    'isHot': True,
                    'isNew': False,
                    'source': 'Coze',
                    'type': 'workflow',
                    'tags': ['财务', '审批', '自动化']
                },
                {
                    'id': 'ext_wf_10',
                    'name': '短视频制作流程',
                    'description': '脚本创作→素材准备→视频剪辑→发布推广',
                    'agents': ['脚本创作', '素材搜索', '剪辑建议', '发布优化'],
                    'executionCount': 6543,
                    'successRate': 92.8,
                    'likeCount': 2456,
                    'isHot': True,
                    'isNew': False,
                    'source': 'LangFlow',
                    'type': 'workflow',
                    'tags': ['视频', '短视频', '创作']
                }
            ]
        }
    
    def get_combined_data(self, use_mock: bool = True) -> Dict[str, List[Dict]]:
        """
        获取组合数据（本地+外部）
        
        Args:
            use_mock: 是否使用模拟数据（真实爬取时设为False）
            
        Returns:
            组合后的数据
        """
        if use_mock:
            print("[外部数据] 使用模拟数据模式")
            return self.get_mock_external_data()
        else:
            print("[外部数据] 使用真实爬取模式")
            all_agents = []
            all_workflows = []
            
            # 从各平台获取
            all_agents.extend(self.fetch_dify_agents())
            all_agents.extend(self.fetch_coze_agents())
            
            # TODO: 添加工作流获取
            
            return {
                'agents': all_agents,
                'workflows': all_workflows
            }


# 全局实例
external_fetcher = ExternalCommunityFetcher()


if __name__ == '__main__':
    # 测试
    fetcher = ExternalCommunityFetcher()
    data = fetcher.get_mock_external_data()
    
    print("\n" + "="*60)
    print("外部数据示例")
    print("="*60)
    print(f"\nAgents: {len(data['agents'])} 个")
    for agent in data['agents'][:3]:
        print(f"  • {agent['icon']} {agent['name']} (来自 {agent['source']})")
    
    print(f"\n工作流: {len(data['workflows'])} 个")
    for wf in data['workflows']:
        print(f"  • {wf['name']} (来自 {wf['source']})")

