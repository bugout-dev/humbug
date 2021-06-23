package humbug;

import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.json.JSONObject;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.stream.Stream;

/**
 * Reporter engine that will send reports to bugout.dev server
 */
public class Reporter {
    private static String apiURL =  "https://spire.bugout.dev";

    private final SystemInformation systemInformation;
    private String name;
    private HumbugConsent consent;
    private String clientId;
    private String sessionId;
    private String bugoutToken;

    public Reporter(String name, HumbugConsent consent, String clientId, String sessionId, String bugoutToken) {
        this.systemInformation = SystemInformation.generateSystemInformation();
        this.name = name;
        this.consent = consent;
        this.clientId = clientId;
        this.sessionId = sessionId;
        this.bugoutToken = bugoutToken;
    }

    /**
     *
     * @return System information tags
     */
    private String[] getSystemTags() {
        String[] tags = new String[]{
                "humbug",
                "source:" + this.name,
                "os:" + this.systemInformation.getOs(),
                "arch:" + this.systemInformation.getArch(),
                "jvm:" + this.systemInformation.getJava_vm_name(),
                "java_version:" + this.systemInformation.getJava_version(),
                "session:" + this.sessionId,
                "client:" + this.clientId
        };
        return tags;
    }

    /**
     *
     * @param report Report to publish
     * @return null if successfully published
     * @throws IOException if failed to publish
     */
    private Object publish(Report report) throws IOException {
        if (!this.consent.check())
            return null;

        JSONObject json = new JSONObject();
        json.put("title", report.getTitle());
        json.put("content", report.getContent());
        json.put("tags", report.getTags());

        try (CloseableHttpClient httpClient = HttpClientBuilder.create().build()) {
            HttpPost request = new HttpPost(apiURL + "/humbug/reports");
            StringEntity params = new StringEntity(json.toString());
            request.addHeader("content-type", "application/json");
            request.addHeader("Authorization", "Bearer " + bugoutToken);
            request.setEntity(params);
            httpClient.execute(request);

        }

        return null;
    }

    /**
     *
     * @return System information content in markdown
     */
    private String generateSystemContent() {
        LocalDateTime time = LocalDateTime.now();
        ContentBuilder c = new ContentBuilder()
                .addHeader("User timestamp")
                .addMultilineCode(time.toString())
                .addHeader("Os")
                .addMultilineCode(this.systemInformation.getOs()).addLine()
                .addString("Release: ")
                .addCode(this.systemInformation.getOs_release()).addLine().addLine()
                .addHeader("Processor")
                .addMultilineCode(this.systemInformation.getArch()).addLine()
                .addHeader("Java")
                .addMultilineCode(this.systemInformation.getJava_vm_name())
                .addString("Java version: ")
                .addCode(this.systemInformation.getJava_version()).addLine();
        return c.toString();
    }

    /**
     *
     * @param error Exception that needs to be reported
     * @return Error content in markdown
     */
    private String generateErrorContent(Exception error) {
        LocalDateTime time = LocalDateTime.now();
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        error.printStackTrace(pw);

        ContentBuilder c = new ContentBuilder()
                .addHeader("User timestamp")
                .addMultilineCode(time.toString()).addLine()
                .addHeader("Exception summary")
                .addMultilineCode(error.getMessage()).addLine()
                .addHeader("Stacktrace")
                .addMultilineCode(sw.toString());
        try {
            sw.close();
            pw.close();
        }
        catch (Exception e) {
            throw new IllegalStateException("Failed to generate ErrorContent");
        }

        return c.toString();

    }

    /**
     * Reports system information to bugout.dev
     * @param tags additional tags to report
     * @return Report if successfully reported, @null, otherwise
     */
    public Report systemReport(String[] tags) {
        String  title = this.name + " - System information";
        String[] allTags =  Stream.concat(Arrays.stream(getSystemTags()), Arrays.stream(tags))
                                    .toArray(String[]::new);

        Report report = new Report(title, generateSystemContent(), allTags);

        try {
            publish(report);
        }
        catch (Exception e) {
            return null;
        }
        return report;
    }

    /**
     * Reports exception to bugout.dev, adds system information, exception name
     * tags to the report
     * @param exception Exception that needs to be reported
     * @param tags Additional tags to add to report
     * @return
     */
    public Report errorReport(Exception exception,  String[] tags) {
        String title = this.name + " - " + exception.getClass().getName();

        String[] allTags = Stream.concat(Stream.concat(Arrays.stream(getSystemTags()), Arrays.stream(tags)), Arrays.stream(new String[]{"type:error"}))
                .toArray(String[]::new);

        Report r = new Report(title, generateErrorContent(exception), allTags);

        try {
            publish(r);
        }
        catch (Exception e) {
            return null;
        }
        return r;
    }

}
