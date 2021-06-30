# Java humbug library

## How to use:
### Install
* Download source code
* Add `humbug/` folder from `src/humbug/ ` to your project
* Copy dependencies from [dependencies](#dependencies) and add to your exsisting 
java maven project's `pom.xml` file

### Reporting
``` java
import humbug.HumbugConsent;
import humbug.Reporter;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class Example {
    public static void main(String[] args) {
    
        HumbugConsent consent = new HumbugConsent();    
        String token = "<ADD_YOUR_TOKEN_HERE>";   //Your bugout token
        Reporter r = new Reporter(
                "java app",            //Name of reports
                 consent,               //Consent 
                 "<client_id>",         //Client Id
                 "<session_id>",        //Session Id
                 token                  //bugout-dev Integration token
        );

        String[] tags = new String[]{"<app_version>"};

        r.systemReport(tags);  //Reporting system information

        // Exception report examples:
        try {
            int i = 1/0;
        }
        catch (Exception e) {
            r.errorReport(e, tags);
        }

        try {
            InputStream i = new FileInputStream("not_existed_file");
        }
        catch (IOException e) {
            r.systemReport(tags);
            r.errorReport(e, tags);
        }
    }
}
```

## Dependencies:
```xml
<dependency>
  <groupId>org.json</groupId>
  <artifactId>json</artifactId>
  <version>20180130</version>
</dependency>
<dependency>
  <groupId>org.apache.httpcomponents</groupId>
  <artifactId>httpclient</artifactId>
  <version>4.5.13</version>
</dependency>
```
