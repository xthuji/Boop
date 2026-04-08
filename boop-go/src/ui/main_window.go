package ui

import (
	"boop-go/src/core/config"
	"boop-go/src/core/log"
	"boop-go/src/core/path"
	"boop-go/src/core/script"
	"boop-go/src/ui/editor"
	"boop-go/src/utils"
	"fmt"
	"strings"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/driver/desktop"
)

// MainWindow 主窗口
type MainWindow struct {
	Content            fyne.CanvasObject
	MainMenu           *fyne.MainMenu
	Editor             *editor.Editor
	StatusBar          *StatusBar
	ScriptManager      *script.ScriptManager
	ScriptExecutor     *script.ScriptExecutor
	ScriptPickerWindow *ScriptPickerWindow
	ConfigManager      *config.Manager
	PreferencesWindow  *PreferencesWindow
	Window             fyne.Window
}

// LoadScripts 加载脚本元数据并更新相关UI组件
func (w *MainWindow) LoadScripts() {
	go func() {
		scriptLoadStart := time.Now()
		scripts := w.ScriptManager.GetScripts() // 触发脚本加载（如果尚未加载）
		log.Info("[数据加载] 脚本元数据加载完成，耗时: %.2fms", float64(time.Since(scriptLoadStart))/1e6)

		// 在UI线程中更新数据
		fyne.Do(func() {
			if w.ScriptPickerWindow != nil {
				w.ScriptPickerWindow.allScripts = scripts
				w.ScriptPickerWindow.filteredScripts = scripts
				// 如果ScriptPickerWindow已初始化，刷新列表
				if w.ScriptPickerWindow.scriptList != nil {
					w.ScriptPickerWindow.scriptList.Refresh()
					w.ScriptPickerWindow.updateStatus()
				}
			}
			w.updateScriptCount()
		})
	}()
}

func NewMainWindow(configManager *config.Manager, boopCoreWindow fyne.Window) *MainWindow {
	startTime := time.Now()

	boopEditor := editor.NewEditor(configManager)

	scriptConfig := configManager.GetScriptConfig()
	scriptDirs := scriptConfig.ScriptDirs
	if len(scriptDirs) == 0 {
		scriptDirs = []string{path.ScriptsDir()}
	}

	// 创建脚本管理器
	scriptManager := script.NewScriptManager(scriptDirs)

	// 创建脚本执行器
	scriptExecutor := script.NewScriptExecutor(scriptConfig.PythonPath, time.Duration(scriptConfig.Timeout)*time.Second)

	// 初始化 StatusBar
	statusBar := NewStatusBar(boopEditor)

	textEditor := boopEditor.GetCurrentTextEditor()
	textEditor.OnCursorChanged = func() {
		statusBar.Refresh()
	}

	content := container.NewBorder(
		nil,
		statusBar.Content,
		nil,
		nil,
		boopEditor.Content,
	)

	// 创建 MainWindow 实例
	mw := &MainWindow{
		Content:        content,
		Editor:         boopEditor,
		StatusBar:      statusBar,
		ScriptManager:  scriptManager,
		ScriptExecutor: scriptExecutor,
		ConfigManager:  configManager,
		Window:         boopCoreWindow,
	}

	// 设置主窗口的关闭拦截：当用户关闭主窗口时，退出应用
	boopCoreWindow.SetCloseIntercept(func() {
		fyne.CurrentApp().Quit()
	})

	// 创建 ScriptPickerWindow 实例
	scriptPickerWindow := &ScriptPickerWindow{
		scriptManager:  scriptManager,
		scriptExecutor: scriptExecutor,
		selectedIndex:  -1,
		parentWindow:   boopCoreWindow,
		mainWindow:     mw,
	}
	mw.ScriptPickerWindow = scriptPickerWindow

	// 创建 PreferencesWindow 实例
	preferencesWindow := &PreferencesWindow{
		scriptManager: scriptManager,
		configManager: configManager,
		scriptDirs:    make([]string, 0),
		parentWindow:  boopCoreWindow,
		mainWindow:    mw,
	}
	mw.PreferencesWindow = preferencesWindow

	// 快捷键回调现在通过 main_window.go 中的 AddShortcut 方法绑定

	// 设置脚本选择回调，使用 mw 实例避免 StatusBar 为 nil
	scriptPickerWindow.OnScriptSelected = func(metadata *script.ScriptMetadata) {
		mw.ExecuteScript(metadata)
	}

	// 异步加载脚本
	mw.LoadScripts()

	mw.MainMenu = mw.createMainMenu()

	log.Info("[窗口创建] NewMainWindow 总耗时: %.2fms", float64(time.Since(startTime))/1e6)
	return mw
}

// updateScriptCount 更新状态栏中的脚本数量
func (w *MainWindow) updateScriptCount() {
	scriptCount := len(w.ScriptManager.GetScripts())
	w.StatusBar.SetScriptCount(scriptCount)
}

func (w *MainWindow) createMainMenu() *fyne.MainMenu {
	// 从配置中获取快捷键设置
	shortcutsConfig := w.ConfigManager.GetShortcutsConfig()

	// 创建菜单项
	aboutItem := fyne.NewMenuItem("About Boop", func() {
		dialog.ShowInformation("About Boop", "Boop - A text editor with scriptable transformations\nVersion 1.0.0", w.Window)
	})
	preferencesItem := fyne.NewMenuItem("Preferences...", func() {
		w.ShowPreferencesWindow()
	})
	quitItem := fyne.NewMenuItem("Quit Boop", func() {
		fyne.CurrentApp().Quit()
	})
	runScriptItem := fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Run Script...", shortcutsConfig.RunScript[0]), func() {
		w.ShowScriptPickerWindow()
	})

	go func() {
		// 添加首选项快捷键
		if len(shortcutsConfig.Preferences) > 0 {
			preferencesItem.Shortcut = &desktop.CustomShortcut{}
			if shortcut, err := utils.ParseFyneShortcut(shortcutsConfig.Preferences[0]); err == nil {
				preferencesItem.Shortcut = shortcut
			}
		}
		// 添加运行脚本快捷键
		if !w.ConfigManager.GetAppConfig().EnableGlobalHotkeys && len(shortcutsConfig.RunScript) > 0 {
			runScriptItem.Shortcut = &desktop.CustomShortcut{}
			if shortcut, err := utils.ParseFyneShortcut(shortcutsConfig.RunScript[0]); err == nil {
				runScriptItem.Shortcut = shortcut
			}
		}
	}()

	reloadScriptsItem := fyne.NewMenuItem("Reload Scripts", func() {
		w.ScriptManager.LoadScripts()
		w.LoadScripts()
		w.SetStatusMessage("Scripts reloaded")
		w.ScriptPickerWindow.Preload(false)
	})

	// 构建菜单
	boopMenu := fyne.NewMenu("Boop",
		aboutItem,
		fyne.NewMenuItemSeparator(),
		fyne.NewMenuItem("User Guide", func() {}),
		fyne.NewMenuItemSeparator(),
		preferencesItem,
		fyne.NewMenuItemSeparator(),
		quitItem,
	)

	scriptMenu := fyne.NewMenu("Script",
		runScriptItem,
		fyne.NewMenuItemSeparator(),
		reloadScriptsItem,
	)

	return fyne.NewMainMenu(
		boopMenu,
		fyne.NewMenu("Edit",
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Undo", shortcutsConfig.Undo[0]), func() {
				w.Editor.Undo()
			}),
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Redo", shortcutsConfig.Redo[0]), func() {
				w.Editor.Redo()
			}),
			fyne.NewMenuItemSeparator(),
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Cut", shortcutsConfig.Cut[0]), func() {
				w.Editor.Cut()
			}),
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Copy", shortcutsConfig.Copy[0]), func() {
				w.Editor.Copy()
			}),
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Paste", shortcutsConfig.Paste[0]), func() {
				w.Editor.Paste()
			}),
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Select All", shortcutsConfig.SelectAll[0]), func() {
				w.Editor.SelectAll()
			}),
			fyne.NewMenuItemSeparator(),
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Move To Start", shortcutsConfig.MoveToStart[0]), func() {
				w.Editor.MoveToStart()
			}),
			fyne.NewMenuItem(utils.BuildMenuItemStringWithShortcut("Move To End", shortcutsConfig.MoveToEnd[0]), func() {
				w.Editor.MoveToEnd()
			}),
		),
		scriptMenu,
	)
}

func (w *MainWindow) BindEditorWindowShortcuts() {
	// 绑定编辑器相关的快捷键
	go func() {
		if w.Editor != nil {
			w.Editor.BindEditorShortcuts(w.Window.Canvas())
		}
	}()
}

func (w *MainWindow) SetStatusMessage(message string) {
}

// 将焦点设置到编辑器的编辑区域
func (w *MainWindow) FocusEditor() {
	w.Window.Show()
	if w.Editor != nil {
		w.Editor.Focus()
	}
}

func (w *MainWindow) ShowScriptPickerWindow() {
	if w.ScriptPickerWindow == nil {
		// 窗口尚未初始化，显示加载提示
		dialog.ShowInformation("Loading", "Script picker is initializing. Please wait...", w.Window)
		return
	}
	w.ScriptPickerWindow.Show(w.Window)
}

func (w *MainWindow) ShowPreferencesWindow() {
	if w.PreferencesWindow == nil {
		// 窗口尚未初始化，显示加载提示
		dialog.ShowInformation("Loading", "Preferences window is initializing. Please wait...", w.Window)
		return
	}
	w.PreferencesWindow.Show()
}

func (w *MainWindow) ExecuteScript(metadata *script.ScriptMetadata) {
	if metadata == nil {
		return
	}

	content := w.Editor.GetCurrentTextEditor().GetContent()

	if strings.HasPrefix(content, "-h") {
		w.ShowScriptHelp(metadata)
		return
	}

	log.Info("Executing script: %s", metadata.Name)

	fyne.Do(func() {
		w.StatusBar.SetScriptCount(-1)
	})

	go func() {
		output, execErr, _, errorMsgs := w.ScriptExecutor.Execute(metadata.FilePath, content)

		fyne.Do(func() {
			w.Editor.GetCurrentTextEditor().SetContent(output)

			if execErr != nil {
				log.Error("脚本执行失败: %s, 错误: %v", metadata.Name, execErr)
				if len(errorMsgs) > 0 {
					dialog.ShowError(fmt.Errorf("%s", errorMsgs[0]), w.Window)
				} else {
					dialog.ShowError(fmt.Errorf("脚本执行失败: %v", execErr), w.Window)
				}
			} else if len(errorMsgs) > 0 {
				log.Warning("脚本执行完成但有错误消息: %s, 错误: %s", metadata.Name, errorMsgs[0])
				dialog.ShowError(fmt.Errorf("%s", errorMsgs[0]), w.Window)
			} else {
				log.Info("脚本执行成功: %s", metadata.Name)
			}
		})
	}()
}

func (w *MainWindow) ShowScriptHelp(metadata *script.ScriptMetadata) {
	content := w.Editor.GetCurrentTextEditor().GetContent()
	lines := strings.SplitN(content, "\n", 2)

	var body string
	if len(lines) > 1 {
		body = lines[1]
	}

	helpContent := fmt.Sprintf("-h\n\n%s\n\n%s", metadata.Help, body)
	w.Editor.GetCurrentTextEditor().SetContent(helpContent)
	w.StatusBar.SetMessage(fmt.Sprintf("Showing help for: %s", metadata.Name))
}
