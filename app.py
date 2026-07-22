from flask import Flask, render_template_string
import akshare as ak
import pandas as pd
import datetime
import time

app = Flask(__name__)

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
        df_spot = ak.stock_zh_a_spot_em()
        df_spot = df_spot[['代码', '名称', '最新价', '涨跌幅', '成交额']]
        df_limit = df_spot[df_spot['涨跌幅'] > 9.5].copy()
        
        p1 = df_limit[['代码', '名称', '最新价', '涨跌幅']].head(8)
        p2 = df_limit[df_limit['成交额'] > 200000000][['代码', '名称', '最新价', '涨跌幅']].head(6)
        p3 = df_limit[['代码', '名称', '最新价', '涨跌幅']].head(5)
        p4 = df_spot[df_spot['涨跌幅'] > 10][['代码', '名称', '最新价', '涨跌幅']].head(5)
        p5 = df_spot[(df_spot['涨跌幅'] > 9.5) & (df_spot['成交额'] > 500000000)][['代码', '名称', '最新价', '涨跌幅']].head(6)
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
        empty_df = pd.DataFrame(columns=['代码', '名称', '最新价', '涨跌幅'])
        return {f"⚠️ 数据异常 (请刷新)": empty_df}

@app.route('/')
def home():
    start = time.time()
    pools = get_pools()
    print(f"数据处理耗时: {time.time()-start:.2f}秒")
    return render_template_string(HTML_TEMPLATE, pools=pools, update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
