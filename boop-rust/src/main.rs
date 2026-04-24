//! Boop Rust 应用程序

use iced::{Element, Task};

mod core;
mod ui;
mod utils;

use core::{Config, init, info, get_scripts_path, ScriptManager};
use ui::{MainWindow, MainWindowMessage};
use utils::ShortcutManager;

struct BoopApp {
    config: Config,
    main_window: MainWindow,
    shortcut_manager: ShortcutManager,
    script_manager: ScriptManager,
}

#[derive(Debug, Clone)]
enum BoopMessage {
    MainWindowMessage(MainWindowMessage),
}

fn new() -> BoopApp {
    // 初始化日志系统
    init();
    info("Boop Rust 应用程序启动");

    // 加载配置
    let config = Config::default();

    // 初始化脚本管理器
    let script_manager = ScriptManager::new(get_scripts_path());

    // 初始化主窗口
    let main_window = MainWindow::new();

    // 初始化快捷键管理器
    let shortcut_manager = ShortcutManager::new();
    shortcut_manager.register_shortcuts();

    BoopApp {
        config,
        main_window,
        shortcut_manager,
        script_manager,
    }
}

fn update(state: &mut BoopApp, message: BoopMessage) -> Task<BoopMessage> {
    match message {
        BoopMessage::MainWindowMessage(main_window_message) => {
            let task = state.main_window.update(main_window_message);
            task.map(BoopMessage::MainWindowMessage)
        }
    }
}

fn view(state: &BoopApp) -> Element<'_, BoopMessage> {
    state.main_window.view().map(BoopMessage::MainWindowMessage)
}

pub fn main() -> iced::Result {
    let config = Config::default();
    iced::application(new, update, view)
        .theme(iced::Theme::Light)
        .window_size((config.window_width, config.window_height))
        .run()
}
