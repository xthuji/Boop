package editor

import (
	"boop-go/src/core/config"
	"boop-go/src/utils"
	"fmt"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

// customEntry 增强版
type customEntry struct {
	widget.Entry
	parentScroll *container.Scroll
	editor       *Editor
}

// MinSize 关键：高度随内容扩展，禁用内部滚动
func (e *customEntry) MinSize() fyne.Size {
	ms := e.Entry.MinSize()
	lineCount := float32(strings.Count(e.Text, "\n") + 1)
	textProps := fyne.TextStyle{Monospace: true}
	lineHeight := fyne.MeasureText("M", theme.TextSize(), textProps).Height + (theme.Padding() * 0.5)
	ms.Height = lineCount * lineHeight
	return ms
}

// Scrolled 透传滚动事件
func (e *customEntry) Scrolled(f *fyne.ScrollEvent) {
	if e.parentScroll != nil {
		e.parentScroll.Scrolled(f)
	}
}

func (e *customEntry) TypedKey(key *fyne.KeyEvent) {
	e.Entry.TypedKey(key)
}

func (e *customEntry) TypedShortcut(shortcut fyne.Shortcut) {
	// 让父类处理所有快捷键，忽略系统默认的 Undo/Redo 快捷键
	// 编辑器相关的快捷键通过 BindShortcuts 方法绑定
	e.Entry.TypedShortcut(shortcut)
}

func (e *customEntry) scrollToCursor() {
	if e.parentScroll == nil {
		return
	}
	lineHeight := fyne.MeasureText("M", theme.TextSize(), fyne.TextStyle{Monospace: true}).Height + (theme.Padding() * 0.5)
	cursorY := float32(e.CursorRow) * lineHeight
	scrollPos := e.parentScroll.Offset.Y
	viewHeight := e.parentScroll.Size().Height

	if cursorY < scrollPos {
		e.parentScroll.Offset.Y = cursorY
		e.parentScroll.Refresh()
	} else if cursorY+lineHeight > scrollPos+viewHeight {
		e.parentScroll.Offset.Y = cursorY - viewHeight + lineHeight
		e.parentScroll.Refresh()
	}
}

// TextEditor 结构
type TextEditor struct {
	Entry           *customEntry
	lineNumbers     *widget.Label
	CursorRow       int
	CursorCol       int
	SelectionRow    int // 修复编译报错：添加此字段
	OnCursorChanged func()
	modified        bool
	history         []string
	historyIndex    int
	saveEnabled     bool
}

// GetContent 修复编译报错
func (te *TextEditor) GetContent() string {
	return te.Entry.Text
}

// SetContent 修复编译报错
func (te *TextEditor) SetContent(text string) {
	te.Entry.SetText(text)
}

type Editor struct {
	Content       *container.Scroll
	TextEditor    *TextEditor
	ConfigManager *config.Manager
}

func (e *Editor) GetCurrentTextEditor() *TextEditor {
	return e.TextEditor
}

func NewEditor(configManager *config.Manager) *Editor {
	entry := newCustomEntry()
	lineNumbers := widget.NewLabel("1")
	lineNumbers.TextStyle = fyne.TextStyle{Monospace: true}
	lineNumbers.Alignment = fyne.TextAlignTrailing

	textEditor := &TextEditor{
		Entry:        entry,
		lineNumbers:  lineNumbers,
		history:      []string{""},
		historyIndex: 0,
		saveEnabled:  true,
	}

	editor := &Editor{
		TextEditor:    textEditor,
		ConfigManager: configManager,
	}
	entry.editor = editor

	entry.OnChanged = func(s string) {
		linesCount := strings.Count(s, "\n") + 1
		var sb strings.Builder
		for i := 1; i <= linesCount; i++ {
			if i > 1 {
				sb.WriteString("\n")
			}
			sb.WriteString(fmt.Sprintf("%d", i))
		}
		lineNumbers.SetText(sb.String())
		entry.Refresh()

		textEditor.modified = true
		if textEditor.OnCursorChanged != nil {
			textEditor.OnCursorChanged()
		}
		textEditor.saveState()
		entry.scrollToCursor()
	}

	leftColumn := container.NewVBox(lineNumbers)
	editorLayout := container.NewBorder(nil, nil, leftColumn, nil, entry)
	scroll := container.NewScroll(editorLayout)
	entry.parentScroll = scroll
	editor.Content = scroll

	return editor
}

// BindEditorShortcuts 绑定编辑器相关的快捷键
func (e *Editor) BindEditorShortcuts(canvas fyne.Canvas) {
	if e.ConfigManager == nil {
		return
	}

	// 从配置中获取快捷键设置
	shortcutsConfig := e.ConfigManager.GetShortcutsConfig()
	utils.BindShortcuts(canvas, shortcutsConfig.Undo, func(_ fyne.Shortcut) { e.Undo() })
	utils.BindShortcuts(canvas, shortcutsConfig.Redo, func(_ fyne.Shortcut) { e.Redo() })
	utils.BindShortcuts(canvas, shortcutsConfig.Cut, func(_ fyne.Shortcut) { e.Cut() })
	utils.BindShortcuts(canvas, shortcutsConfig.Copy, func(_ fyne.Shortcut) { e.Copy() })
	utils.BindShortcuts(canvas, shortcutsConfig.Paste, func(_ fyne.Shortcut) { e.Paste() })
	utils.BindShortcuts(canvas, shortcutsConfig.SelectAll, func(_ fyne.Shortcut) { e.SelectAll() })
	utils.BindShortcuts(canvas, shortcutsConfig.MoveToStart, func(_ fyne.Shortcut) { e.MoveToStart() })
	utils.BindShortcuts(canvas, shortcutsConfig.MoveToEnd, func(_ fyne.Shortcut) { e.MoveToEnd() })

}

func newCustomEntry() *customEntry {
	e := &customEntry{}
	e.MultiLine = true
	e.Wrapping = fyne.TextWrapOff
	e.Scroll = fyne.ScrollNone
	e.TextStyle = fyne.TextStyle{Monospace: true}
	e.ExtendBaseWidget(e)
	return e
}

// 历史与功能方法
func (te *TextEditor) saveState() {
	if !te.saveEnabled {
		return
	}
	currentText := te.Entry.Text
	if te.historyIndex < len(te.history)-1 {
		te.history = te.history[:te.historyIndex+1]
	}
	if len(te.history) > 0 && te.history[len(te.history)-1] == currentText {
		return
	}
	te.history = append(te.history, currentText)
	te.historyIndex = len(te.history) - 1
}

func (e *Editor) Undo() {
	te := e.TextEditor
	if te.historyIndex > 0 {
		te.historyIndex--
		te.applyHistoryState(te.history[te.historyIndex])
	}
}

func (e *Editor) Redo() {
	te := e.TextEditor
	if te.historyIndex < len(te.history)-1 {
		te.historyIndex++
		te.applyHistoryState(te.history[te.historyIndex])
	}
}

func (te *TextEditor) applyHistoryState(text string) {
	te.saveEnabled = false
	te.Entry.SetText(text)
	te.saveEnabled = true
}

func (e *Editor) Focus() {
	fyne.Do(func() {
		if fyne.CurrentApp() != nil {
			canvas := fyne.CurrentApp().Driver().CanvasForObject(e.TextEditor.Entry)
			if canvas != nil {
				canvas.Focus(e.TextEditor.Entry)
			}
		}
	})
}

func (e *Editor) Cut()       { e.TextEditor.Entry.TypedShortcut(&fyne.ShortcutCut{}) }
func (e *Editor) Copy()      { e.TextEditor.Entry.TypedShortcut(&fyne.ShortcutCopy{}) }
func (e *Editor) Paste()     { e.TextEditor.Entry.TypedShortcut(&fyne.ShortcutPaste{}) }
func (e *Editor) SelectAll() { e.TextEditor.Entry.TypedShortcut(&fyne.ShortcutSelectAll{}) }
func (e *Editor) MoveToStart() {
	entry := e.TextEditor.Entry
	entry.CursorRow = 0
	entry.CursorColumn = 0
	entry.Refresh()
	entry.scrollToCursor()
}

func (e *Editor) MoveToEnd() {
	entry := e.TextEditor.Entry
	lines := strings.Split(entry.Text, "\n")
	entry.CursorRow = len(lines) - 1
	entry.CursorColumn = len(lines[entry.CursorRow])
	entry.Refresh()
	entry.scrollToCursor()
}
