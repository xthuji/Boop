package log

import (
	"boop-go/src/core/path"
	"fmt"
	"os"
	"time"

	"gopkg.in/natefinch/lumberjack.v2"
)

type LogLevel int

const (
	DEBUG LogLevel = iota
	INFO
	WARNING
	ERROR
	FATAL
)

var levelNames = map[LogLevel]string{
	DEBUG:   "DEBUG",
	INFO:    "INFO",
	WARNING: "WARNING",
	ERROR:   "ERROR",
	FATAL:   "FATAL",
}

var logLevel = INFO
var logFile *lumberjack.Logger

func Init(level LogLevel) error {
	logLevel = level

	logsDir := path.LogsDir()
	if err := os.MkdirAll(logsDir, 0755); err != nil {
		return fmt.Errorf("创建logs目录失败: %v", err)
	}

	logFile = &lumberjack.Logger{
		Filename:   logsDir + "/boop.log",
		MaxSize:    1,
		MaxBackups: 3,
		MaxAge:     3,
		Compress:   true,
	}

	Info("日志系统初始化成功")
	return nil
}

func Close() error {
	if logFile != nil {
		Info("日志系统关闭")
		err := logFile.Close()
		logFile = nil
		return err
	}
	return nil
}

func GetLogPath() string {
	if logFile != nil {
		Info("日志文件路径: %s", logFile.Filename)
		return logFile.Filename
	}
	return ""
}

func Debug(format string, args ...interface{}) {
	if logLevel <= DEBUG {
		log(DEBUG, format, args...)
	}
}

func Info(format string, args ...interface{}) {
	if logLevel <= INFO {
		log(INFO, format, args...)
	}
}

func Warning(format string, args ...interface{}) {
	if logLevel <= WARNING {
		log(WARNING, format, args...)
	}
}

func Error(format string, args ...interface{}) {
	if logLevel <= ERROR {
		log(ERROR, format, args...)
	}
}

func log(level LogLevel, format string, args ...interface{}) {
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	message := fmt.Sprintf(format, args...)
	logMessage := fmt.Sprintf("[%s] [%s] %s\n", timestamp, levelNames[level], message)

	fmt.Print(logMessage)

	if logFile != nil {
		logFile.Write([]byte(logMessage))
	}
}
