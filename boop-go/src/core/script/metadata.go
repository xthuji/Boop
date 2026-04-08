package script

import (
	"boop-go/src/core/log"
	"boop-go/src/core/path"
	"encoding/json"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// ScriptMetadata 脚本元数据结构
type ScriptMetadata struct {
	Name         string   `json:"name"`         // 脚本名称
	Description  string   `json:"description"`  // 脚本描述
	Tags         []string `json:"tags"`         // 脚本标签
	Dependencies []string `json:"dependencies"` // 依赖项
	Icon         string   `json:"icon"`         // 图标
	Help         string   `json:"help"`         // 脚本帮助信息
	FilePath     string   `json:"file_path"`    // 脚本文件路径
	ModuleName   string   `json:"module_name"`  // 模块名称
	Bias         int      `json:"bias"`         // 偏置值
	Filename     string   `json:"filename"`     // 文件名
}

// cache 缓存数据，格式与Python一致: {file_path: {'mtime': mtime, 'metadata': metadata}}
var cache = make(map[string]map[string]interface{})
var cacheLoaded bool

// getCachePath 获取缓存文件路径
func getCachePath() string {
	// 使用path包中的CacheDir函数获取缓存目录
	cacheDir := path.CacheDir()
	
	// 确保缓存目录存在
	if err := os.MkdirAll(cacheDir, 0755); err != nil {
		log.Error("创建缓存目录失败: %v", err)
		return "metadata.json"
	}

	// 构建缓存文件路径
	cachePath := filepath.Join(cacheDir, "metadata.json")
	log.Debug("缓存文件路径: %s", cachePath)

	return cachePath
}

// IsCacheExists 检查缓存文件是否存在
func IsCacheExists() bool {
	cachePath := getCachePath()
	_, err := os.Stat(cachePath)
	return !os.IsNotExist(err)
}

// loadCache 加载缓存
func loadCache() error {
	if cacheLoaded {
		return nil
	}

	cachePath := getCachePath()

	// 检查缓存文件是否存在
	if _, err := os.Stat(cachePath); os.IsNotExist(err) {
		cacheLoaded = true
		return nil
	}

	// 读取缓存文件
	content, err := os.ReadFile(cachePath)
	if err != nil {
		return err
	}

	// 解析缓存
	if err := json.Unmarshal(content, &cache); err != nil {
		return err
	}

	cacheLoaded = true
	return nil
}

// ClearCache 清除缓存
func ClearCache() {
	cache = make(map[string]map[string]interface{})
	cacheLoaded = false

	cachePath := getCachePath()
	os.Remove(cachePath)
}

// saveCache 保存缓存
func saveCache() error {
	cachePath := getCachePath()

	// 序列化缓存
	content, err := json.MarshalIndent(cache, "", "  ")
	if err != nil {
		return err
	}

	// 写入缓存文件
	return os.WriteFile(cachePath, content, 0644)
}

// toMap 将ScriptMetadata转换为map[string]interface{}
func (m *ScriptMetadata) toMap() map[string]interface{} {
	return map[string]interface{}{
		"name":         m.Name,
		"description":  m.Description,
		"tags":         m.Tags,
		"dependencies": m.Dependencies,
		"icon":         m.Icon,
		"help":         m.Help,
		"module_name":  m.ModuleName,
		"bias":         m.Bias,
		"filename":     m.Filename,
	}
}

// fromMap 从map[string]interface{}创建ScriptMetadata
func fromMap(data map[string]interface{}, filePath string) *ScriptMetadata {
	metadata := &ScriptMetadata{}
	
	// 设置文件路径
	metadata.FilePath = filePath
	
	// 从map中提取字段
	if name, ok := data["name"].(string); ok && name != "" {
		metadata.Name = name
	}
	
	if description, ok := data["description"].(string); ok {
		metadata.Description = description
	}
	
	// 处理标签
	tags := data["tags"]
	if tagStr, ok := tags.(string); ok {
		// 逗号分隔的标签
		tagList := strings.Split(tagStr, ",")
		for i, tag := range tagList {
			tagList[i] = strings.TrimSpace(tag)
		}
		metadata.Tags = tagList
	} else if tagList, ok := tags.([]interface{}); ok {
		// 标签数组
		metadata.Tags = make([]string, len(tagList))
		for i, tag := range tagList {
			if tagStr, ok := tag.(string); ok {
				metadata.Tags[i] = tagStr
			}
		}
	} else {
		// 默认空数组
		metadata.Tags = []string{}
	}
	
	// 处理依赖项
	dependencies := data["dependencies"]
	if depStr, ok := dependencies.(string); ok {
		// 逗号分隔的依赖项
		depList := strings.Split(depStr, ",")
		for i, dep := range depList {
			depList[i] = strings.TrimSpace(dep)
		}
		metadata.Dependencies = depList
	} else if depList, ok := dependencies.([]interface{}); ok {
		// 依赖项数组
		metadata.Dependencies = make([]string, len(depList))
		for i, dep := range depList {
			if depStr, ok := dep.(string); ok {
				metadata.Dependencies[i] = depStr
			}
		}
	} else {
		// 默认空数组
		metadata.Dependencies = []string{}
	}
	
	if icon, ok := data["icon"].(string); ok {
		metadata.Icon = icon
	}
	
	if help, ok := data["help"].(string); ok {
		metadata.Help = help
	}
	
	// 模块名称始终从文件路径生成，与Python实现一致
	
	if bias, ok := data["bias"].(float64); ok {
		metadata.Bias = int(bias)
	}
	
	// 文件名始终从文件路径生成，与Python实现一致
	
	// 从文件路径设置其他字段（如果未设置）
	setMetadataFromPath(metadata, filePath)
	
	return metadata
}

// ParseMetadata 从脚本文件中解析元数据
func ParseMetadata(filePath string) (*ScriptMetadata, error) {
	// 加载缓存
	if err := loadCache(); err != nil {
		// 缓存加载失败，继续解析
	}

	// 获取文件信息
	info, err := os.Stat(filePath)
	if err != nil {
		return nil, err
	}

	// 检查缓存
	if cachedData, ok := cache[filePath]; ok {
		// 检查文件修改时间
		if mtime, ok := cachedData["mtime"].(float64); ok {
			if int64(mtime) == info.ModTime().Unix() {
				// 缓存有效，直接返回
				if metadataMap, ok := cachedData["metadata"].(map[string]interface{}); ok {
					metadata := fromMap(metadataMap, filePath)
					return metadata, nil
				}
			}
		}
	}

	// 读取脚本文件内容
	content, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	// 提取注释中的JSON元数据
	metadata, err := extractMetadata(string(content), filePath)
	if err != nil {
		return nil, err
	}

	// 检查元数据是否为nil
	if metadata == nil {
		// 创建默认元数据
		metadata = createDefaultMetadata(filePath)
	} else {
		// 设置文件路径
		metadata.FilePath = filePath
		// 从文件路径设置其他字段
		setMetadataFromPath(metadata, filePath)
	}

	// 更新缓存，使用与Python一致的格式
	metadataMap := metadata.toMap()
	cache[filePath] = map[string]interface{}{
		"mtime":    float64(info.ModTime().Unix()),
		"metadata": metadataMap,
	}

	// 保存缓存
	if err := saveCache(); err != nil {
		// 缓存保存失败，继续返回元数据
	}

	return metadata, nil
}

// extractMetadata 从脚本内容中提取元数据
func extractMetadata(content string, filePath string) (*ScriptMetadata, error) {
	// 查找多行注释中的JSON（支持单引号和双引号格式）
	// 先查找单引号格式
	reSingle := regexp.MustCompile(`^(?:\s*#[^\n]*\n*)*\s*'''([\s\S]*?)'''`)
	matches := reSingle.FindStringSubmatch(content)
	
	// 如果没有找到，查找双引号格式
	if len(matches) < 2 {
		reDouble := regexp.MustCompile(`^(?:\s*#[^\n]*\n*)*\s*"""([\s\S]*?)"""`)
		matches = reDouble.FindStringSubmatch(content)
	}

	if len(matches) < 2 {
		return nil, nil // 没有找到元数据
	}

	// 解析JSON
	var metadataMap map[string]interface{}
	err := json.Unmarshal([]byte(strings.TrimSpace(matches[1])), &metadataMap)
	if err != nil {
		// JSON解析错误，返回nil，让调用者创建默认元数据
		return nil, nil
	}

	// 从map创建ScriptMetadata
	metadata := fromMap(metadataMap, filePath)

	return metadata, nil
}

// createDefaultMetadata 创建默认元数据
func createDefaultMetadata(filePath string) *ScriptMetadata {
	metadata := &ScriptMetadata{}
	setMetadataFromPath(metadata, filePath)
	metadata.Description = "Script from " + filepath.Base(filePath)
	metadata.Dependencies = []string{}
	return metadata
}

// setMetadataFromPath 从文件路径设置元数据字段
func setMetadataFromPath(metadata *ScriptMetadata, filePath string) {
	filename := filepath.Base(filePath)
	stem := strings.TrimSuffix(filename, filepath.Ext(filename))
	
	// 设置文件名
	metadata.Filename = filename
	
	// 设置模块名称
	metadata.ModuleName = "script_" + stem
	
	// 如果名称为空，从文件名推断
	if metadata.Name == "" {
		// 将下划线替换为空格，并首字母大写
		displayName := strings.ReplaceAll(stem, "_", " ")
		// 首字母大写
		if len(displayName) > 0 {
			displayName = strings.ToUpper(displayName[:1]) + displayName[1:]
		}
		metadata.Name = displayName
	}
	
	// 设置文件路径
	metadata.FilePath = filePath
	
	// 确保Tags和Dependencies是数组
	if metadata.Tags == nil {
		metadata.Tags = []string{}
	}
	if metadata.Dependencies == nil {
		metadata.Dependencies = []string{}
	}
}

// IsValid 检查元数据是否有效
func (m *ScriptMetadata) IsValid() bool {
	return m.Name != ""
}
