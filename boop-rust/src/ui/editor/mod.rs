//! 编辑器模块

use iced::widget::{text_editor, container, row, text, scrollable, column};
use iced::{Element, Font, Length, Alignment, Task};
use crate::core::config::Config;


pub struct Editor {
    pub content: text_editor::Content,
    pub cursor_position: (usize, usize), // (行, 列)
    pub status_bar: StatusBar,
}

pub struct StatusBar {
    pub cursor_position: (usize, usize), // (行, 列)
}

#[derive(Debug, Clone)]
pub enum EditorMessage {
    Edit(text_editor::Action),
    StatusBarMessage(StatusBarMessage),
}

#[derive(Debug, Clone)]
pub enum StatusBarMessage {
    // 状态栏消息
}

impl StatusBar {
    pub fn new() -> Self {
        Self {
            cursor_position: (1, 1), // 初始光标位置 (行, 列)
        }
    }

    pub fn update_cursor_position(&mut self, position: (usize, usize)) {
        self.cursor_position = position;
    }

    pub fn update(&mut self, _message: StatusBarMessage) -> Task<StatusBarMessage> {
        Task::none()
    }

    pub fn view(&self) -> Element<'_, StatusBarMessage> {
        container(
            row!(
                text("状态栏").size(12),
                text("").width(Length::Fill), // 占位符，将光标位置推到右侧
                text(format!("行: {}, 列: {}", self.cursor_position.0, self.cursor_position.1))
                    .size(12)
            )
            .width(Length::Fill)
            .align_y(Alignment::Center)
        )
        .padding(4)
        .width(Length::Fill)
        .height(24)
        .into()
    }
}

impl Editor {
    pub fn new() -> Self {
        Self {
            content: text_editor::Content::new(),
            cursor_position: (1, 1), // 初始光标位置 (行, 列)
            status_bar: StatusBar::new(),
        }
    }

    pub fn update(&mut self, message: EditorMessage) -> Task<EditorMessage> {
        match message {
            EditorMessage::Edit(action) => {
                self.content.perform(action);
                // 更新光标位置
                let cursor = self.content.cursor();
                self.cursor_position = (cursor.position.line + 1, cursor.position.column + 1); // 转换为 1-based 索引
                // 更新状态栏的光标位置
                self.status_bar.update_cursor_position(self.cursor_position);
            }
            EditorMessage::StatusBarMessage(status_bar_message) => {
                // 处理状态栏消息
                let _ = self.status_bar.update(status_bar_message);
            }
        }
        
        Task::none()
    }

    pub fn view(&self) -> Element<'_, EditorMessage> {
        // 构建核心编辑器窗口
        let config = Config::default();
        let editor = text_editor(&self.content)
            .on_action(EditorMessage::Edit)
            .font(Font::MONOSPACE)
            .size(14)
            .min_height(config.window_height - config.status_bar_height - 20);
    
        // 计算行数并生成行号，确保至少显示20行
        let lines = std::cmp::max(20, self.content.lines().count());
        let line_numbers_text = (1..=lines).map(|i| i.to_string()).collect::<Vec<_>>().join("\n");
        let line_numbers = container(
            text(line_numbers_text)
                .font(Font::MONOSPACE)
                .size(14)
        )
        .padding(2)
        .width(40)
        .height(Length::Fill)
        .align_x(Alignment::End);

        // 构建编辑器和行号的组合
        let editor_with_line_numbers = row!(
            line_numbers,
            editor
        )
        .spacing(4)
        .width(Length::Fill)
        .height(Length::Fill);

        // 构建状态栏
        let status_bar_view = self.status_bar.view().map(EditorMessage::StatusBarMessage);

        // 构建带滚动条的编辑器
        let scrollable_editor = scrollable(
            container(editor_with_line_numbers)
                .padding(2)
                .width(Length::Fill)
                .height(Length::Fill)
        )
        .width(Length::Fill)
        .height(Length::Fill);

        // 组合布局
        column!(
            scrollable_editor,
            status_bar_view
        )
        .height(Length::Fill) 
        .width(Length::Fill)
        .into()
    }
}
