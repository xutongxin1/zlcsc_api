// ==UserScript==
// @name         替换Un函数并注入Console拦截器 - 完整版
// @namespace    http://tampermonkey.net/
// @version      4.0
// @description  在HTML加载前替换Un函数并注入console日志拦截器
// @author       You
// @match        file:///*InteractiveBOM*.html
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    // 检查是否已经处理过，避免无限刷新
    if (window.location.href.includes('#un-replaced') ||
        sessionStorage.getItem('un-replaced') ||
        window.location.protocol === 'blob:') {
        console.log('页面已经处理过或是blob URL，跳过替换');
        return;
    }

    console.log('Tampermonkey脚本开始执行...');
    // 新的Un函数定义
    const newUnFunction = `function Un(uniqueId, state, context, flag) {
    if (state.ids[uniqueId]) {
        // 如果该ID已经被选中，并且flag不为true，则取消选中
        if (flag !== true) {
            // 更新选择状态为未选中
            Zr(uniqueId, false);
            // 从已选中ID列表中移除
            delete state.ids[uniqueId];
        }
    } else {
        // 如果该ID未被选中，并且flag不为false，则进行选中操作
        if (flag !== false) {
            // 遍历所有ID的数据，找到匹配的ID并更新光标位置
            state.allIdsData.forEach(item => {
                if (item.UniqueID === uniqueId) {
                    console.log(\`器件编号:\${item.Customer_Component_Code}, 器件名称:\${item.Customer_Comment}, 封装:\${item.Customer_Footprint_Name}\`);
                    context.cursorPosition = {
                        x: item["Mid X"] / Mi, // 假设Mi是一个已定义的缩放因子
                        y: item["Mid Y"] / Mi
                    };
                    // 重新渲染界面
                    context.render();
                }
            });
            // 更新选择状态为选中
            Zr(uniqueId, true);
            // 将该ID标记为已选中
            state.ids[uniqueId] = true;
        }
    }
}`;

    // Console拦截器代码
    const consoleInterceptorCode = `
    <script>
    (function() {
        'use strict';
        console.log('Console拦截器已注入并开始运行...');

        const serverUrl = 'http://127.0.0.1:18888/log'; // 替换为你的HTTP服务器地址和端口

        // 保存原始的console方法引用
        const originalConsole = {
            log: console.log.bind(console),
            error: console.error.bind(console),
            warn: console.warn.bind(console),
            info: console.info.bind(console),
            debug: console.debug.bind(console)
        };

        // 检查日志是否以"器件编号"开头
        function shouldSendLog(args) {
            if (args.length === 0) return false;

            // 获取第一个参数
            const firstArg = args[0];

            // 如果是字符串，直接检查
            if (typeof firstArg === 'string') {
                return firstArg.startsWith('器件编号');
            }

            // 如果是对象，尝试转换为字符串后检查
            try {
                const str = String(firstArg);
                return str.startsWith('器件编号');
            } catch (e) {
                return false;
            }
        }

        // 拦截console方法
        const methods = ['log', 'error', 'warn', 'info', 'debug'];
        methods.forEach(function(method) {
            console[method] = function(...args) {
                // 调用原始的console方法
                originalConsole[method].apply(console, args);

                // 只有以"器件编号"开头的日志才发送
                if (!shouldSendLog(args)) {
                    return;
                }

                // 构建消息对象
                const message = {
                    method: method,
                    arguments: args,
                    timestamp: new Date().toISOString(),
                    url: window.location.href
                };

                // 发送到HTTP服务器
                fetch(serverUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(message)
                }).catch(err => {
                    // 使用原始的console方法记录错误，避免无限递归
                    originalConsole.error('发送日志到服务器失败:', err);
                });
            };
        });

        console.log('Console拦截器设置完成');
    })();
    </script>`;

    // 修复Blob URL的路径问题
    function createNewPageFixed() {
        window.stop();
        const originalUrl = window.location.href;
        const baseUrl = originalUrl.substring(0, originalUrl.lastIndexOf('/') + 1);

        fetch(originalUrl)
            .then(response => response.text())
            .then(html => {
            console.log('获取到原始HTML，准备创建新页面...');

            // 替换Un函数
            let modifiedHtml = replaceUnFunctionInHtml(html);

            // 修复相对路径问题 - 添加base标签
            const baseTag = `<base href="${baseUrl}">`;
            if (!modifiedHtml.includes('<base')) {
                modifiedHtml = modifiedHtml.replace('<head>', `<head>\n${baseTag}`);
            }

            // 注入console拦截器代码
            // 将代码插入到head标签的末尾，确保在其他脚本之前运行
            modifiedHtml = modifiedHtml.replace('</head>', `${consoleInterceptorCode}\n</head>`);

            // 如果没有head标签，则插入到body之前
            if (!modifiedHtml.includes('</head>')) {
                modifiedHtml = modifiedHtml.replace('<body', `${consoleInterceptorCode}\n<body`);
            }

            // 添加标记，表示页面已经处理过
            modifiedHtml = modifiedHtml.replace('<html', '<html data-un-replaced="true"');

            // 创建Blob URL
            const blob = new Blob([modifiedHtml], { type: 'text/html' });
            const newUrl = URL.createObjectURL(blob);

            // 设置标记
            sessionStorage.setItem('un-replaced', 'true');

            // 跳转到新页面
            window.location.replace(newUrl);
        })
            .catch(error => {
            console.error('处理失败:', error);
        });
    }


    // 通用的Un函数替换方法
    function replaceUnFunctionInHtml(html) {
        const startPattern = /function\s+Un\s*\(\s*r\s*,\s*n\s*,\s*t\s*,\s*e\s*\)\s*\{/g;

        let result = html;
        let lastIndex = 0;
        let output = '';
        let match;

        while ((match = startPattern.exec(html)) !== null) {
            const startIndex = match.index;
            const afterStart = startIndex + match[0].length;

            // 找到平衡的结束大括号
            let braceCount = 1;
            let i = afterStart;

            while (i < html.length && braceCount > 0) {
                if (html[i] === '{') {
                    braceCount++;
                } else if (html[i] === '}') {
                    braceCount--;
                }
                i++;
            }

            if (braceCount === 0) {
                // 找到了完整的函数
                output += html.substring(lastIndex, startIndex) + newUnFunction;
                lastIndex = i;
                console.log('成功替换一处Un函数');
            }
        }

        // 添加剩余部分
        output += html.substring(lastIndex);

        return output !== '' ? output : html;
    }

    // 执行替换
    createNewPageFixed();
})();