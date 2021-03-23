package humbug

import (
	"fmt"
	"runtime"
	"runtime/debug"
	"strings"
)

type Report struct {
	Title   string
	Tags    []string
	Content string
}

func SystemReport() Report {
	title := "System report"

	goos := runtime.GOOS
	renderedGoos := fmt.Sprintf("## Operating system\n`%s`", goos)

	goarch := runtime.GOARCH
	numCPUs := runtime.NumCPU()
	renderedCPUs := fmt.Sprintf("## CPUs\nArchitecture: `%s`\nNumber: `%d`", goarch, numCPUs)

	goVersion := runtime.Version()
	renderedGoVersion := fmt.Sprintf("## Go version\n`%s`", goVersion)

	content := strings.Join([]string{renderedGoos, renderedCPUs, renderedGoVersion}, "\n\n")

	tags := []string{"type:system", fmt.Sprintf("os:%s", goos), fmt.Sprintf("arch:%s", goarch)}

	return Report{Title: title, Tags: tags, Content: content}
}

func PanicReport(message interface{}) Report {
	title := fmt.Sprintf("Panic: %v", message)
	content := string(debug.Stack())
	tags := []string{"type:error"}
	return Report{Title: title, Tags: tags, Content: content}
}
