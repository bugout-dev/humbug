import dev.bugout.humbug.ContentBuilder;
import dev.bugout.humbug.HumbugConsent;
import dev.bugout.humbug.Reporter;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class Example {
    public static void main(String[] args) {

        HumbugConsent c = new HumbugConsent(()-> true, ()-> true);

        String token = "95cfa467-94ae-4891-951b-7874d6a13e2c";

        Reporter r = new Reporter("java app report", c, "200", "201", token);

        r.systemReport("0.0.2", "test");  //Reporting system information

        // Exception report examples:
        try {
            int i = 1/0;
        }
        catch (Exception e) {
            r.errorReport(e, "0.0.2", "test");
        }

        try {
            InputStream i = new FileInputStream("not_existed_file");
        }
        catch (IOException e) {
            r.errorReport(e, "0.0.2", "test");
        }

        //Custom report example
        String content = new ContentBuilder()
                .addHeader("Custom header")
                .addMultilineCode("Testing java")
                .toString();
        r.customReport("Custom title", content, "important", "wtf");


    }
}
