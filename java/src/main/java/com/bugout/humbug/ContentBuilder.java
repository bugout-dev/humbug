package com.bugout.humbug;

/**
 * Report content builder to easily work with markdown.
 */
public class ContentBuilder {
    StringBuilder content = new StringBuilder();
    public ContentBuilder() {

    }

    /**
     * Adds markdown header "### header\n"
     */
    public ContentBuilder addHeader(String header) {
        this.content.append("### ").append(header).append('\n');
        return this;
    }

    /**
     * Adds new line
     */
    public ContentBuilder addLine() {
        this.content.append('\n');
        return this;
    }

    /**
     * Adds string
     */
    public ContentBuilder addString(String s) {
        this.content.append(s);
        return this;
    }

    /**
     * Adds markdown code `string`
     */
    public ContentBuilder addCode(String s) {
        this.content.append('`').append(s).append('`');
        return this;
    }

    /**
     * Adds multiline code
     * ```
     * code
     * ```
     */
    public ContentBuilder addMultilineCode(String s) {
        this.content.append("```").append('\n').append(s).append('\n').append("```").append('\n');
        return this;
    }

    public String toString() {
        return content.toString();
    }
}
