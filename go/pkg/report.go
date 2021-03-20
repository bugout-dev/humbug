package humbug

type Report struct {
	Title   string
	Tags    []string
	Content string
}

type Reporter interface {
	Tags() []string
	AddTags([]string)
	Publish(Report) error
}
