package ui

import (
	"fmt"
	"strings"
	"time"

	"boop-go/src/core/log"
	"boop-go/src/core/script"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

// 自定义 Entry 组件，支持上下方向键控制脚本列表
type scriptPickerEntry struct {
	*widget.Entry
	scriptPicker *ScriptPickerWindow
}

// TypedKey 覆盖父类的 TypedKey 方法
func (e *scriptPickerEntry) TypedKey(key *fyne.KeyEvent) {
	if key.Name == fyne.KeyUp || key.Name == fyne.KeyDown {
		// 处理上下方向键事件
		if len(e.scriptPicker.filteredScripts) > 0 {
			if key.Name == fyne.KeyUp {
				// 向上移动选中项，支持循环
				e.scriptPicker.selectedIndex = (e.scriptPicker.selectedIndex - 1 + len(e.scriptPicker.filteredScripts)) % len(e.scriptPicker.filteredScripts)
			} else {
				// 向下移动选中项，支持循环
				e.scriptPicker.selectedIndex = (e.scriptPicker.selectedIndex + 1) % len(e.scriptPicker.filteredScripts)
			}
			e.scriptPicker.scriptList.Select(e.scriptPicker.selectedIndex)
			e.scriptPicker.updateDetails(e.scriptPicker.filteredScripts[e.scriptPicker.selectedIndex])
			e.scriptPicker.scriptList.ScrollTo(e.scriptPicker.selectedIndex)
		}
	} else if key.Name == fyne.KeyEscape {
		// 处理 Esc 键：只有当输入框为空时才关闭窗口
		// 这样在输入法输入过程中，Esc 键会由输入法处理
		if e.Text == "" {
			e.scriptPicker.hideAndFocusToEditor()
		} else {
			// 输入框有内容，交给父类处理（可能是取消输入法输入）
			e.Entry.TypedKey(key)
		}
	} else if key.Name == fyne.KeyReturn || key.Name == fyne.KeyEnter {
		// 处理 Enter 键：执行选中的脚本
		// 即使输入框有内容，也执行脚本
		// 这样用户可以在输入搜索词后直接按 Enter 执行当前选中的脚本
		e.scriptPicker.executeSelected()
	} else {
		// 其他键事件交给父类处理
		e.Entry.TypedKey(key)
	}
}

// 自定义布局：固定比例的水平分割布局
type fixedRatioLayout struct {
	leftRatio float64 // 左侧区域占比
}

// NewFixedRatioLayout 创建一个固定比例的水平分割布局
func NewFixedRatioLayout(leftRatio float64) *fixedRatioLayout {
	return &fixedRatioLayout{leftRatio: leftRatio}
}

// Layout 实现 fyne.Layout 接口
func (l *fixedRatioLayout) Layout(objects []fyne.CanvasObject, size fyne.Size) {
	if len(objects) != 2 {
		return
	}

	// 计算左侧和右侧的宽度
	leftWidth := float32(float64(size.Width) * l.leftRatio)
	rightWidth := size.Width - leftWidth

	// 设置左侧对象的位置和大小
	objects[0].Move(fyne.NewPos(0, 0))
	objects[0].Resize(fyne.NewSize(leftWidth, size.Height))

	// 设置右侧对象的位置和大小
	objects[1].Move(fyne.NewPos(leftWidth, 0))
	objects[1].Resize(fyne.NewSize(rightWidth, size.Height))
}

// MinSize 实现 fyne.Layout 接口
func (l *fixedRatioLayout) MinSize(objects []fyne.CanvasObject) fyne.Size {
	if len(objects) != 2 {
		return fyne.NewSize(0, 0)
	}

	leftMin := objects[0].MinSize()
	rightMin := objects[1].MinSize()

	width := leftMin.Width + rightMin.Width
	height := fyne.Max(leftMin.Height, rightMin.Height)

	return fyne.NewSize(width, height)
}

type ScriptPickerWindow struct {
	scriptManager  *script.ScriptManager
	scriptExecutor *script.ScriptExecutor

	// 数据定义
	allScripts      []*script.ScriptMetadata
	filteredScripts []*script.ScriptMetadata

	// 状态跟踪
	selectedIndex int
	searchQuery   string

	// UI 组件 - 顶部
	searchInput *scriptPickerEntry

	// UI 组件 - 左侧列表
	scriptList *widget.List

	// UI 组件 - 右侧详情
	detailName        *widget.Label
	detailFilename    *widget.Label
	detailDescription *widget.Label
	detailTags        *widget.Label
	detailHelp        *widget.Entry // 可滚动的多行文本框

	// UI 组件 - 底部
	statusLabel *widget.Label
	runButton   *widget.Button

	// 窗口实例
	window       fyne.Window
	parentWindow fyne.Window
	mainWindow   *MainWindow

	// 回调
	OnScriptSelected func(metadata *script.ScriptMetadata)
}

func (w *ScriptPickerWindow) initData() {
	w.allScripts = w.scriptManager.GetScripts()
	w.filteredScripts = w.allScripts
}

func (w *ScriptPickerWindow) initComponents() {
	// 1. 顶部搜索框（核心组件，立即创建）
	w.searchInput = &scriptPickerEntry{
		Entry:        widget.NewEntry(),
		scriptPicker: w,
	}
	w.searchInput.SetPlaceHolder("Search scripts...")
	w.searchInput.OnChanged = func(s string) {
		w.searchQuery = s
		w.applyFilters()
	}

	// 2. 左侧脚本列表（核心组件，立即创建）
	w.scriptList = widget.NewList(
		func() int { return len(w.filteredScripts) },
		func() fyne.CanvasObject {
			name := widget.NewLabelWithStyle("", fyne.TextAlignLeading, fyne.TextStyle{Bold: true})
			desc := widget.NewLabel("")
			desc.Truncation = fyne.TextTruncateEllipsis

			// 布局：一行两列，名称、描述
			return container.NewGridWithColumns(2, name, desc)
		},
		func(i widget.ListItemID, o fyne.CanvasObject) {
			if i >= len(w.filteredScripts) {
				return
			}
			s := w.filteredScripts[i]
			root := o.(*fyne.Container)

			// 设置文本
			root.Objects[0].(*widget.Label).SetText(s.Icon + " " + s.Name)
			root.Objects[1].(*widget.Label).SetText(s.Description)
		},
	)

	w.scriptList.OnSelected = func(id widget.ListItemID) {
		w.selectedIndex = id
		w.updateDetails(w.filteredScripts[id])
	}

	// 3. 立即创建所有组件，避免空指针异常
	// 右侧详情组件
	w.detailName = widget.NewLabelWithStyle("-", fyne.TextAlignLeading, fyne.TextStyle{Bold: true})
	w.detailName.Wrapping = fyne.TextWrapWord
	w.detailFilename = widget.NewLabel("-")
	w.detailFilename.Wrapping = fyne.TextWrapWord
	w.detailDescription = widget.NewLabel("-")
	w.detailDescription.Wrapping = fyne.TextWrapWord
	w.detailTags = widget.NewLabel("-")
	w.detailTags.Wrapping = fyne.TextWrapWord

	w.detailHelp = widget.NewMultiLineEntry()
	// w.detailHelp.Disable() // 使其只读
	w.detailHelp.Wrapping = fyne.TextWrapWord

	// 底部组件
	w.statusLabel = widget.NewLabelWithStyle("", fyne.TextAlignCenter, fyne.TextStyle{Italic: true})
	w.runButton = widget.NewButtonWithIcon("Run", theme.ConfirmIcon(), func() {
		w.executeSelected()
	})
	w.runButton.Importance = widget.HighImportance
	w.runButton.Disable() // 初始未选中时禁用
}

func (w *ScriptPickerWindow) updateDetails(s *script.ScriptMetadata) {
	w.detailName.SetText(s.Name)
	// 假设 FilePath 是完整路径，我们只显示文件名
	parts := strings.Split(s.FilePath, "/")
	w.detailFilename.SetText(parts[len(parts)-1])
	w.detailDescription.SetText(s.Description)
	w.detailTags.SetText(strings.Join(s.Tags, ", "))

	// 设置 Help 内容，使用元数据中的 help 字段
	var helpContent string
	if s.Help != "" {
		helpContent = fmt.Sprintf("# Help Documentation\n\n%s", s.Help)
	} else {
		helpContent = "# Help Documentation\n\nNo help documentation available."
	}
	w.detailHelp.SetText(helpContent)

	w.runButton.Enable()
}

func (w *ScriptPickerWindow) applyFilters() {
	query := strings.ToLower(w.searchQuery)
	w.filteredScripts = nil

	for _, s := range w.allScripts {
		if query == "" ||
			strings.Contains(strings.ToLower(s.Name), query) ||
			strings.Contains(strings.ToLower(s.Description), query) ||
			strings.Contains(strings.ToLower(strings.Join(s.Tags, " ")), query) {
			w.filteredScripts = append(w.filteredScripts, s)
		}
	}

	w.scriptList.Refresh()
	w.updateStatus()

	if len(w.filteredScripts) > 0 {
		w.scriptList.Select(0)
	} else {
		w.selectedIndex = -1
		w.runButton.Disable()
	}
}

func (w *ScriptPickerWindow) updateStatus() {
	w.statusLabel.SetText(fmt.Sprintf("%d scripts", len(w.filteredScripts)))
}

// 隐藏窗口并将焦点定位到编辑器的编辑区域
func (w *ScriptPickerWindow) hideAndFocusToEditor() {
	// startTime := time.Now()
	w.window.Hide()
	// 恢复焦点到主窗口编辑区
	if w.mainWindow != nil {
		w.mainWindow.FocusEditor()
	}
	// log.Info("ScriptPickerWindow hideAndFocusToEditor 耗时: %v", time.Since(startTime))
}

// initWindow 初始化窗口和布局
func (w *ScriptPickerWindow) initWindow() {
	// 如果窗口已经存在，不需要重新创建
	if w.window != nil {
		return
	}

	w.window = fyne.CurrentApp().NewWindow("Script Picker")

	w.window.Resize(fyne.NewSize(800, 600))
	w.window.CenterOnScreen()

	// 设置关闭拦截：当用户点击关闭按钮时，改为隐藏窗口而不是关闭
	w.window.SetCloseIntercept(func() {
		w.hideAndFocusToEditor()
	})

	// 立即设置窗口内容，所有组件都已经初始化完成
	fyne.Do(func() {
		// --- 布局组装 ---

		// 1. 顶部：搜索框 (全宽)
		topArea := container.NewPadded(container.NewVBox(
			w.searchInput,
			widget.NewSeparator(),
		))

		// 2. 右侧详情容器 (使用 Form 排版元数据)
		detailForm := widget.NewForm(
			widget.NewFormItem("Name:", w.detailName),
			widget.NewFormItem("File:", w.detailFilename),
			widget.NewFormItem("Description:", w.detailDescription),
			widget.NewFormItem("Tags:", w.detailTags),
		)

		// 详情区：上方是 Form，下方是占据剩余空间的 Help 文本框
		rightContent := container.NewBorder(
			detailForm,
			nil, nil, nil,
			w.detailHelp,
		)

		// 右侧详情容器，使用自适应宽度，确保内容能够自动换行
		rightContentContainer := container.NewVScroll(rightContent)

		// 3. 中间区域：使用自定义布局实现固定比例分割
		// 左侧占 3/5（60%），右侧占 2/5（40%）
		// 使用自定义布局，不允许用户拖动调整

		// 为左侧脚本列表添加边框
		borderedScriptList := container.NewBorder(
			nil, nil, nil, widget.NewSeparator(), // 右侧添加分隔线作为边框
			w.scriptList,
		)

		middleArea := container.New(NewFixedRatioLayout(0.6), borderedScriptList, rightContentContainer)

		// 底部控制栏
		cancelBtn := widget.NewButton("Cancel", func() {
			w.hideAndFocusToEditor()
		})

		// 底部布局：Cancel (左) | Count (中) | Run (右)
		bottomBar := container.NewVBox(
			widget.NewSeparator(),
			container.NewGridWithColumns(3,
				container.NewHBox(cancelBtn, layout.NewSpacer()),
				container.NewCenter(w.statusLabel),
				container.NewHBox(layout.NewSpacer(), w.runButton),
			),
		)

		// 5. 整体组装
		content := container.NewBorder(topArea, bottomBar, nil, nil, middleArea)
		w.window.SetContent(content)

		// 键盘支持
		w.window.Canvas().SetOnTypedKey(func(e *fyne.KeyEvent) {
			if e.Name == fyne.KeyEscape {
				w.hideAndFocusToEditor()
			} else if e.Name == fyne.KeyReturn || e.Name == fyne.KeyEnter {
				w.executeSelected()
			} else if e.Name == fyne.KeyUp {
				// 向上移动选中项，支持循环
				if len(w.filteredScripts) > 0 {
					w.selectedIndex = (w.selectedIndex - 1 + len(w.filteredScripts)) % len(w.filteredScripts)
					w.scriptList.Select(w.selectedIndex)
					w.updateDetails(w.filteredScripts[w.selectedIndex])
					w.scriptList.ScrollTo(w.selectedIndex)
				}
			} else if e.Name == fyne.KeyDown {
				// 向下移动选中项，支持循环
				if len(w.filteredScripts) > 0 {
					w.selectedIndex = (w.selectedIndex + 1) % len(w.filteredScripts)
					w.scriptList.Select(w.selectedIndex)
					w.updateDetails(w.filteredScripts[w.selectedIndex])
					w.scriptList.ScrollTo(w.selectedIndex)
				}
			}
		})
	})
}

// Preload 预加载脚本选择窗口
func (w *ScriptPickerWindow) Preload(show bool) {
	if w.window == nil {
		// 确保数据已初始化
		if len(w.allScripts) == 0 {
			w.allScripts = w.scriptManager.GetScripts()
			w.filteredScripts = w.allScripts
		}

		// 初始化 UI 组件
		w.initComponents()
		w.initWindow()
		// 初始化选中项
		if len(w.filteredScripts) > 0 {
			w.selectedIndex = 0
		} else if len(w.filteredScripts) == 0 {
			w.selectedIndex = -1
			w.runButton.Disable()
		}
	}

	// 显示窗口
	if show {
		w.DoShowWindow()
	}
}

func (w *ScriptPickerWindow) DoShowWindow() {
	// 显示窗口
	w.window.Show()
	// 自动聚焦到搜索输入框，同时通过 OnTypedKey 支持上下方向键控制脚本列表
	w.window.Canvas().Focus(w.searchInput)
	if len(w.filteredScripts) > 0 && w.selectedIndex >= 0 {
		w.scriptList.Select(w.selectedIndex)
		w.updateDetails(w.filteredScripts[w.selectedIndex])
	}
}

func (w *ScriptPickerWindow) Show(parent fyne.Window) {
	startTime := time.Now()

	// 保存主窗口引用
	w.parentWindow = parent

	// 确保所有组件都已初始化
	if w.window == nil || w.scriptList == nil || w.searchInput == nil {
		// 显示加载提示
		dialog.ShowInformation("Loading", "Script picker is initializing. Please wait...", parent)

		// 如果窗口尚未初始化，启动初始化
		if w.window == nil {
			go func() {
				// 确保数据已初始化 & 显示窗口
				w.Preload(true)
				log.Info("[窗口打开-未初始化] ScriptPickerWindow 打开完成，耗时: %.2fms", float64(time.Since(startTime))/1e6)
			}()
		}
		return
	}

	w.DoShowWindow()
	log.Info("[窗口打开-已初始化] ScriptPickerWindow 打开完成，耗时: %.2fms", float64(time.Since(startTime))/1e6)
}

func (w *ScriptPickerWindow) executeSelected() {
	if w.selectedIndex >= 0 && w.selectedIndex < len(w.filteredScripts) {
		selected := w.filteredScripts[w.selectedIndex]
		w.hideAndFocusToEditor()
		if w.OnScriptSelected != nil {
			w.OnScriptSelected(selected)
		}
	}
}
