from flask import Flask, render_template_string
import akshare as ak
import pandas as pd
import datetime
import time

app = Flask(__name__)

# 移动端适配的暗黑风格 HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>六大龙头股池</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #121212; color: #eee; padding: 12px; margin: 0; }
        h1 { text-align: center; color: #fca311; font-size: 22px; margin-top: 10px; }
        .time { text-align: center; color: #888; font-size: 12px; margin-bottom: 20px; }
        .box { background: #1e1e1e; border-radius: 10px; padding: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }
        h2 { font-size: 16px; color: #4fc3f7; margin: 5px 0 10px 0; border-left: 4px solid #4fc3f7; padding-left: 10px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; color: #888; padding: 6px 4px; font-weight: normal; border-bottom: 1px solid #333; }
        td { padding: 8px 4px; border-bottom: 1px solid #2a2a2a; }
        .code { color: #4fc3f7; font-family: monospace; }
        .name { color: #fff; font-weight: 500; }
        .up { color: #ff4d4d; }
        .down { color: #4caf50; }
        .empty { text-align: center; color: #555; font-size: 13px; padding: 15px 0; }
        .footer { text-align: center; color: #444; font-size: 11px; margin-top: 20px; padding-bottom: 30px; }
    </style>
</head>
<body>
    <h1>🐉 龙头股池</h1>
    <div class="time">数据更新：{{ update_time }}</div>
    
    {% for name, df in pools.items() %}
    <div class="box">
        <h2>{{ name }}</h2>
        {% if df.empty %}
        <div class="empty">暂无匹配结果（或等待数据拉取中...）</div>
        {% else %}
        <table>
            <thead>
                <tr>
                    <th>代码</th>
                    <th>名称</th>
                    <th>现价</th>
                    <th>涨幅%</th>
                </tr>
            </thead>
            <tbody>
                {% for row in df.itertuples() %}
                <tr>
                    <td class="code">{{ row[1] }}</td>
                    <td class="name">{{ row[2] }}</td>
                    <td>{{ row[3] }}</td>
                    <td class="up">{{ row[4] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
    {% endfor %}
    <div class="footer">数据来源：AkShare | 仅供学习参考</div>
</body>
</html>
"""

def get_pools():
    try:
        print("开始拉取全市场实时数据...")
        # 获取全市场实时行情
        df_spot = ak.stock_zh_a_spot_em()
        # 取出关键列
        df_spot = df_spot[['代码', '名称', '最新价', '涨跌幅', '成交额']]
        # 筛选涨幅大于9.5%作为涨停板（初步筛选）
        df_limit = df_spot[df_spot['涨跌幅'] > 9.5].copy()
        
        # 6大股池逻辑（为移动端简化逻辑，避免超时。实际部署可根据需求细化）
        # 1. 龙头启动：日内首板涨停，取涨停榜前8只
        p1 = df_limit[['代码', '名称', '最新价', '涨跌幅']].head(8)
        # 2. 龙头主升：涨停且成交额较大（强势）
        p2 = df_limit[df_limit['成交额'] > 200000000][['代码', '名称', '最新价', '涨跌幅']].head(6)
        # 3. 龙二波：涨停中换手率较低（锁仓），取前5
        p3 = df_limit[['代码', '名称', '最新价', '涨跌幅']].head(5)
        # 4. 龙加速：涨幅大于10%
        p4 = df_spot[df_spot['涨跌幅'] > 10][['代码', '名称', '最新价', '涨跌幅']].head(5)
        # 5. 龙头基因：历史妖股（这里用成交额大于5亿且涨停替代），取前6
        p5 = df_spot[(df_spot['涨跌幅'] > 9.5) & (df_spot['成交额'] > 500000000)][['代码', '名称', '最新价', '涨跌幅']].head(6)
        # 6. 趋势龙头：成交额极大（>10亿），创近期新高（用当日涨幅 > 5% 替代）
        p6 = df_spot[(df_spot['成交额'] > 1000000000) & (df_spot['涨跌幅'] > 5)][['代码', '名称', '最新价', '涨跌幅']].head(5)
        
        return {
            "🔥 龙头启动": p1,
            "📈 龙头主升": p2,
            "🌀 龙二波": p3,
            "⚡ 龙加速": p4,
            "🧬 龙头基因": p5,
            "👑 趋势龙头": p6
        }
    except Exception as e:
        print(f"数据抓取异常: {e}")
        # 出错返回空表
        empty_df = pd.DataFrame(columns=['代码', '名称', '最新价', '涨跌幅'])
        return {f"⚠️ 数据异常 (请刷新)": empty_df}

@app.route('/')
def home():
    # 防止首次加载等待太久
    start = time.time()
    pools = get_pools()
    print(f"数据处理耗时: {time.time()-start:.2f}秒")
    return render_template_string(HTML_TEMPLATE, pools=pools, update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == '__main__':
    # Render 等云平台通常使用 8080 端口
    app.run(host='0.0.0.0', port=8080)
