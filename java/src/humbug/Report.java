package humbug;

/**
 * Represents report that will be send to bugout.dev server
 */
public class Report {
    private String title;
    private String content;
    private String[] tags;

    public Report(String title, String content, String[] tags) {
        this.title = title;
        this.content = content;
        this.tags = tags;
    }

    /**
     *
     * @return Title of Report
     */
    public String getTitle() {
        return title;
    }

    /**
     *
     * @return content of Report in markdown
     */
    public String getContent() {
        return content;
    }

    /**
     *
     * @return Tags of report
     */
    public String[] getTags() {
        return tags;
    }
}
