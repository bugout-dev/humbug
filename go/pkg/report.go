package humbug

import (
	bugout "github.com/bugout-dev/bugout-go/pkg"
)

type Report struct {
	Title   string
	Tags    []string
	Content string
}

type Reporter interface {
	Tags() []string
	Publish(Report) error
}

type HumbugReporter struct {
	client bugout.BugoutClient
}
