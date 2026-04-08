package script

import (
	"bytes"
	"context"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"
)

// ScriptExecutor 脚本执行器
type ScriptExecutor struct {
	PythonPath string                    // Python 解释器路径
	Timeout    time.Duration             // 脚本执行超时时间
	stdout     bytes.Buffer              // 重用的标准输出缓冲区
	stderr     bytes.Buffer              // 重用的标准错误缓冲区
	scriptCache map[string]string        // 脚本缓存，键为脚本路径，值为编译后的脚本
	cacheMutex sync.RWMutex              // 缓存并发锁
}

// NewScriptExecutor 创建新的脚本执行器
func NewScriptExecutor(pythonPath string, timeout time.Duration) *ScriptExecutor {
	return &ScriptExecutor{
		PythonPath: pythonPath,
		Timeout:    timeout,
		stdout:     bytes.Buffer{},
		stderr:     bytes.Buffer{},
		scriptCache: make(map[string]string),
		cacheMutex: sync.RWMutex{},
	}
}

// Execute 执行脚本
func (e *ScriptExecutor) Execute(scriptPath, text string) (string, error, []string, []string) {
	// 从缓存中获取包装脚本，或构建新的包装脚本
	var wrapperScript string
	e.cacheMutex.RLock()
	cachedScript, ok := e.scriptCache[scriptPath]
	e.cacheMutex.RUnlock()
	
	if ok {
		wrapperScript = cachedScript
	} else {
		// 构建包装脚本
		wrapperScript = e.buildWrapperScript(scriptPath)
		// 缓存包装脚本
		e.cacheMutex.Lock()
		e.scriptCache[scriptPath] = wrapperScript
		e.cacheMutex.Unlock()
	}

	// 创建上下文，支持超时
	ctx, cancel := context.WithTimeout(context.Background(), e.Timeout)
	defer cancel()

	// 执行 Python 子进程
	cmd := exec.CommandContext(ctx, e.PythonPath, "-c", wrapperScript)
	cmd.Stdin = strings.NewReader(text)

	// 重用缓冲区，避免每次都创建新的缓冲区
	e.stdout.Reset()
	e.stderr.Reset()
	cmd.Stdout = &e.stdout
	cmd.Stderr = &e.stderr

	// 执行命令
	err := cmd.Run()

	// 解析输出
	result := strings.TrimSpace(e.stdout.String())
	errorOutput := strings.TrimSpace(e.stderr.String())

	// 解析信息和错误消息
	infoMessages, errorMessages := e.parseMessages(errorOutput)

	return result, err, infoMessages, errorMessages
}

// buildWrapperScript 构建包装脚本
func (e *ScriptExecutor) buildWrapperScript(scriptPath string) string {
	// 读取原始脚本内容
	scriptContent, err := os.ReadFile(scriptPath)
	if err != nil {
		return fmt.Sprintf("print('Error reading script: %v')", err)
	}

	// 构建包装脚本
	wrapper := `
import sys

class State:
    def __init__(self, text):
        self.text = text
        self._info_messages = []
        self._error_messages = []

    def insert(self, text, position=None):
        if position is None:
            self.text += text
        else:
            self.text = self.text[:position] + text + self.text[position:]

    def post_info(self, message):
        self._info_messages.append(message)

    def post_error(self, message):
        self._error_messages.append(message)

# 读取输入文本
text = sys.stdin.read()

# 创建状态对象
state = State(text)

# 执行脚本
`

	// 添加原始脚本
	wrapper += string(scriptContent)

	// 添加执行 main 函数和输出结果的代码
	wrapper += `
# 执行 main 函数
try:
    main(state)
except Exception as e:
    state.post_error(str(e))

# 输出结果
print(state.text)

# 输出信息和错误消息
for msg in state._info_messages:
    print('INFO:', msg, file=sys.stderr)
for msg in state._error_messages:
    print('ERROR:', msg, file=sys.stderr)
`

	return wrapper
}

// parseMessages 解析信息和错误消息
func (e *ScriptExecutor) parseMessages(output string) ([]string, []string) {
	var infoMessages, errorMessages []string

	lines := strings.Split(output, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "INFO:") {
			infoMessages = append(infoMessages, strings.TrimPrefix(line, "INFO:"))
		} else if strings.HasPrefix(line, "ERROR:") {
			errorMessages = append(errorMessages, strings.TrimPrefix(line, "ERROR:"))
		}
	}

	return infoMessages, errorMessages
}
