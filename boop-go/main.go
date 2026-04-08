package main

import (
	"boop-go/src/core/config"
	"boop-go/src/core/log"
	"boop-go/src/core/path"
	"boop-go/src/ui"
	"boop-go/src/utils"
	"sync"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"golang.design/x/hotkey"
)

// --- 修复点 1: 建立全局管理器，确保对象永久存活且不被 GC ---
var (
	hotkeyRegistry []*hotkey.Hotkey
	registryMu     sync.Mutex
)

func main() {
	startTime := time.Now()

	// 初始化系统
	initSystem()

	// 创建应用
	fyneApp, configManager := createApp()

	// 创建并配置主窗口
	boopCoreWindow, mainWindow := createMainWindow(fyneApp, configManager)

	// 立即启动窗口预加载
	go preloadWindows(mainWindow, startTime)
	// 绑定编辑器窗口相关快捷键
	go mainWindow.BindEditorWindowShortcuts()
	// 显示Boop窗口
	go fyne.Do(mainWindow.FocusEditor)

	// --- 修复点 2: 延迟注册 ---
	if configManager.GetAppConfig().EnableGlobalHotkeys {
		// 确保 Fyne 的初始化流程已经进入稳定状态后再注入全局钩子
		go func() {
			time.Sleep(1 * time.Second)
			setupGlobalHotkeys(configManager, boopCoreWindow, mainWindow)
		}()
	}

	// 运行应用 (阻塞主线程)
	fyneApp.Run()

	// 记录退出时间
	logExitTime(startTime)
}

// setupGlobalHotkeys 独立的快捷键设置函数，增强稳定性
func setupGlobalHotkeys(configManager *config.Manager, boopCoreWindow fyne.Window, mainWindow *ui.MainWindow) {
	appConfig := configManager.GetAppConfig()
	if !appConfig.EnableGlobalHotkeys {
		return
	}

	shortcutsConfig := configManager.GetShortcutsConfig()
	for _, shortcutStr := range shortcutsConfig.GlobalRunScript {
		// 修复点 3: 强制局部作用域变量，防止闭包逃逸问题
		currentStr := shortcutStr

		go func(s string) {
			// 1. 解析快捷键
			// 注意：请确保 utils.ParseShortcut 返回的是 hotkey.Key 所需的系统键码
			mods, key, err := utils.ParseShortcut(currentStr) // 直接获取正确的类型
			if err != nil {
				log.Error("Failed to parse global hotkey %s: %v", currentStr, err)
				return
			}

			hk := hotkey.New(mods, key)

			// 2. 注册到系统
			if err := hk.Register(); err != nil {
				log.Error("[热键故障] 系统注册失败 %s: %v (请检查权限或冲突)", s, err)
				return
			}

			// 3. 持久化存储
			registryMu.Lock()
			hotkeyRegistry = append(hotkeyRegistry, hk)
			registryMu.Unlock()

			// log.Info("[热键激活] 绑定全局快捷键: %s (Keycode: %s)", s, key)

			// 4. 监听循环
			for {
				// 使用阻塞监听，确保不会漏掉事件
				<-hk.Keydown()
				// startTime := time.Now()
				// log.Info("[热键触发] 检测到按键按下: %s", s)

				// 唤醒 UI 必须在 Fyne 线程执行
				fyne.Do(func() {
					boopCoreWindow.Show()
					boopCoreWindow.RequestFocus()
					mainWindow.ShowScriptPickerWindow()
					// log.Info("Global hotkey %s activated, focusing Boop window, 耗时: %v", currentStr, time.Since(startTime))
				})
			}
		}(currentStr)
	}
}

// ---------------------------
// 以下为原有的辅助函数，保持不变
// ---------------------------

func initSystem() {
	if err := path.Init(); err != nil {
		panic(err)
	}
	if err := log.Init(log.INFO); err != nil {
		panic(err)
	}
	log.Info("应用系统初始化完成")
}

func createApp() (fyne.App, *config.Manager) {
	fyneApp := app.NewWithID("boop_app_main")
	configManager := config.NewManager()
	return fyneApp, configManager
}

func createMainWindow(fyneApp fyne.App, configManager *config.Manager) (fyne.Window, *ui.MainWindow) {
	boopCoreWindow := fyneApp.NewWindow("Boop")
	mainWindow := ui.NewMainWindow(configManager, boopCoreWindow)
	boopCoreWindow.SetContent(mainWindow.Content)
	boopCoreWindow.SetMainMenu(mainWindow.MainMenu)

	appConfig := configManager.GetAppConfig()
	if appConfig.MaximizeWindow {
		boopCoreWindow.Resize(fyne.NewSize(1920, 1080))
	} else {
		boopCoreWindow.Resize(fyne.NewSize(float32(appConfig.WindowWidth), float32(appConfig.WindowHeight)))
	}
	return boopCoreWindow, mainWindow
}

type Preloadable interface {
	Preload(show bool)
}

func preloadWindow(wg *sync.WaitGroup, window Preloadable, windowName string) {
	wg.Add(1)
	go func() {
		doneChan := make(chan struct{})
		fyne.Do(func() {
			defer close(doneChan)
			window.Preload(false)
			log.Info("[预加载] %s 完成", windowName)
		})
		<-doneChan
		wg.Done()
	}()
}

func preloadWindows(mainWindow *ui.MainWindow, startTime time.Time) {
	var wg sync.WaitGroup
	if mainWindow.ScriptPickerWindow != nil {
		preloadWindow(&wg, mainWindow.ScriptPickerWindow, "ScriptPicker")
	}
	if mainWindow.PreferencesWindow != nil {
		preloadWindow(&wg, mainWindow.PreferencesWindow, "Preferences")
	}
	wg.Wait()
	log.Info("[系统] 启动总耗时: %v", time.Since(startTime))
}

func logExitTime(startTime time.Time) {
	log.Info("应用退出，总运行时间: %v", utils.FormatTimeDuration(time.Since(startTime)))
}
