import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# 需要排除的非活动字段
EXCLUDED_FIELDS = [
    "您的微信号", "想说的话", "判断", "扫码交社费", 
    "您来到爱心社希望收获", "您来到爱心社希望收获：其他","（旧题）",
    "主要活动的部组（多选）", "骨干", "入社日期", "姓名", "学号", "年级", "性别", "院系"
]

# 活动到反馈表的映射
ACTIVITY_FEEDBACK_MAP = {
    '9月20日同心圆游园会':'tblKZ7dWs35qQAdk',
    "2025蒲公英支教":"tblSAg9XFeDDCemv",
    "2025儿童之家":"tbleo0cd0JCWqjao",
    "2025同心活动":"tblaiSue8q3UL0Xk",
    "2025心障关怀":"tbl0vRlv9k1C21ad",
    "2025乡镇学堂":"tbl5X2BndS1SE0gj",
    "2025海豚乐乐":"tbl25fXAzpa1vktZ",

    "2025秋金盲杖":"tblB74WxX7708aKd",
    "9.13守望星空影展":"tblj972yK3WmBLC3",
    '9.09手工x海淀团委':'tblV3D5hQtH2u7y9',
    "2025秋温馨家园":"tblHyvs5bWUwKgEd",
    "2025秋无障碍素拓":"tblRTFLHDADtOlax",
    "2025秋罕见病群体交流":"tblwOmSFeQNiNkXn",
    "2025秋教英语":"tbloJuVXxu7Mk9We",
    "2025秋图书校对":"tblbJgXM8ez2hIQK",
    "2025秋守望星空":"tblQrJ0NajzSvd2O",
    "2025秋无障碍茶会":"tblFnwoiVE4C0QJ1",
    "2025秋盲文小团":"tblLboOXFqwTHo81",
    "9月20日无障碍部迎新会":"tbl7cSMfL5JoTcDa",

    "2025秋敬老院活动":"tblZpgbczef3891J",
    "2025秋人生回忆录":"tblPrN3wxvRyOEzC",
    "2025秋护老周":"tblumfhfNHjaQQRq",
    "2025秋智能手机教学":"tblJa0JBjkEYvXYO",
    "2025秋入户陪伴活动":"tblQgWfWcJ1tWwoz",

    '2025暑王搏计划走访':'tblG5s8CyTQFd1Oe',
    "2025暑苹果北大行":"tblgCIUX1f3Masm5",
    "2025暑资助部电访":"tblmBaPRWLMMDWgT",
    "2025秋河北计划十一走访":"tblohlhZpCL4tCuK",
    "2025秋联络资助人":"tblqs99pEzh7XQmi",
    "2025秋友伴我行书信活动":"tblZ7gn7VIut1w8g",
    "2025秋友伴我行线下活动":"tblhZAbDiqnOhZ2f",
    "2025秋王搏计划影展":"tbli1bx3nSLbW1uX",
    "2025秋河北计划讲座":"tblu55MQza5nG4s9",

    "2025暑修社史": "tblwatMzzNIg79pp",
    "2025秋百团大战":"tblr5kAZxK0eU3ZN",
    "2025秋迎新大会":"tbleSdFN5iQ5hqql",
    "2025秋社庆":"tbl6CN0bIuUvpH5c",
    "2025秋收衣服":"tbl2b6lTEihx5MMs",
    "2025秋定向越野":"tblDT2e4VYVRXxxx",
    "2025秋社办整理":"tblLhFZDP3Smm6j2",
    "2025秋周边征订与发放":"tblnXVc3VQDhjwn0",
    "2025秋游":"tbljB20axcFQLyga",

    '2025秋社刊美编':'tblu7KQSebGtkPbY',
    "2025秋视频拍摄&剪辑培训":"tblI4hJryPqBZcHZ",
    "9月21日宣传部第一次例会":"tblHUK4BwIbDQjS8",
    "2025秋平面设计培训":"tblTeEU3KlWBS0ru",

    "9.28北京天文馆无障碍交流活动":"tbl1ifyIewQaqtRt",
    "9.12-9.14福祉博览会展览":"tblcIDBLNKMQ2U47",
    "2025秋再回首手语班":"tblr2zj9g5f7GqSu",
    "2025秋聋听交流":"tblGsO4jYiAaoi5q",
    "2025秋燕园浮生手语班":"tbleB7SQQOUsKfVE",
    "2025秋手随歌舞手语角":"tblHeNUD64rj5s3C",
    "2025秋初相见手语班":"tbldAv2wNn3VMet8",
    "2025秋百团快闪":"tblsVkYmBLyQcGFT",

    "2025秋第二十九届万里行茶话会":"tblhMI9ExnSS0PW8",
    "2025秋万里行茶话会":"tblLTQBetLiw0ecx",
    "2025秋项目组面试":"tblaRILhQasCbOCE",
    "2025秋万里行纪念品制作":"tblOPr3RxhG5DTJ0",
    "2025秋项目组修史":"tblxdgjpH3clJXnj",
    "2025万里行学校征集":"tblacJmKsE51nXQK",
    "2025万里行学校考察":"tblq44HLbcAMZV2w",

    "2025秋中医药文化进校园活动":"tbl0coPekbAr8D92",
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

def search_member_directly(tenant_access_token, app_token, table_id, name, student_id):
    """直接搜索特定成员（逐页搜索，找到即停止）"""
    page_token = ''
    has_more = True
    page_count = 0
    
    # 使用while循环逐页搜索
    while has_more:
        page_count += 1
        
        # 获取当前页数据
        result = get_bitable_datas(tenant_access_token, app_token, table_id, page_token)
        
        if result.get("code") != 0:
            error_msg = result.get("msg", "未知错误")
            raise Exception(f"获取数据失败: {error_msg}")
        
        data = result.get("data", {})
        items = data.get("items", [])
        
        # 在当前页中搜索目标成员
        for item in items:
            fields = item.get("fields", {})
            record_id = item.get("record_id", "")
            
            # 提取基本信息用于匹配
            name_data = fields.get("姓名", [{}])
            current_name = name_data[0].get("text", "") if name_data and isinstance(name_data, list) else ""
            current_student_id = fields.get("学号", "")
            
            # 检查是否匹配目标成员
            if current_name == name and str(current_student_id) == str(student_id):
                # 处理找到的成员数据
                processed_member = process_single_member(item)
                return processed_member
        
        # 检查是否有更多数据
        has_more = data.get("has_more", False)
        page_token = data.get("page_token", '')
        
        # 添加短暂延迟避免API限制
        import time
        time.sleep(0.05)
        
        # 安全限制：最多搜索25页数据
        if page_count >= 25:
            st.warning("已达到最大页数限制（25页），停止搜索")
            break
    
    return None

def calculate_days_since_join(join_date_timestamp):
    """计算入社至今的天数"""
    if not join_date_timestamp or join_date_timestamp == 0:
        return None
    
    try:
        # 将时间戳转换为datetime对象
        join_date = datetime.fromtimestamp(join_date_timestamp / 1000)
        
        # 计算与当前日期的差值
        today = datetime.now()
        days_since_join = (today - join_date).days
        
        return days_since_join
    except:
        return None

def process_single_member(item):
    """处理单个成员数据"""
    fields = item.get("fields", {})
    record_id = item.get("record_id", "")
    
    # 提取基本信息
    name_data = fields.get("姓名", [{}])
    name = name_data[0].get("text", "") if name_data and isinstance(name_data, list) else ""
    
    student_id = fields.get("学号", "")
    grade = fields.get("年级", "")
    gender = fields.get("性别", "")
    department = fields.get("院系", "")
    join_date_timestamp = fields.get("入社日期", 0)
    
    # 处理入社日期
    join_date = ""
    days_since_join = None
    
    if join_date_timestamp and join_date_timestamp != 0:
        try:
            join_date = datetime.fromtimestamp(join_date_timestamp / 1000).strftime('%Y-%m-%d')
            days_since_join = calculate_days_since_join(join_date_timestamp)
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
    
    return {
        "record_id": record_id,
        "姓名": name,
        "学号": student_id,
        "年级": grade,
        "性别": gender,
        "院系": department,
        "入社日期": join_date,
        "入社天数": days_since_join,
        "参加活动数": len(activities),
        "参加的活动": activities
    }

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

def parse_volunteer_hours(hours_str):
    """解析志愿学时字符串，提取数字"""
    if not hours_str:
        return 0
    
    try:
        # 移除可能的中文和空格，只保留数字和小数点
        import re
        # 匹配数字（包括小数）
        numbers = re.findall(r'\d+\.?\d*', str(hours_str))
        if numbers:
            return float(numbers[0])
        else:
            return 0
    except:
        return 0

def process_feedback_data(feedback_items):
    """处理反馈数据，返回反馈列表和总志愿学时"""
    feedbacks = []
    total_hours = 0
    
    for item in feedback_items:
        fields = item.get("fields", {})
        
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
        volunteer_hours_str = extract_text_from_field(fields.get("志愿学时", ""))
        volunteer_hours = parse_volunteer_hours(volunteer_hours_str)
        total_hours += volunteer_hours
        
        feedbacks.append({
            "核心内容": core_content,
            "感想": reflection,
            "志愿学时": volunteer_hours_str,  # 保留原始字符串用于显示
            "志愿学时数值": volunteer_hours   # 数值用于计算总和
        })
    
    return feedbacks, total_hours

def calculate_total_volunteer_hours(tenant_access_token, app_token, member_activities, student_id):
    """计算成员所有活动的总志愿学时"""
    total_hours = 0
    activity_hours = {}  # 存储每个活动的学时
    
    if not member_activities:
        return 0, {}
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, activity in enumerate(member_activities):
        status_text.text(f"{activity} ({i+1}/{len(member_activities)})")
        progress_bar.progress((i + 1) / len(member_activities))
        
        # 检查是否有对应的反馈表
        feedback_table_id = ACTIVITY_FEEDBACK_MAP.get(activity)
        
        if feedback_table_id:
            # 获取活动反馈
            feedback_items = get_activity_feedback(
                tenant_access_token, 
                app_token, 
                feedback_table_id, 
                student_id
            )
            
            if feedback_items:
                feedbacks, activity_total_hours = process_feedback_data(feedback_items)
                total_hours += activity_total_hours
                activity_hours[activity] = activity_total_hours
    
    # 清理进度条
    progress_bar.empty()
    status_text.empty()
    st.success(f"您的爱心足迹已生成！")
    return total_hours, activity_hours

# Streamlit界面
st.set_page_config(page_title="成员活动查询系统", layout="wide")
st.title("🎯 成员活动记录查询系统")

# 应用配置
app_id = os.environ.get('APP_ID', 'default_app_id')
app_secret = os.environ.get('APP_SECRET', 'default_app_secret')
app_token = os.environ.get('APP_TOKEN', 'default_app_token')
table_id = os.environ.get('TABLE_ID','default_table_id')

# 初始化session state
if 'tenant_access_token' not in st.session_state:
    st.session_state.tenant_access_token = None

# 查询界面
st.subheader("个人信息查询")
st.info("请输入您的姓名和学号查询个人活动记录（仅可查询2025年暑期之后参加的活动噢~）")

col1, col2 = st.columns(2)
with col1:
    search_name = st.text_input("姓名", placeholder="请输入您的姓名")
with col2:
    search_id = st.text_input("学号", placeholder="请输入您的学号")

# 搜索功能
if search_name and search_id:
    with st.spinner("小爱同学正在回顾您的爱心足迹..."):
        try:
            # 获取访问令牌
            if st.session_state.tenant_access_token is None:
                st.session_state.tenant_access_token = get_tenant_access_token(app_id, app_secret)
            
            # 直接搜索成员（找到即停止）
            member = search_member_directly(
                st.session_state.tenant_access_token, 
                app_token, 
                table_id, 
                search_name, 
                search_id
            )
            
            if not member:
                st.warning("小爱同学查找失败了，请检查姓名和学号是否正确。若确实无误且您之前已加入过爱心社，请填写问卷：https://acngyried1he.feishu.cn/share/base/form/shrcnsgqhMNq6pJ43llUQ7M7rgg")
            else:
                
                # 计算总志愿学时
                total_hours, activity_hours = calculate_total_volunteer_hours(
                    st.session_state.tenant_access_token,
                    app_token,
                    member['参加的活动'],
                    member['学号']
                )
                
                # 显示个人信息
                st.subheader("社员概况")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # 显示入社日期和天数（如果不为空）
                    if member['入社日期']:
                        st.write(f"**入社日期**: {member['入社日期']}")
                        if member['入社天数'] is not None:
                            st.write(f"**入社天数**: {member['入社天数']} 天")
                
                with col2:
                    st.write(f"**参加活动数**: {member['参加活动数']}")
                
                with col3:
                    st.write(f"**总志愿学时**: **{total_hours:.1f}** 小时")
                    
                # 如果入社日期为空，在第四列显示提示信息
                with col4:
                    if not member['入社日期']:
                        st.info("💡 您的入社日期信息尚未录入")
                
                # 显示活动记录
                st.subheader("与爱心社的故事")
                if member["参加的活动"]:
                    for i, activity in enumerate(member["参加的活动"], 1):
                        # 检查是否有对应的反馈表
                        feedback_table_id = ACTIVITY_FEEDBACK_MAP.get(activity)
                        activity_hour = activity_hours.get(activity, 0)
                        
                        if feedback_table_id:
                            # 使用展开器显示活动详情和反馈
                            with st.expander(f"{i}. {activity} ", expanded=False):
                                # 获取活动反馈
                                feedback_items = get_activity_feedback(
                                    st.session_state.tenant_access_token, 
                                    app_token, 
                                    feedback_table_id, 
                                    member["学号"]
                                )
                                
                                if feedback_items:
                                    feedbacks, _ = process_feedback_data(feedback_items)
                                    
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
                            st.write(f"{i}. {activity} (暂无反馈表)")
                else:
                    st.info("似乎2025的暑假后还没有和爱心社的故事噢~期待在下次活动中与您相遇！")
                
                # 导出功能
                st.subheader("导出记录")
                if st.button("导出我的活动记录"):
                    # 创建数据框
                    df_data = []
                    for activity in member["参加的活动"]:
                        activity_hour = activity_hours.get(activity, 0)
                        df_data.append({
                            "姓名": member["姓名"],
                            "学号": member["学号"],
                            "入社日期": member["入社日期"],
                            "入社天数": member["入社天数"] if member["入社天数"] is not None else "",
                            "活动名称": activity,
                            "志愿学时": activity_hour
                        })
                    
                    df = pd.DataFrame(df_data)
                    
                    # 生成CSV
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载CSV文件",
                        data=csv,
                        file_name=f"{member['姓名']}_活动记录_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"足迹生成过程中发生错误: {e}，请联系技术负责人反馈问题：gao1632717769")
elif search_name or search_id:
    st.warning("请同时输入姓名和学号进行查询")

# 添加使用说明
st.sidebar.title("使用说明")
st.sidebar.info("""
1. 输入您的姓名和学号查询个人活动记录
2. 系统只会显示与您姓名和学号完全匹配的记录
3. 如果您的入社日期已录入，系统会显示入社至今的天数
4. 您可以导出您的活动记录为CSV文件
""")

# 添加隐私声明
st.sidebar.title("隐私声明")
st.sidebar.warning("""
本系统仅用于查询个人活动记录，不会显示其他成员的信息。
您的个人信息将严格保密，不会用于其他用途。
""")

# 添加重置按钮
if st.sidebar.button("重置查询"):
    st.session_state.tenant_access_token = None
    st.experimental_rerun()




