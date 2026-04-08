package ui

import (
	"boop-go/src/ui/editor"
	"fmt"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

type StatusBar struct {
	Content     fyne.CanvasObject
	editor      *editor.Editor
	infoLbl     *widget.Label
	positionLbl *widget.Label
	scriptCount int
}

func NewStatusBar(ed *editor.Editor) *StatusBar {
	infoLbl := widget.NewLabel("")
	infoLbl.Alignment = fyne.TextAlignCenter

	positionLbl := widget.NewLabel("")
	positionLbl.Alignment = fyne.TextAlignTrailing

	// 创建右侧容器，只包含位置信息
	rightContainer := container.NewHBox(
		positionLbl,
	)

	// 创建主容器，使用Border布局
	content := container.NewBorder(
		nil,
		nil,
		nil,
		rightContainer,
		infoLbl,
	)

	return &StatusBar{
		Content:     content,
		editor:      ed,
		infoLbl:     infoLbl,
		positionLbl: positionLbl,
		scriptCount: 0,
	}
}



func (sb *StatusBar) SetScriptCount(count int) {
	sb.scriptCount = count
	sb.updateStatus()
}

func (sb *StatusBar) updateStatus() {
	// 显示脚本数量
	scriptText := fmt.Sprintf("Scripts: %d", sb.scriptCount)
	sb.infoLbl.SetText(scriptText)

	// 显示光标位置和选中文本行数
	if sb.editor != nil {
		textEditor := sb.editor.GetCurrentTextEditor()
		if textEditor != nil {
			cursorRow := textEditor.CursorRow
			cursorCol := textEditor.CursorCol
			selectionRow := textEditor.SelectionRow

			var positionText string
			if selectionRow > 0 {
				positionText = fmt.Sprintf("Ln %d, Col %d | %d lines selected", cursorRow, cursorCol, selectionRow)
			} else {
				positionText = fmt.Sprintf("Ln %d, Col %d", cursorRow, cursorCol)
			}
			sb.positionLbl.SetText(positionText)
		}
	}
}

func (sb *StatusBar) Refresh() {
	sb.updateStatus()
}

func (sb *StatusBar) SetMessage(message string) {
	sb.infoLbl.SetText(message)
}
