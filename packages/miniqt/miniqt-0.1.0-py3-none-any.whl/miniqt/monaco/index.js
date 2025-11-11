var bridge = null;
var editor = null;

require.config({ paths: { 'vs': 'monaco-editor/min/vs' } });
require(['vs/editor/editor.main'], () => {
    container = document.getElementById('container')
    editor = monaco.editor.create(container, {
        fontFamily: "Verdana",
        automaticLayout: true,
        language: "python",

        acceptSuggestionOnCommitCharacter: true, // 接受关于提交字符的建议
        acceptSuggestionOnEnter: 'on', // 接受输入建议 "on" | "off" | "smart" 
        accessibilityPageSize: 10, // 辅助功能页面大小 Number 说明：控制编辑器中可由屏幕阅读器读出的行数。警告：这对大于默认值的数字具有性能含义。
        accessibilitySupport: 'on', // 辅助功能支持 控制编辑器是否应在为屏幕阅读器优化的模式下运行。"auto" | "off" | "on"
        autoClosingBrackets: 'always', // 是否自动添加结束括号(包括中括号) "always" | "languageDefined" | "beforeWhitespace" | "never"
        autoClosingDelete: 'always', // 是否自动删除结束括号(包括中括号) "always" | "never" | "auto"
        autoClosingOvertype: 'always', // 是否关闭改写 即使用insert模式时是覆盖后面的文字还是不覆盖后面的文字 "always" | "never" | "auto"
        autoClosingQuotes: 'always', // 是否自动添加结束的单引号 双引号 "always" | "languageDefined" | "beforeWhitespace" | "never"
        autoIndent: 'None', // 控制编辑器在用户键入、粘贴、移动或缩进行时是否应自动调整缩进
        codeLens: false, // 是否显示codeLens 通过 CodeLens，你可以在专注于工作的同时了解代码所发生的情况 – 而无需离开编辑器。 可以查找代码引用、代码更改、关联的 Bug、工作项、代码评审和单元测试。
        codeLensFontFamily: '', // codeLens的字体样式
        codeLensFontSize: 14, // codeLens的字体大小
        comments: {
            ignoreEmptyLines: true, // 插入行注释时忽略空行。默认为真。
            insertSpace: true // 在行注释标记之后和块注释标记内插入一个空格。默认为真。
        }, // 注释配置
        contextmenu: true, // 启用上下文菜单
        columnSelection: false, // 启用列编辑 按下shift键位然后按↑↓键位可以实现列选择 然后实现列编辑
        autoSurround: 'never', // 是否应自动环绕选择
        copyWithSyntaxHighlighting: true, // 是否应将语法突出显示复制到剪贴板中 即 当你复制到word中是否保持文字高亮颜色
        cursorBlinking: 'Solid', // 光标动画样式
        cursorSmoothCaretAnimation: true, // 是否启用光标平滑插入动画  当你在快速输入文字的时候 光标是直接平滑的移动还是直接"闪现"到当前文字所处位置
        cursorStyle: 'UnderlineThin', // "Block"|"BlockOutline"|"Line"|"LineThin"|"Underline"|"UnderlineThin" 光标样式
        cursorSurroundingLines: 0, // 光标环绕行数 当文字输入超过屏幕时 可以看见右侧滚动条中光标所处位置是在滚动条中间还是顶部还是底部 即光标环绕行数 环绕行数越大 光标在滚动条中位置越居中
        cursorSurroundingLinesStyle: 'all', // "default" | "all" 光标环绕样式
        cursorWidth: 2, // <=25 光标宽度
        minimap: {
            enabled: true // 是否启用预览图
        }, // 预览图设置
        folding: true, // 是否启用代码折叠
        links: true, // 是否点击链接
        overviewRulerBorder: false, // 是否应围绕概览标尺绘制边框
        renderLineHighlight: 'gutter', // 当前行突出显示方式
        roundedSelection: false, // 选区是否有圆角
        scrollBeyondLastLine: false, // 设置编辑器是否可以滚动到最后一行之后
        readOnly: false, // 是否为只读模式
        foldingHighlight: true, // 折叠等高线
        foldingStrategy: "indentation", // 折叠方式  auto | indentation
        showFoldingControls: "always", // 是否一直显示折叠 always | mouseover
        disableLayerHinting: true, // 等宽优化
        emptySelectionClipboard: false, // 空选择剪切板
        selectionClipboard: false, // 选择剪切板
        colorDecorators: true, // 颜色装饰器
        lineNumbers: "on", // 行号 取值： "on" | "off" | "relative" | "interval" | function
        lineNumbersMinChars: 4, // 行号最小字符   number
    });
    editor.onDidChangeModelContent((event) => {
        sendToPython("value", editor.getModel().getValue())
    })
    editor.onDidChangeModelLanguage((event) => {
        sendToPython("language", event.newLanguage)
    })
});

monaco.languages.registerCompletionItemProvider('python', {
    provideCompletionItems: function (model, position) {
        var word = model.getWordUntilPosition(position);
        var range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn
        };
        return {
            suggestions: createDependencyProposals(range, languageService, editor, word)
        };
    }
});


var python_keys = [
    // python keywords
    "and", "or", "not", "if", "elif", "else","for","while", "True","False","continue","break", "pass","try","except","finally","raise",
    "import","from","as","def","return","class","lambda","del","global","nonlocal","in","is","None","assert","with","yield","async","await",
    
    
    // python built-in functions
    'abs',
    'sum',
    // pd
    "DataFrame","Series"
];

function createDependencyProposals(range, languageService = false, editor, curWord) {
    // snippets的定义同上
	// keys（泛指一切待补全的预定义词汇）的定义：
	let keys = [];
	for (const item of python_keys) {
    	keys.push({
        	label: item,
        	kind: monaco.languages.CompletionItemKind.Keyword,
        	documentation: "",
        	insertText: item,
        	range: range
    	});
	}
	return snippets.concat(keys);
}
function init() {
    sendToPython("value", editor.getModel().getValue());
    sendToPython("language", editor.getModel().getLanguageId());
    sendToPython("theme", editor._themeService._theme.themeName);
}

function sendToPython(name, value) {
    bridge.receive_from_js(name, JSON.stringify(value));
}

function updateFromPython(name, value) {
    var data = JSON.parse(value)
    switch (name) {
        case "value":
            editor.getModel().setValue(data);
            break;
        case "language":
            monaco.editor.setModelLanguage(editor.getModel(), data);
            break;
        case "theme":
            monaco.editor.setTheme(data);
            sendToPython("theme", editor._themeService._theme.themeName);
            break;
    }
}

window.onload = function () {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        bridge = channel.objects.bridge;
        bridge.sendDataChanged.connect(updateFromPython);
        bridge.init();
        init();
    });
}
