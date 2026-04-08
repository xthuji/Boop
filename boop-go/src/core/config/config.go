package config

import (
	"boop-go/src/core/log"
	"boop-go/src/core/path"
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"sync"
)

type Config struct {
	App       AppConfig       `json:"app"`
	Editor    EditorConfig    `json:"editor"`
	Script    ScriptConfig    `json:"script"`
	Shortcuts ShortcutsConfig `json:"shortcuts"`
}

type AppConfig struct {
	WindowWidth         int  `json:"window_width"`
	WindowHeight        int  `json:"window_height"`
	MaximizeWindow      bool `json:"maximize_window"`
	EnableGlobalHotkeys bool `json:"enable_global_hotkeys"`
}

type EditorConfig struct {
	FontFamily string `json:"font_family"`
	FontSize   int    `json:"font_size"`
}

type ScriptConfig struct {
	PythonPath  string   `json:"python_path"`
	ScriptDirs  []string `json:"script_dirs"`
	Timeout     int      `json:"timeout"`
	FilterDelay int      `json:"filter_delay"`
}

type ShortcutsConfig struct {
	Quit            []string `json:"quit"`
	RunScript       []string `json:"run_script"`
	GlobalRunScript []string `json:"global_run_script"`
	Preferences     []string `json:"preferences"`
	Undo            []string `json:"undo"`
	Redo            []string `json:"redo"`
	Cut             []string `json:"cut"`
	Copy            []string `json:"copy"`
	Paste           []string `json:"paste"`
	SelectAll       []string `json:"select_all"`
	MoveToStart     []string `json:"move_to_start"`
	MoveToEnd       []string `json:"move_to_end"`
	Indent          []string `json:"indent"`
	Outdent         []string `json:"outdent"`
}

func getDefaultShortcuts() ShortcutsConfig {
	isMac := runtime.GOOS == "darwin"

	if isMac {
		return ShortcutsConfig{
			Quit:            []string{"Command+q"},
			RunScript:       []string{"Command+b"},
			GlobalRunScript: []string{"Command+b"},
			Preferences:     []string{"Command+,"},
			Undo:            []string{"Command+z"},
			Redo:            []string{"Command+Shift+Z", "Command+y"},
			Cut:             []string{"Command+x"},
			Copy:            []string{"Command+c"},
			Paste:           []string{"Command+v"},
			SelectAll:       []string{"Command+a"},
			MoveToStart:     []string{"Command+Up"},
			MoveToEnd:       []string{"Command+Down"},
			Indent:          []string{"Tab"},
			Outdent:         []string{"Shift+Tab"},
		}
	}

	return ShortcutsConfig{
		Quit:            []string{"Control+q"},
		RunScript:       []string{"Control+b"},
		GlobalRunScript: []string{"Control+b"},
		Preferences:     []string{"Control+,"},
		Undo:            []string{"Control+z"},
		Redo:            []string{"Control+Shift+Z", "Control+y"},
		Cut:             []string{"Control+x"},
		Copy:            []string{"Control+c"},
		Paste:           []string{"Control+v"},
		SelectAll:       []string{"Control+a"},
		MoveToStart:     []string{"Control+Home"},
		MoveToEnd:       []string{"Control+End"},
		Indent:          []string{"Tab"},
		Outdent:         []string{"Shift+Tab"},
	}
}

func DefaultConfig() *Config {
	return &Config{
		App: AppConfig{
			WindowWidth:    800,
			WindowHeight:   600,
			MaximizeWindow: false,
		},
		Editor: EditorConfig{
			FontFamily: "Monaco",
			FontSize:   14,
		},
		Script: ScriptConfig{
			PythonPath: "python3",
			Timeout:    10,
		},
		Shortcuts: getDefaultShortcuts(),
	}
}

func (c *Config) Validate() error {
	defaults := DefaultConfig()

	if c.App.WindowWidth < 400 {
		c.App.WindowWidth = 400
	}
	if c.App.WindowHeight < 300 {
		c.App.WindowHeight = 300
	}

	if c.Editor.FontFamily == "" {
		c.Editor.FontFamily = defaults.Editor.FontFamily
	}
	if c.Editor.FontSize < 8 {
		c.Editor.FontSize = 8
	} else if c.Editor.FontSize > 72 {
		c.Editor.FontSize = 72
	}

	if c.Script.PythonPath == "" {
		c.Script.PythonPath = defaults.Script.PythonPath
	}
	if c.Script.Timeout < 1 {
		c.Script.Timeout = 1
	} else if c.Script.Timeout > 60 {
		c.Script.Timeout = 60
	}

	c.Script.PythonPath = path.ExpandPath(c.Script.PythonPath)
	for i, dir := range c.Script.ScriptDirs {
		c.Script.ScriptDirs[i] = path.ExpandPath(dir)
	}

	return nil
}

type Manager struct {
	config     *Config
	configPath string
	mutex      sync.RWMutex
}

func NewManager() *Manager {
	configPath := getConfigPath()
	config, err := loadConfig(configPath)
	if err != nil {
		log.Warning("读取配置失败，使用默认配置: %v", err)
		config = DefaultConfig()
	}

	return &Manager{
		config:     config,
		configPath: configPath,
	}
}

func getConfigPath() string {
	dataDir := path.DataDir()
	if err := os.MkdirAll(dataDir, 0755); err != nil {
		log.Error("创建数据目录失败: %v", err)
		return "config.json"
	}
	configPath := filepath.Join(dataDir, "config.json")
	log.Debug("配置文件路径: %s", configPath)
	return configPath
}

func loadConfig(configPath string) (*Config, error) {
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		return DefaultConfig(), nil
	}

	content, err := os.ReadFile(configPath)
	if err != nil {
		return DefaultConfig(), err
	}

	config := &Config{}
	if err := json.Unmarshal(content, config); err != nil {
		return DefaultConfig(), err
	}

	if err := config.Validate(); err != nil {
		return config, err
	}

	if config.Shortcuts.Quit == nil {
		config.Shortcuts = getDefaultShortcuts()
	}

	return config, nil
}

func saveConfig(configPath string, config *Config) error {
	if err := config.Validate(); err != nil {
		return err
	}

	configCopy := *config
	configCopy.Shortcuts = ShortcutsConfig{}

	content, err := json.MarshalIndent(configCopy, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(configPath, content, 0644)
}

func (m *Manager) GetConfig() *Config {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	config := *m.config
	return &config
}

func (m *Manager) GetAppConfig() AppConfig {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	return m.config.App
}

func (m *Manager) GetEditorConfig() EditorConfig {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	return m.config.Editor
}

func (m *Manager) GetScriptConfig() ScriptConfig {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	return m.config.Script
}

func (m *Manager) GetShortcutsConfig() ShortcutsConfig {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	return m.config.Shortcuts
}

func (m *Manager) SetConfig(config *Config) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	if err := config.Validate(); err != nil {
		return err
	}

	m.config = config
	return saveConfig(m.configPath, config)
}

func (m *Manager) UpdateAppConfig(appConfig AppConfig) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.config.App = appConfig
	if err := m.config.Validate(); err != nil {
		return err
	}
	return saveConfig(m.configPath, m.config)
}

func (m *Manager) UpdateEditorConfig(editorConfig EditorConfig) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.config.Editor = editorConfig
	if err := m.config.Validate(); err != nil {
		return err
	}
	return saveConfig(m.configPath, m.config)
}

func (m *Manager) UpdateScriptConfig(scriptConfig ScriptConfig) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.config.Script = scriptConfig
	if err := m.config.Validate(); err != nil {
		return err
	}
	return saveConfig(m.configPath, m.config)
}

func (m *Manager) Load() error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	config, err := loadConfig(m.configPath)
	if err != nil {
		return err
	}
	m.config = config
	return nil
}

func (m *Manager) Save() error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	if err := m.config.Validate(); err != nil {
		return err
	}
	return saveConfig(m.configPath, m.config)
}

func (m *Manager) GetConfigPath() string {
	return m.configPath
}
