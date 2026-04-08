package utils

import (
	"boop-go/src/core/log"
	"fmt"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/driver/desktop"
	"golang.design/x/hotkey" // 引入 hotkey 库以获取正确的底层键码
)

// KeyInfo 表示按键的信息
type KeyInfo struct {
	Hotkey   hotkey.Key   // 对应系统的底层键码
	FyneName fyne.KeyName // Fyne 的 KeyName
}

// ModifierInfo 表示修饰键的信息
type ModifierInfo struct {
	Hotkey  hotkey.Modifier  // 对应系统的底层修饰键码
	FyneMod fyne.KeyModifier // Fyne 的 KeyModifier
}

// 键值映射：使用 hotkey.KeyXXX 确保跨平台兼容性
var keyMap = map[string]KeyInfo{
	"a":      {hotkey.KeyA, fyne.KeyA},
	"b":      {hotkey.KeyB, fyne.KeyB},
	"c":      {hotkey.KeyC, fyne.KeyC},
	"d":      {hotkey.KeyD, fyne.KeyD},
	"e":      {hotkey.KeyE, fyne.KeyE},
	"f":      {hotkey.KeyF, fyne.KeyF},
	"g":      {hotkey.KeyG, fyne.KeyG},
	"h":      {hotkey.KeyH, fyne.KeyH},
	"i":      {hotkey.KeyI, fyne.KeyI},
	"j":      {hotkey.KeyJ, fyne.KeyJ},
	"k":      {hotkey.KeyK, fyne.KeyK},
	"l":      {hotkey.KeyL, fyne.KeyL},
	"m":      {hotkey.KeyM, fyne.KeyM},
	"n":      {hotkey.KeyN, fyne.KeyN},
	"o":      {hotkey.KeyO, fyne.KeyO},
	"p":      {hotkey.KeyP, fyne.KeyP},
	"q":      {hotkey.KeyQ, fyne.KeyQ},
	"r":      {hotkey.KeyR, fyne.KeyR},
	"s":      {hotkey.KeyS, fyne.KeyS},
	"t":      {hotkey.KeyT, fyne.KeyT},
	"u":      {hotkey.KeyU, fyne.KeyU},
	"v":      {hotkey.KeyV, fyne.KeyV},
	"w":      {hotkey.KeyW, fyne.KeyW},
	"x":      {hotkey.KeyX, fyne.KeyX},
	"y":      {hotkey.KeyY, fyne.KeyY},
	"z":      {hotkey.KeyZ, fyne.KeyZ},
	"1":      {hotkey.Key1, fyne.Key1},
	"2":      {hotkey.Key2, fyne.Key2},
	"3":      {hotkey.Key3, fyne.Key3},
	"4":      {hotkey.Key4, fyne.Key4},
	"5":      {hotkey.Key5, fyne.Key5},
	"6":      {hotkey.Key6, fyne.Key6},
	"7":      {hotkey.Key7, fyne.Key7},
	"8":      {hotkey.Key8, fyne.Key8},
	"9":      {hotkey.Key9, fyne.Key9},
	"0":      {hotkey.Key0, fyne.Key0},
	"space":  {hotkey.KeySpace, fyne.KeySpace},
	"enter":  {hotkey.KeyReturn, fyne.KeyEnter},
	"tab":    {hotkey.KeyTab, fyne.KeyTab},
	"escape": {hotkey.KeyEscape, fyne.KeyEscape},
	"delete": {hotkey.KeyDelete, fyne.KeyDelete},
	"up":     {hotkey.KeyUp, fyne.KeyUp},
	"down":   {hotkey.KeyDown, fyne.KeyDown},
	"left":   {hotkey.KeyLeft, fyne.KeyLeft},
	"right":  {hotkey.KeyRight, fyne.KeyRight},
	",":      {0, fyne.KeyComma},
}

// 修饰键映射：映射到 hotkey.ModXXX
var modifierMap = map[string]ModifierInfo{
	"command": {hotkey.ModCmd, fyne.KeyModifierSuper},
	"cmd":     {hotkey.ModCmd, fyne.KeyModifierSuper},
	"super":   {hotkey.ModCmd, fyne.KeyModifierSuper},
	"control": {hotkey.ModCtrl, fyne.KeyModifierControl},
	"ctrl":    {hotkey.ModCtrl, fyne.KeyModifierControl},
	"shift":   {hotkey.ModShift, fyne.KeyModifierShift},
	"alt":     {hotkey.ModOption, fyne.KeyModifierAlt},
	"option":  {hotkey.ModOption, fyne.KeyModifierAlt},
}

// ParseShortcut 解析快捷键字符串，返回 hotkey 库需要的修饰键和按键
// 修复：返回类型直接使用 hotkey 定义的类型
func ParseShortcut(shortcut string) ([]hotkey.Modifier, hotkey.Key, error) {
	parts := strings.Split(strings.ToLower(shortcut), "+")
	if len(parts) < 1 {
		return nil, 0, fmt.Errorf("invalid shortcut format")
	}

	// 最后一个部分是按键
	keyStr := strings.TrimSpace(parts[len(parts)-1])
	keyInfo, ok := keyMap[keyStr]
	if !ok {
		return nil, 0, fmt.Errorf("unsupported key: %s", keyStr)
	}

	// 前面的部分是修饰键
	var modifiers []hotkey.Modifier
	for i := 0; i < len(parts)-1; i++ {
		modStr := strings.TrimSpace(parts[i])
		modInfo, ok := modifierMap[modStr]
		if !ok {
			return nil, 0, fmt.Errorf("unsupported modifier: %s", modStr)
		}
		modifiers = append(modifiers, modInfo.Hotkey)
	}

	return modifiers, keyInfo.Hotkey, nil
}

// ParseFyneShortcut 保持不变，用于 Fyne 内部快捷键处理
func ParseFyneShortcut(shortcutStr string) (*desktop.CustomShortcut, error) {
	parts := strings.Split(strings.ToLower(shortcutStr), "+")
	if len(parts) < 1 {
		return nil, fmt.Errorf("invalid shortcut format")
	}

	keyStr := strings.TrimSpace(parts[len(parts)-1])
	keyInfo, ok := keyMap[keyStr]
	if !ok {
		return nil, fmt.Errorf("unsupported key: %s", keyStr)
	}

	var modifier fyne.KeyModifier
	for i := 0; i < len(parts)-1; i++ {
		modStr := strings.TrimSpace(parts[i])
		modInfo, ok := modifierMap[modStr]
		if !ok {
			return nil, fmt.Errorf("unsupported modifier: %s", modStr)
		}
		modifier |= modInfo.FyneMod
	}

	return &desktop.CustomShortcut{
		KeyName:  keyInfo.FyneName,
		Modifier: modifier,
	}, nil
}

// BindShortcuts 绑定快捷键到指定的 Canvas
func BindShortcuts(canvas fyne.Canvas, shortcuts []string, handler func(fyne.Shortcut)) {
	if len(shortcuts) > 0 {
		for _, shortcutStr := range shortcuts {
			if shortcut, err := ParseFyneShortcut(shortcutStr); err == nil {
				canvas.AddShortcut(shortcut, handler)
				// log.Info("[热键激活] 绑定快捷键: %s", shortcutStr)
			} else {
				log.Error("[热键激活] 解析快捷键失败: %s", err.Error())
			}
		}
	} else {
		log.Info("[热键激活] 未配置快捷键 %v", shortcuts)
	}
}

func BuildMenuItemStringWithShortcut(name string, shortcut string) string {
	// 使用 strings.Replacer 进行批量替换，支持链式替换
	shortcutStr := strings.NewReplacer(
		"Command", "⌘", "Cmd", "⌘",
		"Control", "⌃", "Ctrl", "⌃",
		"Shift", "⇧",
		"Alt", "⌥", "Option", "⌥",
		"Tab", "⇥", "tab", "⇥",
		"Escape", "⎋", "Esc", "⎋",
		"Space", "␣",
		"Enter", "⏎", "Return", "⏎",
		"Delete", "⌫", "Backspace", "⌫",
		"Up", "↑", "Down", "↓", "Left", "←", "Right", "→",
		"Home", "↖", "End", "↘",
		"PageUp", "⇞", "PageDown", "⇟",
		"Windows", "⊞", "Win", "⊞",
		"+", " ",
	).Replace(shortcut)
	// 判断 name 与 shortcutStr 字段的长度， 添加tab键进行对齐
	return name + strings.Repeat("\t", (23-len(name))/5) + shortcutStr
}
