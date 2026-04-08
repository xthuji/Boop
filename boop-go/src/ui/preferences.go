package ui

import (
	"boop-go/src/core/config"
	"boop-go/src/core/log"
	"boop-go/src/core/script"
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

// PreferencesWindow 设置窗口结构体
type PreferencesWindow struct {
	scriptManager *script.ScriptManager
	configManager *config.Manager

	// 标签页容器
	tabContainer *container.AppTabs

	// General 标签页组件
	fontFamilyEntry          *widget.Entry
	fontSizeEntry            *widget.Entry
	windowWidthEntry         *widget.Entry
	windowHeightEntry        *widget.Entry
	maximizeWindowCheck      *widget.Check
	enableGlobalHotkeysCheck *widget.Check

	// Scripts 标签页组件
	scriptDirsList     *widget.List
	scriptDirs         []string
	selectedDirIndex   int
	pythonPathEntry    *widget.Entry
	scriptTimeoutEntry *widget.Entry
	filterDelayEntry   *widget.Entry

	// Logs 标签页组件
	logPathEntry *widget.Entry
	logContent   *widget.Entry

	// 窗口实例
	window       fyne.Window
	parentWindow fyne.Window
	mainWindow   *MainWindow
}

// createGroup 辅助函数：创建一个带标题和分割线的视觉分组，模拟 Python 的 LabelFrame
func createGroup(title string, content fyne.CanvasObject) fyne.CanvasObject {
	return container.NewVBox(
		widget.NewLabelWithStyle(title, fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		content,
		widget.NewSeparator(),
	)
}

// initComponents 初始化组件及其布局
func (w *PreferencesWindow) initComponents() {
	// --- 立即创建核心组件 ---
	// General 标签页核心组件
	w.fontFamilyEntry = widget.NewEntry()
	w.fontSizeEntry = widget.NewEntry()
	w.windowWidthEntry = widget.NewEntry()
	w.windowHeightEntry = widget.NewEntry()

	// 联动逻辑：勾选最大化时禁用宽高输入
	w.maximizeWindowCheck = widget.NewCheck("Maximize Window", func(checked bool) {
		if checked {
			w.windowWidthEntry.Disable()
			w.windowHeightEntry.Disable()
		} else {
			w.windowWidthEntry.Enable()
			w.windowHeightEntry.Enable()
		}
	})
	w.enableGlobalHotkeysCheck = widget.NewCheck("Enable Global Hotkeys Back To App", nil)

	// --- 异步创建非核心组件 ---
	go func() {
		fyne.Do(func() {
			// Scripts 标签页核心组件
			w.scriptDirsList = widget.NewList(
				func() int { return len(w.scriptDirs) },
				func() fyne.CanvasObject { return widget.NewLabel("") },
				func(i widget.ListItemID, o fyne.CanvasObject) {
					if i < len(w.scriptDirs) {
						o.(*widget.Label).SetText(w.scriptDirs[i])
					}
				},
			)
			w.scriptDirsList.OnSelected = func(i widget.ListItemID) {
				w.selectedDirIndex = i
			}
			// Scripts 标签页非核心组件
			w.pythonPathEntry = widget.NewEntry()
			w.scriptTimeoutEntry = widget.NewEntry()
			w.filterDelayEntry = widget.NewEntry()

			// Logs 标签页组件
			w.logPathEntry = widget.NewEntry()
			w.logContent = widget.NewMultiLineEntry()
			w.logContent.TextStyle = fyne.TextStyle{Monospace: true} // 日志通常使用等宽字体

			// 创建具体布局
			w.createTabs()
		})
	}()
}

// createTabs 构建标签页视图
func (w *PreferencesWindow) createTabs() {
	// 1. General Tab: 使用 Form 布局实现标签对齐
	windowForm := widget.NewForm(
		widget.NewFormItem("", w.enableGlobalHotkeysCheck),
		widget.NewFormItem("", w.maximizeWindowCheck),
		widget.NewFormItem("Window Width", w.windowWidthEntry),
		widget.NewFormItem("Window Height", w.windowHeightEntry),
	)
	fontForm := widget.NewForm(
		widget.NewFormItem("Font Family", w.fontFamilyEntry),
		widget.NewFormItem("Font Size", w.fontSizeEntry),
	)
	generalTab := container.NewPadded(container.NewVBox(
		createGroup("Window Layout", windowForm),
		createGroup("Editor Typography", fontForm),
	))

	// 2. Scripts Tab
	dirActionButtons := container.NewVBox(
		widget.NewButtonWithIcon("Add", theme.ContentAddIcon(), func() {
			// 打开文件夹选择对话框
			dialog.ShowFolderOpen(func(uri fyne.ListableURI, err error) {
				if err == nil && uri != nil {
					// 获取选中的目录路径
					dirPath := uri.Path()
					// 检查目录是否已存在
					exists := false
					for _, dir := range w.scriptDirs {
						if dir == dirPath {
							exists = true
							break
						}
					}
					// 如果目录不存在，添加到列表
					if !exists {
						w.scriptDirs = append(w.scriptDirs, dirPath)
						// 刷新列表显示
						w.scriptDirsList.Refresh()
					}
				}
			}, w.window)
		}),
		widget.NewButtonWithIcon("Remove", theme.ContentRemoveIcon(), func() {
			// 检查是否有选中的目录
			if w.selectedDirIndex >= 0 && w.selectedDirIndex < len(w.scriptDirs) {
				// 从切片中移除选中的目录
				w.scriptDirs = append(w.scriptDirs[:w.selectedDirIndex], w.scriptDirs[w.selectedDirIndex+1:]...)
				// 重置选中索引
				w.selectedDirIndex = -1
				// 刷新列表显示
				w.scriptDirsList.Refresh()
			}
		}),
	)

	listContainer := container.NewScroll(w.scriptDirsList)
	listContainer.SetMinSize(fyne.NewSize(0, 80)) // 限制列表高度

	scriptDirsGroup := container.NewBorder(nil, nil, nil, dirActionButtons, listContainer)

	pythonForm := widget.NewForm(
		widget.NewFormItem("Interpreter", container.NewBorder(nil, nil, nil, widget.NewButtonWithIcon("Browse", theme.FileIcon(), func() {
			// 打开文件选择对话框，选择 Python 可执行文件
			dialog.ShowFileOpen(func(uri fyne.URIReadCloser, err error) {
				if err == nil && uri != nil {
					// 获取选中的文件路径
					filePath := uri.URI().Path()
					// 设置到 Python 路径输入框
					w.pythonPathEntry.SetText(filePath)
				}
			}, w.window)
		}), w.pythonPathEntry)),
		widget.NewFormItem("Timeout (s)", w.scriptTimeoutEntry),
		widget.NewFormItem("Filter Delay (ms)", w.filterDelayEntry),
	)

	maintButtons := container.NewHBox(
		widget.NewButtonWithIcon("Install Script Dependencies", theme.DownloadIcon(), func() {
			// 显示安装依赖的进度窗口
			progressWindow := fyne.CurrentApp().NewWindow("Installing Dependencies")
			progressWindow.Resize(fyne.NewSize(400, 300))
			progressWindow.CenterOnScreen()

			// 创建进度条和状态文本
			progressBar := widget.NewProgressBar()
			statusText := widget.NewMultiLineEntry()
			statusText.SetText("Collecting dependencies...")

			// 布局：使用Border布局，让滚动容器占据剩余空间
			scrollContainer := container.NewScroll(statusText)
			content := container.NewBorder(
				container.NewVBox(
					widget.NewLabel("Installing Script Dependencies"),
					progressBar,
				),
				nil,
				nil,
				nil,
				scrollContainer,
			)
			progressWindow.SetContent(content)
			progressWindow.Show()

			// 异步执行依赖安装
			go func() {
				// 收集所有脚本的依赖
				dependencies := make(map[string]bool)
				allMetadata := w.scriptManager.GetAllMetadata()

				for _, metadata := range allMetadata {
					if metadata.Dependencies != nil {
						for _, dep := range metadata.Dependencies {
							dependencies[dep] = true
						}
					}
				}

				// 转换为切片
				depList := make([]string, 0, len(dependencies))
				for dep := range dependencies {
					depList = append(depList, dep)
				}

				// 检查是否有依赖
				if len(depList) == 0 {
					fyne.Do(func() {
						statusText.SetText("No dependencies found in scripts.")
						dialog.ShowInformation("Info", "No dependencies found in scripts.", progressWindow)
						progressWindow.Close()
					})
					return
				}

				// 检查 Python 路径
				pythonPath := w.pythonPathEntry.Text
				if pythonPath == "" {
					fyne.Do(func() {
						statusText.SetText("No Python interpreter found. Please set Python path in preferences.")
						dialog.ShowError(fmt.Errorf("No Python interpreter found. Please set Python path in preferences."), progressWindow)
						progressWindow.Close()
					})
					return
				}

				// 更新状态
				fyne.Do(func() {
					statusText.SetText(fmt.Sprintf("Found %d dependencies to install:\n", len(depList)))
					for _, dep := range depList {
						statusText.SetText(statusText.Text + "- " + dep + "\n")
					}
					statusText.SetText(statusText.Text + "\nInstalling...\n")
				})

				// 安装依赖
				for i, dep := range depList {
					// 更新进度
					progress := float64(i) / float64(len(depList))
					fyne.Do(func() {
						progressBar.SetValue(progress)
						statusText.SetText(statusText.Text + "Installing " + dep + "...\n")
					})

					// 执行 pip install 命令
					cmd := exec.Command(pythonPath, "-m", "pip", "install", dep)
					output, err := cmd.CombinedOutput()

					// 更新状态
					fyne.Do(func() {
						if err != nil {
							statusText.SetText(statusText.Text + "✗ Failed to install " + dep + ": " + string(output) + "\n")
						} else {
							statusText.SetText(statusText.Text + "✓ Successfully installed " + dep + "\n")
						}
					})
				}

				// 完成安装
				fyne.Do(func() {
					progressBar.SetValue(1.0)
					statusText.SetText(statusText.Text + "\nDependency installation completed!\n")
					dialog.ShowInformation("Success", "Dependency installation completed successfully.", progressWindow)
					progressWindow.Close()
				})
			}()
		}),
		widget.NewButtonWithIcon("Refresh Script Metadata Cache", theme.ViewRefreshIcon(), func() {
			// 显示刷新缓存的进度窗口
			progressWindow := fyne.CurrentApp().NewWindow("Refreshing Metadata Cache")
			progressWindow.Resize(fyne.NewSize(300, 150))
			progressWindow.CenterOnScreen()

			// 创建进度条和状态文本
			progressBar := widget.NewProgressBarInfinite()
			statusText := widget.NewLabel("Refreshing script metadata cache...")

			// 布局
			content := container.NewVBox(
				statusText,
				progressBar,
			)
			progressWindow.SetContent(content)
			progressWindow.Show()

			// 异步执行缓存刷新
			go func() {
				// 调用脚本管理器的 LoadScripts 方法来刷新缓存
				err := w.scriptManager.LoadScripts()

				// 计算加载的脚本数量
				scriptCount := len(w.scriptManager.GetScripts())

				// 更新状态
				fyne.Do(func() {
					progressWindow.Close()
					if err != nil {
						dialog.ShowError(err, w.window)
					} else {
						dialog.ShowInformation("Success", fmt.Sprintf("Metadata cache refreshed successfully.\nLoaded %d scripts.", scriptCount), w.window)
					}
				})
			}()
		}),
	)

	scriptsTab := container.NewPadded(container.NewVBox(
		createGroup("Script Directories", scriptDirsGroup),
		createGroup("Python Engine", pythonForm),
		createGroup("Maintenance", maintButtons),
	))

	// 3. Logs Tab
	logHeader := container.NewBorder(nil, nil, nil, widget.NewButtonWithIcon("Clear Logs", theme.DeleteIcon(), func() {
		// 显示确认对话框
		dialog.ShowConfirm("Clear Logs", "Are you sure you want to clear all logs?", func(confirmed bool) {
			if confirmed {
				// 尝试删除日志文件
				logPath := w.logPathEntry.Text
				if logPath != "" {
					err := os.Remove(logPath)
					if err != nil {
						dialog.ShowError(err, w.window)
					} else {
						// 重新加载日志内容
						w.logContent.SetText("Logs cleared successfully.")
						dialog.ShowInformation("Success", "Logs cleared successfully.", w.window)
					}
				}
			}
		}, w.window)
	}),
		widget.NewForm(widget.NewFormItem("Log Path", w.logPathEntry)))

	logsTab := container.NewPadded(container.NewBorder(
		createGroup("Configuration", logHeader),
		nil, nil, nil,
		container.NewScroll(w.logContent),
	))

	// 组装标签页，添加图标增强视觉
	w.tabContainer = container.NewAppTabs(
		container.NewTabItemWithIcon("General", theme.SettingsIcon(), generalTab),
		container.NewTabItemWithIcon("Scripts", theme.DocumentIcon(), scriptsTab),
		container.NewTabItemWithIcon("Logs", theme.InfoIcon(), logsTab),
	)

	// 添加标签页切换事件处理
	w.tabContainer.OnSelected = func(tab *container.TabItem) {
		if tab.Text == "Logs" {
			// 当切换到 Logs 标签时，加载日志内容
			w.loadLogContent()
		}
	}
}

// loadConfig 载入配置到 UI
func (w *PreferencesWindow) loadConfig() {
	appConfig := w.configManager.GetAppConfig()
	editorConfig := w.configManager.GetEditorConfig()
	scriptConfig := w.configManager.GetScriptConfig()

	// 加载核心组件的配置
	w.fontFamilyEntry.SetText(editorConfig.FontFamily)
	w.fontSizeEntry.SetText(strconv.Itoa(editorConfig.FontSize))
	w.windowWidthEntry.SetText(strconv.Itoa(appConfig.WindowWidth))
	w.windowHeightEntry.SetText(strconv.Itoa(appConfig.WindowHeight))
	w.maximizeWindowCheck.SetChecked(appConfig.MaximizeWindow)
	w.enableGlobalHotkeysCheck.SetChecked(appConfig.EnableGlobalHotkeys)

	w.scriptDirs = scriptConfig.ScriptDirs

	// 加载非核心组件的配置（确保组件已经创建）
	if w.pythonPathEntry != nil {
		w.pythonPathEntry.SetText(scriptConfig.PythonPath)
	}
	if w.scriptTimeoutEntry != nil {
		w.scriptTimeoutEntry.SetText(strconv.Itoa(scriptConfig.Timeout))
	}
	if w.filterDelayEntry != nil {
		w.filterDelayEntry.SetText(strconv.Itoa(scriptConfig.FilterDelay))
	}

	if w.logPathEntry != nil {
		// 使用日志系统当前的日志文件路径
		logPath := log.GetLogPath()
		w.logPathEntry.SetText(logPath)
	}
	if w.logContent != nil {
		w.logContent.SetText("Loading logs...")
	}
}

// loadLogContent 异步加载日志文件内容
func (w *PreferencesWindow) loadLogContent() {
	if w.logContent == nil || w.logPathEntry == nil {
		return
	}

	// 异步加载日志内容
	go func() {
		startTime := time.Now()
		logPath := w.logPathEntry.Text
		if logPath == "" {
			fyne.Do(func() {
				w.logContent.SetText("No log path set.")
			})
			log.Info("Log content loading completed in %.3fs (no log path)", time.Since(startTime).Seconds())
			return
		}

		// 读取日志文件
		log.Debug("Starting to read log file: %s", logPath)
		file, err := os.Open(logPath)
		if err != nil {
			fyne.Do(func() {
				w.logContent.SetText("Error reading log file: " + err.Error())
			})
			log.Info("Log content loading failed in %.3fs: %v", time.Since(startTime).Seconds(), err)
			return
		}
		defer file.Close()

		// 读取文件末尾的内容，限制行数
		const maxLines = 300
		var lines []string

		// 使用 scanner 逐行读取
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			lines = append(lines, scanner.Text())
			// 只保留最后 maxLines 行
			if len(lines) > maxLines {
				lines = lines[1:]
			}
		}

		if err := scanner.Err(); err != nil {
			fyne.Do(func() {
				w.logContent.SetText("Error reading log file: " + err.Error())
			})
			log.Info("Log content loading failed in %.3fs: %v", time.Since(startTime).Seconds(), err)
			return
		}

		// 拼接日志内容
		content := strings.Join(lines, "\n")
		log.Debug("Log file read completed, lines: %d, size: %d bytes", len(lines), len(content))

		// 更新日志内容并滚动到底部
		fyne.Do(func() {
			updateStart := time.Now()
			w.logContent.SetText(content)
			// 滚动到最下方
			w.logContent.CursorRow = len(lines)
			w.logContent.Refresh()
			log.Debug("UI update completed in %.3fs", time.Since(updateStart).Seconds())
		})

		log.Info("Log content loading completed in %.3fs", time.Since(startTime).Seconds())
	}()
}

// 隐藏窗口并将焦点定位到编辑器的编辑区域
func (w *PreferencesWindow) hideAndFocusToEditor() {
	// startTime := time.Now()
	w.window.Hide()
	// 恢复焦点到主窗口
	if w.mainWindow != nil {
		w.mainWindow.FocusEditor()
	}
	// log.Info("PreferencesWindow hideAndFocusToEditor 耗时: %v", time.Since(startTime))
}

// initWindow 初始化窗口和布局
func (w *PreferencesWindow) initWindow() {
	// 如果窗口已经存在，不需要重新创建
	if w.window != nil {
		return
	}

	// 先创建窗口实例
	w.window = fyne.CurrentApp().NewWindow("Preferences")
	w.window.Resize(fyne.NewSize(700, 580)) // 适配内容尺寸
	w.window.CenterOnScreen()

	// 异步设置窗口内容，确保所有组件都已初始化
	go func() {
		fyne.Do(func() {
			// 底部操作区：取消在左，保存项在右且高亮
			cancelBtn := widget.NewButton("Cancel (Esc)", func() {
				w.hideAndFocusToEditor()
			})

			saveBtn := widget.NewButton("Save (Enter)", func() {
				w.saveConfig()
				w.hideAndFocusToEditor()
			})
			saveBtn.Importance = widget.HighImportance // 突出保存按钮

			// 使用 Spacer 撑开左右两端
			buttonRow := container.NewHBox(
				cancelBtn,
				layout.NewSpacer(),
				saveBtn,
			)

			// 整体边框布局
			mainLayout := container.NewBorder(
				nil,
				container.NewPadded(buttonRow),
				nil,
				nil,
				w.tabContainer,
			)

			w.window.SetContent(mainLayout)

			// 设置关闭拦截：当用户点击关闭按钮时，改为隐藏窗口而不是关闭
			w.window.SetCloseIntercept(func() {
				w.hideAndFocusToEditor()
			})

			// 键盘监听
			w.window.Canvas().SetOnTypedKey(func(e *fyne.KeyEvent) {
				if e.Name == fyne.KeyEscape {
					w.hideAndFocusToEditor()
				} else if e.Name == fyne.KeyReturn {
					w.saveConfig()
					w.hideAndFocusToEditor()
				}
			})
		})
	}()
}

// Preload 预加载设置窗口
func (w *PreferencesWindow) Preload(show bool) {
	if w.window == nil {
		// 初始化组件和数据
		w.initComponents()
		w.loadConfig()
		w.initWindow()
	}
	// 显示窗口
	if show {
		w.window.Show()
	}
}

// Show 显示设置窗口
func (w *PreferencesWindow) Show() {
	startTime := time.Now()

	// 确保所有组件都已初始化
	if w.window == nil || w.tabContainer == nil {
		// 显示加载提示
		dialog.ShowInformation("Loading", "Preferences window is initializing. Please wait...", w.parentWindow)

		// 如果窗口尚未初始化，启动初始化
		if w.window == nil {
			go func() {
				// 初始化组件和数据&显示窗口
				w.Preload(true)
				log.Info("[窗口打开-未初始化] PreferencesWindow 打开完成，耗时: %.2fms", float64(time.Since(startTime))/1e6)
			}()
		}
		return
	}

	// 加载最新配置
	w.loadConfig()

	// 显示窗口
	w.window.Show()
	log.Info("[窗口打开-已初始化] PreferencesWindow 打开完成，耗时: %.2fms", float64(time.Since(startTime))/1e6)
}

// saveConfig 从 UI 读取并持久化配置
func (w *PreferencesWindow) saveConfig() {
	fontSize, _ := strconv.Atoi(w.fontSizeEntry.Text)
	windowWidth, _ := strconv.Atoi(w.windowWidthEntry.Text)
	windowHeight, _ := strconv.Atoi(w.windowHeightEntry.Text)
	timeout, _ := strconv.Atoi(w.scriptTimeoutEntry.Text)
	filterDelay, _ := strconv.Atoi(w.filterDelayEntry.Text)

	// 更新各模块配置
	w.configManager.UpdateAppConfig(config.AppConfig{
		WindowWidth:         windowWidth,
		WindowHeight:        windowHeight,
		MaximizeWindow:      w.maximizeWindowCheck.Checked,
		EnableGlobalHotkeys: w.enableGlobalHotkeysCheck.Checked,
	})

	w.configManager.UpdateEditorConfig(config.EditorConfig{
		FontFamily: w.fontFamilyEntry.Text,
		FontSize:   fontSize,
	})

	w.configManager.UpdateScriptConfig(config.ScriptConfig{
		ScriptDirs:  w.scriptDirs,
		PythonPath:  w.pythonPathEntry.Text,
		Timeout:     timeout,
		FilterDelay: filterDelay,
	})
}
