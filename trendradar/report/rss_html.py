# coding=utf-8
"""
RSS HTML 报告渲染模块

提供 RSS 订阅内容的 HTML 格式报告生成功能
"""

from datetime import datetime
from typing import Dict, List, Optional, Callable

from trendradar.report.helpers import html_escape


def render_rss_html_content(
    rss_items: List[Dict],
    total_count: int,
    feeds_info: Optional[Dict[str, str]] = None,
    *,
    get_time_func: Optional[Callable[[], datetime]] = None,
) -> str:
    """渲染 RSS HTML 内容

    Args:
        rss_items: RSS 条目列表，每个条目包含:
            - title: 标题
            - feed_id: RSS 源 ID
            - feed_name: RSS 源名称
            - url: 链接
            - published_at: 发布时间
            - summary: 摘要（可选）
            - author: 作者（可选）
        total_count: 条目总数
        feeds_info: RSS 源 ID 到名称的映射
        get_time_func: 获取当前时间的函数（可选，默认使用 datetime.now）

    Returns:
        渲染后的 HTML 字符串
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>章鱼 AI·新闻雷达 · RSS 订阅</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" integrity="sha512-BNaRQnYJYiPSqHHDb58B0yaPfCu+Wgds8Gp/gU33kqBtgNS4tSPHuGibyoeqMV/TJlSKda6FXzoEyYGjTe+vXA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                margin: 0;
                padding: 16px;
                background: #fafafa;
                color: #333333;
                line-height: 1.5;
            }

            .container {
                max-width: 700px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 16px rgba(0,0,0,0.06);
            }

            .header {
                background: linear-gradient(135deg, #747474 0%, #919191 100%);
                color: white;
                padding: 32px 24px;
                text-align: center;
                position: relative;
            }

            .save-buttons {
                position: absolute;
                top: 16px;
                right: 16px;
                display: flex;
                gap: 8px;
            }

            .save-btn {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s ease;
                backdrop-filter: blur(10px);
                white-space: nowrap;
            }

            .save-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
                transform: translateY(-1px);
            }

            .save-btn:active {
                transform: translateY(0);
            }

            .save-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .header-title {
                font-size: 22px;
                font-weight: 700;
                margin: 0 0 20px 0;
            }

            .header-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                font-size: 14px;
                opacity: 0.95;
            }

            .info-item {
                text-align: center;
            }

            .info-label {
                display: block;
                font-size: 12px;
                opacity: 0.8;
                margin-bottom: 4px;
            }

            .info-value {
                font-weight: 600;
                font-size: 16px;
            }

            .content {
                padding: 24px;
            }

            .feed-group {
                margin-bottom: 32px;
            }

            .feed-group:last-child {
                margin-bottom: 0;
            }

            .feed-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 16px;
                padding-bottom: 8px;
                border-bottom: 2px solid #919191;
            }

            .feed-name {
                font-size: 16px;
                font-weight: 600;
                color: #747474;
            }

            .feed-count {
                color: #666666;
                font-size: 13px;
                font-weight: 500;
            }

            .rss-item {
                margin-bottom: 16px;
                padding: 16px;
                background: #fafafa;
                border-radius: 8px;
                border-left: 3px solid #919191;
            }

            .rss-item:last-child {
                margin-bottom: 0;
            }

            .rss-meta {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 8px;
                flex-wrap: wrap;
            }

            .rss-time {
                color: #727272;
                font-size: 12px;
            }

            .rss-author {
                color: #747474;
                font-size: 12px;
                font-weight: 500;
            }

            .rss-title {
                font-size: 15px;
                line-height: 1.5;
                color: #1a1a1a;
                margin: 0 0 8px 0;
                font-weight: 500;
            }

            .rss-link {
                color: #606060;
                text-decoration: none;
            }

            .rss-link:hover {
                text-decoration: underline;
            }

            .rss-link:visited {
                color: #555555;
            }

            .rss-summary {
                font-size: 13px;
                color: #727272;
                line-height: 1.6;
                margin: 0;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }

            .footer {
                margin-top: 32px;
                padding: 20px 24px;
                background: #f9f9f9;
                border-top: 1px solid #e7e7e7;
                text-align: center;
            }

            .footer-content {
                font-size: 13px;
                color: #727272;
                line-height: 1.6;
            }

            .footer-link {
                color: #747474;
                text-decoration: none;
                font-weight: 500;
                transition: color 0.2s ease;
            }

            .footer-link:hover {
                color: #919191;
                text-decoration: underline;
            }

            .project-name {
                font-weight: 600;
                color: #404040;
            }

            @media (max-width: 480px) {
                body { padding: 12px; }
                .header { padding: 24px 20px; }
                .content { padding: 20px; }
                .footer { padding: 16px 20px; }
                .header-info { grid-template-columns: 1fr; gap: 12px; }
                .rss-meta { gap: 8px; }
                .rss-item { padding: 12px; }
                .save-buttons {
                    position: static;
                    margin-bottom: 16px;
                    display: flex;
                    gap: 8px;
                    justify-content: center;
                    flex-direction: column;
                    width: 100%;
                }
                .save-btn {
                    width: 100%;
                }
            }

        /* 墨水屏风格：黑白灰配色，保留清晰的新闻阅读层级 */
        :root { color-scheme: light; }
        body {
            background: #e7e7e7;
            color: #292929;
            line-height: 1.65;
            letter-spacing: 0.01em;
        }
        .container {
            background: #fafafa;
            border: 1px solid #c3c3c3;
            border-radius: 6px;
            box-shadow: none;
        }
        .header {
            background: #292929;
            background-image: none;
            border-bottom: 1px solid #141414;
        }
        .header-title {
            font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
            font-size: 24px;
            letter-spacing: 0.04em;
        }
        .header-title { margin-bottom: 6px; }
        .header-subtitle {
            color: #cccccc;
            font-size: 14px;
            margin: 0 0 20px;
            letter-spacing: 0.03em;
        }
        .content { background: #fafafa; }
        .feed-header { border-bottom-color: #777777; }
        .feed-name { color: #303030; }
        .rss-item { border-color: #c6c6c6; }
        .rss-title,
        .project-name { color: #252525; }
        .news-link,
        .rss-link,
        .footer-link,
        .rss-author { color: #3b3b3b; }
        .news-link:visited,
        .rss-link:visited { color: #686868; }
        .rss-item {
            background: #efefef;
            border-left-color: #626262;
            border-radius: 4px;
        }
        .footer {
            background: #eeeeee;
            border-top-color: #c3c3c3;
        }
        .footer-content { color: #555555; }
        .save-btn {
            color: #ffffff;
            background: rgba(255,255,255,0.14);
            border-color: rgba(255,255,255,0.42);
            border-radius: 4px;
            box-shadow: none;
            backdrop-filter: none;
            transition: background-color 0.15s ease;
        }
        .save-btn:hover { background: rgba(255,255,255,0.25); }
</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="save-buttons">
                    <button class="save-btn" onclick="saveAsImage()">保存为图片</button>
                </div>
                <div class="header-title">章鱼 AI·新闻雷达</div>
                <div class="header-subtitle">RSS 订阅内容</div>
                <div class="header-info">
                    <div class="info-item">
                        <span class="info-label">订阅条目</span>
                        <span class="info-value">"""

    html += f"{total_count} 条"

    html += """</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">生成时间</span>
                        <span class="info-value">"""

    # 使用提供的时间函数或默认 datetime.now
    if get_time_func:
        now = get_time_func()
    else:
        now = datetime.now()
    html += now.strftime("%m-%d %H:%M")

    html += """</span>
                    </div>
                </div>
            </div>

            <div class="content">"""

    # 按 feed_id 分组
    feeds_map: Dict[str, List[Dict]] = {}
    for item in rss_items:
        feed_id = item.get("feed_id", "unknown")
        if feed_id not in feeds_map:
            feeds_map[feed_id] = []
        feeds_map[feed_id].append(item)

    # 渲染每个 RSS 源的内容
    for feed_id, items in feeds_map.items():
        feed_name = items[0].get("feed_name", feed_id) if items else feed_id
        if feeds_info and feed_id in feeds_info:
            feed_name = feeds_info[feed_id]

        escaped_feed_name = html_escape(feed_name)

        html += f"""
                <div class="feed-group">
                    <div class="feed-header">
                        <div class="feed-name">{escaped_feed_name}</div>
                        <div class="feed-count">{len(items)} 条</div>
                    </div>"""

        for item in items:
            raw_title = item.get("title", "")
            if not raw_title or not raw_title.strip():
                raw_title = item.get("url", "") or item.get("feed_name", "")
            escaped_title = html_escape(raw_title)
            url = item.get("url", "")
            published_at = item.get("published_at", "")
            author = item.get("author", "")
            summary = item.get("summary", "")

            html += """
                    <div class="rss-item">
                        <div class="rss-meta">"""

            if published_at:
                html += f'<span class="rss-time">{html_escape(published_at)}</span>'

            if author:
                html += f'<span class="rss-author">by {html_escape(author)}</span>'

            html += """
                        </div>
                        <div class="rss-title">"""

            if url:
                escaped_url = html_escape(url)
                html += f'<a href="{escaped_url}" target="_blank" class="rss-link">{escaped_title}</a>'
            else:
                html += escaped_title

            html += """
                        </div>"""

            if summary:
                escaped_summary = html_escape(summary)
                html += f"""
                        <p class="rss-summary">{escaped_summary}</p>"""

            html += """
                    </div>"""

        html += """
                </div>"""

    html += """
            </div>

            <div class="footer">
                <div class="footer-content">
                    由 <span class="project-name">TrendRadar</span> 生成 ·
                    <a href="https://github.com/sansan0/TrendRadar" target="_blank" class="footer-link">
                        GitHub 开源项目
                    </a>
                </div>
            </div>
        </div>

        <script>
            async function saveAsImage() {
                const button = event.target;
                const originalText = button.textContent;

                try {
                    button.textContent = '生成中...';
                    button.disabled = true;
                    window.scrollTo(0, 0);

                    await new Promise(resolve => setTimeout(resolve, 200));

                    const buttons = document.querySelector('.save-buttons');
                    buttons.style.visibility = 'hidden';

                    await new Promise(resolve => setTimeout(resolve, 100));

                    const container = document.querySelector('.container');

                    const canvas = await html2canvas(container, {
                        backgroundColor: '#ffffff',
                        scale: 1.5,
                        useCORS: true,
                        allowTaint: false,
                        imageTimeout: 10000,
                        removeContainer: false,
                        foreignObjectRendering: false,
                        logging: false,
                        width: container.offsetWidth,
                        height: container.offsetHeight,
                        x: 0,
                        y: 0,
                        scrollX: 0,
                        scrollY: 0,
                        windowWidth: window.innerWidth,
                        windowHeight: window.innerHeight
                    });

                    buttons.style.visibility = 'visible';

                    const link = document.createElement('a');
                    const now = new Date();
                    const filename = `章鱼AI_RSS订阅_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.png`;

                    link.download = filename;
                    link.href = canvas.toDataURL('image/png', 1.0);

                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);

                    button.textContent = '保存成功!';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.disabled = false;
                    }, 2000);

                } catch (error) {
                    const buttons = document.querySelector('.save-buttons');
                    buttons.style.visibility = 'visible';
                    button.textContent = '保存失败';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.disabled = false;
                    }, 2000);
                }
            }

            document.addEventListener('DOMContentLoaded', function() {
                window.scrollTo(0, 0);
            });
        </script>
    </body>
    </html>
    """

    return html
