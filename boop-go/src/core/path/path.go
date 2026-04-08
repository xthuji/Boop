package path

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

var (
	// AppRoot 应用根目录
	AppRoot string
	// IsDevelopment 是否为开发环境
	IsDevelopment bool
)

// Init 初始化路径处理
func Init() error {
	// 首先尝试从当前工作目录查找项目根目录
	cwd, err := os.Getwd()
	if err == nil {
		if projectRoot := findProjectRoot(cwd); projectRoot != "" {
			AppRoot = projectRoot
			IsDevelopment = true
			fmt.Printf("开发环境，应用根目录: %s\n", AppRoot)
			
			// 确保所有必要的目录存在
			if err := ensureDirectories(); err != nil {
				return err
			}
			
			return nil
		}
	}

	// 如果从当前工作目录找不到，尝试从可执行文件路径查找
	execPath, err := os.Executable()
	if err != nil {
		return err
	}

	// 获取可执行文件所在目录
	execDir := filepath.Dir(execPath)

	// 检查是否为开发环境
	// 开发环境：可执行文件位于项目根目录或其子目录
	// 正式环境：可执行文件位于系统软件目录
	IsDevelopment = isDevelopmentEnvironment(execDir)

	if IsDevelopment {
		// 开发环境：使用项目根目录
		// 假设可执行文件位于项目根目录或其子目录
		// 向上查找，直到找到包含 go.mod 文件的目录
		AppRoot = findProjectRoot(execDir)
		fmt.Printf("开发环境，应用根目录: %s\n", AppRoot)
	} else {
		// 正式环境：使用可执行文件所在目录
		AppRoot = execDir
		fmt.Printf("正式环境，应用根目录: %s\n", AppRoot)
	}

	// 确保所有必要的目录存在
	if err := ensureDirectories(); err != nil {
		return err
	}

	return nil
}

// isDevelopmentEnvironment 检测是否为开发环境
func isDevelopmentEnvironment(execDir string) bool {
	// 检查是否存在 go.mod 文件
	for dir := execDir; dir != "/"; dir = filepath.Dir(dir) {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return true
		}
	}

	// 检查是否为常见的系统软件目录
	systemDirs := []string{
		"/Applications",
		"/usr/local/bin",
		"/usr/bin",
		"/bin",
	}

	for _, sysDir := range systemDirs {
		if strings.HasPrefix(execDir, sysDir) {
			return false
		}
	}

	// 默认认为是开发环境
	return true
}

// findProjectRoot 查找项目根目录
func findProjectRoot(startDir string) string {
	for dir := startDir; dir != "/"; dir = filepath.Dir(dir) {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
	}
	// 如果找不到，返回空字符串
	return ""
}

// ensureDirectories 确保所有必要的目录存在
func ensureDirectories() error {
	dirs := []string{
		ScriptsDir(),
		DataDir(),
		CacheDir(),
		LogsDir(),
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return err
		}
	}

	return nil
}

// ScriptsDir 获取脚本目录
func ScriptsDir() string {
	return filepath.Join(AppRoot, "scripts")
}

// DataDir 获取数据目录
func DataDir() string {
	return filepath.Join(AppRoot, "data")
}

// CacheDir 获取缓存目录
func CacheDir() string {
	return filepath.Join(DataDir(), "cache")
}

// LogsDir 获取日志目录
func LogsDir() string {
	return filepath.Join(AppRoot, "logs")
}

// ExpandPath 展开路径中的 ~ 为用户目录
func ExpandPath(p string) string {
	if strings.HasPrefix(p, "~/") || p == "~" {
		home, err := os.UserHomeDir()
		if err != nil {
			return p
		}
		if p == "~" {
			return home
		}
		return filepath.Join(home, p[2:])
	}
	return p
}
