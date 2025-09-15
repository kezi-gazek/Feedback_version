import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# 需要排除的非活动字段
EXCLUDED_FIELDS = [
    "您的微信号", "想说的话", "判断", "扫码交社费", 
    "您来到爱心社希望收获", "您来到爱心社希望收获：其他","（旧题）",
    "主要活动的部组（多选）", "骨干", "入社日期", "姓名", "学号", "年级", "性别", "院系"
]

# 活动到反馈表的映射
ACTIVITY_FEEDBACK_MAP = {
    "2025暑修社史": "tblwatMzzNIg79pp",
    '2025秋社刊美编':'tblu7KQSebGtkPbY',
    '9.09手工x海淀团委':'tblV3D5hQtH2u7y9',
    "2025秋百团大战":"",
    "2025秋迎新大会反馈、学时问卷":"",
    "2025秋社庆反馈、学时问卷":"",
    "2025秋收衣服反馈、学时问卷":"",
    "2025秋定向越野反馈、学时问卷":"",
    "2025秋社办整理反馈、学时问卷":"",
    "2025秋周边征订与发放反馈、学时问卷":"",
    "2025秋游反馈、学时问卷":"",
    "2025暑苹果北大行":"tblgCIUX1f3Masm5",
    "2025暑资助部电访":"tblmBaPRWLMMDWgT",
    '2025暑王搏计划走访':'tblG5s8CyTQFd1Oe',
    "2025秋河北计划十一走访":"",
    "2025秋联络资助人":"",
    "2025秋友伴我行书信活动":"",
    "2025秋友伴我行线下活动":"",
    "2025秋王搏计划影展":"",
    "2025秋河北计划讲座":"",
    "2025蒲公英支教":"",
    "2025儿童之家":"",
    "2025同心活动":"",
    "2025心障关怀":"",
    "2025海豚乐乐":"",
    "2025乡镇学堂":"",
    "2025秋中医药文化进校园活动":"",
    "2025秋敬老院活动":"",
    "2025秋智能手机教学":"tblJa0JBjkEYvXYO",
    "2025秋入户陪伴活动":"",
    "2025秋护老周":"",
    "2025秋人生回忆录":"",
    "2025秋视频拍摄 & 剪辑培训":"",
    "9.13守望星空影展":"tblj972yK3WmBLC3",
    "2025秋金盲杖":"",
    "2025秋温馨家园":"",
    "2025秋教英语":"",
    "2025秋图书校对":"",
    "2025秋无障碍茶会":"tblFnwoiVE4C0QJ1",
    "2025秋盲文小团":"",
    "2025秋守望星空":"",
    "2025秋无障碍素拓":"",
    "2025秋罕见病群体交流":"",
    "9.20北京天文馆无障碍交流活动":"",
    "9.12-9.14福祉博览会展览":"",
    "2025秋百团快闪":"",
    "2025秋再回首手语班":"",
    "2025秋聋听交流":"",
    "2025秋燕园浮生手语班":"",
    "2025秋手随歌舞手语角":"",
    "2025秋初相见手语班":"",
    "2025秋第二十九届万里行茶话会":"",
    "2025秋万里行茶话会":"",
    "2025秋项目组面试":"",
    "2025秋万里行纪念品制作":"",
    "2025秋项目组修史":"",
    "2025万里行学校征集":"",
    "2025万里行学校":""
    # 添加更多活动到反馈表的映射
    # "活动名称": "table_id",
}

def get_tenant_access_token(app_id, app_secret):
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({
        "app_id": app_id,
        "app_secret": app_secret
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json()
    if result.get("code") == 0:
        return result['tenant_access_token']
    else:
        raise Exception(f"获取访问令牌失败: {result.get('msg')}")

def get_bitable_datas(tenant_access_token, app_token, table_id, page_token='', page_size=500):
    """获取多维表格数据（支持分页）"""
    # 使用URL参数而不是请求体传递分页参数
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}"
    
    if page_token:
        url += f"&page_token={page_token}"
    
    # 添加user_id_type参数
    url += "&user_id_type=user_id"
    
    # 使用空请求体
    payload = json.dumps({})
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant_access_token}'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json()
    return result

def get_all_records(tenant_access_token, app_token, table_id):
    """获取所有记录（使用分页机制）"""
    all_items = []
    page_token = ''
    has_more = True
    page_count = 0
    
    # 使用while循环获取所有分页数据
    while has_more:
        page_count += 1
        st.info(f"正在获取第 {page_count} 页数据...")
        
        # 获取当前页数据
        result = get_bitable_datas(tenant_access_token, app_token, table_id, page_token)
        
        if result.get("code") != 0:
            error_msg = result.get("msg", "未知错误")
            raise Exception(f"获取数据失败 (第{page_count}页): {error_msg}")
        
        data = result.get("data", {})
        items = data.get("items", [])
        all_items.extend(items)
        
        # 检查是否有更多数据
        has_more = data.get("has_more", False)
        page_token = data.get("page_token", '')
        
        # 添加短暂延迟避免API限制
        import time
        time.sleep(0.05)
        
        # 安全限制：最多获取25页数据（2500条记录）
        if page_count >= 25:
            st.warning("已达到最大页数限制（25页），停止获取更多数据")
            break
    
    return all_items

def process_member_data(items):
    """处理成员数据"""
    processed_data = []
    
    for item in items:
        fields = item.get("fields", {})
        record_id = item.get("record_id", "")
        
        # 提取基本信息
        name_data = fields.get("姓名", [{}])
        name = name_data[0].get("text", "") if name_data and isinstance(name_data, list) else ""
        
        student_id = fields.get("学号", "")
        grade = fields.get("年级", "")
        gender = fields.get("性别", "")
        department = fields.get("院系", "")
        join_date = fields.get("入社日期", 0)
        
        # 转换时间戳为日期
        if join_date:
            try:
                join_date = datetime.fromtimestamp(join_date / 1000).strftime('%Y-%m-%d')
            except:
                join_date = "未知日期"
        
        # 提取参加的活动（排除指定字段）
        activities = []
        for key, value in fields.items():
            # 跳过排除字段
            if key in EXCLUDED_FIELDS:
                continue
            
            # 如果值不为空，表示参加了该活动
            if value is not None and value != {} and value != []:
                activities.append(key)
        
        # 添加到处理后的数据
        processed_data.append({
            "record_id": record_id,
            "姓名": name,
            "学号": student_id,
            "年级": grade,
            "性别": gender,
            "院系": department,
            "入社日期": join_date,
            "参加活动数": len(activities),
            "参加的活动": activities
        })
    
    return processed_data

def search_member_by_info(member_data, name, student_id):
    """根据姓名和学号搜索成员"""
    results = []
    
    for member in member_data:
        # 严格匹配姓名和学号
        name_match = member["姓名"] == name
        id_match = str(member["学号"]) == str(student_id)
        
        if name_match and id_match:
            results.append(member)
            break  # 找到匹配记录后立即停止搜索
    
    return results

def get_activity_feedback(tenant_access_token, app_token, feedback_table_id, student_id):
    """获取活动反馈数据"""
    # 使用正确的飞书API查询格式
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{feedback_table_id}/records/search"
    
    # 构建正确的查询条件格式
    payload = json.dumps({
        "view_id": "vewhAjevsI",  # 添加视图ID
        "filter": {
            "conjunction": "and",  # 使用conjunction而不是operator
            "conditions": [
                {
                    "field_name": "学号",
                    "operator": "is",
                    "value": [str(student_id)]  # 将值包装在列表中
                }
            ]
        },
        "automatic_fields": True
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant_access_token}'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json()
    
    # 调试信息
    # st.write(f"反馈查询响应: {result}")
    
    if result.get("code") != 0:
        st.error(f"反馈查询失败: {result.get('msg')}")
        return []
    
    return result.get("data", {}).get("items", [])

def extract_text_from_field(value):
    """从飞书字段中提取纯文本"""
    if value is None:
        return ""
    
    # 如果是列表，处理每个元素
    if isinstance(value, list):
        texts = []
        for item in value:
            if isinstance(item, dict) and 'text' in item:
                texts.append(item['text'])
            elif isinstance(item, str):
                texts.append(item)
        return ", ".join(texts)
    
    # 如果是字典，尝试提取text字段
    if isinstance(value, dict) and 'text' in value:
        return value['text']
    
    # 其他情况，直接转换为字符串
    return str(value)

def process_feedback_data(feedback_items):
    """处理反馈数据"""
    feedbacks = []
    
    for item in feedback_items:
        fields = item.get("fields", {})
        
        # 调试信息
        # st.write(f"原始反馈字段: {fields}")
        
        # 提取核心内容
        core_content = extract_text_from_field(fields.get("是否是核心内容", ""))
        other_content = extract_text_from_field(fields.get("其他活动内容", ""))
        
        # 处理核心内容
        if core_content and "其他" in core_content:
            # 提取除了"其他"外的内容
            core_parts = [part.strip() for part in core_content.split(",") if part.strip() != "其他"]
            core_content = ", ".join(core_parts)
            
            # 如果有其他内容，添加到核心内容中
            if other_content:
                core_content = f"{core_content}, {other_content}" if core_content else other_content
        
        # 查找包含"感想"的字段
        reflection = ""
        for key, value in fields.items():
            if "感想" in key:
                reflection = extract_text_from_field(value)
                break
        
        # 提取志愿学时
        volunteer_hours = extract_text_from_field(fields.get("志愿学时", ""))
        
        feedbacks.append({
            "核心内容": core_content,
            "感想": reflection,
            "志愿学时": volunteer_hours
        })
    
    return feedbacks

# Streamlit界面
st.set_page_config(page_title="成员活动查询系统", layout="wide")
st.title("🎯 成员活动记录查询系统")

# 应用配置
app_id = 'cli_a84f183c3ff8100d'
app_secret = 'b8ELILD9IqaaYFbOOB6L2cyX6oODLczj'
app_token = 'NPcMbmMI6a06jmsaXoscwLcqnBf'
table_id = "tblE5QYLVyf7YBmE"

# 初始化session state
if 'all_member_data' not in st.session_state:
    st.session_state.all_member_data = None
if 'tenant_access_token' not in st.session_state:
    st.session_state.tenant_access_token = None

# 查询界面
st.subheader("个人信息查询")
st.info("请输入您的姓名和学号查询个人活动记录")

col1, col2 = st.columns(2)
with col1:
    search_name = st.text_input("姓名", placeholder="请输入您的姓名")
with col2:
    search_id = st.text_input("学号", placeholder="请输入您的学号")

# 搜索功能
if search_name and search_id:
    with st.spinner("正在查询..."):
        try:
            # 如果还没有加载所有数据，则先加载
            if st.session_state.all_member_data is None:
                # 获取访问令牌
                if st.session_state.tenant_access_token is None:
                    st.session_state.tenant_access_token = get_tenant_access_token(app_id, app_secret)
                
                # 获取所有记录
                st.info("首次查询需要加载所有数据，请稍候...")
                all_items = get_all_records(st.session_state.tenant_access_token, app_token, table_id)
                
                # 处理数据
                st.session_state.all_member_data = process_member_data(all_items)
                st.success(f"成功加载 {len(st.session_state.all_member_data)} 条成员记录")
            
            # 搜索成员
            results = search_member_by_info(st.session_state.all_member_data, search_name, search_id)
            
            if not results:
                st.warning("未找到匹配的成员记录，请检查姓名和学号是否正确")
            else:
                member = results[0]
                
                st.success(f"找到您的记录: {member['姓名']} ({member['学号']})")
                
                # 显示个人信息
                st.subheader("个人信息")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**年级**: {member['年级']}")
                    st.write(f"**性别**: {member['性别']}")
                with col2:
                    st.write(f"**院系**: {member['院系']}")
                    st.write(f"**入社日期**: {member['入社日期']}")
                with col3:
                    st.write(f"**参加活动数**: {member['参加活动数']}")
                
                # 显示活动记录
                st.subheader("参加的活动")
                if member["参加的活动"]:
                    for i, activity in enumerate(member["参加的活动"], 1):
                        # 检查是否有对应的反馈表
                        feedback_table_id = ACTIVITY_FEEDBACK_MAP.get(activity)
                        
                        if feedback_table_id:
                            # 使用展开器显示活动详情和反馈
                            with st.expander(f"{i}. {activity} (点击查看详情)", expanded=False):
                                # 获取活动反馈
                                feedback_items = get_activity_feedback(
                                    st.session_state.tenant_access_token, 
                                    app_token, 
                                    feedback_table_id, 
                                    member["学号"]
                                )
                                
                                if feedback_items:
                                    feedbacks = process_feedback_data(feedback_items)
                                    
                                    for idx, feedback in enumerate(feedbacks, 1):
                                        st.write(f"**反馈记录 {idx}**")
                                        if feedback["核心内容"]:
                                            st.write(f"**参与活动内容**: {feedback['核心内容']}")
                                        if feedback["感想"]:
                                            st.write(f"**感想**: {feedback['感想']}")
                                        if feedback["志愿学时"]:
                                            st.write(f"**志愿学时**: {feedback['志愿学时']}")
                                        if idx < len(feedbacks):
                                            st.write("---")
                                else:
                                    st.info("暂无反馈记录")
                        else:
                            st.write(f"{activity}")
                else:
                    st.info("暂无活动记录")
                
                # 导出功能
                st.subheader("导出记录")
                if st.button("导出我的活动记录"):
                    # 创建数据框
                    df = pd.DataFrame([{
                        "姓名": member["姓名"],
                        "学号": member["学号"],
                        "年级": member["年级"],
                        "性别": member["性别"],
                        "院系": member["院系"],
                        "入社日期": member["入社日期"],
                        "活动名称": activity
                    } for activity in member["参加的活动"]])
                    
                    # 生成CSV
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载CSV文件",
                        data=csv,
                        file_name=f"{member['姓名']}_活动记录_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"查询过程中发生错误: {e}")
elif search_name or search_id:
    st.warning("请同时输入姓名和学号进行查询")

# 添加使用说明
st.sidebar.title("使用说明")
st.sidebar.info("""
1. 输入您的姓名和学号查询个人活动记录
2. 系统只会显示与您姓名和学号完全匹配的记录
3. 首次查询需要加载所有数据，请耐心等待
4. 对于有反馈记录的活动，可以点击活动名称查看详情
5. 您可以导出您的活动记录为CSV文件
""")

# 添加隐私声明
st.sidebar.title("隐私声明")
st.sidebar.warning("""
本系统仅用于查询个人活动记录，不会显示其他成员的信息。
您的个人信息将严格保密，不会用于其他用途。
""")

# 添加重置按钮
if st.sidebar.button("重置查询"):
    st.session_state.all_member_data = None
    st.session_state.tenant_access_token = None
    st.experimental_rerun()

