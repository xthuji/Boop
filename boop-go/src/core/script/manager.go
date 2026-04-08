package script

import (
	"boop-go/src/core/log"
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// ScriptManager 脚本管理器
type ScriptManager struct {
	scripts      []*ScriptMetadata // 脚本列表
	scriptDirs   []string         // 脚本目录
	lastScanTime time.Time         // 最后扫描时间
	mutex        sync.RWMutex      // 并发锁
	loaded       bool              // 脚本是否已加载
}

// NewScriptManager 创建新的脚本管理器
func NewScriptManager(scriptDirs []string) *ScriptManager {
	manager := &ScriptManager{
		scriptDirs: scriptDirs,
		scripts:    make([]*ScriptMetadata, 0),
		loaded:     false,
	}

	// 检查缓存文件是否存在，如果存在则尝试从缓存加载
	if IsCacheExists() {
		// 从缓存加载脚本元数据
		if err := loadFromCache(manager); err == nil {
			manager.loaded = true
			log.Info("从缓存加载脚本元数据成功")
		} else {
			log.Warning("从缓存加载脚本元数据失败: %v，将重新加载脚本", err)
			// 缓存加载失败，异步加载脚本
			go manager.LoadScripts()
		}
	} else {
		// 缓存文件不存在，异步加载脚本
		go manager.LoadScripts()
	}

	return manager
}

// loadFromCache 从缓存加载脚本元数据
func loadFromCache(m *ScriptManager) error {
	cachePath := getCachePath()
	file, err := os.Open(cachePath)
	if err != nil {
		return err
	}
	defer file.Close()

	data, err := io.ReadAll(file)
	if err != nil {
		return err
	}

	var scripts []*ScriptMetadata
	if err := json.Unmarshal(data, &scripts); err != nil {
		return err
	}

	m.scripts = scripts
	m.lastScanTime = time.Now()
	return nil
}

// LoadScripts 加载所有脚本
func (m *ScriptManager) LoadScripts() error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	ClearCache()

	var scripts []*ScriptMetadata
	var wg sync.WaitGroup
	var mu sync.Mutex
	var walkErr error

	log.Info("开始加载脚本，脚本目录: %v", m.scriptDirs)

	// 并行扫描所有脚本目录
	for _, dir := range m.scriptDirs {
		wg.Add(1)
		go func(dir string) {
			defer wg.Done()
			
			if err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
				if err != nil {
					mu.Lock()
					walkErr = err
					mu.Unlock()
					log.Error("遍历脚本目录失败: %v", err)
					return err
				}

				// 跳过 lib 目录
				if info.IsDir() && info.Name() == "lib" {
					log.Debug("跳过 lib 目录: %s", path)
					return filepath.SkipDir
				}

				// 只处理 .py 文件，跳过 __init__.py
				if !info.IsDir() && strings.HasSuffix(path, ".py") && info.Name() != "__init__.py" {
					// 获取完整路径
					absPath, err := filepath.Abs(path)
					if err != nil {
						// 获取完整路径失败，使用原始路径
						log.Warning("获取完整路径失败: %v，使用原始路径: %s", err, path)
						absPath = path
					}
					// 解析脚本元数据
					metadata, err := ParseMetadata(absPath)
					if err != nil {
						log.Error("解析脚本元数据失败: %v，脚本路径: %s", err, absPath)
					} else if metadata != nil && metadata.IsValid() {
						mu.Lock()
						scripts = append(scripts, metadata)
						mu.Unlock()
						log.Debug("加载脚本成功: %s", metadata.Name)
					}
				}

				return nil
			}); err != nil {
				mu.Lock()
				walkErr = err
				mu.Unlock()
				log.Error("扫描脚本目录失败: %v", err)
			}
		}(dir)
	}

	// 等待所有目录扫描完成
	wg.Wait()

	// 检查是否有错误
	if walkErr != nil {
		return walkErr
	}

	// 按名称排序
	sort.Slice(scripts, func(i, j int) bool {
		return scripts[i].Name < scripts[j].Name
	})

	m.scripts = scripts
	m.lastScanTime = time.Now()
	m.loaded = true

	log.Info("脚本加载完成，共加载 %d 个脚本", len(scripts))

	// 保存脚本元数据到缓存文件
	go func() {
		if err := saveScriptsToCache(scripts); err != nil {
			log.Warning("保存脚本元数据到缓存失败: %v", err)
		} else {
			log.Info("脚本元数据已保存到缓存")
		}
	}()

	return nil
}

// saveScriptsToCache 保存脚本元数据到缓存文件
func saveScriptsToCache(scripts []*ScriptMetadata) error {
	cachePath := getCachePath()

	// 序列化脚本元数据
	data, err := json.MarshalIndent(scripts, "", "  ")
	if err != nil {
		return err
	}

	// 写入缓存文件
	if err := os.WriteFile(cachePath, data, 0644); err != nil {
		return err
	}

	return nil
}

// ensureScriptsLoaded 确保脚本已加载（从缓存或重新加载）
func (m *ScriptManager) ensureScriptsLoaded() {
	m.mutex.RLock()
	if m.loaded {
		m.mutex.RUnlock()
		return
	}
	m.mutex.RUnlock()

	// 脚本未加载，尝试从缓存加载
	if IsCacheExists() {
		// 从缓存加载
		m.mutex.Lock()
		if err := loadFromCache(m); err == nil {
			m.loaded = true
			log.Info("从缓存加载脚本元数据成功")
		} else {
			log.Warning("从缓存加载脚本元数据失败: %v，将重新加载脚本", err)
			// 缓存加载失败，重新加载脚本
			m.LoadScripts()
		}
		m.mutex.Unlock()
	} else {
		// 缓存不存在，重新加载脚本
		m.LoadScripts()
	}
}

// GetScripts 获取所有脚本
func (m *ScriptManager) GetScripts() []*ScriptMetadata {
	m.ensureScriptsLoaded()
	return m.scripts
}

// SearchScripts 搜索脚本
func (m *ScriptManager) SearchScripts(query string) []*ScriptMetadata {
	m.ensureScriptsLoaded()

	m.mutex.RLock()
	defer m.mutex.RUnlock()

	if query == "" {
		return m.scripts
	}

	query = strings.ToLower(query)
	var results []*ScriptMetadata

	for _, script := range m.scripts {
		// 搜索名称
		if strings.Contains(strings.ToLower(script.Name), query) {
			results = append(results, script)
			continue
		}

		// 搜索描述
		if strings.Contains(strings.ToLower(script.Description), query) {
			results = append(results, script)
			continue
		}

		// 搜索标签
		for _, tag := range script.Tags {
			if strings.Contains(strings.ToLower(tag), query) {
				results = append(results, script)
				break
			}
		}
	}

	return results
}

// GetScriptByPath 根据路径获取脚本
func (m *ScriptManager) GetScriptByPath(path string) *ScriptMetadata {
	m.ensureScriptsLoaded()

	m.mutex.RLock()
	defer m.mutex.RUnlock()

	for _, script := range m.scripts {
		if script.FilePath == path {
			return script
		}
	}

	return nil
}

// AddScriptDir 添加脚本目录
func (m *ScriptManager) AddScriptDir(dir string) {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	// 检查目录是否已存在
	for _, d := range m.scriptDirs {
		if d == dir {
			return
		}
	}

	m.scriptDirs = append(m.scriptDirs, dir)
}

// RemoveScriptDir 移除脚本目录
func (m *ScriptManager) RemoveScriptDir(dir string) {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	for i, d := range m.scriptDirs {
		if d == dir {
			m.scriptDirs = append(m.scriptDirs[:i], m.scriptDirs[i+1:]...)
			break
		}
	}
}

// GetScriptDirs 获取脚本目录
func (m *ScriptManager) GetScriptDirs() []string {
	m.mutex.RLock()
	defer m.mutex.RUnlock()

	return m.scriptDirs
}

// LastScanTime 获取最后扫描时间
func (m *ScriptManager) LastScanTime() time.Time {
	m.mutex.RLock()
	defer m.mutex.RUnlock()

	return m.lastScanTime
}

// GetAllMetadata 获取所有脚本的元数据（用于依赖管理）
func (m *ScriptManager) GetAllMetadata() map[string]*ScriptMetadata {
	m.ensureScriptsLoaded()

	m.mutex.RLock()
	defer m.mutex.RUnlock()

	result := make(map[string]*ScriptMetadata)
	for _, script := range m.scripts {
		result[script.FilePath] = script
	}
	return result
}
