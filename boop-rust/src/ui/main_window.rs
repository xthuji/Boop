//! 主窗口模块

use iced::widget::{column};
use iced::{Element, Length, Task};

use super::editor::Editor;

pub struct MainWindow {
    pub editor: Editor,
}

#[derive(Debug, Clone)]
pub enum MainWindowMessage {
    EditorMessage(super::editor::EditorMessage),
}

impl MainWindow {
    pub fn new() -> Self {
        Self {
            editor: Editor::new(),
        }
    }

    pub fn update(&mut self, message: MainWindowMessage) -> Task<MainWindowMessage> {
        match message {
            MainWindowMessage::EditorMessage(editor_message) => {
                let _ = self.editor.update(editor_message);
                Task::none()
            }
        }
    }

    pub fn view(&self) -> Element<'_, MainWindowMessage> {
        let editor_view = self.editor.view().map(MainWindowMessage::EditorMessage);

        column!(
            editor_view
        )
        .height(Length::Fill) 
        .width(Length::Fill)
        .into()
    }
}
